# database.py
import sqlite3

def setup_database():
    """Builds the database and creates all the empty tables."""
    
    # 1. Open the filing cabinet (this creates the file if it doesn't exist)
    conn = sqlite3.connect('registration.db')
    cursor = conn.cursor()
    print("Warehouse Worker: Opened registration.db")

    # 2. [span_1](start_span)[span_2](start_span)Create the Projects Table[span_1](end_span)[span_2](end_span)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            specialization TEXT NOT NULL,
            prerequisites TEXT, 
            max_students INTEGER DEFAULT 3,
            allocated_students INTEGER DEFAULT 0,
            required_facilities TEXT,
            supervisor TEXT,
            status TEXT DEFAULT 'open'
        )
    ''')

    # 3. [span_3](start_span)Create the Students Table[span_3](end_span)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            program TEXT NOT NULL,
            completed_courses TEXT, 
            gpa REAL NOT NULL
        )
    ''')

    # 4. [span_4](start_span)Create the Teams Table[span_4](end_span)
    # We leave project_id blank (NULL) until they actually register for one.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            project_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
    ''')

    # 5. [span_5](start_span)Create the Team Members linking table[span_5](end_span)
    # This links the 3 students to their specific team.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            team_id INTEGER,
            student_id TEXT UNIQUE,
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # 6. [span_6](start_span)Create the Faculty Table[span_6](end_span)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            max_supervisions INTEGER DEFAULT 3,
            current_supervisions INTEGER DEFAULT 0
        )
    ''')

    # 7. [span_7](start_span)Create the Facilities Table[span_7](end_span)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facilities (
            facility_name TEXT PRIMARY KEY,
            capacity INTEGER NOT NULL,
            booked_slots INTEGER DEFAULT 0
        )
    ''')

    # Save the changes and close the cabinet
    conn.commit()
    conn.close()
    print("Warehouse Worker: All tables created successfully! The database is ready.")

# When you run this file directly, it will trigger the setup function.
if __name__ == '__main__':
    setup_database()