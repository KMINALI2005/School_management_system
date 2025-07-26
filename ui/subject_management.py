from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                           QLineEdit, QComboBox, QSpinBox, QMessageBox, QLabel,
                           QHeaderView, QAbstractItemView, QTextEdit, QGroupBox,
                           QCheckBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database.db_manager import DatabaseManager
from utils.translations import tr

class SubjectManagement(QWidget):
    """إدارة المواد الدراسية"""
    
    def __init__(self, language='ar', user_data=None):
        super().__init__()
        self.language = language
        self.user_data = user_data
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_subjects()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # شريط الأدوات العلوي
        toolbar_layout = QHBoxLayout()
        
        # زر إضافة مادة جديدة
        self.add_btn = QPushButton(f"➕ {tr('add_subject', self.language)}")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.add_subject)
        toolbar_layout.addWidget(self.add_btn)
        
        # زر تعديل المادة
        self.edit_btn = QPushButton(f"✏️ {tr('edit_subject', self.language)}")
        self.edit_btn.setObjectName("secondaryButton")
        self.edit_btn.clicked.connect(self.edit_subject)
        self.edit_btn.setEnabled(False)
        toolbar_layout.addWidget(self.edit_btn)
        
        # زر حذف المادة
        self.delete_btn = QPushButton(f"🗑️ {tr('delete_subject', self.language)}")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.clicked.connect(self.delete_subject)
        self.delete_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_btn)
        
        # زر تعيين المعلمين
        self.assign_teachers_btn = QPushButton(f"👨‍🏫 {tr('assign_teachers', self.language)}")
        self.assign_teachers_btn.setObjectName("infoButton")
        self.assign_teachers_btn.clicked.connect(self.assign_teachers)
        self.assign_teachers_btn.setEnabled(False)
        toolbar_layout.addWidget(self.assign_teachers_btn)
        
        toolbar_layout.addStretch()
        
        # زر التحديث
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.clicked.connect(self.load_subjects)
        toolbar_layout.addWidget(refresh_btn)
        
        layout.addLayout(toolbar_layout)
        
        # جدول المواد
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        # معلومات إضافية
        info_layout = QHBoxLayout()
        
        # عدد المواد
        self.subjects_count_label = QLabel()
        self.subjects_count_label.setStyleSheet("""
            padding: 10px;
            background-color: #E3F2FD;
            border-radius: 5px;
            font-weight: bold;
            color: #1976D2;
        """)
        info_layout.addWidget(self.subjects_count_label)
        
        # إجمالي الساعات
        self.total_hours_label = QLabel()
        self.total_hours_label.setStyleSheet("""
            padding: 10px;
            background-color: #FFF3E0;
            border-radius: 5px;
            font-weight: bold;
            color: #F57C00;
        """)
        info_layout.addWidget(self.total_hours_label)
        
        layout.addLayout(info_layout)
        
        # تطبيق اتجاه النص حسب اللغة
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def setup_table(self):
        """إعداد جدول المواد"""
        headers = [
            tr('subject_name', self.language),
            tr('subject_code', self.language),
            tr('credit_hours', self.language),
            tr('subject_type', self.language),
            tr('assigned_teachers', self.language),
            tr('classes_count', self.language),
            tr('status', self.language)
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # تحديد عرض الأعمدة
        self.table.setColumnWidth(0, 200)  # اسم المادة
        self.table.setColumnWidth(1, 120)  # رمز المادة
        self.table.setColumnWidth(2, 100)  # عدد الساعات
        self.table.setColumnWidth(3, 120)  # نوع المادة
        self.table.setColumnWidth(4, 200)  # المعلمون المعينون
        self.table.setColumnWidth(5, 100)  # عدد الصفوف
        
        # ربط إشارة تحديد المادة
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # إعداد النقر المزدوج للتعديل
        self.table.doubleClicked.connect(self.edit_subject)
    
    def load_subjects(self):
        """تحميل بيانات المواد"""
        try:
            # جلب بيانات المواد مع معلومات إضافية
            subjects_data = self.db.cursor.execute("""
                SELECT 
                    s.id,
                    s.subject_name,
                    s.subject_code,
                    s.credit_hours,
                    s.subject_type,
                    GROUP_CONCAT(t.full_name, ', ') as teachers,
                    COUNT(DISTINCT tt.class_id) as classes_count,
                    s.status
                FROM subjects s
                LEFT JOIN teacher_subjects ts ON s.id = ts.subject_id
                LEFT JOIN teachers t ON ts.teacher_id = t.id
                LEFT JOIN timetable tt ON s.id = tt.subject_id
                GROUP BY s.id, s.subject_name, s.subject_code, s.credit_hours, s.subject_type, s.status
                ORDER BY s.subject_name
            """).fetchall()
            
            # تحديث الجدول
            self.table.setRowCount(len(subjects_data))
            
            for row, subject_data in enumerate(subjects_data):
                # حفظ ID المادة في العمود الأول
                item = QTableWidgetItem(subject_data[1])  # اسم المادة
                item.setData(Qt.ItemDataRole.UserRole, subject_data[0])  # ID
                self.table.setItem(row, 0, item)
                
                # رمز المادة
                self.table.setItem(row, 1, QTableWidgetItem(subject_data[2] or ''))
                
                # عدد الساعات
                self.table.setItem(row, 2, QTableWidgetItem(str(subject_data[3])))
                
                # نوع المادة
                subject_type = subject_data[4] or 'core'
                type_text = tr(subject_type, self.language)
                self.table.setItem(row, 3, QTableWidgetItem(type_text))
                
                # المعلمون المعينون
                teachers = subject_data[5] or tr('no_teachers_assigned', self.language)
                self.table.setItem(row, 4, QTableWidgetItem(teachers))
                
                # عدد الصفوف
                classes_count = subject_data[6] or 0
                self.table.setItem(row, 5, QTableWidgetItem(str(classes_count)))
                
                # الحالة
                status_text = tr('active', self.language) if subject_data[7] == 'active' else tr('inactive', self.language)
                status_item = QTableWidgetItem(status_text)
                if subject_data[7] == 'active':
                    status_item.setBackground(Qt.GlobalColor.lightGreen)
                else:
                    status_item.setBackground(Qt.GlobalColor.lightGray)
                
                self.table.setItem(row, 6, status_item)
            
            # تحديث معلومات الإحصائيات
            self.update_statistics()
            
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        try:
            # عدد المواد
            subjects_count = self.db.cursor.execute(
                "SELECT COUNT(*) FROM subjects WHERE status = 'active'"
            ).fetchone()[0]
            
            # إجمالي الساعات
            total_hours = self.db.cursor.execute(
                "SELECT SUM(credit_hours) FROM subjects WHERE status = 'active'"
            ).fetchone()[0] or 0
            
            # تحديث التسميات
            self.subjects_count_label.setText(
                f"{tr('total_subjects', self.language)}: {subjects_count}"
            )
            
            self.total_hours_label.setText(
                f"{tr('total_credit_hours', self.language)}: {total_hours}"
            )
            
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")
    
    def on_selection_changed(self):
        """تفعيل/إلغاء تفعيل الأزرار حسب التحديد"""
        has_selection = len(self.table.selectionModel().selectedRows()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.assign_teachers_btn.setEnabled(has_selection)
    
    def add_subject(self):
        """إضافة مادة جديدة"""
        dialog = SubjectDialog(self.language, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_subjects()
    
    def edit_subject(self):
        """تعديل المادة المحددة"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        subject_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = SubjectDialog(self.language, subject_id=subject_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_subjects()
    
    def delete_subject(self):
        """حذف المادة المحددة"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        subject_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        subject_name = self.table.item(row, 0).text()
        
        # التحقق من وجود درجات أو جدول زمني للمادة
        grades_count = self.db.cursor.execute(
            "SELECT COUNT(*) FROM grades WHERE subject_id = ?",
            (subject_id,)
        ).fetchone()[0]
        
        timetable_count = self.db.cursor.execute(
            "SELECT COUNT(*) FROM timetable WHERE subject_id = ?",
            (subject_id,)
        ).fetchone()[0]
        
        if grades_count > 0 or timetable_count > 0:
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('cannot_delete_subject_has_data', self.language)
            )
            return
        
        # تأكيد الحذف
        reply = QMessageBox.question(
            self,
            tr('confirm_delete_subject', self.language),
            tr('confirm_delete_subject_message', self.language).format(
                name=subject_name
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # حذف تعيينات المعلمين أولا
                self.db.cursor.execute(
                    "DELETE FROM teacher_subjects WHERE subject_id = ?",
                    (subject_id,)
                )
                
                # حذف المادة
                self.db.cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
                self.db.connection.commit()
                
                QMessageBox.information(
                    self,
                    tr('success', self.language),
                    tr('subject_deleted', self.language)
                )
                
                self.load_subjects()
                
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def assign_teachers(self):
        """تعيين المعلمين للمادة"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        subject_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        subject_name = self.table.item(row, 0).text()
        
        dialog = TeacherAssignmentDialog(
            self.language, subject_id, subject_name, parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_subjects()


class SubjectDialog(QDialog):
    """نافذة إضافة/تعديل المادة"""
    
    def __init__(self, language='ar', subject_id=None, parent=None):
        super().__init__(parent)
        self.language = language
        self.subject_id = subject_id
        self.db = DatabaseManager()
        self.setup_ui()
        
        if subject_id:
            self.load_subject_data()
    
    def setup_ui(self):
        self.setWindowTitle(
            tr('edit_subject', self.language) if self.subject_id 
            else tr('add_subject', self.language)
        )
        self.setFixedSize(500, 500)
        
        layout = QVBoxLayout(self)
        
        # معلومات أساسية
        basic_group = QGroupBox(tr('basic_information', self.language))
        basic_layout = QFormLayout(basic_group)
        
        # اسم المادة
        self.subject_name_edit = QLineEdit()
        self.subject_name_edit.setPlaceholderText(tr('enter_subject_name', self.language))
        basic_layout.addRow(tr('subject_name', self.language), self.subject_name_edit)
        
        # رمز المادة
        self.subject_code_edit = QLineEdit()
        self.subject_code_edit.setPlaceholderText(tr('enter_subject_code', self.language))
        basic_layout.addRow(tr('subject_code', self.language), self.subject_code_edit)
        
        # عدد الساعات الائتمانية
        self.credit_hours_spin = QSpinBox()
        self.credit_hours_spin.setRange(1, 10)
        self.credit_hours_spin.setValue(3)
        basic_layout.addRow(tr('credit_hours', self.language), self.credit_hours_spin)
        
        # نوع المادة
        self.subject_type_combo = QComboBox()
        self.subject_type_combo.addItem(tr('core_subject', self.language), 'core')
        self.subject_type_combo.addItem(tr('elective_subject', self.language), 'elective')
        self.subject_type_combo.addItem(tr('practical_subject', self.language), 'practical')
        self.subject_type_combo.addItem(tr('theoretical_subject', self.language), 'theoretical')
        basic_layout.addRow(tr('subject_type', self.language), self.subject_type_combo)
        
        # الحالة
        self.status_combo = QComboBox()
        self.status_combo.addItem(tr('active', self.language), 'active')
        self.status_combo.addItem(tr('inactive', self.language), 'inactive')
        basic_layout.addRow(tr('status', self.language), self.status_combo)
        
        layout.addWidget(basic_group)
        
        # معلومات إضافية
        additional_group = QGroupBox(tr('additional_information', self.language))
        additional_layout = QFormLayout(additional_group)
        
        # الوصف
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText(tr('enter_subject_description', self.language))
        additional_layout.addRow(tr('description', self.language), self.description_edit)
        
        # متطلبات سابقة
        self.prerequisites_edit = QLineEdit()
        self.prerequisites_edit.setPlaceholderText(tr('enter_prerequisites', self.language))
        additional_layout.addRow(tr('prerequisites', self.language), self.prerequisites_edit)
        
        # الكتاب المقرر
        self.textbook_edit = QLineEdit()
        self.textbook_edit.setPlaceholderText(tr('enter_textbook', self.language))
        additional_layout.addRow(tr('textbook', self.language), self.textbook_edit)
        
        layout.addWidget(additional_group)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        # زر الحفظ
        save_btn = QPushButton(tr('save', self.language))
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_subject)
        buttons_layout.addWidget(save_btn)
        
        # زر الإلغاء
        cancel_btn = QPushButton(tr('cancel', self.language))
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # تطبيق اتجاه النص
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def load_subject_data(self):
        """تحميل بيانات المادة للتعديل"""
        try:
            subject_data = self.db.cursor.execute("""
                SELECT subject_name, subject_code, credit_hours, subject_type,
                       status, description, prerequisites, textbook
                FROM subjects WHERE id = ?
            """, (self.subject_id,)).fetchone()
            
            if subject_data:
                self.subject_name_edit.setText(subject_data[0])
                self.subject_code_edit.setText(subject_data[1] or '')
                self.credit_hours_spin.setValue(subject_data[2])
                
                # تحديد نوع المادة
                type_index = self.subject_type_combo.findData(subject_data[3])
                if type_index >= 0:
                    self.subject_type_combo.setCurrentIndex(type_index)
                
                # تحديد الحالة
                status_index = self.status_combo.findData(subject_data[4])
                if status_index >= 0:
                    self.status_combo.setCurrentIndex(status_index)
                
                # معلومات إضافية
                if subject_data[5]:
                    self.description_edit.setPlainText(subject_data[5])
                if subject_data[6]:
                    self.prerequisites_edit.setText(subject_data[6])
                if subject_data[7]:
                    self.textbook_edit.setText(subject_data[7])
                    
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def save_subject(self):
        """حفظ بيانات المادة"""
        # التحقق من صحة البيانات
        if not self.subject_name_edit.text().strip():
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('subject_name_required', self.language)
            )
            self.subject_name_edit.setFocus()
            return
        
        # التحقق من عدم تكرار اسم المادة
        subject_name = self.subject_name_edit.text().strip()
        
        existing_subject = self.db.cursor.execute("""
            SELECT id FROM subjects 
            WHERE subject_name = ? AND id != ?
        """, (subject_name, self.subject_id or 0)).fetchone()
        
        if existing_subject:
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('subject_name_exists', self.language)
            )
            return
        
        # التحقق من رمز المادة إذا كان موجوداً
        subject_code = self.subject_code_edit.text().strip()
        if subject_code:
            existing_code = self.db.cursor.execute("""
                SELECT id FROM subjects 
                WHERE subject_code = ? AND id != ?
            """, (subject_code, self.subject_id or 0)).fetchone()
            
            if existing_code:
                QMessageBox.warning(
                    self,
                    tr('warning', self.language),
                    tr('subject_code_exists', self.language)
                )
                return
        
        try:
            # جمع البيانات
            credit_hours = self.credit_hours_spin.value()
            subject_type = self.subject_type_combo.currentData()
            status = self.status_combo.currentData()
            description = self.description_edit.toPlainText().strip() or None
            prerequisites = self.prerequisites_edit.text().strip() or None
            textbook = self.textbook_edit.text().strip() or None
            
            if self.subject_id:
                # تحديث المادة الموجودة
                self.db.cursor.execute("""
                    UPDATE subjects SET
                        subject_name = ?, subject_code = ?, credit_hours = ?,
                        subject_type = ?, status = ?, description = ?,
                        prerequisites = ?, textbook = ?
                    WHERE id = ?
                """, (subject_name, subject_code or None, credit_hours, subject_type,
                      status, description, prerequisites, textbook, self.subject_id))
                
                message = tr('subject_updated', self.language)
            else:
                # إضافة مادة جديدة
                self.db.cursor.execute("""
                    INSERT INTO subjects 
                    (subject_name, subject_code, credit_hours, subject_type,
                     status, description, prerequisites, textbook, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (subject_name, subject_code or None, credit_hours, subject_type,
                      status, description, prerequisites, textbook))
                
                message = tr('subject_added', self.language)
            
            self.db.connection.commit()
            
            QMessageBox.information(
                self,
                tr('success', self.language),
                message
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))


class TeacherAssignmentDialog(QDialog):
    """نافذة تعيين المعلمين للمادة"""
    
    def __init__(self, language='ar', subject_id=None, subject_name='', parent=None):
        super().__init__(parent)
        self.language = language
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_teachers()
    
    def setup_ui(self):
        self.setWindowTitle(
            f"{tr('assign_teachers', self.language)} - {self.subject_name}"
        )
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # عنوان
        title_label = QLabel(tr('select_teachers_for_subject', self.language))
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # منطقة التمرير للمعلمين
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.teachers_layout = QVBoxLayout(scroll_widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        # زر تحديد الكل
        select_all_btn = QPushButton(tr('select_all', self.language))
        select_all_btn.clicked.connect(self.select_all_teachers)
        buttons_layout.addWidget(select_all_btn)
        
        # زر إلغاء تحديد الكل
        deselect_all_btn = QPushButton(tr('deselect_all', self.language))
        deselect_all_btn.clicked.connect(self.deselect_all_teachers)
        buttons_layout.addWidget(deselect_all_btn)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # أزرار الحفظ والإلغاء
        action_buttons_layout = QHBoxLayout()
        
        # زر الحفظ
        save_btn = QPushButton(tr('save', self.language))
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_assignments)
        action_buttons_layout.addWidget(save_btn)
        
        # زر الإلغاء
        cancel_btn = QPushButton(tr('cancel', self.language))
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        action_buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(action_buttons_layout)
        
        # تطبيق اتجاه النص
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def load_teachers(self):
        """تحميل قائمة المعلمين"""
        try:
            # جلب جميع المعلمين النشطين
            teachers = self.db.cursor.execute("""
                SELECT id, full_name, specialization FROM teachers 
                WHERE status = 'active'
                ORDER BY full_name
            """).fetchall()
            
            # جلب المعلمين المعينين حالياً للمادة
            assigned_teachers = self.db.cursor.execute("""
                SELECT teacher_id FROM teacher_subjects 
                WHERE subject_id = ?
            """, (self.subject_id,)).fetchall()
            
            assigned_ids = [t[0] for t in assigned_teachers]
            
            # إنشاء checkboxes للمعلمين
            self.teacher_checkboxes = {}
            
            for teacher in teachers:
                teacher_id, name, specialization = teacher
                
                checkbox = QCheckBox(f"{name} - {specialization or ''}")
                checkbox.setChecked(teacher_id in assigned_ids)
                
                # تخزين معرف المعلم
                checkbox.teacher_id = teacher_id
                
                self.teachers_layout.addWidget(checkbox)
                self.teacher_checkboxes[teacher_id] = checkbox
                
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def select_all_teachers(self):
        """تحديد جميع المعلمين"""
        for checkbox in self.teacher_checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all_teachers(self):
        """إلغاء تحديد جميع المعلمين"""
        for checkbox in self.teacher_checkboxes.values():
            checkbox.setChecked(False)
    
    def save_assignments(self):
        """حفظ تعيينات المعلمين"""
        try:
            # حذف التعيينات الحالية
            self.db.cursor.execute(
                "DELETE FROM teacher_subjects WHERE subject_id = ?",
                (self.subject_id,)
            )
            
            # إضافة التعيينات الجديدة
            for teacher_id, checkbox in self.teacher_checkboxes.items():
                if checkbox.isChecked():
                    self.db.cursor.execute("""
                        INSERT INTO teacher_subjects (teacher_id, subject_id, assigned_at)
                        VALUES (?, ?, datetime('now'))
                    """, (teacher_id, self.subject_id))
            
            self.db.connection.commit()
            
            QMessageBox.information(
                self,
                tr('success', self.language),
                tr('teacher_assignments_saved', self.language)
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
