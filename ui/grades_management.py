from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QComboBox, QDialog,
                           QFormLayout, QMessageBox, QLabel, QSpinBox,
                           QHeaderView, QAbstractItemView, QLineEdit,
                           QDateEdit, QTextEdit)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor
from database.db_manager import DatabaseManager
from utils.translations import tr
import datetime

class GradesManagement(QWidget):
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
        
        # فلتر الصف
        self.class_filter = QComboBox()
        self.class_filter.setMinimumWidth(150)
        filters_layout.addWidget(QLabel(tr('class', self.language)))
        filters_layout.addWidget(self.class_filter)
        
        # فلتر المادة
        self.subject_filter = QComboBox()
        self.subject_filter.setMinimumWidth(150)
        filters_layout.addWidget(QLabel(tr('subject', self.language)))
        filters_layout.addWidget(self.subject_filter)
        
        # فلتر نوع الامتحان
        self.exam_type_filter = QComboBox()
        self.exam_type_filter.addItem(tr('all_exams', self.language), None)
        self.exam_type_filter.addItem(tr('midterm', self.language), 'midterm')
        self.exam_type_filter.addItem(tr('final', self.language), 'final')
        self.exam_type_filter.addItem(tr('quiz', self.language), 'quiz')
        self.exam_type_filter.addItem(tr('assignment', self.language), 'assignment')
        filters_layout.addWidget(QLabel(tr('exam_type', self.language)))
        filters_layout.addWidget(self.exam_type_filter)
        
        filters_layout.addStretch()
        
        # زر البحث
        search_btn = QPushButton(tr('search', self.language))
        search_btn.setObjectName("primaryButton")
        search_btn.clicked.connect(self.load_grades)
        filters_layout.addWidget(search_btn)
        
        layout.addLayout(filters_layout)
        
        # شريط الأدوات
        toolbar = QHBoxLayout()
        
        # زر إضافة درجات
        add_grades_btn = QPushButton(f"➕ {tr('add_grades', self.language)}")
        add_grades_btn.setObjectName("successButton")
        add_grades_btn.clicked.connect(self.show_add_grades_dialog)
        toolbar.addWidget(add_grades_btn)
        
        # زر إضافة امتحان
        add_exam_btn = QPushButton(f"📝 {tr('add_exam', self.language)}")
        add_exam_btn.clicked.connect(self.show_add_exam_dialog)
        toolbar.addWidget(add_exam_btn)
        
        toolbar.addStretch()
        
        # زر التصدير
        export_btn = QPushButton(f"📥 {tr('export_grades', self.language)}")
        export_btn.clicked.connect(self.export_grades)
        toolbar.addWidget(export_btn)
        
        # زر الإحصائيات
        stats_btn = QPushButton(f"📊 {tr('statistics', self.language)}")
        stats_btn.clicked.# ... تكملة من الكود السابق
        stats_btn.clicked.connect(self.show_statistics)
        toolbar.addWidget(stats_btn)
        
        layout.addLayout(toolbar)
        
        # جدول الدرجات
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        # شريط المعلومات والإحصائيات
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            padding: 10px;
            background-color: #F5F6FA;
            border-radius: 5px;
            color: #7F8C8D;
        """)
        info_layout.addWidget(self.info_label)
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            padding: 10px;
            background-color: #E8F5E9;
            border-radius: 5px;
            color: #2E7D32;
        """)
        info_layout.addWidget(self.stats_label)
        
        layout.addLayout(info_layout)
        
        # ربط الأحداث
        self.class_filter.currentIndexChanged.connect(self.on_class_changed)
        self.subject_filter.currentIndexChanged.connect(self.load_grades)
        self.exam_type_filter.currentIndexChanged.connect(self.load_grades)
    
    def setup_table(self):
        headers = [
            tr('student_name', self.language),
            tr('student_id', self.language),
            tr('exam_name', self.language),
            tr('exam_type', self.language),
            tr('date', self.language),
            tr('score', self.language),
            tr('max_score', self.language),
            tr('percentage', self.language),
            tr('grade', self.language),
            tr('actions', self.language)
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # تحديد عرض الأعمدة
        self.table.setColumnWidth(0, 200)  # اسم الطالب
        self.table.setColumnWidth(1, 100)  # رقم الطالب
        self.table.setColumnWidth(2, 150)  # اسم الامتحان
        self.table.setColumnWidth(3, 100)  # نوع الامتحان
        self.table.setColumnWidth(4, 100)  # التاريخ
        self.table.setColumnWidth(5, 80)   # الدرجة
        self.table.setColumnWidth(6, 80)   # الدرجة الكاملة
        self.table.setColumnWidth(7, 80)   # النسبة
        self.table.setColumnWidth(8, 80)   # التقدير
        self.table.setColumnWidth(9, 100)  # الإجراءات
    
    def load_filters(self):
        # تحميل الصفوف
        self.class_filter.clear()
        self.class_filter.addItem(tr('select_class', self.language), None)
        
        if self.user_data and self.user_data['user_type'] == 'teacher':
            # للمعلم: عرض الصفوف التي يدرسها فقط
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
        self.subject_filter.addItem(tr('select_subject', self.language), None)
        
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
            # للمدير: عرض جميع المواد للصف
            subjects = self.db.cursor.execute(
                """SELECT DISTINCT s.id, s.subject_name 
                   FROM subjects s
                   JOIN timetable t ON s.id = t.subject_id
                   WHERE t.class_id = ?""",
                (class_id,)
            ).fetchall()
            
            for subject in subjects:
                self.subject_filter.addItem(subject[1], subject[0])
    
    def load_grades(self):
        """تحميل الدرجات حسب الفلاتر"""
        self.table.setRowCount(0)
        
        class_id = self.class_filter.currentData()
        subject_id = self.subject_filter.currentData()
        exam_type = self.exam_type_filter.currentData()
        
        if not class_id or not subject_id:
            return
        
        # استعلام الدرجات
        query = """
            SELECT g.id, s.full_name, s.student_id, e.exam_name, e.exam_type,
                   e.exam_date, g.score, e.max_score, g.notes,
                   ROUND((g.score * 100.0 / e.max_score), 2) as percentage
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN exams e ON g.exam_id = e.id
            WHERE e.class_id = ? AND e.subject_id = ?
        """
        params = [class_id, subject_id]
        
        if exam_type:
            query += " AND e.exam_type = ?"
            params.append(exam_type)
        
        query += " ORDER BY s.full_name, e.exam_date DESC"
        
        grades = self.db.cursor.execute(query, params).fetchall()
        
        for grade in grades:
            self.add_grade_to_table(grade)
        
        self.update_info_labels()
    
    def add_grade_to_table(self, grade):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # البيانات
        grade_id, student_name, student_id, exam_name, exam_type, exam_date, score, max_score, notes, percentage = grade
        
        # تحديد التقدير
        grade_letter = self.get_grade_letter(percentage)
        
        # إضافة البيانات للجدول
        self.table.setItem(row, 0, QTableWidgetItem(student_name))
        self.table.setItem(row, 1, QTableWidgetItem(student_id))
        self.table.setItem(row, 2, QTableWidgetItem(exam_name))
        self.table.setItem(row, 3, QTableWidgetItem(tr(f"exam_{exam_type}", self.language)))
        self.table.setItem(row, 4, QTableWidgetItem(str(exam_date)))
        
        # الدرجة مع تلوين حسب الأداء
        score_item = QTableWidgetItem(str(score))
        if percentage >= 90:
            score_item.setForeground(QColor("#27AE60"))
        elif percentage >= 75:
            score_item.setForeground(QColor("#3498DB"))
        elif percentage >= 60:
            score_item.setForeground(QColor("#F39C12"))
        else:
            score_item.setForeground(QColor("#E74C3C"))
        self.table.setItem(row, 5, score_item)
        
        self.table.setItem(row, 6, QTableWidgetItem(str(max_score)))
        self.table.setItem(row, 7, QTableWidgetItem(f"{percentage}%"))
        
        # التقدير مع تلوين
        grade_item = QTableWidgetItem(grade_letter)
        grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if grade_letter == 'A+' or grade_letter == 'A':
            grade_item.setForeground(QColor("#27AE60"))
        elif grade_letter == 'B':
            grade_item.setForeground(QColor("#3498DB"))
        elif grade_letter == 'C':
            grade_item.setForeground(QColor("#F39C12"))
        else:
            grade_item.setForeground(QColor("#E74C3C"))
        self.table.setItem(row, 8, grade_item)
        
        # الإجراءات
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip(tr('edit', self.language))
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(lambda: self.edit_grade(grade_id))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip(tr('delete', self.language))
        delete_btn.setFixedSize(30, 30)
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_grade(grade_id))
        actions_layout.addWidget(delete_btn)
        
        self.table.setCellWidget(row, 9, actions_widget)
    
    def get_grade_letter(self, percentage):
        """تحديد التقدير بناءً على النسبة المئوية"""
        if percentage >= 95:
            return 'A+'
        elif percentage >= 90:
            return 'A'
        elif percentage >= 85:
            return 'B+'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 75:
            return 'C+'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 65:
            return 'D+'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def show_add_exam_dialog(self):
        """عرض نافذة إضافة امتحان جديد"""
        dialog = ExamDialog(self.language, self.class_filter.currentData(), 
                          self.subject_filter.currentData(), parent=self)
        if dialog.exec():
            self.load_grades()
    
    def show_add_grades_dialog(self):
        """عرض نافذة إضافة درجات"""
        if not self.class_filter.currentData() or not self.subject_filter.currentData():
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('select_class_and_subject', self.language)
            )
            return
        
        dialog = GradesEntryDialog(
            self.language, 
            self.class_filter.currentData(),
            self.subject_filter.currentData(),
            parent=self
        )
        if dialog.exec():
            self.load_grades()
    
    def edit_grade(self, grade_id):
        """تعديل درجة"""
        # الحصول على بيانات الدرجة
        grade_data = self.db.cursor.execute(
            """SELECT g.*, s.full_name, e.exam_name 
               FROM grades g
               JOIN students s ON g.student_id = s.id
               JOIN exams e ON g.exam_id = e.id
               WHERE g.id = ?""",
            (grade_id,)
        ).fetchone()
        
        if grade_data:
            dialog = EditGradeDialog(self.language, grade_data, self)
            if dialog.exec():
                self.load_grades()
    
    def delete_grade(self, grade_id):
        """حذف درجة"""
        msg = QMessageBox.question(
            self, tr('confirm_delete', self.language),
            tr('delete_grade_confirm', self.language),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
                self.db.connection.commit()
                self.load_grades()
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def export_grades(self):
        """تصدير الدرجات إلى Excel"""
        from PyQt6.QtWidgets import QFileDialog
        import pandas as pd
        
        if self.table.rowCount() == 0:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('no_data_to_export', self.language)
            )
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr('save_file', self.language),
            f"grades_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # جمع البيانات
                data = []
                headers = []
                
                # ... تكملة من الكود السابق
                for col in range(self.table.columnCount() - 1):  # استثناء عمود الإجراءات
                    headers.append(self.table.horizontalHeaderItem(col).text())
                
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount() - 1):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else '')
                    data.append(row_data)
                
                # إنشاء DataFrame وحفظه
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_path, index=False)
                
                QMessageBox.information(
                    self,
                    tr('success', self.language),
                    tr('export_success', self.language)
                )
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def show_statistics(self):
        """عرض إحصائيات الدرجات"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('no_data_for_statistics', self.language)
            )
            return
        
        dialog = StatisticsDialog(
            self.language,
            self.class_filter.currentData(),
            self.subject_filter.currentData(),
            self.exam_type_filter.currentData(),
            parent=self
        )
        dialog.exec()
    
    def update_info_labels(self):
        """تحديث معلومات الجدول والإحصائيات"""
        total = self.table.rowCount()
        
        if total > 0:
            # حساب الإحصائيات
            scores = []
            for row in range(total):
                score_item = self.table.item(row, 5)
                max_score_item = self.table.item(row, 6)
                if score_item and max_score_item:
                    percentage = (float(score_item.text()) / float(max_score_item.text())) * 100
                    scores.append(percentage)
            
            if scores:
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                passed = sum(1 for s in scores if s >= 60)
                
                self.info_label.setText(
                    tr('grades_info', self.language).format(
                        total=total, passed=passed, failed=total-passed
                    )
                )
                
                self.stats_label.setText(
                    tr('grades_stats', self.language).format(
                        avg=f"{avg_score:.1f}%",
                        max=f"{max_score:.1f}%",
                        min=f"{min_score:.1f}%"
                    )
                )
            else:
                self.info_label.setText(tr('no_grades', self.language))
                self.stats_label.setText("")
        else:
            self.info_label.setText(tr('no_grades', self.language))
            self.stats_label.setText("")
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_filters()
        self.load_grades()


class ExamDialog(QDialog):
    """نافذة إضافة امتحان جديد"""
    
    def __init__(self, language, class_id, subject_id, parent=None):
        super().__init__(parent)
        self.language = language
        self.class_id = class_id
        self.subject_id = subject_id
        self.db = DatabaseManager()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle(tr('add_exam', self.language))
        self.setFixedWidth(450)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # اسم الامتحان
        self.exam_name = QLineEdit()
        form.addRow(tr('exam_name', self.language), self.exam_name)
        
        # نوع الامتحان
        self.exam_type = QComboBox()
        self.exam_type.addItem(tr('midterm', self.language), 'midterm')
        self.exam_type.addItem(tr('final', self.language), 'final')
        self.exam_type.addItem(tr('quiz', self.language), 'quiz')
        self.exam_type.addItem(tr('assignment', self.language), 'assignment')
        form.addRow(tr('exam_type', self.language), self.exam_type)
        
        # تاريخ الامتحان
        self.exam_date = QDateEdit()
        self.exam_date.setCalendarPopup(True)
        self.exam_date.setDate(QDate.currentDate())
        form.addRow(tr('exam_date', self.language), self.exam_date)
        
        # الدرجة الكاملة
        self.max_score = QSpinBox()
        self.max_score.setMinimum(1)
        self.max_score.setMaximum(200)
        self.max_score.setValue(100)
        form.addRow(tr('max_score', self.language), self.max_score)
        
        # الوصف
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        form.addRow(tr('description', self.language), self.description)
        
        layout.addLayout(form)
        
        # الأزرار
        buttons = QHBoxLayout()
        save_btn = QPushButton(tr('save', self.language))
        save_btn.setObjectName("successButton")
        save_btn.clicked.connect(self.save_exam)
        cancel_btn = QPushButton(tr('cancel', self.language))
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def save_exam(self):
        if not self.exam_name.text().strip():
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('exam_name_required', self.language)
            )
            return
        
        try:
            self.db.cursor.execute(
                """INSERT INTO exams (exam_name, exam_type, exam_date, max_score, 
                   description, class_id, subject_id) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    self.exam_name.text().strip(),
                    self.exam_type.currentData(),
                    self.exam_date.date().toString('yyyy-MM-dd'),
                    self.max_score.value(),
                    self.description.toPlainText().strip(),
                    self.class_id,
                    self.subject_id
                )
            )
            self.db.connection.commit()
            QMessageBox.information(
                self, tr('success', self.language),
                tr('exam_added_success', self.language)
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))


