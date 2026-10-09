# system.py
import sqlite3
import bcrypt 
from models import Student, Project, Team, Faculty, Facility

class RegistrationSystem:
    """The Manager class that controls the rules and talks to the database."""
    
    # ==========================================
    # GLOBAL SYSTEM SETTINGS
    # ==========================================
    MASTER_ADMIN_EMAIL = 'admin' 
    
    def __init__(self):
        self.conn = sqlite3.connect('registration.db')
        self.cursor = self.conn.cursor()
        
        # --- THE BLUEPRINTS ---
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS projects (project_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, description TEXT, specialization TEXT, prerequisites TEXT, required_facilities TEXT, supervisor TEXT, creator_email TEXT, status TEXT DEFAULT 'open', allocated_students INTEGER DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS teams (team_id INTEGER PRIMARY KEY AUTOINCREMENT, team_name TEXT UNIQUE, project_id INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS team_members (team_id INTEGER, student_id TEXT, PRIMARY KEY (team_id, student_id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS faculty (faculty_id TEXT PRIMARY KEY, name TEXT, email TEXT, department TEXT, max_supervisions INTEGER, current_supervisions INTEGER DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS facilities (facility_name TEXT PRIMARY KEY, capacity INTEGER, booked_slots INTEGER DEFAULT 0)''')
        
        # --- SECURITY & LOGGING BLUEPRINTS ---
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, user TEXT, action TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, role TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS student_subjects (email TEXT, subject TEXT, PRIMARY KEY(email, subject))''')
        
        # --- DEFAULT SECURE ACCOUNTS ---
        def hash_default(pwd):
            return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
        admin_hash = hash_default('123') 
        fac_hash = hash_default('faculty123')
        stu_hash = hash_default('student123')
        ahmed_hash = hash_default('pass')
        omar_hash = hash_default('pass')

        self.cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 'Admin')", (self.MASTER_ADMIN_EMAIL, admin_hash))
        
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES ('faculty@uni.edu', ?, 'Faculty')", (fac_hash,))
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES ('student@uni.edu', ?, 'Student')", (stu_hash,))
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES ('ahmed@kau.edu.sa', ?, 'Student')", (ahmed_hash,)) 
        self.cursor.execute("INSERT OR IGNORE INTO users VALUES ('omar@kau.edu.sa', ?, 'Student')", (omar_hash,)) 
        
        # Give testing accounts all subjects so you can still test freely!
        test_students = ['student@uni.edu', 'ahmed@kau.edu.sa', 'omar@kau.edu.sa']
        foundational_subs = ['Math', 'Circuits', 'Programming', 'Systems', 'Design']
        for s in test_students:
            for sub in foundational_subs:
                self.cursor.execute("INSERT OR IGNORE INTO student_subjects VALUES (?, ?)", (s, sub))
        
        self.conn.commit()
        print("System Manager: Connected to the database. Full Architecture & Cryptographic Security active.")

    # ---------------------------------------------------------
    # UPGRADED AUTHENTICATION (CRASH-PROOFED)
    # ---------------------------------------------------------
    def verify_login(self, email, password, role):
        self.cursor.execute("SELECT password FROM users WHERE email = ? AND role = ?", (email, role))
        row = self.cursor.fetchone()
        
        if row:
            stored_hash = row[0].encode('utf-8')
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return True
            except ValueError:
                print(f"CRITICAL WARNING: Found an old plain-text password for {email}. Please ensure registration.db is deleted!")
                return False
        return False

    def register_user(self, email, password, role, subjects=None):
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            self.cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, hashed_password, role))
            
            if role == "Student" and subjects:
                for sub in subjects:
                    self.cursor.execute("INSERT INTO student_subjects (email, subject) VALUES (?, ?)", (email, sub))
                    
            self.conn.commit()
            self.log_activity(role, email, "Created a new secure account.")
            return "Success: Account created successfully!"
        except sqlite3.IntegrityError:
            return "Error: An account with this email already exists."

    # ---------------------------------------------------------
    # SECURE METHODS FOR FACULTY
    # ---------------------------------------------------------
    def add_project(self, project, creator_email=""):
        prereqs_str = ",".join(project.prerequisites) if project.prerequisites else ""
        try:
            self.cursor.execute('''
                INSERT INTO projects (title, description, specialization, prerequisites, required_facilities, supervisor, creator_email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (project.title, project.description, project.specialization, prereqs_str, project.required_facilities, creator_email, creator_email))
            self.conn.commit()
            project.project_id = self.cursor.lastrowid 
            return "Success: Project added to the database."
        except sqlite3.IntegrityError:
            return "Error: Project title already exists."

    def get_faculty_projects(self, creator_email):
        self.cursor.execute("SELECT project_id, title, specialization, status, allocated_students FROM projects WHERE creator_email = ?", (creator_email,))
        return self.cursor.fetchall()

    def get_project_by_id(self, project_id):
        self.cursor.execute('''
            SELECT project_id, title, description, specialization, prerequisites, required_facilities, supervisor 
            FROM projects 
            WHERE project_id = ?
        ''', (project_id,))
        return self.cursor.fetchone()

    def update_own_project(self, project_id, title, desc, spec, prereqs, lab, creator_email):
        self.cursor.execute("SELECT project_id FROM projects WHERE title = ? AND project_id != ?", (title, project_id))
        if self.cursor.fetchone(): return "Error: Title already exists."

        self.cursor.execute('''
            UPDATE projects 
            SET title = ?, description = ?, specialization = ?, prerequisites = ?, required_facilities = ?, supervisor = ?
            WHERE project_id = ? AND creator_email = ?
        ''', (title, desc, spec, prereqs, lab, creator_email, project_id, creator_email))
        self.conn.commit()
        return "Success: Your project was updated successfully."

    def delete_own_project(self, project_id, creator_email):
        self.cursor.execute("DELETE FROM projects WHERE project_id = ? AND creator_email = ?", (project_id, creator_email))
        self.conn.commit()
        return "Success: Your project was permanently deleted."

    def get_faculty_students(self, faculty_email):
        self.cursor.execute('''
            SELECT tm.student_id, p.title, t.team_name, p.status
            FROM projects p
            JOIN teams t ON p.project_id = t.project_id
            JOIN team_members tm ON t.team_id = tm.team_id
            WHERE p.creator_email = ?
            ORDER BY p.status DESC, p.title ASC
        ''', (faculty_email,))
        return self.cursor.fetchall()

    def mark_project_completed(self, project_id, faculty_email=None):
        if faculty_email:
            self.cursor.execute("SELECT creator_email FROM projects WHERE project_id = ?", (project_id,))
            proj = self.cursor.fetchone()
            if not proj or proj[0] != faculty_email:
                return "Error: You can only complete your own projects."

        self.cursor.execute("SELECT status FROM projects WHERE project_id = ?", (project_id,))
        status = self.cursor.fetchone()
        if not status: return "Error: Project not found."
        if status[0] == 'completed': return "Error: Project is already marked as completed."

        self.cursor.execute("UPDATE projects SET status = 'completed' WHERE project_id = ?", (project_id,))
        self.conn.commit()
        return f"Success: Project {project_id} is now officially Completed!"

    # ---------------------------------------------------------
    # METHODS FOR STUDENTS
    # ---------------------------------------------------------
    def get_all_students(self):
        self.cursor.execute("SELECT email FROM users WHERE role = 'Student'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_student_project(self, student_email):
        self.cursor.execute('''
            SELECT p.project_id, p.title, p.status
            FROM projects p
            JOIN teams t ON p.project_id = t.project_id
            JOIN team_members tm ON t.team_id = tm.team_id
            WHERE tm.student_id = ?
        ''', (student_email,))
        return self.cursor.fetchone()

    def get_available_projects(self, specialization):
        self.cursor.execute('''
            SELECT project_id, title, description, specialization, prerequisites, required_facilities, supervisor 
            FROM projects 
            WHERE specialization = ? AND status = 'open'
        ''', (specialization,))
        rows = self.cursor.fetchall()
        project_list = []
        for row in rows:
            prereq_list = row[4].split(",") if row[4] else []
            proj = Project(row[0], row[1], row[2], row[3], prereq_list, row[5], row[6])
            project_list.append(proj)
        return project_list

    def create_team(self, team, project_id):
        if len(team.members) != 3: return "Error: A team must have exactly 3 members."
            
        for student in team.members:
            if self.get_student_project(student.student_id):
                return f"Registration Failed: Student {student.student_id} is already registered for a graduation project."

        self.cursor.execute("SELECT prerequisites FROM projects WHERE project_id = ?", (project_id,))
        proj_data = self.cursor.fetchone()
        if not proj_data: return "Error: Project not found."
            
        prereqs = proj_data[0]
        if prereqs:
            required_subjects = [r.strip() for r in prereqs.split(',') if r.strip()]
            for student in team.members:
                self.cursor.execute("SELECT subject FROM student_subjects WHERE email = ?", (student.student_id,))
                completed = [row[0] for row in self.cursor.fetchall()]
                
                missing_subjects = [req for req in required_subjects if req not in completed]
                if missing_subjects:
                    missing_str = ", ".join(missing_subjects)
                    return f"Registration Failed: Student {student.student_id} is missing foundational subjects: {missing_str}."

        try:
            self.cursor.execute("INSERT INTO teams (team_name, project_id) VALUES (?, ?)", (team.team_name, project_id))
            team_id = self.cursor.lastrowid
            
            for student in team.members:
                self.cursor.execute("INSERT INTO team_members (team_id, student_id) VALUES (?, ?)", (team_id, student.student_id))
                
            self.cursor.execute("UPDATE projects SET allocated_students = allocated_students + 3 WHERE project_id = ?", (project_id,))
            self.conn.commit()
            return "Success: Team successfully registered for the graduation project!"
        except sqlite3.IntegrityError:
            return "Error: Database Integrity Error."

    def get_team_by_id(self, team_id):
        self.cursor.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,))
        team_data = self.cursor.fetchone()
        if team_data:
            return f"Team found: {team_data[1]} (Project ID: {team_data[2]})"
        return "Error: Team not found."

    # ---------------------------------------------------------
    # METHODS FOR ADMIN 
    # ---------------------------------------------------------
    def get_team_students(self, team_id):
        self.cursor.execute("SELECT student_id FROM team_members WHERE team_id = ?", (team_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def delete_project(self, project_id):
        self.cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        self.conn.commit()
        return "Success: Project deleted by Admin."

    def get_all_projects(self):
        self.cursor.execute("SELECT project_id, title, supervisor, status, allocated_students FROM projects")
        return self.cursor.fetchall()

    def get_all_teams(self):
        self.cursor.execute('''
            SELECT t.team_id, t.team_name, t.project_id, p.status 
            FROM teams t 
            LEFT JOIN projects p ON t.project_id = p.project_id
        ''')
        return self.cursor.fetchall()

    def log_activity(self, role, user, action):
        self.cursor.execute("INSERT INTO audit_logs (role, user, action) VALUES (?, ?, ?)", (role, user, action))
        self.conn.commit()

    def get_audit_logs(self):
        self.cursor.execute("SELECT log_id, role, user, action, timestamp FROM audit_logs ORDER BY timestamp DESC")
        return self.cursor.fetchall()

    def get_all_users(self):
        self.cursor.execute('''
            SELECT u.email, u.role, p.status, t.team_name
            FROM users u
            LEFT JOIN team_members tm ON u.email = tm.student_id
            LEFT JOIN teams t ON tm.team_id = t.team_id
            LEFT JOIN projects p ON t.project_id = p.project_id
            ORDER BY u.role ASC, u.email ASC
        ''')
        return self.cursor.fetchall()

    def delete_user(self, email):
        if email == self.MASTER_ADMIN_EMAIL: 
            return "Error: You cannot delete the master Admin account!"
            
        self.cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        self.conn.commit()
        return f"Success: Account {email} has been deleted."

    def delete_team(self, team_id):
        self.cursor.execute("DELETE FROM team_members WHERE team_id = ?", (team_id,))
        self.cursor.execute("DELETE FROM teams WHERE team_id = ?", (team_id,))
        self.conn.commit()
        return f"Success: Team {team_id} deleted."

    def delete_log(self, log_id):
        self.cursor.execute("DELETE FROM audit_logs WHERE log_id = ?", (log_id,))
        self.conn.commit()
        return f"Success: Log record deleted."