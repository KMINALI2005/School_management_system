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
        self.cursor.execute(query, (# ... تكملة من الكود السابق
            student_data['full_name'],
            student_data['date_of_birth'],
            student_data['gender'],
            student_data['address'],
            student_data['phone'],
            student_data['parent_phone'],
            student_data['class_id'],
            student_id
        ))
        self.connection.commit()
    
    def delete_student(self, student_id):
        """حذف طالب (soft delete)"""
        self.cursor.execute(
            "UPDATE students SET status = 'inactive' WHERE id = ?", 
            (student_id,)
        )
        self.connection.commit()
    
    def add_teacher(self, teacher_data):
        """إضافة معلم جديد"""
        # أولاً إنشاء حساب مستخدم للمعلم
        password_hash = hashlib.sha256(teacher_data['password'].encode()).hexdigest()
        self.cursor.execute('''
            INSERT INTO users (username, password, role, full_name, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            teacher_data['username'],
            password_hash,
            'teacher',
            teacher_data['full_name'],
            teacher_data['email'],
            teacher_data['phone']
        ))
        user_id = self.cursor.lastrowid
        
        # ثم إضافة بيانات المعلم
        self.cursor.execute('''
            INSERT INTO teachers (teacher_id, full_name, email, phone, 
                                specialization, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            teacher_data['teacher_id'],
            teacher_data['full_name'],
            teacher_data['email'],
            teacher_data['phone'],
            teacher_data['specialization'],
            user_id
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_teachers(self):
        """الحصول على جميع المعلمين"""
        self.cursor.execute('''
            SELECT t.*, u.username 
            FROM teachers t
            JOIN users u ON t.user_id = u.id
        ''')
        return self.cursor.fetchall()
    
    def add_class(self, class_data):
        """إضافة صف جديد"""
        self.cursor.execute('''
            INSERT INTO classes (class_name, grade_level, section, 
                               capacity, academic_year)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            class_data['class_name'],
            class_data['grade_level'],
            class_data['section'],
            class_data['capacity'],
            class_data['academic_year']
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_classes(self):
        """الحصول على جميع الصفوف"""
        self.cursor.execute('''
            SELECT c.*, 
                   (SELECT COUNT(*) FROM students WHERE class_id = c.id AND status = 'active') as student_count
            FROM classes c
        ''')
        return self.cursor.fetchall()
    
    def add_subject(self, subject_data):
        """إضافة مادة جديدة"""
        self.cursor.execute('''
            INSERT INTO subjects (subject_name, subject_code, credits, description)
            VALUES (?, ?, ?, ?)
        ''', (
            subject_data['subject_name'],
            subject_data['subject_code'],
            subject_data['credits'],
            subject_data['description']
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_subjects(self):
        """الحصول على جميع المواد"""
        self.cursor.execute("SELECT * FROM subjects")
        return self.cursor.fetchall()
    
    def assign_teacher_to_subject(self, teacher_id, subject_id):
        """ربط معلم بمادة"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO teacher_subjects (teacher_id, subject_id)
            VALUES (?, ?)
        ''', (teacher_id, subject_id))
        self.connection.commit()
    
    def add_grade(self, grade_data):
        """إضافة درجة"""
        self.cursor.execute('''
            INSERT INTO grades (student_id, subject_id, exam_type, 
                              score, max_score, teacher_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            grade_data['student_id'],
            grade_data['subject_id'],
            grade_data['exam_type'],
            grade_data['score'],
            grade_data['max_score'],
            grade_data['teacher_id']
        ))
        self.connection.commit()
    
    def get_student_grades(self, student_id):
        """الحصول على درجات طالب"""
        self.cursor.execute('''
            SELECT g.*, s.subject_name, t.full_name as teacher_name
            FROM grades g
            JOIN subjects s ON g.subject_id = s.id
            JOIN teachers t ON g.teacher_id = t.id
            WHERE g.student_id = ?
            ORDER BY g.date DESC
        ''', (student_id,))
        return self.cursor.fetchall()
    
    def mark_attendance(self, attendance_data):
        """تسجيل الحضور"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO attendance (student_id, date, status, notes)
            VALUES (?, ?, ?, ?)
        ''', (
            attendance_data['student_id'],
            attendance_data['date'],
            attendance_data['status'],
            attendance_data.get('notes', '')
        ))
        self.connection.commit()
    
    def get_attendance_by_date(self, date, class_id=None):
        """الحصول على الحضور حسب التاريخ"""
        if class_id:
            query = '''
                SELECT a.*, s.full_name, s.student_id
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.date = ? AND s.class_id = ?
            '''
            self.cursor.execute(query, (date, class_id))
        else:
            query = '''
                SELECT a.*, s.full_name, s.student_id
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.date = ?
            '''
            self.cursor.execute(query, (date,))
        return self.cursor.fetchall()
    
    def add_timetable_entry(self, timetable_data):
        """إضافة حصة للجدول الدراسي"""
        self.cursor.execute('''
            INSERT INTO timetable (class_id, subject_id, teacher_id, 
                                 day, start_time, end_time, room)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            timetable_data['class_id'],
            timetable_data['subject_id'],
            timetable_data['teacher_id'],
            timetable_data['day'],
            timetable_data['start_time'],
            timetable_data['end_time'],
            timetable_data['room']
        ))
        self.connection.commit()
    
    def get_timetable_by_class(self, class_id):
        """الحصول على الجدول الدراسي لصف معين"""
        self.cursor.execute('''
            SELECT t.*, s.subject_name, te.full_name as teacher_name
            FROM timetable t
            JOIN subjects s ON t.subject_id = s.id
            JOIN teachers te ON t.teacher_id = te.id
            WHERE t.class_id = ?
            ORDER BY 
                CASE t.day 
                    WHEN 'الأحد' THEN 1
                    WHEN 'الإثنين' THEN 2
                    WHEN 'الثلاثاء' THEN 3
                    WHEN 'الأربعاء' THEN 4
                    WHEN 'الخميس' THEN 5
                END,
                t.start_time
        ''', (class_id,))
        return self.cursor.fetchall()
    
    def add_notification(self, notification_data):
        """إضافة إشعار"""
        self.cursor.execute('''
            INSERT INTO notifications (sender_id, recipient_id, title, 
                                     message, type)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            notification_data['sender_id'],
            notification_data.get('recipient_id'),
            notification_data['title'],
            notification_data['message'],
            notification_data.get('type', 'general')
        ))
        self.connection.commit()
    
    def get_user_notifications(self, user_id):
        """الحصول على إشعارات المستخدم"""
        self.cursor.execute('''
            SELECT n.*, u.full_name as sender_name
            FROM notifications n
            LEFT JOIN users u ON n.sender_id = u.id
            WHERE n.recipient_id = ? OR n.recipient_id IS NULL
            ORDER BY n.created_at DESC
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def mark_notification_read(self, notification_id):
        """تحديد الإشعار كمقروء"""
        self.cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ?",
            (notification_id,)
        )
        self.connection.commit()
    
    def get_dashboard_stats(self):
        """إحصائيات لوحة التحكم"""
        stats = {}
        
        # عدد الطلاب
        self.cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'active'")
        stats['total_students'] = self.cursor.fetchone()[0]
        
        # عدد المعلمين
        self.cursor.execute("SELECT COUNT(*) FROM teachers")
        stats['total_teachers'] = self.cursor.fetchone()[0]
        
        # عدد الصفوف
        self.cursor.execute("SELECT COUNT(*) FROM classes")
        stats['total_classes'] = self.cursor.fetchone()[0]
        
        # عدد المواد
        self.cursor.execute("SELECT COUNT(*) FROM subjects")
        stats['total_subjects'] = self.cursor.fetchone()[0]
        
        # نسبة الحضور اليوم
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT 
                COUNT(CASE WHEN status = 'present' THEN 1 END) as present,
                COUNT(*) as total
            FROM attendance
            WHERE date = ?
        ''', (today,))
        result = self.cursor.fetchone()
        if result and result['total'] > 0:
            stats['attendance_rate'] = (result['present'] / result['total']) * 100
        else:
            stats['attendance_rate'] = 0
        
        return stats
    
    def close(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        self.connection.close()
            
