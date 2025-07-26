from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QComboBox, QDialog,
                           QFormLayout, QMessageBox, QLabel, QDateEdit,
                           QHeaderView, QAbstractItemView, QCheckBox,
                           QTextEdit, QCalendarWidget)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont
from database.db_manager import DatabaseManager
from utils.translations import tr
import datetime

class AttendanceManagement(QWidget):
    def __init__(self, language='ar', user_data=None):
        super().__init__()
        self.language = language
        self.user_data = user_data
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_filters()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # شريط الفلاتر
        filters_layout = QHBoxLayout()
        
        # تاريخ الحضور
        filters_layout.addWidget(QLabel(tr('date', self.language)))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.dateChanged.connect(self.load_attendance)
        filters_layout.addWidget(self.date_picker)
        
        # فلتر الصف
        filters_layout.addWidget(QLabel(tr('class', self.language)))
        self.class_filter = QComboBox()
        self.class_filter.setMinimumWidth(150)
        self.class_filter.currentIndexChanged.connect(self.on_class_changed)
        filters_layout.addWidget(self.class_filter)
        
        # فلتر المادة
        filters_layout.addWidget(QLabel(tr('subject', self.language)))
        self.subject_filter = QComboBox()
        self.subject_filter.setMinimumWidth(150)
        self.subject_filter.currentIndexChanged.connect(self.load_attendance)
        filters_layout.addWidget(self.subject_filter)
        
        filters_layout.addStretch()
        
        # زر اليوم
        today_btn = QPushButton(tr('today', self.language))
        today_btn.clicked.connect(lambda: self.date_picker.setDate(QDate.currentDate()))
        filters_layout.addWidget(today_btn)
        
        layout.addLayout(filters_layout)
        
        # شريط الأدوات
        toolbar = QHBoxLayout()
        
        # زر تسجيل الحضور
        record_btn = QPushButton(f"✓ {tr('record_attendance', self.language)}")
        record_btn.setObjectName("successButton")
        record_btn.clicked.connect(self.save_attendance)
        toolbar.addWidget(record_btn)
        
        # زر طباعة التقرير
        print_btn = QPushButton(f"🖨️ {tr('print_report', self.language)}")
        print_btn.clicked.connect(self.print_report)
        toolbar.addWidget(print_btn)
        
        # زر الإحصائيات
        stats_btn = QPushButton(f"📊 {tr('statistics', self.language)}")
        stats_btn.clicked.connect(self.show_statistics)
        toolbar.addWidget(stats_btn)
        
        toolbar.addStretch()
        
        # زر التحديث
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.clicked.connect(self.load_attendance)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # جدول الحضور
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        # شريط المعلومات
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            padding: 10px;
            background-color: #F5F6FA;
            border-radius: 5px;
            color: #7F8C8D;
        """)
        info_layout.addWidget(self.info_label)
        
        # ملخص سريع
        self.summary_label = QLabel()  
        self.summary_label.setStyleSheet("""
            padding: 10px;
            background-color: #E8F5E9;
            border-radius: 5px;
            color: #2E7D32;
        """)
        info_layout.addWidget(self.summary_label)
        
        layout.addLayout(info_layout)
    
    def setup_table(self):
        headers = [
            tr('student_name', self.language),
            tr('student_id', self.language),
            tr('status', self.language),
            tr('arrival_time', self.language),
            tr('notes', self.language)
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # تحديد عرض الأعمدة
        self.table.setColumnWidth(0, 250)  # اسم الطالب
        self.table.setColumnWidth(1, 120)  # رقم الطالب
        self.table.setColumnWidth(2, 150)  # الحالة
        self.table.setColumnWidth(3, 120)  # وقت الحضور
        
    def load_filters(self):
        """تحميل الصفوف المتاحة"""
        self.class_filter.clear()
        self.class_filter.addItem(tr('select_class', self.language), None)
        
        if self.user_data and self.user_data['user_type'] == 'teacher':
            # للمعلم: عرض الصفوف التي يدرسها
            teacher_id = self.db.cursor.execute(
                "SELECT id FROM teachers WHERE user_id = ?",
                (self.user_data['user_id'],)
            ).fetchone()
            
            if teacher_id:
                classes = self.db.cursor.execute(
                    """SELECT DISTINCT c.id, c.class_name, c.section 
                       FROM classes c
                       JOIN timetable t ON c.id = t.class_id
                       WHERE t.teacher_id = ?""",
                    (teacher_id[0],)
                ).fetchall()
                
                for class_data in classes:
                    self.class_filter.addItem(
                        f"{class_data[1]} - {class_data[2]}", 
                        class_data[0]
                    )
        else:
            # للمدير: عرض جميع الصفوف
            classes = self.db.get_all_classes()
            for class_data in classes:
                self.class_filter.addItem(
                    f"{class_data['class_name']} - {class_data['section']}", 
                    class_data['id']
                )
    
    def on_class_changed(self):
        """تحديث قائمة المواد عند تغيير الصف"""
        self.subject_filter.clear()
        self.subject_filter.addItem(tr('all_subjects', self.language), None)
        
        class_id = self.class_filter.currentData()
        if not class_id:
            return
        
        if self.user_data and self.user_data['user_type'] == 'teacher':
            # للمعلم: عرض المواد التي يدرسها في هذا الصف
            teacher_id = self.db.cursor.execute(
                "SELECT id FROM teachers WHERE user_id = ?",
                (self.user_data['user_id'],)
            ).fetchone()
            
            if teacher_id:
                subjects = self.db.cursor.execute(
                    """SELECT DISTINCT s.id, s.subject_name 
                       FROM subjects s
                       JOIN teacher_subjects ts ON s.id = ts.subject_id
                       JOIN timetable t ON s.id = t.subject_id
                       WHERE ts.teacher_id = ? AND t.class_id = ?""",
                    (teacher_id[0], class_id)
                ).fetchall()
                
                for subject in subjects:
                    self.subject_filter.addItem(subject[1], subject[0])
        else:
            # للمدير: عرض جميع المواد
            subjects = self.db.cursor.execute(
                """SELECT DISTINCT s.id, s.subject_name 
                   FROM subjects s
                   JOIN timetable t ON s.id = t.subject_id
                   WHERE t.class_id = ?""",
                (class_id,)
            ).fetchall()
            
            for subject in subjects:
                self.subject_filter.addItem(subject[1], subject[0])
        
        self.load_attendance()
    
    def load_attendance(self):
        """تحميل بيانات الحضور"""
        self.table.setRowCount(0)
        
        class_id = self.class_filter.currentData()
        if not class_id:
            return
        
        # جلب الطلاب
        students = self.db.cursor.execute(
            """SELECT id, full_name, student_id 
               FROM students 
               WHERE class_id = ?
               ORDER BY full_name""",
            (class_id,)
        ).fetchall()
        
        # التاريخ المحدد
        date = self.date_picker.date().toString('yyyy-MM-dd')
        subject_id = self.subject_filter.currentData()
        
        for student in students:
            self.add_student_to_table(student, date, subject_id)
        
        self.update_info_labels()
    
    def add_student_to_table(self, student, date, subject_id):
        """إضافة طالب إلى جدول الحضور"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # اسم الطالب
        self.table.setItem(row, 0, QTableWidgetItem(student[1]))
        self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, student[0])
        
        # رقم الطالب
        self.table.setItem(row, 1, QTableWidgetItem(student[2]))
        
        # البحث عن سجل الحضور
        attendance = self.db.cursor.execute(
            """SELECT status, check_in_time, notes 
               FROM attendance 
               WHERE student_id = ? AND date = ? 
               AND (subject_id = ? OR (? IS NULL AND subject_id IS NULL))""",
            (student[0], date, subject_id, subject_id)
        ).fetchone()
        
        # إنشاء ودجت الحالة
        status_widget = QComboBox()
        status_widget.addItem(tr('present', self.language), 'present')
        status_widget.addItem(tr('absent', self.language), 'absent')
        status_widget.addItem(tr('late', self.language), 'late')
        status_widget.addItem(tr('excused', self.language), 'excused')
        
        # إنشاء حقل وقت الحضور
        time_widget = QLineEdit()
        time_widget.setPlaceholderText("HH:MM")
        time_widget.setMaximumWidth(100)
        
        # إنشاء حقل الملاحظات
        notes_widget = QLineEdit()
        notes_widget.setPlaceholderText(tr('notes', self.language))
        
        if attendance:
            # تعيين القيم المحفوظة
            index = status_widget.findData(attendance[0])
            if index >= 0:
                status_widget.setCurrentIndex(index)
            
            if attendance[1]:
                time_widget.setText(attendance[1])
            
            if attendance[2]:
                notes_widget.setText(attendance[2])
        else:
            # القيمة الافتراضية
            status_widget.setCurrentIndex(0)  # حاضر
            time_widget.setText(datetime.datetime.now().strftime("%H:%M"))
        
        # تلوين الصف حسب الحالة
        status_widget.currentIndexChanged.connect(
            lambda: self.update_row_color(row, status_widget.currentData())
        )
        self.update_row_color(row, status_widget.currentData())
        
        self.table.setCellWidget(row, 2, status_widget)
        self.table.setCellWidget(row, 3, time_widget)
        self.table.setCellWidget(row, 4, notes_widget)
    
    def update_row_color(self, row, status):
        """تحديث لون الصف حسب حالة الحضور"""
        colors = {
            'present': QColor("#E8F5E9"),
            'absent': QColor("#FFEBEE"),
            'late': QColor("#FFF3E0"),
            'excused': QColor("#E3F2FD")
        }
        
        color = colors.get(status, QColor("#FFFFFF"))
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)
    
    def save_attendance(self):
        """حفظ بيانات الحضور"""
        class_id = self.class_filter.currentData()
        if not class_id:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('select_class_first', self.language)
            )
            return
        
        date = self.date_picker.date().toString('yyyy-MM-dd')
        subject_id = self.subject_filter.currentData()
        
        try:
            for row in range(self.table.rowCount()):
                student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                status_widget = self.table.cellWidget(row, 2)
                time_widget = self.table.cellWidget(row, 3)
                notes_widget = self.table.cellWidget(row, 4)
                
                status = status_widget.currentData()
                check_in_time = time_widget.text().strip() if time_widget.text().strip() else None
                notes = notes_widget.text().strip()
                
                # التحقق من وجود سجل سابق
                existing = self.db.cursor.execute(
                    """SELECT id FROM attendance 
                       WHERE student_id = ? AND date = ? 
                       AND (subject_id = ? OR (? IS NULL AND subject_id IS NULL))""",
                    (student_id, date, subject_id, subject_id)
                ).fetchone()
                
                # ... تكملة من الكود السابق
                if existing:
                    # تحديث السجل الموجود
                    self.db.cursor.execute(
                        """UPDATE attendance 
                           SET status = ?, check_in_time = ?, notes = ?
                           WHERE id = ?""",
                        (status, check_in_time, notes, existing[0])
                    )
                else:
                    # إضافة سجل جديد
                    self.db.cursor.execute(
                        """INSERT INTO attendance 
                           (student_id, date, status, check_in_time, notes, subject_id)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (student_id, date, status, check_in_time, notes, subject_id)
                    )
            
            self.db.connection.commit()
            QMessageBox.information(
                self, tr('success', self.language),
                tr('attendance_saved_success', self.language)
            )
            self.update_info_labels()
            
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def print_report(self):
        """طباعة تقرير الحضور"""
        from utils.pdf_generator import PDFGenerator
        
        class_id = self.class_filter.currentData()
        if not class_id:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('select_class_first', self.language)
            )
            return
        
        # جمع البيانات للتقرير
        data = []
        for row in range(self.table.rowCount()):
            student_name = self.table.item(row, 0).text()
            student_id = self.table.item(row, 1).text()
            status = self.table.cellWidget(row, 2).currentText()
            time = self.table.cellWidget(row, 3).text()
            notes = self.table.cellWidget(row, 4).text()
            
            data.append({
                'student_name': student_name,
                'student_id': student_id,
                'status': status,
                'time': time,
                'notes': notes
            })
        
        # معلومات التقرير
        class_info = self.db.cursor.execute(
            "SELECT class_name, section FROM classes WHERE id = ?",
            (class_id,)
        ).fetchone()
        
        report_data = {
            'title': tr('attendance_report', self.language),
            'class': f"{class_info[0]} - {class_info[1]}",
            'date': self.date_picker.date().toString('yyyy-MM-dd'),
            'data': data,
            'summary': self.get_attendance_summary()
        }
        
        # توليد PDF
        pdf_gen = PDFGenerator(self.language)
        file_path = pdf_gen.generate_attendance_report(report_data)
        
        if file_path:
            QMessageBox.information(
                self, tr('success', self.language),
                tr('report_generated', self.language)
            )
    
    def show_statistics(self):
        """عرض إحصائيات الحضور"""
        class_id = self.class_filter.currentData()
        if not class_id:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('select_class_first', self.language)
            )
            return
        
        dialog = AttendanceStatisticsDialog(
            self.language, 
            class_id,
            self.subject_filter.currentData(),
            parent=self
        )
        dialog.exec()
    
    def get_attendance_summary(self):
        """حساب ملخص الحضور"""
        present = absent = late = excused = 0
        
        for row in range(self.table.rowCount()):
            status = self.table.cellWidget(row, 2).currentData()
            if status == 'present':
                present += 1
            elif status == 'absent':
                absent += 1
            elif status == 'late':
                late += 1
            elif status == 'excused':
                excused += 1
        
        return {
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'total': self.table.rowCount()
        }
    
    def update_info_labels(self):
        """تحديث ملصقات المعلومات"""
        summary = self.get_attendance_summary()
        
        self.info_label.setText(
            tr('attendance_info', self.language).format(
                total=summary['total'],
                present=summary['present'],
                absent=summary['absent']
            )
        )
        
        attendance_rate = (summary['present'] + summary['late']) / summary['total'] * 100 if summary['total'] > 0 else 0
        
        self.summary_label.setText(
            tr('attendance_rate', self.language).format(
                rate=f"{attendance_rate:.1f}%",
                late=summary['late'],
                excused=summary['excused']
            )
        )


class AttendanceStatisticsDialog(QDialog):
    """نافذة إحصائيات الحضور"""
    
    def __init__(self, language, class_id, subject_id=None, parent=None):
        super().__init__(parent)
        self.language = language
        self.class_id = class_id
        self.subject_id = subject_id
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_statistics()
    
    def setup_ui(self):
        self.setWindowTitle(tr('attendance_statistics', self.language))
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel(tr('attendance_statistics', self.language))
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # فترة التقرير
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel(tr('from', self.language)))
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        period_layout.addWidget(self.from_date)
        
        period_layout.addWidget(QLabel(tr('to', self.language)))
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        period_layout.addWidget(self.to_date)
        
        update_btn = QPushButton(tr('update', self.language))
        update_btn.clicked.connect(self.load_statistics)
        period_layout.addWidget(update_btn)
        
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # إحصائيات عامة
        self.general_stats = QWidget()
        self.general_layout = QHBoxLayout(self.general_stats)
        self.general_stats.setStyleSheet("""
            QWidget {
                background-color: #F5F6FA;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.general_stats)
        
        # جدول إحصائيات الطلاب
        students_label = QLabel(tr('student_statistics', self.language))
        students_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(students_label)
        
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels([
            tr('student_name', self.language),
            tr('total_days', self.language),
            tr('present_days', self.language),
            tr('absent_days', self.language),
            tr('late_days', self.language),
            tr('excused_days', self.language),
            tr('attendance_rate', self.language)
        ])
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.setAlternatingRowColors(True)
        layout.addWidget(self.students_table)
        
        # أزرار
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton(tr('export_excel', self.language))
        export_btn.clicked.connect(self.export_to_excel)
        buttons_layout.addWidget(export_btn)
        
        close_btn = QPushButton(tr('close', self.language))
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def load_statistics(self):
        """تحميل الإحصائيات"""
        from_date = self.from_date.date().toString('yyyy-MM-dd')
        to_date = self.to_date.date().toString('yyyy-MM-dd')
        
        # إحصائيات عامة
        self.load_general_statistics(from_date, to_date)
        
        # إحصائيات الطلاب
        self.load_student_statistics(from_date, to_date)
    
    def load_general_statistics(self, from_date, to_date):
        """تحميل الإحصائيات العامة"""
        # مسح الويدجات السابقة
        for i in reversed(range(self.general_layout.count())): 
            self.general_layout.itemAt(i).widget().setParent(None)
        
        # إجمالي الأيام الدراسية
        total_days = self.db.cursor.execute(
            """SELECT COUNT(DISTINCT date) FROM attendance 
               WHERE date BETWEEN ? AND ? AND student_id IN 
               (SELECT id FROM students WHERE class_id = ?)""",
            (from_date, to_date, self.class_id)
        ).fetchone()[0]
        
        # إحصائيات الحضور
        stats = self.db.cursor.execute(
            """SELECT status, COUNT(*) FROM attendance 
               WHERE date BETWEEN ? AND ? AND student_id IN 
               (SELECT id FROM students WHERE class_id = ?)
               GROUP BY status""",
            (from_date, to_date, self.class_id)
        ).fetchall()
        
        stats_dict = dict(stats)
        
        # عرض الإحصائيات
        self.add_stat_widget(tr('total_school_days', self.language), str(total_days))
        self.add_stat_widget(tr('total_present', self.language), str(stats_dict.get('present', 0)))
        self.add_stat_widget(tr('total_absent', self.language), str(stats_dict.get('absent', 0)))
        self.add_stat_widget(tr('total_late', self.language), str(stats_dict.get('late', 0)))
        self.add_stat_widget(tr('total_excused', self.language), str(stats_dict.get('excused', 0)))
    
    def add_stat_widget(self, label, value):
        """إضافة ويدجت إحصائية"""
        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498DB;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget_layout.addWidget(value_label)
        
        text_label = QLabel(label)
        text_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget_layout.addWidget(text_label)
        
        self.general_layout.addWidget(widget)
    
    def load_student_statistics(self, from_date, to_date):
        """تحميل إحصائيات الطلاب"""
        # جلب الطلاب
        students = self.db.cursor.execute(
            """SELECT id, full_name FROM students 
               WHERE class_id = ? ORDER BY full_name""",
            (self.class_id,)
        ).fetchall()
        
        self.students_table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # اسم الطالب
            self.students_table.setItem(row, 0, QTableWidgetItem(student[1]))
            
            # إحصائيات الحضور
            stats = self.db.cursor.execute(
                """SELECT 
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                   SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent,
                   SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late,
                   SUM(CASE WHEN status = 'excused' THEN 1 ELSE 0 END) as excused
                   FROM attendance 
                   WHERE student_id = ? AND date BETWEEN ? AND ?""",
                (student[0], from_date, to_date)
            ).fetchone()
            
            if stats and stats[0] > 0:
                self.students_table.setItem(row, 1, QTableWidgetItem(str(stats[0])))
                self.students_table.setItem(row, 2, QTableWidgetItem(str(stats[1])))
                self.students_table.setItem(row, 3, QTableWidgetItem(str(stats[2])))
                self.students_table.setItem(row, 4, QTableWidgetItem(str(stats[3])))
                self.students_table.setItem(row, 5, QTableWidgetItem(str(stats[4])))
                
                # نسبة الحضور
                attendance_rate = ((stats[1] + stats[3]) / stats[0]) * 100
                rate_item = QTableWidgetItem(f"{attendance_rate:.1f}%")
                
                # تلوين حسب النسبة
                if attendance_rate >= 90:
                    rate_item.setForeground(QColor("#27AE60"))
                elif attendance_rate >= 75:
                    rate_item.setForeground(QColor("#F39C12"))
                else:
                    rate_item.setForeground(QColor("#E74C3C"))
                
                self.students_table.setItem(row, 6, rate_item)
            else:
                for col in range(1, 7):
                    self.students_table.setItem(row, col, QTableWidgetItem("0"))
    
    def export_to_excel(self):
        """تصدير الإحصائيات إلى Excel"""
        from PyQt6.QtWidgets import QFileDialog
        import pandas as pd
        
        file_path, _ = QFileDialog.