class GradesEntryDialog(QDialog):
    """نافذة إدخال الدرجات"""
    
    def __init__(self, language, class_id, subject_id, parent=None):
        super().__init__(parent)
        self.language = language
        self.class_id = class_id
        self.subject_id = subject_id
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle(tr('add_grades', self.language))
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # اختيار الامتحان
        exam_layout = QHBoxLayout()
        exam_layout.addWidget(QLabel(tr('select_exam', self.language)))
        
        self.exam_combo = QComboBox()
        self.exam_combo.setMinimumWidth(300)
        self.exam_combo.currentIndexChanged.connect(self.on_exam_changed)
        exam_layout.addWidget(self.exam_combo)
        
        exam_layout.addStretch()
        
        self.exam_info_label = QLabel()
        exam_layout.addWidget(self.exam_info_label)
        
        layout.addLayout(exam_layout)
        
        # جدول إدخال الدرجات
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            tr('student_name', self.language),
            tr('student_id', self.language),
            tr('score', self.language),
            tr('notes', self.language)
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 100)
        
        layout.addWidget(self.table)
        
        # الأزرار
        buttons = QHBoxLayout()
        
        # زر الحفظ
        save_btn = QPushButton(tr('save_grades', self.language))
        save_btn.setObjectName("successButton")
        save_btn.clicked.connect(self.save_grades)
        buttons.addWidget(save_btn)
        
        # زر الإلغاء
        cancel_btn = QPushButton(tr('cancel', self.language))
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def load_data(self):
        """تحميل الامتحانات والطلاب"""
        # تحميل الامتحانات
        exams = self.db.cursor.execute(
            """SELECT id, exam_name, exam_type, exam_date, max_score 
               FROM exams 
               WHERE class_id = ? AND subject_id = ?
               ORDER BY exam_date DESC""",
            (self.class_id, self.subject_id)
        ).fetchall()
        
        self.exam_combo.clear()
        self.exam_combo.addItem(tr('select_exam', self.language), None)
        
        for exam in exams:
            exam_text = f"{exam[1]} - {tr(f'exam_{exam[2]}', self.language)} ({exam[3]})"
            self.exam_combo.addItem(exam_text, {
                'id': exam[0],
                'max_score': exam[4]
            })
    
    def on_exam_changed(self):
        """عند تغيير الامتحان المحدد"""
        exam_data = self.exam_combo.currentData()
        if not exam_data:
            self.table.setRowCount(0)
            self.exam_info_label.setText("")
            return
        
        # عرض معلومات الامتحان
        self.exam_info_label.setText(
            tr('max_score', self.language) + f": {exam_data['max_score']}"
        )
        
        # تحميل الطلاب
        students = self.db.cursor.execute(
            """SELECT id, full_name, student_id 
               FROM students 
               WHERE class_id = ?
               ORDER BY full_name""",
            (self.class_id,)
        ).fetchall()
        
        self.table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # اسم الطالب
            self.table.setItem(row, 0, QTableWidgetItem(student[1]))
            self.table.item(row, 0).setFlags(Qt.ItemFlag.ItemIsEnabled)
            
            # رقم الطالب
            self.table.setItem(row, 1, QTableWidgetItem(student[2]))
            self.table.item(row, 1).setFlags(Qt.ItemFlag.ItemIsEnabled)
            
            # التحقق من وجود درجة سابقة
            existing_grade = self.db.cursor.execute(
                """SELECT score, notes FROM grades 
                   WHERE student_id = ? AND exam_id = ?""",
                (student[0], exam_data['id'])
            ).fetchone()
            
            # حقل الدرجة
            score_input = QSpinBox()
            score_input.setMinimum(0)
            score_input.setMaximum(exam_data['max_score'])
            if existing_grade:
                score_input.setValue(existing_grade[0])
            self.table.setCellWidget(row, 2, score_input)
            
            # حقل الملاحظات
            notes_input = QLineEdit()
            if existing_grade and existing_grade[1]:
                notes_input.setText(existing_grade[1])
            self.table.setCellWidget(row, 3, notes_input)
            
            # حفظ معرف الطالب
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, student[0])
    
    def save_grades(self):
        """حفظ الدرجات"""
        exam_data = self.exam_combo.currentData()
        if not exam_data:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('select_exam_first', self.language)
            )
            return
        
        try:
            for row in range(self.table.rowCount()):
                student_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                score_widget = self.table.cellWidget(row, 2)
                notes_widget = self.table.cellWidget(row, 3)
                
                score = score_widget.value()
                notes = notes_widget.text().strip()
                
                # التحقق من وجود درجة سابقة
                existing = self.db.cursor.execute(
                    "SELECT id FROM grades WHERE student_id = ? AND exam_id = ?",
                    (student_id, exam_data['id'])
                ).fetchone()
                
                if existing:
                    # تحديث الدرجة الموجودة
                    self.db.cursor.execute(
                        "UPDATE grades SET score = ?, notes = ? WHERE id = ?",
                        (score, notes, existing[0])
                    )
                else:
                    # إضافة درجة جديدة
                    self.db.cursor.execute(
                        "INSERT INTO grades (student_id, exam_id, score, notes) VALUES (?, ?, ?, ?)",
                        (student_id, exam_data['id'], score, notes)
                    )
            
            self.db.connection.commit()
            QMessageBox.information(
                self, tr('success', self.language),
                tr('grades_saved_success', self.language)
            )
            self.accept()
        except Exception as e:
            # ... تكملة من الكود السابق
            QMessageBox.critical(self, tr('error', self.language), str(e))


