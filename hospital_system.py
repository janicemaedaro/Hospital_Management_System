import uuid
import datetime
from typing import Optional, Any, List, Dict


# --- 1. LINKED LIST IMPLEMENTATION (FOR PATIENT QUEUE) ---

class PatientNode:
    """Represents a patient in the queue."""

    def __init__(self, patient_id: str, name: str, condition: str):
        self.patient_id = patient_id
        self.name = name
        self.condition = condition
        self.next: Optional['PatientNode'] = None

    def to_dict(self) -> Dict[str, str]:
        """Converts patient data to a dictionary for API response."""
        return {"id": self.patient_id, "name": self.name, "condition": self.condition}


class PatientQueue:
    """Implements a FIFO Queue using a Linked List."""

    def __init__(self):
        self.head: Optional[PatientNode] = None
        self.tail: Optional[PatientNode] = None
        self.size: int = 0

    def is_empty(self) -> bool:
        return self.head is None

    def enqueue(self, name: str, condition: str) -> PatientNode:
        """Adds a new patient to the end of the queue (tail)."""
        patient_id = str(uuid.uuid4())[:8]  # Generate a unique, short ID
        new_patient = PatientNode(patient_id, name, condition)

        if self.is_empty():
            self.head = new_patient
            self.tail = new_patient
        else:
            if self.tail:
                self.tail.next = new_patient
            self.tail = new_patient

        self.size += 1
        return new_patient

    def dequeue(self) -> Optional[PatientNode]:
        """Removes and returns the next patient to be treated (head)."""
        if self.is_empty():
            return None

        patient_to_treat = self.head
        self.head = self.head.next

        if self.head is None:
            self.tail = None

        self.size -= 1
        return patient_to_treat

    def to_list(self) -> List[Dict[str, str]]:
        """Returns all patients in the queue as a list of dictionaries."""
        patients = []
        current = self.head
        while current:
            patients.append(current.to_dict())
            current = current.next
        return patients


# --- 2. STACK IMPLEMENTATION (FOR TREATMENT HISTORY) ---

class TreatmentStack:
    """Implements a LIFO Stack for treatment history."""

    def __init__(self):
        self._items: List[dict] = []
        self.patient_id: Optional[str] = None  # Stores the ID of the patient this stack belongs to
        self.initial_condition: str = ""
        self.status: str = "Waiting"
        self.assigned_doctor: Optional[str] = None

    def push(self, treatment_detail: str):
        """Adds a new treatment record to the stack."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._items.append({
            "timestamp": timestamp,
            "detail": treatment_detail
        })

    def pop(self) -> Optional[dict]:
        """Removes and returns the last treatment (undo feature)."""
        if not self._items:
            return None

        return self._items.pop()

    def get_history(self) -> List[dict]:
        """Returns the full treatment history (the underlying list)."""
        return self._items

    def to_dict(self) -> Dict[str, Any]:
        """Returns the full record state."""
        return {
            "patient_id": self.patient_id,
            "condition": self.initial_condition,
            "status": self.status,
            "assigned_doctor": self.assigned_doctor,
            "treatment_history": self._items
        }


# --- 3. TREE IMPLEMENTATION (FOR DOCTOR SPECIALIZATIONS) ---

class SpecializationNode:
    """Represents a department or specialization in the Tree hierarchy."""

    def __init__(self, name: str):
        self.name = name
        # Stores doctors as a dictionary {name: description} internally
        self.doctors: Dict[str, str] = {}
        self.children: List['SpecializationNode'] = []

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the node and its children to a dictionary for JSON output.
        IMPORTANT CHANGE: Transforms the internal doctors dictionary into a
        list of objects to make it iterable for the frontend.
        """
        doctor_list = [
            {"name": name, "description": desc}
            for name, desc in self.doctors.items()
        ]

        return {
            "name": self.name,
            "doctors": doctor_list,  # Now returns a list of objects
            "children": [child.to_dict() for child in self.children]
        }


