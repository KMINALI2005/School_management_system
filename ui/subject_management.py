from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
                           QFormLayout, QMessageBox, QLabel, QTextEdit,
                           QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from utils.translations import tr

class SubjectManagement(QWidget):
    def __init__(self, language='ar'):
        super().__init__()
        self.language = language
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_subjects()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # شريط الأدوات
        toolbar = QHBoxLayout()
        
        # زر إضافة مادة
        self.add_button = QPushButton(f"➕ {tr('add_subject', self.language)}")
        self.add_button.setObjectName("successButton")
        self.add_button.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(self.add_button)
        
        # البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('search_subjects', self.language))
        self.search_input.textChanged.connect(self.search_subjects)
        self.search_input.setMaximumWidth(300)
        toolbar.addWidget(self.search_input)
        
        toolbar.addStretch()
        
        # زر التحديث
        refresh_button = QPushButton("🔄")
        refresh_button.setFixedSize(40, 40)
        refresh_button.clicked.connect(self.refresh_table)
        toolbar.addWidget(refresh_button)
        
        layout.addLayout(toolbar)
        
        # الجدول
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        # شريط المعلومات
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""
            padding: 10px;
            background-color: #F5F6FA;
      # ... تكملة من الكود السابق
            border-radius: 5px;
            color: #7F8C8D;
        """)
        layout.addWidget(self.info_label)
    
    def setup_table(self):
        headers = [
            tr('subject_code', self.language),
            tr('subject_name', self.language),
            tr('description', self.language),
            tr('assigned_teachers', self.language),
            tr('assigned_classes', self.language),
            tr('actions', self.language)
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # تحديد عرض الأعمدة
        self.table.setColumnWidth(0, 120)  # رمز المادة
        self.table.setColumnWidth(1, 200)  # اسم المادة
        self.table.setColumnWidth(2, 250)  # الوصف
        self.table.setColumnWidth(3, 200)  # المعلمون
        self.table.setColumnWidth(4, 150)  # الصفوف
        self.table.setColumnWidth(5, 150)  # الإجراءات
    
    def load_subjects(self):
        self.table.setRowCount(0)
        subjects = self.db.get_all_subjects()
        
        for subject in subjects:
            self.add_subject_to_table(subject)
        
        self.update_info_label()
    
    def add_subject_to_table(self, subject):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # الحصول على المعلمين المسندين
        teachers = self.db.cursor.execute(
            """SELECT t.full_name FROM teachers t
               JOIN teacher_subjects ts ON t.id = ts.teacher_id
               WHERE ts.subject_id = ?""",
            (subject['id'],)
        ).fetchall()
        teachers_text = ", ".join([t[0] for t in teachers]) if teachers else tr('no_teachers', self.language)
        
        # الحصول على الصفوف المسندة
        classes = self.db.cursor.execute(
            """SELECT DISTINCT c.class_name, c.section FROM classes c
               JOIN timetable t ON c.id = t.class_id
               WHERE t.subject_id = ?""",
            (subject['id'],)
        ).fetchall()
        classes_text = ", ".join([f"{c[0]}-{c[1]}" for c in classes]) if classes else tr('no_classes', self.language)
        
        # البيانات
        self.table.setItem(row, 0, QTableWidgetItem(subject['subject_code']))
        self.table.setItem(row, 1, QTableWidgetItem(subject['subject_name']))
        self.table.setItem(row, 2, QTableWidgetItem(subject.get('description', '')))
        self.table.setItem(row, 3, QTableWidgetItem(teachers_text))
        self.table.setItem(row, 4, QTableWidgetItem(classes_text))
        
        # الإجراءات
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip(tr('edit', self.language))
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(lambda: self.edit_subject(subject['id']))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip(tr('delete', self.language))
        delete_btn.setFixedSize(30, 30)
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_subject(subject['id']))
        actions_layout.addWidget(delete_btn)
        
        assign_btn = QPushButton("👥")
        assign_btn.setToolTip(tr('assign_teachers', self.language))
        assign_btn.setFixedSize(30, 30)
        assign_btn.clicked.connect(lambda: self.assign_teachers(subject['id']))
        actions_layout.addWidget(assign_btn)
        
        self.table.setCellWidget(row, 5, actions_widget)
    
    def show_add_dialog(self):
        dialog = SubjectDialog(self.language, parent=self)
        if dialog.exec():
            try:
                self.db.add_subject(dialog.get_data())
                self.refresh_table()
                QMessageBox.information(
                    self, tr('success', self.language),
                    tr('subject_added_success', self.language)
                )
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def edit_subject(self, subject_id):
        subject_data = self.db.cursor.execute(
            "SELECT * FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        
        if subject_data:
            columns = [description[0] for description in self.db.cursor.description]
            subject_dict = dict(zip(columns, subject_data))
            
            dialog = SubjectDialog(self.language, subject_dict, self)
            if dialog.exec():
                try:
                    data = dialog.get_data()
                    self.db.cursor.execute(
                        """UPDATE subjects SET subject_code = ?, subject_name = ?, 
                           description = ? WHERE id = ?""",
                        (data['subject_code'], data['subject_name'], 
                         data['description'], subject_id)
                    )
                    self.db.connection.commit()
                    self.refresh_table()
                except Exception as e:
                    QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def delete_subject(self, subject_id):
        # التحقق من الارتباطات
        teacher_count = self.db.cursor.execute(
            "SELECT COUNT(*) FROM teacher_subjects WHERE subject_id = ?", 
            (subject_id,)
        ).fetchone()[0]
        
        timetable_count = self.db.cursor.execute(
            "SELECT COUNT(*) FROM timetable WHERE subject_id = ?", 
            (subject_id,)
        ).fetchone()[0]
        
        if teacher_count > 0 or timetable_count > 0:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('subject_has_dependencies', self.language)
            )
            return
        
        msg = QMessageBox.question(
            self, tr('confirm_delete', self.language),
            tr('delete_subject_confirm', self.language),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
                self.db.connection.commit()
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def assign_teachers(self, subject_id):
        """فتح نافذة إسناد المعلمين للمادة"""
        from ui.teacher_management import SubjectAssignDialog
        # يمكن إنشاء نافذة مخصصة لإسناد المعلمين للمادة
        pass
    
    def search_subjects(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def refresh_table(self):
        self.load_subjects()
        self.search_input.clear()
    
    def update_info_label(self):
        total = self.table.rowCount()
        visible = sum(1 for row in range(total) if not self.table.isRowHidden(row))
        self.info_label.setText(
            tr('showing_subjects', self.language).format(visible=visible, total=total)
        )


class SubjectDialog(QDialog):
    def __init__(self, language, subject_data=None, parent=None):
        super().__init__(parent)
        self.language = language
        self.subject_data = subject_data
        self.setup_ui()
        
        if subject_data:
            self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle(
            tr('edit_subject', self.language) if self.subject_data 
            else tr('add_subject', self.language)
        )
        self.setFixedWidth(450)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # رمز المادة
        self.subject_code = QLineEdit()
        form.addRow(tr('subject_code', self.language), self.subject_code)
        
        # اسم المادة
        self.subject_name = QLineEdit()
        form.addRow(tr('subject_name', self.language), self.subject_name)
        
        # الوصف
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        form.addRow(tr('description', self.language), self.description)
        
        layout.addLayout(form)
        
        # الأزرار
        buttons = QHBoxLayout()
        save_btn = QPushButton(tr('save', self.language))
        save_btn.setObjectName("successButton")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(tr('cancel', self.language))
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def load_data(self):
        self.subject_code.setText(self.subject_data['subject_code'])
        self.subject_name.setText(self.subject_data['subject_name'])
        self.description.setPlainText(self.subject_data.get('description', ''))
    
    def get_data(self):
        return {
            'subject_code': self.subject_code.text().strip(),
            'subject_name': self.subject_name.text().strip(),
            'description': self.description.toPlainText().strip()
        }
    
    def accept(self):
        if not self.subject_code.text().strip() or not self.subject_name.text().strip():
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('required_fields', self.language)
            )
            return
        super().accept()
