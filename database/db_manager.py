import sqlite3
import hashlib
from datetime import datetime
from config import DATABASE_PATH

class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_PATH)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.create_default_admin()
    
    def create_tables(self):
        # جدول المستخدمين
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الطلاب
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                date_of_birth DATE,
                gender TEXT,
                address TEXT,
                phone TEXT,
                parent_phone TEXT,
                class_id INTEGER,
                enrollment_date DATE DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (class_id) REFERENCES classes (id)
            )
        ''')
        
        # جدول المعلمين
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                specialization TEXT,
                hire_date DATE DEFAULT CURRENT_DATE,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول الصفوف
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                grade_level INTEGER,
                section TEXT,
                capacity INTEGER,
                academic_year TEXT
            )
        ''')
        
        # جدول المواد
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                subject_code TEXT UNIQUE,
                credits INTEGER,
                description TEXT
            )
        ''')
        
        # جدول الدرجات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                exam_type TEXT,
                score REAL,
                max_score REAL,
                date DATE DEFAULT CURRENT_DATE,
                teacher_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id),
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        ''')
        
        # جدول الحضور
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date DATE NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id),
                UNIQUE(student_id, date)
            )
        ''')
        
        # جدول الجدول الدراسي
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                room TEXT,
                FOREIGN KEY (class_id) REFERENCES classes (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id),
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        ''')
        
        # جدول الإشعارات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                recipient_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (recipient_id) REFERENCES users (id)
            )
        ''')
        
        # جدول ربط المعلمين بالمواد
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_subjects (
                teacher_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                PRIMARY KEY (teacher_id, subject_id),
                FOREIGN KEY (teacher_id) REFERENCES teachers (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        self.connection.commit()
    
    def create_default_admin(self):
        """إنشاء حساب مدير افتراضي"""
        try:
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role, full_name)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'admin', 'مدير النظام'))
            self.connection.commit()
        except:
            pass
    
    def authenticate_user(self, username, password):
        """التحقق من بيانات المستخدم"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password_hash))
        return self.cursor.fetchone()
    
    def add_student(self, student_data):
        """إضافة طالب جديد"""
        query = '''
            INSERT INTO students (student_id, full_name, date_of_birth, 
                                gender, address, phone, parent_phone, 
                                class_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            student_data['student_id'],
            student_data['full_name'],
            student_data['date_of_birth'],
            student_data['gender'],
            student_data['address'],
            student_data['phone'],
            student_data['parent_phone'],
            student_data['class_id'],
            student_data.get('status', 'active')
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_students(self):
        """الحصول على جميع الطلاب"""
        query = '''
            SELECT s.*, c.class_name 
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            WHERE s.status = 'active'
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def update_student(self, student_id, student_data):
        """تحديث بيانات طالب"""
        query = '''
            UPDATE students 
            SET full_name = ?, date_of_birth = ?, gender = ?, 
                address = ?, phone = ?, parent_phone = ?, class_id = ?
            WHERE id = ?
        '''
        self.cursor.execute(query, (
            
