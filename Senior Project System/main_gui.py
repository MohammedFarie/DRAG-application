# main_gui.py
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor 
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QMessageBox, 
                             QLineEdit, QFormLayout, QStackedWidget, QComboBox, 
                             QListWidgetItem, QCheckBox) # Added QCheckBox!
from system import RegistrationSystem
from models import Project, Team, Student

class MainWindow(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("ECE Graduation Project Registration System")
        self.setGeometry(100, 100, 750, 650) 

        self.current_user_email = "" 
        self.available_teammates = [] 

        self.stack = QStackedWidget(self)
        
        self.login_screen = self.build_login_screen()
        self.student_screen = self.build_student_screen()
        self.faculty_screen = self.build_faculty_screen()
        self.admin_screen = self.build_admin_screen()
        self.register_screen = self.build_register_screen()

        self.stack.addWidget(self.login_screen)    
        self.stack.addWidget(self.student_screen)  
        self.stack.addWidget(self.faculty_screen)  
        self.stack.addWidget(self.admin_screen)    
        self.stack.addWidget(self.register_screen) 

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    # ==========================================
    # SHARED UI FUNCTIONS
    # ==========================================
    def view_project_details(self, list_widget):
        selected_item = list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a project from the list first.")
            return
            
        text = selected_item.text()
        
        if "Project ID:" not in text and not text.startswith("ID:"):
            QMessageBox.warning(self, "Error", "Please select a Project to view its details.")
            return

        try:
            proj_id = int(text.split("|")[0].split(":")[1].strip())
            proj_data = self.backend.get_project_by_id(proj_id)
            
            if proj_data:
                title = str(proj_data[1]) if proj_data[1] else "N/A"
                desc = str(proj_data[2]) if proj_data[2] else "No description provided."
                prereq_val = str(proj_data[4]) if proj_data[4] else "None"
                prereqs = prereq_val if prereq_val != "None" else "None"
                lab = str(proj_data[5]) if proj_data[5] else "None"
                sup = str(proj_data[6]) if proj_data[6] else "Unknown"

                details = (
                    f"Title: {title}\n"
                    f"Supervisor: {sup}\n"
                    f"Facility/Lab: {lab}\n"
                    f"Required Foundational Subjects: {prereqs}\n"
                    f"{'-'*40}\n"
                    f"Description:\n{desc}"
                )
                
                msg = QMessageBox(self)
                msg.setWindowTitle("Subject Details")
                msg.setText(details)
                msg.exec_()
            else:
                QMessageBox.warning(self, "Error", "Project not found in the database.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load project details: {str(e)}")

    # ==========================================
    # 1. LOGIN SCREEN
    # ==========================================
    def build_login_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Welcome to the ECE Project Portal</h2>"))

        form = QFormLayout()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["Student", "Faculty", "Admin"])

        form.addRow("Email:", self.email_input)
        form.addRow("Password:", self.password_input)
        form.addRow("Role:", self.role_dropdown)
        layout.addLayout(form)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("Create New Account")
        register_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        layout.addWidget(register_btn)

        widget.setLayout(layout)
        return widget

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        role = self.role_dropdown.currentText()

        if self.backend.verify_login(email, password, role):
            self.current_user_email = email 
            
            if role == "Student":
                self.stack.setCurrentIndex(1)
                self.student_refresh_data() 
            elif role == "Faculty":
                self.stack.setCurrentIndex(2)
                self.faculty_refresh_list() 
            elif role == "Admin":
                self.stack.setCurrentIndex(3)
                self.admin_view_projects() 
            self.password_input.clear() 
        else:
            QMessageBox.warning(self, "Access Denied", "Incorrect email, password, or role!")

    def handle_logout(self):
        self.current_user_email = ""
        self.stack.setCurrentIndex(0)

    # ==========================================
    # 2. REGISTRATION SCREEN (UPGRADED WITH CHECKBOXES)
    # ==========================================
    def build_register_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Register New Account</h2>"))

        form = QFormLayout()
        self.reg_email_input = QLineEdit(placeholderText="example@kau.edu.sa")
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_role_dropdown = QComboBox()
        self.reg_role_dropdown.addItems(["Student", "Faculty", "Admin"])

        form.addRow("Email:", self.reg_email_input)
        form.addRow("Password:", self.reg_password_input)
        form.addRow("Role:", self.reg_role_dropdown)
        layout.addLayout(form)
        
        # UPGRADE: Academic Checklist for Students
        layout.addWidget(QLabel("<b>Foundational Subjects Passed (Students Only):</b>"))
        checkbox_layout = QHBoxLayout()
        self.reg_cb_math = QCheckBox("Math")
        self.reg_cb_circuits = QCheckBox("Circuits")
        self.reg_cb_prog = QCheckBox("Programming")
        self.reg_cb_systems = QCheckBox("Systems")
        self.reg_cb_design = QCheckBox("Design")
        
        checkbox_layout.addWidget(self.reg_cb_math)
        checkbox_layout.addWidget(self.reg_cb_circuits)
        checkbox_layout.addWidget(self.reg_cb_prog)
        checkbox_layout.addWidget(self.reg_cb_systems)
        checkbox_layout.addWidget(self.reg_cb_design)
        layout.addLayout(checkbox_layout)

        submit_reg_btn = QPushButton("Submit Registration")
        submit_reg_btn.clicked.connect(self.submit_registration)
        layout.addWidget(submit_reg_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back_btn)

        widget.setLayout(layout)
        return widget

    def submit_registration(self):
        email = self.reg_email_input.text()
        password = self.reg_password_input.text()
        role = self.reg_role_dropdown.currentText()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill out all fields.")
            return

        subjects = []
        if role == "Student":
            if self.reg_cb_math.isChecked(): subjects.append("Math")
            if self.reg_cb_circuits.isChecked(): subjects.append("Circuits")
            if self.reg_cb_prog.isChecked(): subjects.append("Programming")
            if self.reg_cb_systems.isChecked(): subjects.append("Systems")
            if self.reg_cb_design.isChecked(): subjects.append("Design")

        result = self.backend.register_user(email, password, role, subjects)
        QMessageBox.information(self, "Registration Result", result)

        if "Success" in result:
            self.reg_email_input.clear()
            self.reg_password_input.clear()
            
            # Reset checkboxes
            self.reg_cb_math.setChecked(False)
            self.reg_cb_circuits.setChecked(False)
            self.reg_cb_prog.setChecked(False)
            self.reg_cb_systems.setChecked(False)
            self.reg_cb_design.setChecked(False)
            
            self.stack.setCurrentIndex(0) 

    # ==========================================
    # 3. STUDENT DASHBOARD 
    # ==========================================
    def build_student_screen(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.student_header = QLabel("<h2>Student Dashboard</h2>")
        self.student_header.setAlignment(Qt.AlignCenter) 
        main_layout.addWidget(self.student_header)

        self.student_content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Select Specialization:"))
        self.student_spec_dropdown = QComboBox()
        self.student_spec_dropdown.addItems(["Computer", "Communications", "Power", "Biomedical"])
        filter_layout.addWidget(self.student_spec_dropdown)
        content_layout.addLayout(filter_layout)

        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Load Available Projects")
        load_btn.clicked.connect(self.load_projects)
        btn_layout.addWidget(load_btn)

        details_btn = QPushButton("View Project Details")
        details_btn.clicked.connect(lambda: self.view_project_details(self.project_list))
        btn_layout.addWidget(details_btn)
        content_layout.addLayout(btn_layout)

        self.project_list = QListWidget()
        content_layout.addWidget(self.project_list)

        reg_layout = QVBoxLayout()
        reg_layout.setContentsMargins(0,0,0,0)
        
        reg_layout.addWidget(QLabel("<b>1. Click a Project from the list above, then 2. Register Your Team Below</b>"))
        form = QFormLayout()
        
        self.team_name_input = QLineEdit()
        self.student1_dropdown = QComboBox()
        self.student1_dropdown.setEnabled(False) 
        self.student2_dropdown = QComboBox()
        self.student3_dropdown = QComboBox()

        self.student2_dropdown.currentTextChanged.connect(self.sync_student_dropdowns)
        self.student3_dropdown.currentTextChanged.connect(self.sync_student_dropdowns)

        form.addRow("Team Name:", self.team_name_input)
        form.addRow("Member 1 (You):", self.student1_dropdown)
        form.addRow("Member 2:", self.student2_dropdown)
        form.addRow("Member 3:", self.student3_dropdown)
        reg_layout.addLayout(form)

        submit_btn = QPushButton("Form Team & Register")
        submit_btn.clicked.connect(self.register_team_gui)
        reg_layout.addWidget(submit_btn)
        
        content_layout.addLayout(reg_layout)
        
        self.student_content_widget.setLayout(content_layout)
        main_layout.addWidget(self.student_content_widget) 

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        main_layout.addWidget(logout_btn)

        widget.setLayout(main_layout)
        return widget

    def student_refresh_data(self):
        proj = self.backend.get_student_project(self.current_user_email)
        
        if proj:
            self.student_content_widget.setVisible(False)
            if proj[2] == "completed":
                self.student_header.setText(
                    "<br><br><br>"
                    "<h1 style='color:green;'>🎉 CONGRATULATIONS! 🎉</h1>"
                    "<h3>You have successfully completed your Graduation Project:</h3>"
                    f"<h2 style='color:darkblue;'>{proj[1]}</h2>"
                    "<h3>You are officially cleared for graduation!</h3>"
                    "<br><br><br>"
                )
            else:
                self.student_header.setText(
                    "<br><br><br>"
                    "<h2>Student Dashboard</h2>"
                    "<h3 style='color:orange;'>Status: IN PROGRESS</h3>"
                    "<h3>You are currently working on:</h3>"
                    f"<h2 style='color:darkblue;'>{proj[1]}</h2>"
                    "<h3>Focus on your project. You cannot join other teams.</h3>"
                    "<br><br><br>"
                )
            return
        else:
            self.student_header.setText("<h2>Student Dashboard</h2>")
            self.student_content_widget.setVisible(True)

        self.load_projects()
        all_students = self.backend.get_all_students()
        self.available_teammates = [s for s in all_students if s != self.current_user_email]
        
        self.student1_dropdown.clear()
        self.student1_dropdown.addItem(self.current_user_email)
        self.student1_dropdown.setCurrentText(self.current_user_email)

        self.student2_dropdown.blockSignals(True)
        self.student3_dropdown.blockSignals(True)

        self.student2_dropdown.clear()
        self.student2_dropdown.addItem("Select Teammate...")
        self.student2_dropdown.addItems(self.available_teammates)

        self.student3_dropdown.clear()
        self.student3_dropdown.addItem("Select Teammate...")
        self.student3_dropdown.addItems(self.available_teammates)

        self.student2_dropdown.blockSignals(False)
        self.student3_dropdown.blockSignals(False)

    def sync_student_dropdowns(self):
        s2_selected = self.student2_dropdown.currentText()
        s3_selected = self.student3_dropdown.currentText()
        
        self.student2_dropdown.blockSignals(True)
        self.student3_dropdown.blockSignals(True)
        
        self.student2_dropdown.clear()
        self.student2_dropdown.addItem("Select Teammate...")
        for s in self.available_teammates:
            if s != s3_selected or s3_selected == "Select Teammate...": 
                self.student2_dropdown.addItem(s)
        self.student2_dropdown.setCurrentText(s2_selected if s2_selected != s3_selected else "Select Teammate...")
        
        self.student3_dropdown.clear()
        self.student3_dropdown.addItem("Select Teammate...")
        for s in self.available_teammates:
            if s != s2_selected or s2_selected == "Select Teammate...": 
                self.student3_dropdown.addItem(s)
        self.student3_dropdown.setCurrentText(s3_selected if s3_selected != s2_selected else "Select Teammate...")
        
        self.student2_dropdown.blockSignals(False)
        self.student3_dropdown.blockSignals(False)

    def load_projects(self):
        self.project_list.clear()
        selected_major = self.student_spec_dropdown.currentText()
        projects = self.backend.get_available_projects(selected_major)
        for proj in projects:
            text = f"ID: {proj.project_id} | Title: {proj.title} | Supervisor: {proj.supervisor}"
            self.project_list.addItem(text)

    def register_team_gui(self):
        selected_project = self.project_list.currentItem()
        if not selected_project:
            QMessageBox.warning(self, "Error", "Please select a Project from the list above!")
            return
            
        proj_text = selected_project.text()
        if "ID:" not in proj_text:
            QMessageBox.warning(self, "Error", "Invalid project selected.")
            return
            
        proj_id = int(proj_text.split("|")[0].split(":")[1].strip())
        
        team_name = self.team_name_input.text()
        s1 = self.student1_dropdown.currentText()
        s2 = self.student2_dropdown.currentText()
        s3 = self.student3_dropdown.currentText()
        
        if not team_name:
            QMessageBox.warning(self, "Error", "Team Name must be filled!")
            return
            
        if s2 == "Select Teammate..." or s3 == "Select Teammate...":
            QMessageBox.warning(self, "Error", "Please select valid teammates from the dropdown!")
            return
            
        new_team = Team(team_id=None, team_name=team_name)
        new_team.add_member(Student(s1, "S1", s1, "Computer", ["EE202"], 4.0))
        new_team.add_member(Student(s2, "S2", s2, "Computer", ["EE202"], 4.0))
        new_team.add_member(Student(s3, "S3", s3, "Computer", ["EE202"], 4.0))

        result = self.backend.create_team(new_team, proj_id)
        
        if "Success" in result:
            self.backend.log_activity("Student", team_name, f"Registered team for Project {proj_id}")
            self.team_name_input.clear()
            self.student_refresh_data()
        else:
            # Displays the missing prerequisites error visually if it fails!
            QMessageBox.warning(self, "Registration Blocked", result)
            return
            
        QMessageBox.information(self, "Result", result)

    # ==========================================
    # 4. FACULTY DASHBOARD (UPGRADED WITH CHECKBOXES)
    # ==========================================
    def build_faculty_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.editing_project_id = None 
        
        layout.addWidget(QLabel("<h2>Faculty Dashboard - Manage Your Projects</h2>"))

        form = QFormLayout()
        self.proj_title = QLineEdit()
        self.proj_desc = QLineEdit()
        self.proj_spec = QComboBox()
        self.proj_spec.addItems(["Computer", "Communications", "Power", "Biomedical"])
        self.proj_lab = QLineEdit(placeholderText="Required Lab")

        form.addRow("Title:", self.proj_title)
        form.addRow("Description:", self.proj_desc)
        form.addRow("Specialization:", self.proj_spec)
        form.addRow("Facility/Lab:", self.proj_lab)
        layout.addLayout(form)

        # UPGRADE: Checkboxes for Faculty Prerequisite Creation
        layout.addWidget(QLabel("<b>Require Foundational Subjects:</b>"))
        checkbox_layout = QHBoxLayout()
        self.fac_cb_math = QCheckBox("Math")
        self.fac_cb_circuits = QCheckBox("Circuits")
        self.fac_cb_prog = QCheckBox("Programming")
        self.fac_cb_systems = QCheckBox("Systems")
        self.fac_cb_design = QCheckBox("Design")
        
        checkbox_layout.addWidget(self.fac_cb_math)
        checkbox_layout.addWidget(self.fac_cb_circuits)
        checkbox_layout.addWidget(self.fac_cb_prog)
        checkbox_layout.addWidget(self.fac_cb_systems)
        checkbox_layout.addWidget(self.fac_cb_design)
        layout.addLayout(checkbox_layout)

        btn_layout = QHBoxLayout()
        self.fac_submit_btn = QPushButton("Submit New Proposal")
        self.fac_submit_btn.clicked.connect(self.faculty_save_project)
        btn_layout.addWidget(self.fac_submit_btn)
        
        self.fac_clear_btn = QPushButton("Clear Form")
        self.fac_clear_btn.clicked.connect(self.faculty_clear_form)
        btn_layout.addWidget(self.fac_clear_btn)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("<b>My Proposed Projects:</b>"))
        self.faculty_display_list = QListWidget()
        layout.addWidget(self.faculty_display_list)

        action_layout_row1 = QHBoxLayout()
        fac_view_proj_btn = QPushButton("View My Projects")
        fac_view_proj_btn.clicked.connect(self.faculty_refresh_list)
        action_layout_row1.addWidget(fac_view_proj_btn)
        
        fac_view_students_btn = QPushButton("View Enrolled Students")
        fac_view_students_btn.clicked.connect(self.faculty_view_students)
        action_layout_row1.addWidget(fac_view_students_btn)

        fac_details_btn = QPushButton("View Details")
        fac_details_btn.clicked.connect(lambda: self.view_project_details(self.faculty_display_list))
        action_layout_row1.addWidget(fac_details_btn)

        fac_edit_btn = QPushButton("Load Edit")
        fac_edit_btn.clicked.connect(self.faculty_load_edit)
        action_layout_row1.addWidget(fac_edit_btn)
        layout.addLayout(action_layout_row1)

        action_layout_row2 = QHBoxLayout()
        fac_comp_btn = QPushButton("Mark Completed")
        fac_comp_btn.clicked.connect(self.faculty_mark_completed)
        fac_comp_btn.setStyleSheet("color: darkgreen; font-weight: bold;")
        action_layout_row2.addWidget(fac_comp_btn)

        fac_del_btn = QPushButton("Delete Project")
        fac_del_btn.clicked.connect(self.faculty_delete_project)
        fac_del_btn.setStyleSheet("color: red;")
        action_layout_row2.addWidget(fac_del_btn)
        layout.addLayout(action_layout_row2)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)

        widget.setLayout(layout)
        return widget

    def faculty_refresh_list(self):
        self.faculty_display_list.clear()
        projects = self.backend.get_faculty_projects(self.current_user_email)
        for p in projects:
            status = p[3]
            allocated = p[4]
            text = f"Project ID: {p[0]} | Title: {p[1]} | Spec: {p[2]} | Status: {status}"
            
            item = QListWidgetItem(text)
            if status == 'completed':
                item.setForeground(QColor("darkgreen")) 
            elif allocated and allocated >= 3:
                item.setForeground(QColor("darkgoldenrod")) 
                
            self.faculty_display_list.addItem(item)

    def faculty_view_students(self):
        self.faculty_display_list.clear()
        students = self.backend.get_faculty_students(self.current_user_email)
        if not students:
            self.faculty_display_list.addItem("No students have enrolled in your projects yet.")
            return
        for s in students:
            self.faculty_display_list.addItem(f"Student: {s[0]} | Team: {s[2]} | Project: {s[1]} | Status: {s[3]}")

    def faculty_clear_form(self):
        self.proj_title.clear()
        self.proj_desc.clear()
        self.proj_lab.clear()
        
        self.fac_cb_math.setChecked(False)
        self.fac_cb_circuits.setChecked(False)
        self.fac_cb_prog.setChecked(False)
        self.fac_cb_systems.setChecked(False)
        self.fac_cb_design.setChecked(False)
        
        self.editing_project_id = None
        self.fac_submit_btn.setText("Submit New Proposal") 

    def faculty_save_project(self):
        reqs = []
        if self.fac_cb_math.isChecked(): reqs.append("Math")
        if self.fac_cb_circuits.isChecked(): reqs.append("Circuits")
        if self.fac_cb_prog.isChecked(): reqs.append("Programming")
        if self.fac_cb_systems.isChecked(): reqs.append("Systems")
        if self.fac_cb_design.isChecked(): reqs.append("Design")
        
        if self.editing_project_id:
            result = self.backend.update_own_project(
                self.editing_project_id, self.proj_title.text(), self.proj_desc.text(),
                self.proj_spec.currentText(), ",".join(reqs), self.proj_lab.text(), 
                self.current_user_email
            )
            if "Success" in result:
                self.backend.log_activity("Faculty", self.current_user_email, f"Updated Project ID: {self.editing_project_id}")
        else:
            new_proj = Project(None, self.proj_title.text(), self.proj_desc.text(), self.proj_spec.currentText(),
                               reqs, self.proj_lab.text(), self.current_user_email)
            result = self.backend.add_project(new_proj, self.current_user_email)
            if "Success" in result:
                self.backend.log_activity("Faculty", self.current_user_email, f"Proposed new project: {self.proj_title.text()}")
                
        QMessageBox.information(self, "Result", result)
        self.faculty_clear_form()
        self.faculty_refresh_list()

    def faculty_load_edit(self):
        selected_item = self.faculty_display_list.currentItem()
        if not selected_item or "Project ID:" not in selected_item.text():
            QMessageBox.warning(self, "Error", "Select a project to edit.")
            return
            
        try:
            proj_id = int(selected_item.text().split("|")[0].split(":")[1].strip())
            proj_data = self.backend.get_project_by_id(proj_id)
            
            if proj_data:
                self.editing_project_id = proj_id
                self.proj_title.setText(str(proj_data[1] or ""))
                self.proj_desc.setText(str(proj_data[2] or ""))
                self.proj_spec.setCurrentText(str(proj_data[3] or "Computer"))
                self.proj_lab.setText(str(proj_data[5] or ""))
                
                # Check the corresponding prerequisite boxes
                saved_prereqs = str(proj_data[4] or "")
                self.fac_cb_math.setChecked("Math" in saved_prereqs)
                self.fac_cb_circuits.setChecked("Circuits" in saved_prereqs)
                self.fac_cb_prog.setChecked("Programming" in saved_prereqs)
                self.fac_cb_systems.setChecked("Systems" in saved_prereqs)
                self.fac_cb_design.setChecked("Design" in saved_prereqs)
                
                self.fac_submit_btn.setText("Save Changes to Project") 
                QMessageBox.information(self, "Edit Mode", "Project loaded. Make changes and click 'Save Changes'.")
                
        except Exception as e:
            QMessageBox.critical(self, "System Protection", f"Could not load project data: {str(e)}")

    def faculty_delete_project(self):
        selected_item = self.faculty_display_list.currentItem()
        if not selected_item or "Project ID:" not in selected_item.text():
            QMessageBox.warning(self, "Error", "Select a project to delete.")
            return
            
        proj_id = int(selected_item.text().split("|")[0].split(":")[1].strip())
        result = self.backend.delete_own_project(proj_id, self.current_user_email)
        
        if "Success" in result:
            self.backend.log_activity("Faculty", self.current_user_email, f"Deleted their Project ID: {proj_id}")
            self.faculty_clear_form() 
        
        QMessageBox.information(self, "Result", result)
        self.faculty_refresh_list()

    def faculty_mark_completed(self):
        selected_item = self.faculty_display_list.currentItem()
        if not selected_item or "Project ID:" not in selected_item.text():
            QMessageBox.warning(self, "Error", "Please select a project to mark completed.")
            return

        text = selected_item.text()
        try:
            proj_id = int(text.split("|")[0].split(":")[1].strip())
            result = self.backend.mark_project_completed(proj_id, faculty_email=self.current_user_email)
            if "Success" in result:
                self.backend.log_activity("Faculty", self.current_user_email, f"Marked Project {proj_id} as Completed")
            QMessageBox.information(self, "Result", result)
            self.faculty_refresh_list()
        except Exception as e:
             QMessageBox.warning(self, "Error", f"Could not process completion: {str(e)}")


    # ==========================================
    # 5. ADMIN DASHBOARD
    # ==========================================
    def build_admin_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.current_admin_view = "projects" 

        layout.addWidget(QLabel("<h2>Coordinator Dashboard (God Mode)</h2>"))

        view_layout = QHBoxLayout()
        btn_proj = QPushButton("View Projects")
        btn_proj.clicked.connect(self.admin_view_projects)
        view_layout.addWidget(btn_proj)

        btn_teams = QPushButton("View Teams")
        btn_teams.clicked.connect(self.admin_view_teams)
        view_layout.addWidget(btn_teams)

        btn_users = QPushButton("View Users")
        btn_users.clicked.connect(self.admin_view_users)
        view_layout.addWidget(btn_users)

        btn_logs = QPushButton("View Logs")
        btn_logs.clicked.connect(self.admin_view_logs)
        view_layout.addWidget(btn_logs)
        
        layout.addLayout(view_layout)

        self.admin_display_list = QListWidget()
        layout.addWidget(self.admin_display_list)

        action_layout = QHBoxLayout()
        
        admin_details_btn = QPushButton("View Project Details")
        admin_details_btn.clicked.connect(lambda: self.view_project_details(self.admin_display_list))
        action_layout.addWidget(admin_details_btn)

        admin_team_students_btn = QPushButton("View Team Students")
        admin_team_students_btn.clicked.connect(self.admin_view_team_students)
        action_layout.addWidget(admin_team_students_btn)

        admin_comp_btn = QPushButton("Mark Completed")
        admin_comp_btn.clicked.connect(self.admin_mark_completed)
        admin_comp_btn.setStyleSheet("color: darkgreen; font-weight: bold;")
        action_layout.addWidget(admin_comp_btn)

        univ_del_btn = QPushButton("Delete Selected Item")
        univ_del_btn.clicked.connect(self.admin_universal_delete)
        univ_del_btn.setStyleSheet("color: white; background-color: darkred; font-weight: bold;")
        action_layout.addWidget(univ_del_btn)
        
        layout.addLayout(action_layout)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)

        widget.setLayout(layout)
        return widget

    def admin_view_projects(self):
        self.current_admin_view = "projects"
        self.admin_display_list.clear()
        projects = self.backend.get_all_projects()
        if not projects:
            self.admin_display_list.addItem("No projects currently in the database.")
            return
        for p in projects:
            status = p[3]
            allocated = p[4]
            text = f"Project ID: {p[0]} | Title: {p[1]} | Supervisor: {p[2]}"
            
            item = QListWidgetItem(text)
            if status == 'completed':
                item.setForeground(QColor("darkgreen")) 
            elif allocated and allocated >= 3:
                item.setForeground(QColor("darkgoldenrod")) 
                
            self.admin_display_list.addItem(item)

    def admin_view_teams(self):
        self.current_admin_view = "teams"
        self.admin_display_list.clear()
        teams = self.backend.get_all_teams()
        if not teams:
            self.admin_display_list.addItem("No teams currently in the database.")
            return
        for t in teams:
            proj_id = t[2] if t[2] else "Unassigned"
            p_status = t[3]
            text = f"Team ID: {t[0]} | Team Name: {t[1]} | Assigned Project ID: {proj_id}"
            
            item = QListWidgetItem(text)
            if p_status == 'completed':
                item.setForeground(QColor("darkgreen")) 
            elif proj_id != "Unassigned":
                item.setForeground(QColor("darkgoldenrod")) 
            # UPGRADE: Else do nothing. It defaults to the safe, standard unassigned text color!
                
            self.admin_display_list.addItem(item)

    def admin_view_users(self):
        self.current_admin_view = "users"
        self.admin_display_list.clear()
        users = self.backend.get_all_users()
        if not users:
            self.admin_display_list.addItem("No users found.")
            return
        for u in users:
            email = u[0]
            role = u[1]
            p_status = u[2]
            team_name = u[3]
            
            if role == 'Student':
                display_team = team_name if team_name else "None"
                text = f"Email: {email} | Role: {role} | Team: {display_team}"
            else:
                text = f"Email: {email} | Role: {role}"
            
            item = QListWidgetItem(text)
            
            if role == 'Faculty':
                item.setForeground(QColor("blue")) 
            elif role == 'Admin':
                item.setForeground(QColor("purple"))
            elif role == 'Student':
                if p_status == 'completed':
                    item.setForeground(QColor("darkgreen"))
                elif p_status == 'open':
                    item.setForeground(QColor("darkgoldenrod"))
                # Unassigned students get no forced color so they render cleanly.
                    
            self.admin_display_list.addItem(item)

    def admin_view_team_students(self):
        selected_item = self.admin_display_list.currentItem()
        if not selected_item or "Team ID:" not in selected_item.text() or self.current_admin_view != "teams":
            QMessageBox.warning(self, "Error", "Please select a Team from the 'View Teams' list first.")
            return
            
        team_id = int(selected_item.text().split("|")[0].split(":")[1].strip())
        students = self.backend.get_team_students(team_id)
        
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Students in Team {team_id}")
        if students:
            msg.setText("Enrolled Students:\n\n" + "\n".join(students))
        else:
            msg.setText("No students found in this team.")
        msg.exec_()

    def admin_view_logs(self):
        self.current_admin_view = "logs"
        self.admin_display_list.clear()
        logs = self.backend.get_audit_logs()
        if not logs:
            self.admin_display_list.addItem("No system activity recorded yet.")
            return
        for log in logs:
            text = f"Log ID: {log[0]} | [{log[4]}] {log[1]} ({log[2]}) - {log[3]}"
            self.admin_display_list.addItem(text)

    def admin_mark_completed(self):
        selected_item = self.admin_display_list.currentItem()
        if not selected_item or "Project ID:" not in selected_item.text():
            QMessageBox.warning(self, "Error", "Please select a Project from the list first.")
            return

        text = selected_item.text()
        try:
            proj_id = int(text.split("|")[0].split(":")[1].strip())
            if "Student:" in text and "Project ID:" in text:
                proj_id = int(text.split("|")[1].split(":")[1].strip())

            result = self.backend.mark_project_completed(proj_id)
            if "Success" in result:
                self.backend.log_activity("Admin", self.current_user_email, f"Force Marked Project {proj_id} as Completed")
            QMessageBox.information(self, "Result", result)
            self.admin_view_projects()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not process completion: {str(e)}")

    def admin_universal_delete(self):
        selected_item = self.admin_display_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select an item from the list first.")
            return
            
        text = selected_item.text()
        
        try:
            if self.current_admin_view == "projects" and "Project ID:" in text:
                proj_id = int(text.split("|")[0].split(":")[1].strip())
                result = self.backend.delete_project(proj_id)
                if "Success" in result: self.backend.log_activity("Admin", self.current_user_email, f"Deleted Project ID: {proj_id}")
                QMessageBox.information(self, "Result", result)
                self.admin_view_projects()
                
            elif self.current_admin_view == "teams" and "Team ID:" in text:
                team_id = int(text.split("|")[0].split(":")[1].strip())
                result = self.backend.delete_team(team_id)
                if "Success" in result: self.backend.log_activity("Admin", self.current_user_email, f"Deleted Team ID: {team_id}")
                QMessageBox.information(self, "Result", result)
                self.admin_view_teams()
                
            elif self.current_admin_view == "users" and "Email:" in text:
                email = text.split("|")[0].split(":")[1].strip()
                result = self.backend.delete_user(email)
                if "Success" in result: self.backend.log_activity("Admin", self.current_user_email, f"Deleted User: {email}")
                QMessageBox.information(self, "Result", result)
                self.admin_view_users()
                
            elif self.current_admin_view == "logs" and "Log ID:" in text:
                log_id = int(text.split("|")[0].split(":")[1].strip())
                result = self.backend.delete_log(log_id)
                QMessageBox.information(self, "Result", result)
                self.admin_view_logs()
                
            else:
                QMessageBox.warning(self, "Error", "Mismatch between current view and selected data.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", "Could not process deletion.")

def main():
    app = QApplication(sys.argv)
    my_backend = RegistrationSystem() 
    window = MainWindow(my_backend)   
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()