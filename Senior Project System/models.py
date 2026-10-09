# models.py

class Student:
    """Blueprint for a student user."""
    # The __init__ function is called automatically when you create a new Student.
    # It takes the input data and saves it into the student's "ID card" (attributes).
    def __init__(self, student_id, name, email, program, completed_courses, gpa):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.program = program
        self.completed_courses = completed_courses  # This is a list of strings, e.g., ["EE201", "IE255"]
        self.gpa = gpa
    
    # [span_1](start_span)Method to check if the student has passed a specific course[span_1](end_span).
    def has_passed(self, course_code):
        if course_code in self.completed_courses:
            return True
        return False


class Project:
    """Blueprint for a graduation project proposed by faculty."""
    def __init__(self, project_id, title, description, specialization, prerequisites, required_facilities, supervisor):
        self.project_id = project_id
        self.title = title
        self.description = description
        self.specialization = specialization
        self.prerequisites = prerequisites  # A list of required course codes
        self.max_students = 3               # Locked at 3 as per the project rules[span_2](end_span)
        self.allocated_students = 0         # Starts at 0 until students register
        self.required_facilities = required_facilities
        self.supervisor = supervisor
        self.status = "open"                # Can be "open" or "closed"

    # [span_3](start_span)Method to check if the project is full[span_3](end_span).
    def is_full(self):
        if self.allocated_students >= self.max_students:
            return True
        return False
        
    # [span_4](start_span)Method to verify if a team is allowed to take this project[span_4](end_span).
    def check_eligibility(self, team):
        # First, check if the project is already full.
        if self.is_full():
            return False
        # Second, ask the team object if all members meet the prerequisites.
        if not team.check_prerequisites(self):
            return False
        return True


class Team:
    """Blueprint for a student team."""
    def __init__(self, team_id, team_name):
        self.team_id = team_id
        self.team_name = team_name
        self.members = []   # An empty list that will hold Student objects[span_5](end_span)
        self.project = None # Will hold the project_id once they register[span_6](end_span)

    # [span_7](start_span)Method to add a student to the team, ensuring max 3 members[span_7](end_span).
    def add_member(self, student):
        if len(self.members) < 3:
            self.members.append(student)
            return True
        return False

    # [span_8](start_span)Method to remove a student from the team[span_8](end_span).
    def remove_member(self, student):
        if student in self.members:
            self.members.remove(student)

    # [span_9](start_span)Method to verify all members have passed the project's prerequisites[span_9](end_span).
    def check_prerequisites(self, project):
        for member in self.members:
            for course in project.prerequisites:
                if not member.has_passed(course):
                    return False # If even one member fails one prerequisite, return False
        return True


class Faculty:
    """Blueprint for a faculty member (supervisor)."""
    def __init__(self, faculty_id, name, email, department, max_supervisions=3):
        self.faculty_id = faculty_id
        self.name = name
        self.email = email
        self.department = department
        self.max_supervisions = max_supervisions  # Default max is 3 projects[span_10](end_span)
        self.current_supervisions = 0             # Tracker for their current load[span_11](end_span)

    # [span_12](start_span)Method to verify if the faculty can take on more teams[span_12](end_span).
    def can_supervise(self):
        if self.current_supervisions < self.max_supervisions:
            return True
        return False


class Facility:
    """Blueprint for a required lab or room."""
    def __init__(self, facility_name, capacity):
        self.facility_name = facility_name
        self.capacity = capacity
        self.booked_slots = 0  # Starts at 0[span_13](end_span)