class SpecializationTree:
    """Implements a Tree to organize hospital departments."""

    def __init__(self, hospital_name: str):
        self.root = SpecializationNode(hospital_name)
        self._seed_structure()

    def _seed_structure(self):
        """Initializes a basic hospital hierarchy with Filipino doctors and descriptions."""
        root_name = self.root.name

        # Level 1: Major Departments
        self.add_specialization(root_name, "Emergency")
        self.add_specialization(root_name, "Internal Medicine")
        self.add_specialization(root_name, "Surgery")

        # Level 2: Sub-specialties
        self.add_specialization("Internal Medicine", "Cardiology")
        self.add_specialization("Internal Medicine", "Dermatology")
        self.add_specialization("Internal Medicine", "Pediatrics")
        self.add_specialization("Surgery", "Orthopedics")

        # Level 3: Further Sub-specialties
        self.add_specialization("Cardiology", "Electrophysiology")
        self.add_specialization("Orthopedics", "Sports Medicine")
        self.add_specialization("Emergency", "Trauma")

        # Assign Filipino Doctors (Dr. / Dra. titles used) with descriptions

        # Emergency Department Doctors (Level 1)
        self.assign_doctor("Emergency", "Dr. Ramon Cruz", "Specializes in immediate care and triage management.")
        self.assign_doctor("Emergency", "Dra. Sofia Reyes", "Lead physician for non-critical emergency cases.")

        # Trauma Doctors (Level 3)
        self.assign_doctor("Trauma", "Dr. Paolo Ocampo",
                           "Expert in severe physical injury and complex trauma protocols.")
        self.assign_doctor("Trauma", "Dra. Lea Perez",
                           "Focuses on stabilization and surgical planning for acute trauma.")

        # Internal Medicine Doctors (Level 1)
        self.assign_doctor("Internal Medicine", "Dr. Antonio Dizon",
                           "General internal medicine and chronic disease management.")
        self.assign_doctor("Internal Medicine", "Dra. Maria Santos",
                           "Focuses on diagnostic challenges and long-term adult care.")

        # Cardiology Doctors (Level 2)
        self.assign_doctor("Cardiology", "Dr. Jose Garcia", "Non-invasive cardiology and heart disease prevention.")

        # Electrophysiology Doctors (Level 3)
        self.assign_doctor("Electrophysiology", "Dra. Christine Lopez",
                           "Specialist in heart rhythm disorders and pacemaker implantation.")

        # Dermatology Doctors (Level 2)
        self.assign_doctor("Dermatology", "Dra. Elena Mendoza",
                           "Expert in complex skin conditions and dermatological procedures.")

        # Pediatrics Doctors (Level 2)
        self.assign_doctor("Pediatrics", "Dra. Leila Gonzales",
                           "Dedicated to pediatric primary care and infectious diseases in children.")

        # Surgery Department Doctors (Level 1)
        self.assign_doctor("Surgery", "Dr. Roberto Lim",
                           "General surgeon with focus on abdominal and soft tissue procedures.")

        # Orthopedics Doctors (Level 2)
        self.assign_doctor("Orthopedics", "Dra. Carmen Ramos",
                           "Specialist in joint replacement and geriatric orthopedic care.")

        # Sports Medicine Doctors (Level 3)
        self.assign_doctor("Sports Medicine", "Dr. Miguel Dela Cruz",
                           "Expert in musculoskeletal injuries and rehabilitation.")

    def add_specialization(self, parent_name: str, child_name: str) -> bool:
        """Adds a new department/specialization under a parent node."""
        parent_node = self._find_node(self.root, parent_name)
        if parent_node:
            new_node = SpecializationNode(child_name)
            parent_node.children.append(new_node)
            return True
        return False

    def assign_doctor(self, specialization_name: str, doctor_name: str, description: str) -> bool:
        """
        Assigns a doctor and their description to a specialization.
        """
        node = self._find_node(self.root, specialization_name)
        if node:
            node.doctors[doctor_name] = description  # Stores as key-value pair
            return True
        return False

    def _find_node(self, current_node: SpecializationNode, name: str) -> Optional[SpecializationNode]:
        """Helper function for Depth-First Search (DFS) to find a node by name."""
        if current_node.name.lower() == name.lower():
            return current_node

        for child in current_node.children:
            result = self._find_node(child, name)
            if result:
                return result
        return None


# --- 4. INTEGRATED HOSPITAL MANAGEMENT SYSTEM ---