class EditGradeDialog(QDialog):
    """نافذة تعديل درجة واحدة"""
    
    def __init__(self, language, grade_data, parent=None):
        super().__init__(parent)
        self.language = language
        self.grade_data = grade_data
        self.db = DatabaseManager()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle(tr('edit_grade', self.language))
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # معلومات الطالب (للقراءة فقط)
        student_info = QLineEdit(self.grade_data[1])  # اسم الطالب
        student_info.setReadOnly(True)
        form.addRow(tr('student_name', self.language), student_info)
        
        # معلومات الامتحان (للقراءة فقط)
        exam_info = QLineEdit(self.grade_data[2])  # اسم الامتحان
        exam_info.setReadOnly(True)
        form.addRow(tr('exam_name', self.language), exam_info)
        
        # الدرجة الكاملة
        max_score_info = QLineEdit(str(self.grade_data[7]))  # الدرجة الكاملة
        max_score_info.setReadOnly(True)
        form.addRow(tr('max_score', self.language), max_score_info)
        
        # الدرجة
        self.score_input = QSpinBox()
        self.score_input.setMinimum(0)
        self.score_input.setMaximum(self.grade_data[7])  # max_score
        self.score_input.setValue(self.grade_data[6])  # current score
        form.addRow(tr('score', self.language), self.score_input)
        
        # الملاحظات
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        if self.grade_data[8]:  # notes
            self.notes_input.setPlainText(self.grade_data[8])
        form.addRow(tr('notes', self.language), self.notes_input)
        
        layout.addLayout(form)
        
        # الأزرار
        buttons = QHBoxLayout()
        save_btn = QPushButton(tr('save', self.language))
        save_btn.setObjectName("successButton")
        save_btn.clicked.connect(self.save_grade)
        cancel_btn = QPushButton(tr('cancel', self.language))
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def save_grade(self):
        try:
            self.db.cursor.execute(
                "UPDATE grades SET score = ?, notes = ? WHERE id = ?",
                (
                    self.score_input.value(),
                    self.notes_input.toPlainText().strip(),
                    self.grade_data[0]  # grade_id
                )
            )
            self.db.connection.commit()
            QMessageBox.information(
                self, tr('success', self.language),
                tr('grade_updated_success', self.language)
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))


