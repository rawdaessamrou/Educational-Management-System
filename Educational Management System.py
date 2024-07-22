import json
import hashlib
import re

class User:
    def __init__(self, user_id, username, password, full_name, email):
        self.user_id = user_id
        self.username = username
        self.password = self.encrypt_password(password)
        self.full_name = full_name
        self.email = email

    def encrypt_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def sign_in(self, username, password):
        return self.username == username and self.password == self.encrypt_password(password)

    def log_out(self):
        print("Logged out successfully.")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, user_dict):
        user = cls(user_dict['user_id'], user_dict['username'], user_dict['password'], user_dict['full_name'], user_dict['email'])
        user.password = user_dict['password']  # Directly assigning encrypted password
        return user

    @staticmethod
    def is_valid_email(email):
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None

class Doctor(User):
    def __init__(self, user_id, username, password, full_name, email):
        super().__init__(user_id, username, password, full_name, email)
        self.courses_created = []

    def create_course(self, course_name, course_code):
        course = Course(course_name, course_code, self)
        self.courses_created.append(course)
        return course

    def list_courses(self):
        return self.courses_created

    def view_course(self, course_code):
        for course in self.courses_created:
            if course.course_code == course_code:
                return course
        return None

    def to_dict(self):
        data = super().to_dict()
        data['courses_created'] = [course.to_dict() for course in self.courses_created]
        return data

    @classmethod
    def from_dict(cls, user_dict):
        doctor = super().from_dict(user_dict)
        doctor.courses_created = [Course.from_dict(course) for course in user_dict['courses_created']]
        return doctor


class Student(User):
    def __init__(self, user_id, username, password, full_name, email):
        super().__init__(user_id, username, password, full_name, email)
        self.courses_registered = []

    def register_course(self, course):
        self.courses_registered.append(course)
        course.add_student(self)

    def list_courses(self):
        return self.courses_registered

    def view_course(self, course_code):
        for course in self.courses_registered:
            if course.course_code == course_code:
                return course
        return None

    def view_grades(self):
        grades_report = {}
        for course in self.courses_registered:
            total_grade, total_possible = course.get_student_grade(self)
            grades_report[course.course_code] = (len(course.assignments), total_grade, total_possible)
        return grades_report

    def to_dict(self):
        data = super().to_dict()
        data['courses_registered'] = [course.course_code for course in self.courses_registered]
        return data

    @classmethod
    def from_dict(cls, user_dict):
        student = super().from_dict(user_dict)
        student.courses_registered = user_dict['courses_registered']
        return student


class Course:
    def __init__(self, course_name, course_code, provided_by):
        self.course_name = course_name
        self.course_code = course_code
        self.provided_by = provided_by
        self.registered_students = []
        self.assignments = []

    def add_student(self, student):
        self.registered_students.append(student)

    def remove_student(self, student):
        self.registered_students.remove(student)

    def add_assignment(self, assignment_title, description, deadline):
        assignment = Assignment(assignment_title, description, deadline)
        self.assignments.append(assignment)
        return assignment

    def list_assignments(self):
        return self.assignments

    def get_student_grade(self, student):
        total_grade = 0
        total_possible = 0
        for assignment in self.assignments:
            grade = assignment.get_student_grade(student)
            if grade is not None:
                total_grade += int(grade['grade']) if grade['grade'] else 0
                total_possible += 100  # Assuming each assignment is out of 100
        return total_grade, total_possible

    def to_dict(self):
        return {
            'course_name': self.course_name,
            'course_code': self.course_code,
            'provided_by': self.provided_by.user_id,
            'registered_students': [student.user_id for student in self.registered_students],
            'assignments': [assignment.to_dict() for assignment in self.assignments]
        }

    @classmethod
    def from_dict(cls, course_dict):
        course = cls(course_dict['course_name'], course_dict['course_code'], course_dict['provided_by'])
        course.registered_students = course_dict['registered_students']
        course.assignments = [Assignment.from_dict(assignment) for assignment in course_dict['assignments']]
        return course


class Assignment:
    def __init__(self, assignment_title, description, deadline):
        self.assignment_title = assignment_title
        self.description = description
        self.deadline = deadline
        self.solutions = {}

    def submit_solution(self, student, submission_content):
        self.solutions[student.user_id] = {'content': submission_content, 'grade': None, 'comments': None}

    def grade_solution(self, student, grade, comments):
        if student.user_id in self.solutions:
            self.solutions[student.user_id]['grade'] = grade
            self.solutions[student.user_id]['comments'] = comments

    def get_student_grade(self, student):
        if student.user_id in self.solutions:
            return self.solutions[student.user_id]
        return None

    def to_dict(self):
        return {
            'assignment_title': self.assignment_title,
            'description': self.description,
            'deadline': self.deadline,
            'solutions': self.solutions
        }

    @classmethod
    def from_dict(cls, assignment_dict):
        assignment = cls(assignment_dict['assignment_title'], assignment_dict['description'], assignment_dict['deadline'])
        assignment.solutions = assignment_dict['solutions']
        return assignment


