from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
                           QDialog, QFormLayout, QDateEdit, QMessageBox,
                           QHeaderView, QAbstractItemView, QLabel, QSpinBox)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QIcon
from database.db_manager import DatabaseManager
from utils.translations import tr
from ui.styles import STYLESHEET
import datetime

class StudentManagement(QWidget):
    def __init__(self, language='ar'):
        super().__init__()
        self.language = language
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_students()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # شريط الأدوات
        toolbar_layout = QHBoxLayout()
        
        # زر إضافة طالب
        self.add_button = QPushButton(f"➕ {tr('add_student', self.language)}")
        self.add_button.setObjectName("successButton")
        self.add_button.clicked.connect(self.show_add_dialog)
        toolbar_layout.addWidget(self.add_button)
        
        # مربع البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr('search_students', self.language))
        self.search_input.textChanged.connect(self.search_students)
        self.search_input.setMaximumWidth(300)
        toolbar_layout.addWidget(self.search_input)
        
        # فلتر الصف
        self.class_filter = QComboBox()
        self.class_filter.addItem(tr('all_classes', self.language), None)
        self.load_classes_filter()
        self.class_filter.currentIndexChanged.connect(self.filter_by_class)
        toolbar_layout.addWidget(self.class_filter)
        
        toolbar_layout.addStretch()
        
        # زر التحديث
        refresh_button = QPushButton("🔄")
        refresh_button.setFixedSize(40, 40)
        refresh_button.clicked.connect(self.refresh_table)
        toolbar_layout.addWidget(refresh_button)
        
        # زر التصدير
        export_button = QPushButton(f"📥 {tr('export', self.language)}")
        export_button.clicked.connect(self.export_students)
        toolbar_layout.addWidget(export_button)
        
        layout.addLayout(toolbar_layout)
        
        # جدول الطلاب
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
        self.update_info_label()
    
    def setup_table(self):
        """إعداد جدول الطلاب"""
        headers = [
            tr('student_id', self.language),
            tr('full_name', self.language),
            tr('date_of_birth', self.language),
            tr('gender', self.language),
            tr('class', self.language),
            tr('phone', self.language),
            tr('parent_phone', self.language),
            tr('address', self.language),
            tr('enrollment_date', self.language),
            tr('actions', self.language)
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # تخصيص الجدول
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        
        # تحديد عرض الأعمدة
        self.table.setColumnWidth(0, 100)  # رقم الطالب
        self.table.setColumnWidth(1, 200)  # الاسم
        self.table.setColumnWidth(2, 120)  # تاريخ الميلاد
        self.table.setColumnWidth(3, 80)   # الجنس
        self.table.setColumnWidth(4, 100)  # الصف
        self.table.setColumnWidth(5, 120)  # الهاتف
        self.table.setColumnWidth(6, 120)  # هاتف ولي الأمر
        self.table.setColumnWidth(7, 200)  # العنوان
        self.table.setColumnWidth(8, 120)  # تاريخ التسجيل
        self.table.setColumnWidth(9, 150)  # الإجراءات
    
    def load_students(self):
        """تحميل بيانات الطلاب"""
        self.table.setRowCount(0)
        students = self.db.get_all_students()
        
        for student in students:
            self.add_student_to_table(student)
        
        self.update_info_label()
    
    def add_student_to_table(self, student):
        """إضافة طالب إلى الجدول"""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # إضافة البيانات
        self.table.setItem(row_position, 0, QTableWidgetItem(str(student['student_id'])))
        self.table.setItem(row_position, 1, QTableWidgetItem(student['full_name']))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(student['date_of_birth'] or '')))
        
        # ترجمة الجنس
        gender_text = tr(f"gender_{student['gender']}", self.language) if student['gender'] else ''
        self.table.setItem(row_position, 3, QTableWidgetItem(gender_text))
        
        self.table.setItem(row_position, 4, QTableWidgetItem(student['class_name'] or ''))
        self.table.setItem(row_position, 5, QTableWidgetItem(student['phone'] or ''))
        self.table.setItem(row_position, 6, QTableWidgetItem(student['parent_phone'] or ''))
        self.table.setItem(row_position, 7, QTableWidgetItem(student['address'] or ''))
        self.table.setItem(row_position, 8, QTableWidgetItem(str(student['enrollment_date'] or '')))
        
        # أزرار الإجراءات
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        
        # زر التعديل
        edit_button = QPushButton("✏️")
        edit_button.setToolTip(tr('edit', self.language))
        edit_button.setFixedSize(30, 30)
        edit_button.clicked.connect(lambda: self.edit_student(student['id']))
        actions_layout.addWidget(edit_button)
        
        # زر الحذف
        delete_button = QPushButton("🗑️")
        delete_button.setToolTip(tr('delete', self.language))
        delete_button.setFixedSize(30, 30)
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(lambda: self.delete_student(student['id']))
        actions_layout.addWidget(delete_button)
        
        # زر عرض التفاصيل
        view_button = QPushButton("👁️")
        view_button.setToolTip(tr('view_details', self.language))
        view_button.setFixedSize(30, 30)
        view_button.clicked.connect(lambda: self.view_student_details(student['id']))
        actions_layout.addWidget(view_button)
        
        self.table.setCellWidget(row_position, 9, actions_widget)
    
    def show_add_dialog(self):
        """عرض نافذة إضافة طالب جديد"""
        dialog = StudentDialog(self.language, parent=self)
        if dialog.exec():
            student_data = dialog.get_data()
            try:
                self.db.add_student(student_data)
                self.refresh_table()
                QMessageBox.information(
                    self, 
                    tr('success', self.language),
                    tr('student_added_success', self.language)
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr('error', self.language),
                    str(e)
                )
    
    def edit_student(self, student_id):
        """تعديل بيانات طالب"""
        # الحصول على بيانات الطالب
        students = self.db.get_all_students()
        student = next((s for s in students if s['id'] == student_id), None)
        
        if student:
            dialog = StudentDialog(self.language, student, self)
            if dialog.exec():
                student_data = dialog.get_data()
                try:
                    self.db.update_student(student_id, student_data)
                    self.refresh_table()
                    QMessageBox.information(
                        self,
                        tr('success', self.language),
                        tr('student_updated_success', self.language)
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        tr('error', self.language),
                        str(e)
                    )
    
    def delete_student(self, student_id):
        """حذف طالب"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(tr('confirm_delete', self.language))
        msg.setText(tr('delete_student_confirm', self.language))
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | 
            QMessageBox.StandardButton.No
        )
        
        if self.language == 'ar':
            msg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_student(student_id)
                self.refresh_table()
                QMessageBox.information(
                    self,
                    tr('success', self.language),
                    tr('student_deleted_success', self.language)
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr('error', self.language),
                    str(e)
                )
    
    def view_student_details(self, student_id):
        """عرض تفاصيل الطالب"""
        # يمكن إضافة نافذة لعرض تفاصيل إضافية
        pass
    
    def search_students(self, text):
        """البحث عن الطلاب"""
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount() - 1):  # استثناء عمود الإجراءات
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def filter_by_class(self):
        """تصفية الطلاب حسب الصف"""
        class_id = self.class_filter.currentData()
        
        for row in range(self.table.rowCount()):
            if class_id is None:
                self.table.setRowHidden(row, False)
            else:
                class_item = self.table.item(row, 4)
                if class_item:
                  # ... تكملة من الكود السابق
                    # هنا يمكن تحسين المنطق للمقارنة بناءً على معرف الصف
                    self.table.setRowHidden(row, False)
                else:
                    self.table.setRowHidden(row, True)
    
    def load_classes_filter(self):
        """تحميل الصفوف في قائمة التصفية"""
        classes = self.db.get_all_classes()
        for class_data in classes:
            self.class_filter.addItem(
                f"{class_data['class_name']} - {class_data['section']}",
                class_data['id']
            )
    
    def refresh_table(self):
        """تحديث الجدول"""
        self.load_students()
        self.search_input.clear()
        self.class_filter.setCurrentIndex(0)
    
    def update_info_label(self):
        """تحديث شريط المعلومات"""
        total = self.table.rowCount()
        visible = sum(1 for row in range(total) if not self.table.isRowHidden(row))
        
        info_text = tr('showing_students', self.language).format(
            visible=visible, total=total
        )
        self.info_label.setText(info_text)
    
    def export_students(self):
        """تصدير بيانات الطلاب"""
        from PyQt6.QtWidgets import QFileDialog
        import pandas as pd
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr('save_file', self.language),
            f"students_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # جمع البيانات من الجدول
                data = []
                headers = []
                
                # الحصول على رؤوس الأعمدة
                for col in range(self.table.columnCount() - 1):  # استثناء عمود الإجراءات
                    headers.append(self.table.horizontalHeaderItem(col).text())
                
                # الحصول على البيانات
                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        row_data = []
                        for col in range(self.table.columnCount() - 1):
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else '')
                        data.append(row_data)
                
                # إنشاء DataFrame وحفظه
                df = pd.DataFrame(data, columns=headers)
                
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                QMessageBox.information(
                    self,
                    tr('success', self.language),
                    tr('export_success', self.language)
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr('error', self.language),
                    str(e)
                )


class StudentDialog(QDialog):
    """نافذة إضافة/تعديل طالب"""
    
    def __init__(self, language='ar', student_data=None, parent=None):
        super().__init__(parent)
        self.language = language
        self.student_data = student_data
        self.db = DatabaseManager()
        self.setup_ui()
        
        if student_data:
            self.load_student_data()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        self.setWindowTitle(
            tr('edit_student', self.language) if self.student_data 
            else tr('add_student', self.language)
        )
        self.setFixedWidth(500)
        
        layout = QVBoxLayout(self)
        
        # النموذج
        form_layout = QFormLayout()
        
        # رقم الطالب
        self.student_id_input = QLineEdit()
        form_layout.addRow(tr('student_id', self.language), self.student_id_input)
        
        # الاسم الكامل
        self.full_name_input = QLineEdit()
        form_layout.addRow(tr('full_name', self.language), self.full_name_input)
        
        # تاريخ الميلاد
        self.date_of_birth_input = QDateEdit()
        self.date_of_birth_input.setCalendarPopup(True)
        self.date_of_birth_input.setDate(QDate.currentDate().addYears(-10))
        form_layout.addRow(tr('date_of_birth', self.language), self.date_of_birth_input)
        
        # الجنس
        self.gender_combo = QComboBox()
        self.gender_combo.addItem(tr('gender_male', self.language), 'male')
        self.gender_combo.addItem(tr('gender_female', self.language), 'female')
        form_layout.addRow(tr('gender', self.language), self.gender_combo)
        
        # الصف
        self.class_combo = QComboBox()
        self.load_classes()
        form_layout.addRow(tr('class', self.language), self.class_combo)
        
        # الهاتف
        self.phone_input = QLineEdit()
        form_layout.addRow(tr('phone', self.language), self.phone_input)
        
        # هاتف ولي الأمر
        self.parent_phone_input = QLineEdit()
        form_layout.addRow(tr('parent_phone', self.language), self.parent_phone_input)
        
        # العنوان
        self.address_input = QLineEdit()
        form_layout.addRow(tr('address', self.language), self.address_input)
        
        layout.addLayout(form_layout)
        
        # الأزرار
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton(tr('save', self.language))
        save_button.setObjectName("successButton")
        save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton(tr('cancel', self.language))
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # تحديد اتجاه النص
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def load_classes(self):
        """تحميل الصفوف"""
        self.class_combo.addItem(tr('select_class', self.language), None)
        classes = self.db.get_all_classes()
        for class_data in classes:
            self.class_combo.addItem(
                f"{class_data['class_name']} - {class_data['section']}",
                class_data['id']
            )
    
    def load_student_data(self):
        """تحميل بيانات الطالب للتعديل"""
        self.student_id_input.setText(self.student_data['student_id'])
        self.full_name_input.setText(self.student_data['full_name'])
        
        if self.student_data['date_of_birth']:
            date = QDate.fromString(self.student_data['date_of_birth'], 'yyyy-MM-dd')
            self.date_of_birth_input.setDate(date)
        
        # تحديد الجنس
        index = self.gender_combo.findData(self.student_data['gender'])
        if index >= 0:
            self.gender_combo.setCurrentIndex(index)
        
        # تحديد الصف
        index = self.class_combo.findData(self.student_data['class_id'])
        if index >= 0:
            self.class_combo.setCurrentIndex(index)
        
        self.phone_input.setText(self.student_data.get('phone', ''))
        self.parent_phone_input.setText(self.student_data.get('parent_phone', ''))
        self.address_input.setText(self.student_data.get('address', ''))
    
    def get_data(self):
        """الحصول على البيانات المدخلة"""
        return {
            'student_id': self.student_id_input.text().strip(),
            'full_name': self.full_name_input.text().strip(),
            'date_of_birth': self.date_of_birth_input.date().toString('yyyy-MM-dd'),
            'gender': self.gender_combo.currentData(),
            'class_id': self.class_combo.currentData(),
            'phone': self.phone_input.text().strip(),
            'parent_phone': self.parent_phone_input.text().strip(),
            'address': self.address_input.text().strip()
        }
    
    def accept(self):
        """التحقق من البيانات قبل الحفظ"""
        data = self.get_data()
        
        # التحقق من الحقول المطلوبة
        if not data['student_id'] or not data['full_name']:
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('required_fields', self.language)
            )
            return
        
        # التحقق من تكرار رقم الطالب
        if not self.student_data:  # فقط عند الإضافة
            students = self.db.get_all_students()
            if any(s['student_id'] == data['student_id'] for s in students):
                QMessageBox.warning(
                    self,
                    tr('warning', self.language),
                    tr('student_id_exists', self.language)
                )
                return
        
        super().accept()
                    
