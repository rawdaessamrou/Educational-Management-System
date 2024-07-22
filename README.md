
# Educational Management System

The Educational Management System is a Python-based application designed to manage courses, assignments, and users (doctors and students). It supports features such as user registration, course creation, assignment management, and grade tracking.

## Features

- User registration and authentication for both doctors and students.
- Course creation and management by doctors.
- Assignment creation, submission, grading, and feedback.
- Students can register for courses, submit assignments, and view their grades.
- Email validation during user registration.

## Getting Started
### Prerequisites
- Python 3.x
- Required libraries: json, hashlib, re
### Installation
1. Clone the repository:
```ruby
git clone https://github.com/yourusername/educational-management-system.git
cd educational-management-system
```
 2. Run the application:

 ```ruby
python educational_management_system.py
``` 
## Usage
1. Run the Application:

 ```ruby
python educational_management_system.py
``` 
2. Sign In/Sign Up:

- Sign in using existing credentials.
- Sign up as a new doctor or student.

3. Doctor Menu:

- List courses created by the doctor.
- Create a new course.
- View and manage a specific course and its assignments.

4. Student Menu:

- Register in available courses.
- List registered courses.
- View course details and submit assignments.
- View grades for all registered courses.

## Classes
### User
Base class for all users in the system.

Attributes: 

- user_id (int): Unique identifier for the user.
- username (str): Username of the user.
- password (str): Encrypted password of the user.
- full_name (str): Full name of the user.
- email (str): Email address of the user.

Methods:

- __init__(self, user_id, username, password, full_name, email): Initializes a User object.
- encrypt_password(self, password): Encrypts the password using SHA-256.
- sign_in(self, username, password): Checks if the provided credentials are correct.
- log_out(self): Logs out the user.
- to_dict(self): Converts the user object to a dictionary.
- from_dict(cls, user_dict): Creates a User object from a dictionary.
- is_valid_email(email): Validates the email format using a regular expression.

### Doctor
Inherits from the User class and represents a doctor who can create and manage courses and assignments.

Additional Attributes:

- courses_created (list): List of courses created by the doctor.

Additional Methods:

- create_course(self, course_name, course_code): Creates a new course.
- list_courses(self): Returns the list of courses created by the doctor.
- view_course(self, course_code): Returns the course object with the specified course code.
- to_dict(self): Converts the doctor object to a dictionary.
- from_dict(cls, user_dict): Creates a Doctor object from a dictionary.

### Student
Inherits from the User class and represents a student who can register for courses and submit assignments.

Additional Attributes:

- courses_registered (list): List of courses the student is registered in.

Additional Methods:

- register_course(self, course): Registers the student in a course.
- list_courses(self): Returns the list of courses the student is registered in.
- view_course(self, course_code): Returns the course object with the specified course code.
- view_grades(self): Returns the grades for all registered courses.
- to_dict(self): Converts the student object to a dictionary.
- from_dict(cls, user_dict): Creates a Student object from a dictionary.

### Course
Represents a course with a name, code, provider (doctor), registered students, and assignments.

Attributes:

- course_name (str): Name of the course.
- course_code (str): Code of the course.
- provided_by (Doctor): Doctor who provides the course.
- registered_students (list): List of students registered in the course.
- assignments (list): List of assignments for the course.

Methods:

- __init__(self, course_name, course_code, provided_by): Initializes a Course object.
- add_student(self, student): Adds a student to the course.
- remove_student(self, student): Removes a student from the course.
- add_assignment(self, assignment_title, description, deadline): Adds a new assignment to the course.
- list_assignments(self): Returns the list of assignments for the course.
- get_student_grade(self, student): Returns the total grade for the student in the course.
- to_dict(self): Converts the course object to a dictionary.
- from_dict(cls, course_dict): Creates a Course object from a dictionary.

### Assignment
Represents an assignment with a title, description, deadline, and submitted solutions.

Attributes:

- assignment_title (str): Title of the assignment.
- description (str): Description of the assignment.
- deadline (str): Deadline for the assignment.
- solutions (dict): Dictionary of solutions submitted by students.

Methods:

- __init__(self, assignment_title, description, deadline): Initializes an Assignment object.
- submit_solution(self, student, submission_content): Submits a solution for the assignment.
- grade_solution(self, student, grade, comments): Grades a submitted solution.
- get_student_grade(self, student): Returns the grade for the student's solution.
- to_dict(self): Converts the assignment object to a dictionary.
- from_dict(cls, assignment_dict): Creates an Assignment object from a dictionary.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Contact
If you have any questions or feedback, feel free to contact me at rawdaessamrou@gmail.com