class StatisticsDialog(QDialog):
    """نافذة عرض الإحصائيات"""
    
    def __init__(self, language, class_id, subject_id, exam_type, parent=None):
        super().__init__(parent)
        self.language = language
        self.class_id = class_id
        self.subject_id = subject_id
        self.exam_type = exam_type
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_statistics()
    
    def setup_ui(self):
        self.setWindowTitle(tr('grade_statistics', self.language))
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel(tr('grade_statistics', self.language))
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # معلومات عامة
        self.info_widget = QWidget()
        self.info_layout = QFormLayout(self.info_widget)
        self.info_widget.setStyleSheet("""
            QWidget {
                background-color: #F5F6FA;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.info_widget)
        
        # إحصائيات الامتحانات
        exams_group = QLabel(tr('exams_statistics', self.language))
        exams_group.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(exams_group)
        
        # جدول الإحصائيات
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(6)
        self.stats_table.setHorizontalHeaderLabels([
            tr('exam_name', self.language),
            tr('exam_type', self.language),
            tr('average', self.language),
            tr('highest', self.language),
            tr('lowest', self.language),
            tr('pass_rate', self.language)
        ])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setAlternatingRowColors(True)
        layout.addWidget(self.stats_table)
        
        # إحصائيات الطلاب
        students_group = QLabel(tr('top_students', self.language))
        students_group.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(students_group)
        
        # جدول أفضل الطلاب
        self.top_students_table = QTableWidget()
        self.top_students_table.setColumnCount(3)
        self.top_students_table.setHorizontalHeaderLabels([
            tr('rank', self.language),
            tr('student_name', self.language),
            tr('average_score', self.language)
        ])
        self.top_students_table.horizontalHeader().setStretchLastSection(True)
        self.top_students_table.setMaximumHeight(200)
        layout.addWidget(self.top_students_table)
        
        # زر الإغلاق
        close_btn = QPushButton(tr('close', self.language))
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(100)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def load_statistics(self):
        """تحميل وعرض الإحصائيات"""
        # معلومات عامة
        class_info = self.db.cursor.execute(
            "SELECT class_name, section FROM classes WHERE id = ?",
            (self.class_id,)
        ).fetchone()
        
        subject_info = self.db.cursor.execute(
            "SELECT subject_name FROM subjects WHERE id = ?",
            (self.subject_id,)
        ).fetchone()
        
        total_students = self.db.cursor.execute(
            "SELECT COUNT(*) FROM students WHERE class_id = ?",
            (self.class_id,)
        ).fetchone()[0]
        
        self.info_layout.addRow(
            tr('class', self.language),
            QLabel(f"{class_info[0]} - {class_info[1]}")
        )
        self.info_layout.addRow(
            tr('subject', self.language),
            QLabel(subject_info[0])
        )
        self.info_layout.addRow(
            tr('total_students', self.language),
            QLabel(str(total_students))
        )
        
        # إحصائيات الامتحانات
        query = """
            SELECT e.id, e.exam_name, e.exam_type, e.max_score,
                   AVG(g.score) as avg_score,
                   MAX(g.score) as max_score,
                   MIN(g.score) as min_score,
                   COUNT(g.id) as total_grades,
                   SUM(CASE WHEN g.score >= e.max_score * 0.6 THEN 1 ELSE 0 END) as passed
            FROM exams e
            LEFT JOIN grades g ON e.id = g.exam_id
            WHERE e.class_id = ? AND e.subject_id = ?
        """
        params = [self.class_id, self.subject_id]
        
        if self.exam_type:
            query += " AND e.exam_type = ?"
            params.append(self.exam_type)
        
        query += " GROUP BY e.id ORDER BY e.exam_date DESC"
        
        exams_stats = self.db.cursor.execute(query, params).fetchall()
        
        self.stats_table.setRowCount(len(exams_stats))
        
        for row, exam in enumerate(exams_stats):
            self.stats_table.setItem(row, 0, QTableWidgetItem(exam[1]))  # exam_name
            self.stats_table.setItem(row, 1, QTableWidgetItem(tr(f'exam_{exam[2]}', self.language)))
            
            if exam[4] is not None:  # avg_score
                avg_percentage = (exam[4] / exam[3]) * 100
                self.stats_table.setItem(row, 2, QTableWidgetItem(f"{avg_percentage:.1f}%"))
                
                max_percentage = (exam[5] / exam[3]) * 100
                self.stats_table.setItem(row, 3, QTableWidgetItem(f"{max_percentage:.1f}%"))
                
                min_percentage = (exam[6] / exam[3]) * 100
                self.stats_table.setItem(row, 4, QTableWidgetItem(f"{min_percentage:.1f}%"))
                
                pass_rate = (exam[8] / exam[7]) * 100 if exam[7] > 0 else 0
                self.stats_table.setItem(row, 5, QTableWidgetItem(f"{pass_rate:.1f}%"))
            else:
                self.stats_table.setItem(row, 2, QTableWidgetItem("-"))
                self.stats_table.setItem(row, 3, QTableWidgetItem("-"))
                self.stats_table.setItem(row, 4, QTableWidgetItem("-"))
                self.stats_table.setItem(row, 5, QTableWidgetItem("-"))
        
        # أفضل الطلاب
        top_students = self.db.cursor.execute("""
            SELECT s.full_name,
                   AVG(g.score * 100.0 / e.max_score) as avg_percentage
            FROM students s
            JOIN grades g ON s.id = g.student_id
            JOIN exams e ON g.exam_id = e.id
            WHERE e.class_id = ? AND e.subject_id = ?
            GROUP BY s.id
            ORDER BY avg_percentage DESC
            LIMIT 10
        """, (self.class_id, self.subject_id)).fetchall()
        
        self.top_students_table.setRowCount(len(top_students))
        
        for row, student in enumerate(top_students):
            self.top_students_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.top_students_table.setItem(row, 1, QTableWidgetItem(student[0]))
            self.top_students_table.setItem(row, 2, QTableWidgetItem(f"{student[1]:.1f}%"))
