from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
                           QFormLayout, QMessageBox, QComboBox, QSpinBox,
                           QLabel, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from utils.translations import tr

class ClassManagement(QWidget):
    def __init__(self, language='ar'):
        super().__init__()
        self.language = language
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_classes()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # شريط الأدوات
        toolbar = QHBoxLayout()
        
        # زر إضافة صف
        self.add_button = QPushButton(f"➕ {tr('add_class', self.language)}")
        self.add_button.setObjectName("successButton")
        self.add_button.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(self.add_button)
        
        # البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('search_classes', self.language))
        self.search_input.textChanged.connect(self.search_classes)
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
            border-radius: 5px;
            color: #7F8C8D;
        """)
        layout.addWidget(self.info_label)
    
    def setup_table(self):
        headers = [
            tr('class_name', self.language),
            tr('section', self.language),
            tr('capacity', self.language),
            tr('current_students', self.language),
            tr('supervisor', self.language),
            tr('actions', self.language)
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        
    def load_classes(self):
        self.table.setRowCount(0)
        classes = self.db.get_all_classes()
        
        for class_data in classes:
            self.add_class_to_table(class_data)
        
        self.update_info_label()
    
    def add_class_to_table(self, class_data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # عدد الطلاب الحالي
        student_count = self.db.cursor.execute(
            "SELECT COUNT(*) FROM students WHERE class_id = ?",
            (class_data['id'],)
        ).fetchone()[0]
        
        # اسم المشرف
        supervisor_name = ""
        if class_data['supervisor_id']:
            supervisor = self.db.cursor.execute(
                "SELECT full_name FROM teachers WHERE id = ?",
                (class_data['supervisor_id'],)
            ).fetchone()
            if supervisor:
                supervisor_name = supervisor[0]
        
        # البيانات
        self.table.setItem(row, 0, QTableWidgetItem(class_data['class_name']))
        self.table.setItem(row, 1, QTableWidgetItem(class_data['section']))
        self.table.setItem(row, 2, QTableWidgetItem(str(class_data['capacity'])))
        self.table.setItem(row, 3, QTableWidgetItem(str(student_count)))
        self.table.setItem(row, 4, QTableWidgetItem(supervisor_name))
        
        # الإجراءات
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip(tr('edit', self.language))
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(lambda: self.edit_class(class_data['id']))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip(tr('delete', self.language))
        delete_btn.setFixedSize(30, 30)
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_class(class_data['id']))
        actions_layout.addWidget(delete_btn)
        
        view_btn = QPushButton("👁️")
        view_btn.setToolTip(tr('view_students', self.language))
        view_btn.setFixedSize(30, 30)
        view_btn.clicked.connect(lambda: self.view_students(class_data['id']))
        actions_layout.addWidget(view_btn)
        
        self.table.setCellWidget(row, 5, actions_widget)
    
    def show_add_dialog(self):
        dialog = ClassDialog(self.language, parent=self)
        if dialog.exec():
            try:
                self.db.add_class(dialog.get_data())
                self.refresh_table()
                QMessageBox.information(
                    self, tr('success', self.language),
                    tr('class_added_success', self.language)
                )
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def edit_class(self, class_id):
        class_data = self.db.cursor.execute(
            "SELECT * FROM classes WHERE id = ?", (class_id,)
        ).fetchone()
        
        if class_data:
            # تحويل البيانات إلى dictionary
            columns = [description[0] for description in self.db.cursor.description]
            class_dict = dict(zip(columns, class_data))
            
            dialog = ClassDialog(self.language, class_dict, self)
            if dialog.exec():
                try:
                    data = dialog.get_data()
                    self.db.cursor.execute(
                        """UPDATE classes SET class_name = ?, section = ?, 
                           capacity = ?, supervisor_id = ? WHERE id = ?""",
                        (data['class_name'], data['section'], data['capacity'],
                         data['supervisor_id'], class_id)
                    )
                    self.db.connection.commit()
                    self.refresh_table()
                except Exception as e:
                    QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def delete_class(self, class_id):
        # التحقق من وجود طلاب
        student_count = self.db.cursor.execute(
            "SELECT COUNT(*) FROM students WHERE class_id = ?", (class_id,)
        ).fetchone()[0]
        
        if student_count > 0:
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('class_has_students', self.language)
            )
            return
        
        msg = QMessageBox.question(
            self, tr('confirm_delete', self.language),
            tr('delete_class_confirm', self.language),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
                self.db.connection.commit()
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def view_students(self, class_id):
        # يمكن إضافة نافذة لعرض طلاب الصف
        pass
    
    def search_classes(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def refresh_table(self):
        self.load_classes()
        self.search_input.clear()
    
    def update_info_label(self):
        total = self.table.rowCount()
        visible = sum(1 for row in range(total) if not self.table.isRowHidden(row))
        self.info_label.setText(
            tr('showing_classes', self.language).format(visible=visible, total=total)
        )


class ClassDialog(QDialog):
    def __init__(self, language, class_data=None, parent=None):
        super().__init__(parent)
        self.language = language
        self.class_data = class_data
        self.db = DatabaseManager()
        self.setup_ui()
        
        if class_data:
            self.load_data()
    
    def setup_ui(self):
        self.setWindowTitle(
            tr('edit_class', self.language) if self.class_data 
            else tr('add_class', self.language)
        )
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # اسم الصف
        self.class_name = QLineEdit()
        form.addRow(tr('class_name', self.language), self.class_name)
        
        # الشعبة
        self.section = QLineEdit()
        form.addRow(tr('section', self.language), self.section)
        
        # السعة
        self.capacity = QSpinBox()
        self.capacity.setMinimum(1)
        self.capacity.setMaximum(100)
        self.capacity.setValue(30)
        form.addRow(tr('capacity', self.language), self.capacity)
        
        # المشرف
        self.supervisor = QComboBox()
        self.supervisor.addItem(tr('no_supervisor', self.language), None)
        teachers = self.db.get_all_teachers()
        for teacher in teachers:
            self.supervisor.addItem(teacher['full_name'], teacher['id'])
        form.addRow(tr('supervisor', self.language), self.supervisor)
        
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
    
    def load_data(self):
        self.class_name.setText(self.class_data['class_name'])
        self.section.setText(self.class_data['section'])
        self.capacity.setValue(self.class_data['capacity'])
        
        # تحديد المشرف
        if self.class_data['supervisor_id']:
            index = self.supervisor.findData(self.class_data['supervisor_id'])
            if index >= 0:
                self.supervisor.setCurrentIndex(index)
    
    def get_data(self):
        return {
            'class_name': self.class_name.text().strip(),
            'section': self.section.text().strip(),
            'capacity': self.capacity.value(),
            'supervisor_id': self.supervisor.currentData()
        }
    
    def accept(self):
        if not self.class_name.text().strip() or not self.section.text().strip():
            QMessageBox.warning(
                self, tr('warning', self.language),
                tr('required_fields', self.language)
            )
            return
        super().accept()
