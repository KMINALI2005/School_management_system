from datetime import datetime

class User:
    def __init__(self, id=None, username=None, password=None, role=None, 
                 full_name=None, email=None, phone=None, created_at=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role  # 'admin' or 'teacher'
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.created_at = created_at or datetime.now()

class Student:
    def __init__(self, id=None, student_id=None, full_name=None, 
                 date_of_birth=None, gender=None, address=None, 
                 phone=None, parent_phone=None, class_id=None, 
                 enrollment_date=None, status='active'):
        self.id = id
        self.student_id = student_id
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.address = address
        self.phone = phone
        self.parent_phone = parent_phone
        self.class_id = class_id
        self.enrollment_date = enrollment_date or datetime.now()
        self.status = status

class Teacher:
    def __init__(self, id=None, teacher_id=None, full_name=None, 
                 email=None, phone=None, specialization=None, 
                 hire_date=None, user_id=None):
        self.id = id
        self.teacher_id = teacher_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.specialization = specialization
        self.hire_date = hire_date or datetime.now()
        self.user_id = user_id

class Class:
    def __init__(self, id=None, class_name=None, grade_level=None, 
                 section=None, capacity=None, academic_year=None):
        self.id = id
        self.class_name = class_name
        self.grade_level = grade_level
        self.section = section
        self.capacity = capacity
        self.academic_year = academic_year

class Subject:
    def __init__(self, id=None, subject_name=None, subject_code=None, 
                 credits=None, description=None):
        self.id = id
        self.subject_name = subject_name
        self.subject_code = subject_code
        self.credits = credits
        self.description = description

class Grade:
    def __init__(self, id=None, student_id=None, subject_id=None, 
                 exam_type=None, score=None, max_score=None, 
                 date=None, teacher_id=None):
        self.id = id
        self.student_id = student_id
        self.subject_id = subject_id
        self.exam_type = exam_type
        self.score = score
        self.max_score = max_score
        self.date = date or datetime.now()
        self.teacher_id = teacher_id

class Attendance:
    def __init__(self, id=None, student_id=None, date=None, 
                 status=None, notes=None):
        self.id = id
        self.student_id = student_id
        self.date = date or datetime.now()
        self.status = status  # 'present', 'absent', 'late', 'excused'
        self.notes = notes

class Timetable:
    def __init__(self, id=None, class_id=None, subject_id=None, 
                 teacher_id=None, day=None, start_time=None, 
                 end_time=None, room=None):
        self.id = id
        self.class_id = class_id
        self.subject_id = subject_id
        self.teacher_id = teacher_id
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.room = room

class Notification:
    def __init__(self, id=None, sender_id=None, recipient_id=None, 
                 title=None, message=None, type=None, 
                 is_read=False, created_at=None):
        self.id = id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.title = title
        self.message = message
        self.type = type
        self.is_read = is_read
        self.created_at = created_at or datetime.now()