class HospitalManagementSystem:
    """
    The main system class integrating the three data structures.
    Manages the state of the hospital demo.
    """

    def __init__(self, hospital_name="City General Hospital"):
        self.hospital_name = hospital_name
        self.patient_queue = PatientQueue()
        # Stores all patients who have ever been registered (including those treated/waiting)
        self.patient_records: dict[str, TreatmentStack] = {}
        self.specializations = SpecializationTree(hospital_name)
        self.current_treatment_id: Optional[str] = None
        self.current_patient_name: Optional[str] = None
        self.current_patient_condition: Optional[str] = None
        self.current_patient_doctor: Optional[str] = None

        # --- Pre-load some patients for the demo ---
        p1 = self.patient_queue.enqueue("Alice Johnson", "Severe fever")
        p2 = self.patient_queue.enqueue("Bob Davis", "Broken arm")
        self.patient_records[p1.patient_id] = TreatmentStack()
        self.patient_records[p1.patient_id].patient_id = p1.patient_id
        self.patient_records[p1.patient_id].initial_condition = p1.condition
        self.patient_records[p2.patient_id] = TreatmentStack()
        self.patient_records[p2.patient_id].patient_id = p2.patient_id
        self.patient_records[p2.patient_id].initial_condition = p2.condition

    def register_patient(self, name: str, condition: str) -> str:
        """Adds a new patient to the queue and creates a record."""
        new_patient = self.patient_queue.enqueue(name, condition)

        new_record = TreatmentStack()
        new_record.patient_id = new_patient.patient_id
        new_record.initial_condition = condition
        self.patient_records[new_patient.patient_id] = new_record
        return new_patient.patient_id

    def treat_next_patient(self) -> Optional[str]:
        """Moves the next patient from the queue to the current treatment slot."""
        patient = self.patient_queue.dequeue()

        # Reset current treatment slot
        self.current_treatment_id = None
        self.current_patient_name = None
        self.current_patient_condition = None
        self.current_patient_doctor = None

        if patient:
            self.current_treatment_id = patient.patient_id
            self.current_patient_name = patient.name
            self.current_patient_condition = patient.condition

            # Update status in the records
            record = self.patient_records[patient.patient_id]
            record.status = "In Treatment"

            # Auto-add initial triage step
            record.push(f"Initial Triage for {patient.condition}.")

            return patient.patient_id
        return None

    def add_treatment_step(self, detail: str) -> bool:
        """Adds a treatment step to the currently treated patient's stack."""
        if not self.current_treatment_id:
            return False

        record = self.patient_records[self.current_treatment_id]
        record.push(detail)
        return True

    def undo_last_treatment(self) -> bool:
        """Undoes the last treatment using the Stack's pop operation."""
        if not self.current_treatment_id:
            return False

        record = self.patient_records[self.current_treatment_id]
        return record.pop() is not None

    def get_status_data(self) -> Dict[str, Any]:
        """Returns the overall system status for UI update."""
        current_record = self.patient_records.get(self.current_treatment_id)

        return {
            "queue_size": self.patient_queue.size,
            "queue_data": self.patient_queue.to_list(),
            "current_patient_id": self.current_treatment_id,
            "current_patient_name": self.current_patient_name,
            "current_patient_condition": self.current_patient_condition,
            "assigned_doctor": current_record.assigned_doctor if current_record else None,
            "history_data": current_record.get_history() if current_record else []
        }

    def get_specialization_tree_data(self) -> Dict[str, Any]:
        """Returns the tree structure for rendering."""
        return {"tree_data": self.specializations.root.to_dict()}

    def get_patient_record(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a full patient record by ID."""
        record = self.patient_records.get(patient_id)
        if not record:
            return None

        # In a real system, you'd have multiple visits. For this demo,
        # we treat the single TreatmentStack as the patient's current visit.
        # We wrap it in a 'full_visits' array for future expansion.
        return {
            "id": patient_id,
            "name": self.get_patient_name_by_id(patient_id),
            "full_visits": [{
                "registration_time": record.get_history()[0]['timestamp'] if record.get_history() else 'N/A',
                "condition": record.initial_condition,
                "status": record.status,
                "assigned_doctor": record.assigned_doctor,
                "treatment_history": record.get_history(),
            }]
        }

    def get_patient_name_by_id(self, patient_id: str) -> str:
        """Tries to find the patient name based on their ID."""
        # This is a hack for the demo since patient data is spread.
        # Try to find it in the queue first
        current = self.patient_queue.head
        while current:
            if current.patient_id == patient_id:
                return current.name
            current = current.next

        # If not in the queue, we can't easily retrieve the name from just the stack object
        # In a real system, this would be retrieved from a main patient database/table.
        # For simplicity, we just use a placeholder if not found in the queue.
        return f"Patient {patient_id}"

    def assign_doctor_to_current(self, doctor_name: str) -> bool:
        """Assigns a doctor to the currently treated patient."""
        if not self.current_treatment_id:
            return False

        record = self.patient_records[self.current_treatment_id]
        record.assigned_doctor = doctor_name
        return True