def save_data(users, filename='ems_data.json'):
    data = {
        'users': [user.to_dict() for user in users.values()]
    }
    with open(filename, 'w') as f:
        json.dump(data, f)


def load_data(filename='ems_data.json'):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            users = {}
            for user_data in data['users']:
                if 'courses_created' in user_data:
                    user = Doctor.from_dict(user_data)
                elif 'courses_registered' in user_data:
                    user = Student.from_dict(user_data)
                else:
                    user = User.from_dict(user_data)
                users[user.user_id] = user
            return users
    except FileNotFoundError:
        return {}


def main():
    users = load_data()
    current_user = None
    courses = {}  # Dictionary to store all courses by course code

    # Linking students to courses after loading
    for user in users.values():
        if isinstance(user, Student):
            for course_code in user.courses_registered:
                if course_code in courses:
                    course = courses[course_code]
                else:
                    course = None
                    for doctor in users.values():
                        if isinstance(doctor, Doctor):
                            course = doctor.view_course(course_code)
                            if course:
                                courses[course_code] = course
                                break
                if course:
                    user.register_course(course)

    while True:
        if current_user is None:
            print("Welcome to the Educational Management System")
            print("1. Sign In")
            print("2. Sign Up")
            print("3. Exit")

            choice = input("Enter your choice: ")
            if choice == "1":
                username = input("Username: ")
                password = input("Password: ")
                for user in users.values():
                    if user.sign_in(username, password):
                        current_user = user
                        print("Signed in successfully.")
                        break
                else:
                    print("Invalid credentials. Please try again.")
            elif choice == "2":
                while True:
                    user_type = input("Are you a Doctor or Student? ")
                    if user_type.lower() not in ["doctor", "student"]:
                        print("Invalid user type. Please enter either 'Doctor' or 'Student'.")
                    else:
                        break

                user_id = len(users) + 1
                username = input("Username: ")
                password = input("Password: ")
                full_name = input("Full Name: ")
                email = input("Email: ")

                if not User.is_valid_email(email):
                    print("Invalid email format. Please try again.")
                    continue

                if user_type.lower() == "doctor":
                    user = Doctor(user_id, username, password, full_name, email)
                elif user_type.lower() == "student":
                    user = Student(user_id, username, password, full_name, email)

                users[user_id] = user
                print(f"Sign up successful. Your user ID is {user_id}. You can now sign in.")

            elif choice == "3":
                save_data(users)
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            if isinstance(current_user, Doctor):
                print(f"Welcome Doctor {current_user.full_name}")
                print("1. List Courses")
                print("2. Create Course")
                print("3. View Course")
                print("4. Log Out")

                choice = input("Enter your choice: ")
                if choice == "1":
                    courses = current_user.list_courses()
                    for course in courses:
                        print(f"{course.course_name} ({course.course_code})")
                elif choice == "2":
                    course_name = input("Course Name: ")
                    course_code = input("Course Code: ")
                    current_user.create_course(course_name, course_code)
                    print("Course created successfully.")
                elif choice == "3":
                    course_code = input("Course Code: ")
                    course = current_user.view_course(course_code)
                    if course:
                        print(f"Course: {course.course_name} ({course.course_code})")
                        print("1. List Assignments")
                        print("2. Create Assignment")
                        print("3. View Assignment")
                        print("4. Back")
                        sub_choice = input("Enter your choice: ")
                        if sub_choice == "1":
                            assignments = course.list_assignments()
                            for idx, assignment in enumerate(assignments, 1):
                                print(f"{idx}. {assignment.assignment_title}")
                        elif sub_choice == "2":
                            assignment_title = input("Assignment Title: ")
                            description = input("Description: ")
                            deadline = input("Deadline: ")
                            course.add_assignment(assignment_title, description, deadline)
                            print("Assignment created successfully.")
                        elif sub_choice == "3":
                            assignments = course.list_assignments()
                            for idx, assignment in enumerate(assignments, 1):
                                print(f"{idx}. {assignment.assignment_title}")
                            assignment_idx = int(input("Enter assignment number: ")) - 1
                            if 0 <= assignment_idx < len(assignments):
                                assignment = assignments[assignment_idx]
                                while True:
                                    print(f"\nAssignment: {assignment.assignment_title}")
                                    print("1. Show Info")
                                    print("2. Show Grades Report")
                                    print("3. List Solutions")
                                    print("4. View Solution")
                                    print("5. Back")
                                    assign_choice = input("Enter your choice: ")

                                    if assign_choice == "1":
                                        print(f"Title: {assignment.assignment_title}")
                                        print(f"Description: {assignment.description}")
                                        print(f"Deadline: {assignment.deadline}")
                                    elif assign_choice == "2":
                                        for student_id, solution in assignment.solutions.items():
                                            student = users[student_id]
                                            print(f"Student: {student.full_name} (ID: {student.user_id})")
                                            print(f"Grade: {solution['grade']}")
                                            print(f"Comments: {solution['comments']}")
                                    elif assign_choice == "3":
                                        for student_id, solution in assignment.solutions.items():
                                            student = users[student_id]
                                            print(f"Student: {student.full_name} (ID: {student.user_id})")
                                    elif assign_choice == "4":
                                        student_id = int(input("Enter Student ID: "))
                                        if student_id in assignment.solutions:
                                            solution = assignment.solutions[student_id]
                                            student = users[student_id]
                                            print(f"Student: {student.full_name} (ID: {student.user_id})")
                                            print(f"Content: {solution['content']}")
                                            print(f"Grade: {solution['grade']}")
                                            print(f"Comments: {solution['comments']}")
                                            while True:
                                                print("1. Show Info")
                                                print("2. Set Grade")
                                                print("3. Set a Comment")
                                                print("4. Back")
                                                sol_choice = input("Enter your choice: ")

                                                if sol_choice == "1":
                                                    print(f"Content: {solution['content']}")
                                                    print(f"Grade: {solution['grade']}")
                                                    print(f"Comments: {solution['comments']}")
                                                elif sol_choice == "2":
                                                    grade = input("Enter Grade: ")
                                                    solution['grade'] = grade
                                                    print("Grade updated successfully.")
                                                elif sol_choice == "3":
                                                    comment = input("Enter Comment: ")
                                                    solution['comments'] = comment
                                                    print("Comment updated successfully.")
                                                elif sol_choice == "4":
                                                    break
                                                else:
                                                    print("Invalid choice. Please try again.")
                                        else:
                                            print("Invalid Student ID.")
                                    elif assign_choice == "5":
                                        break
                                    else:
                                        print("Invalid choice. Please try again.")
                            else:
                                print("Invalid assignment number.")
                        
                        elif sub_choice == "5":
                            continue
                        else:
                            print("Invalid choice. Please try again.")
                    else:
                        print("Course not found.")
                elif choice == "4":
                    current_user.log_out()
                    current_user = None
                else:
                    print("Invalid choice. Please try again.")
            elif isinstance(current_user, Student):
                print(f"Welcome Student {current_user.full_name}")
                print("1. Register in Course")
                print("2. List My Courses")
                print("3. View Course")
                print("4. Grades Report")
                print("5. Log Out")

                choice = input("Enter your choice: ")
                if choice == "1":
                    print("Available Courses:")
                    available_courses = []
                    for user in users.values():
                        if isinstance(user, Doctor):
                            for course in user.list_courses():
                                if course not in current_user.courses_registered:
                                    available_courses.append(course)
                                    print(f"{len(available_courses)}. {course.course_name} ({course.course_code}) - Provided by Doctor {course.provided_by.full_name}")
                    
                    if available_courses:
                        course_idx = int(input("Enter the number of the course to register: ")) - 1
                        if 0 <= course_idx < len(available_courses):
                            current_user.register_course(available_courses[course_idx])
                            print("Registered in course successfully.")
                        else:
                            print("Invalid course number.")
                    else:
                        print("No available courses to register.")
                elif choice == "2":
                    courses = current_user.list_courses()
                    for course in courses:
                        print(f"{course.course_name} ({course.course_code}) - Provided by: {course.provided_by.full_name}")
                elif choice == "3":
                    course_code = input("Course Code: ")
                    course = current_user.view_course(course_code)
                    if course:
                        print(f"Course: {course.course_name} ({course.course_code})")
                        print("Assignments:")
                        for idx, assignment in enumerate(course.list_assignments(), 1):
                            submission = assignment.get_student_grade(current_user)
                            status = "Submitted" if submission else "Not Submitted"
                            grade = submission['grade'] if submission else "N/A"
                            print(f"{idx}. {assignment.assignment_title} - {status} - Grade: {grade}")
                        
                        print ("Options :")
                        print("1. Submit Assignment")
                        print("2. Unregister from Course")
                        print("3. Back")
                        sub_choice = input("Enter your choice: ")
                        if sub_choice == "1":
                            assignments = course.list_assignments()
                            for idx, assignment in enumerate(assignments, 1):
                                print(f"{idx}. {assignment.assignment_title}")
                            assignment_idx = int(input("Enter assignment number: ")) - 1
                            if 0 <= assignment_idx < len(assignments):
                                assignment = assignments[assignment_idx]
                                print(f"Title: {assignment.assignment_title}")
                                print(f"Description: {assignment.description}")
                                print(f"Deadline: {assignment.deadline}")
                                submission_content = input("Submission Content: ")
                                assignment.submit_solution(current_user, submission_content)
                                print("Assignment submitted successfully.")
                            else:
                                print("Invalid assignment number.")
                        elif sub_choice == "2":
                            current_user.courses_registered.remove(course)
                            course.remove_student(current_user)
                            print("Unregistered from course successfully.")
                        elif sub_choice == "3":
                            continue
                        else:
                            print("Invalid choice. Please try again.")
                    else:
                        print("Course not found.")
                elif choice == "4":
                    grades_report = current_user.view_grades()
                    for course_code, grades in grades_report.items():
                        num_assignments, total_grade, total_possible = grades
                        print(f"Course Code: {course_code} - Total Assignments: {num_assignments} - Grade: {total_grade}/{total_possible}")
                elif choice == "5":
                    current_user.log_out()
                    current_user = None
                else:
                    print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()