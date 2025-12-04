from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
import os

# Note: Using 'hospital_system' filename as provided in the context
from hospital_system import HospitalManagementSystem

# --- Flask Setup ---
# Calculate the absolute path to the templates folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Initialize Flask, explicitly setting the template_folder path
app = Flask(__name__, template_folder=TEMPLATE_DIR)

# IMPORTANT: Set a secret key for sessions (needed for login and redirects)
app.secret_key = 'a_very_secret_key_for_hospital_mgmt_system'

# Initialize the core hospital system instance
hms = HospitalManagementSystem()

# --- Placeholder for simple authentication (Now a list to store multiple users) ---
MOCK_USERS = [
    {"username": "admin", "password": "password123"}  # Default user
]


# --- Routes ---

@app.route('/')
def root_redirect():
    """Redirects the root path to the login page."""
    # Ensure all endpoints use url_for()
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """
    Handles displaying the login form (GET) and processing credentials (POST).
    """
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check credentials against the list of MOCK_USERS
        user_found = next(
            (user for user in MOCK_USERS if user["username"] == username and user["password"] == password), None)

        if user_found:
            session['logged_in'] = True
            session['username'] = username
            # Redirect to the main application page
            return redirect(url_for('main_app_page'))
        else:
            error = 'Invalid Credentials. Please try again.'

    # Render the login page using the explicitly defined template folder
    return render_template('login.html', error=error)


@app.route('/index.html')
def main_app_page():
    """
    Serves the static index.html file, which is the main application dashboard.
    """
    # Simple check to ensure user is logged in before accessing the app
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    # Ensure a patient is ready for treatment upon entering the dashboard
    if not hms.current_treatment_id and hms.patient_queue.size > 0:
        hms.treat_next_patient()

        # Render the main application page
    return render_template('index.html')


@app.route('/logout')
def logout():
    """Clears the session and redirects to the login page."""
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login_page'))


@app.route('/home.html')
def home_page():
    """Serves the home.html file."""
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """
    Renders the registration page (GET) or processes the registration data (POST)
    and saves the new user temporarily.
    """
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            error = "Username and password are required."
            return render_template('register.html', error=error)

        # Check if user already exists
        if any(user['username'] == username for user in MOCK_USERS):
            error = "Username already exists. Please choose another."
            return render_template('register.html', error=error)

        # Store the new user credentials temporarily in memory
        MOCK_USERS.append({"username": username, "password": password})
        print(f"Registered new user: {username}. Total users: {len(MOCK_USERS)}")

        # Redirect to the login page after successful registration
        return redirect(url_for('login_page'))

    # Render the registration form for GET requests
    return render_template('register.html')


# --- API Endpoints ---
# (API endpoints remain unchanged)
@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the current status of the queue, current patient, and treatment history."""
    try:
        data = hms.get_status_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error fetching status: {str(e)}"})


@app.route('/api/register', methods=['POST'])
def register_patient():
    """Endpoint for registering a new patient (Queue enqueue)."""
    try:
        data = request.json
        name = data.get('name')
        condition = data.get('condition')

        if not name or not condition:
            return jsonify({"status": "error", "message": "Missing name or condition."}), 400

        hms.register_patient(name, condition)
        return jsonify({"status": "success", "message": f"Patient {name} registered to Triage queue."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Registration failed: {str(e)}"})


@app.route('/api/treat_next', methods=['POST'])
def treat_next():
    """Endpoint to start treating the next patient (Queue dequeue)."""
    try:
        # NOTE: The updated treat_next_patient() no longer requires an argument.
        patient_id = hms.treat_next_patient()

        if patient_id:
            # hms.current_treatment_id is now managed inside the class instance.
            return jsonify({"status": "success", "message": f"Started treating patient ID: {patient_id}"})
        else:
            return jsonify({"status": "info", "message": "Queue is empty. No patient to treat."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Treatment start failed: {str(e)}"})


@app.route('/api/add_treatment', methods=['POST'])
def add_treatment():
    """Endpoint to add a step to the current patient's history (Stack push)."""
    try:
        detail = request.json.get('detail')
        if not hms.current_treatment_id:
            return jsonify({"status": "error", "message": "No patient currently selected for treatment."}), 400

        # Add treatment step relies on the internal current_treatment_id
        if hms.add_treatment_step(detail):
            return jsonify({"status": "success", "message": "Treatment step recorded."})
        else:
            return jsonify({"status": "error", "message": "Failed to record treatment step."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Adding treatment failed: {str(e)}"})


@app.route('/api/undo_treatment', methods=['POST'])
def undo_treatment():
    """Endpoint to undo the last treatment step (Stack pop)."""
    try:
        if not hms.current_treatment_id:
            return jsonify({"status": "error", "message": "No patient currently selected for treatment."}), 400

        if hms.undo_last_treatment():
            return jsonify({"status": "info", "message": "Last treatment step successfully undone."})
        else:
            return jsonify({"status": "info", "message": "Treatment history is empty. Nothing to undo."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Undo failed: {str(e)}"})


@app.route('/api/specializations', methods=['GET'])
def get_specializations():
    """Endpoint to get the doctor specialization tree structure."""
    try:
        # The new tree structure method returns the data directly
        data = hms.get_specialization_tree_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error fetching specializations: {str(e)}"})


@app.route('/api/assign_doctor', methods=['POST'])
def assign_doctor():
    """Endpoint to assign a doctor to the currently treated patient."""
    try:
        doctor_name = request.json.get('doctor_name')
        if not hms.current_treatment_id:
            return jsonify({"status": "error", "message": "Please start treating a patient first."}), 400

        # The new assign_doctor method relies on the internal current_treatment_id
        if hms.assign_doctor_to_current(doctor_name):
            return jsonify({"status": "success", "message": f"Doctor {doctor_name} assigned to current patient."})
        else:
            return jsonify({"status": "error", "message": "Failed to assign doctor."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Assignment failed: {str(e)}"})


@app.route('/api/patient_record/<patient_id>', methods=['GET'])
def get_patient_record(patient_id):
    """Endpoint to retrieve a specific patient's full record."""
    try:
        record = hms.get_patient_record(patient_id)
        if record:
            return jsonify(record)
        else:
            return jsonify({"status": "error", "message": "Patient record not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error retrieving record: {str(e)}"}), 500


if __name__ == '__main__':
    # Hospital structure initialization is handled automatically within
    # the HospitalManagementSystem() class upon instantiation.
    app.run(debug=True)