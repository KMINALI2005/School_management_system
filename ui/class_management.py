from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
                           QLineEdit, QComboBox, QSpinBox, QMessageBox, QLabel,
                           QHeaderView, QAbstractItemView, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database.db_manager import DatabaseManager
from utils.translations import tr

class ClassManagement(QWidget):
    """إدارة الصفوف الدراسية"""
    
    def __init__(self, language='ar', user_data=None):
        super().__init__()
        self.language = language
        self.user_data = user_data
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_classes()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # شريط الأدوات العلوي
        toolbar_layout = QHBoxLayout()
        
        # زر إضافة صف جديد
        self.add_btn = QPushButton(f"➕ {tr('add_class', self.language)}")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.add_class)
        toolbar_layout.addWidget(self.add_btn)
        
        # زر تعديل الصف
        self.edit_btn = QPushButton(f"✏️ {tr('edit_class', self.language)}")
        self.edit_btn.setObjectName("secondaryButton")
        self.edit_btn.clicked.connect(self.edit_class)
        self.edit_btn.setEnabled(False)
        toolbar_layout.addWidget(self.edit_btn)
        
        # زر حذف الصف
        self.delete_btn = QPushButton(f"🗑️ {tr('delete_class', self.language)}")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.clicked.connect(self.delete_class)
        self.delete_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_btn)
        
        toolbar_layout.addStretch()
        
        # زر التحديث
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.clicked.connect(self.load_classes)
        toolbar_layout.addWidget(refresh_btn)
        
        layout.addLayout(toolbar_layout)
        
        # جدول الصفوف
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        # معلومات إضافية
        info_layout = QHBoxLayout()
        
        # عدد الصفوف
        self.classes_count_label = QLabel()
        self.classes_count_label.setStyleSheet("""
            padding: 10px;
            background-color: #E3F2FD;
            border-radius: 5px;
            font-weight: bold;
            color: #1976D2;
        """)
        info_layout.addWidget(self.classes_count_label)
        
        # إجمالي الطلاب
        self.total_students_label = QLabel()
        self.total_students_label.setStyleSheet("""
            padding: 10px;
            background-color: #E8F5E9;
            border-radius: 5px;
            font-weight: bold;
            color: #388E3C;
        """)
        info_layout.addWidget(self.total_students_label)
        
        layout.addLayout(info_layout)
        
        # تطبيق اتجاه النص حسب اللغة
        if self.language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def setup_table(self):
        """إعداد جدول الصفوف"""
        headers = [
            tr('class_name', self.language),
            tr('section', self.language),
            tr('class_teacher', self.language),
            tr('capacity', self.language),
            tr('current_students', self.language),
            tr('status', self.language)
        ]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # تحديد عرض الأعمدة
        self.table.setColumnWidth(0, 150)  # اسم الصف
        self.table.setColumnWidth(1, 100)  # الشعبة
        self.table.setColumnWidth(2, 200)  # معلم الصف
        self.table.setColumnWidth(3, 80)   # السعة
        self.table.setColumnWidth(4, 120)  # عدد الطلاب الحالي
        
        # ربط إشارة تحديد الصف
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # إعداد النقر المزدوج للتعديل
        self.table.doubleClicked.connect(self.edit_class)
    
    def load_classes(self):
        """تحميل بيانات الصفوف"""
        try:
            # جلب بيانات الصفوف مع معلومات إضافية
            classes_data = self.db.cursor.execute("""
                SELECT 
                    c.id,
                    c.class_name,
                    c.section,
                    COALESCE(t.full_name, 'غير محدد') as teacher_name,
                    c.capacity,
                    COUNT(s.id) as current_students,
                    c.status
                FROM classes c
                LEFT JOIN teachers t ON c.class_teacher_id = t.id
                LEFT JOIN students s ON c.id = s.class_id
                GROUP BY c.id, c.class_name, c.section, t.full_name, c.capacity, c.status
                ORDER BY c.class_name, c.section
            """).fetchall()
            
            # تحديث الجدول
            self.table.setRowCount(len(classes_data))
            
            for row, class_data in enumerate(classes_data):
                # حفظ ID الصف في العمود الأول
                item = QTableWidgetItem(class_data[1])  # اسم الصف
                item.setData(Qt.ItemDataRole.UserRole, class_data[0])  # ID
                self.table.setItem(row, 0, item)
                
                # الشعبة
                self.table.setItem(row, 1, QTableWidgetItem(class_data[2]))
                
                # معلم الصف
                self.table.setItem(row, 2, QTableWidgetItem(class_data[3]))
                
                # السعة
                self.table.setItem(row, 3, QTableWidgetItem(str(class_data[4])))
                
                # عدد الطلاب الحالي
                current_students = class_data[5]
                capacity = class_data[4]
                students_item = QTableWidgetItem(f"{current_students}/{capacity}")
                
                # تلوين حسب نسبة الامتلاء
                if current_students >= capacity:
                    students_item.setBackground(Qt.GlobalColor.red)
                elif current_students >= capacity * 0.8:
                    students_item.setBackground(Qt.GlobalColor.yellow)
                else:
                    students_item.setBackground(Qt.GlobalColor.lightGreen)
                
                self.table.setItem(row, 4, students_item)
                
                # الحالة
                status_text = tr('active', self.language) if class_data[6] == 'active' else tr('inactive', self.language)
                status_item = QTableWidgetItem(status_text)
                if class_data[6] == 'active':
                    status_item.setBackground(Qt.GlobalColor.lightGreen)
                else:
                    status_item.setBackground(Qt.GlobalColor.lightGray)
                
                self.table.setItem(row, 5, status_item)
            
            # تحديث معلومات الإحصائيات
            self.update_statistics()
            
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        try:
            # عدد الصفوف
            classes_count = self.db.cursor.execute(
                "SELECT COUNT(*) FROM classes WHERE status = 'active'"
            ).fetchone()[0]
            
            # إجمالي الطلاب
            total_students = self.db.cursor.execute(
                "SELECT COUNT(*) FROM students WHERE class_id IS NOT NULL"
            ).fetchone()[0]
            
            # تحديث التسميات
            self.classes_count_label.setText(
                f"{tr('total_classes', self.language)}: {classes_count}"
            )
            
            self.total_students_label.setText(
                f"{tr('total_students', self.language)}: {total_students}"
            )
            
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")
    
    def on_selection_changed(self):
        """تفعيل/إلغاء تفعيل الأزرار حسب التحديد"""
        has_selection = len(self.table.selectionModel().selectedRows()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def add_class(self):
        """إضافة صف جديد"""
        dialog = ClassDialog(self.language, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_classes()
    
    def edit_class(self):
        """تعديل الصف المحدد"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        class_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ClassDialog(self.language, class_id=class_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_classes()
    
    def delete_class(self):
        """حذف الصف المحدد"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        class_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        class_name = self.table.item(row, 0).text()
        section = self.table.item(row, 1).text()
        
        # التحقق من وجود طلاب في الصف
        students_count = self.db.cursor.execute(
            "SELECT COUNT(*) FROM students WHERE class_id = ?",
            (class_id,)
        ).fetchone()[0]
        
        if students_count > 0:
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('cannot_delete_class_has_students', self.language).format(
                    count=students_count
                )
            )
            return
        
        # تأكيد الحذف
        reply = QMessageBox.question(
            self,
            tr('confirm_delete_class', self.language),
            tr('confirm_delete_class_message', self.language).format(
                name=f"{class_name} - {section}"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
                self.db.connection.commit()
                
                QMessageBox.information(
                    self,
                    tr('success', self.language),
                    tr('class_deleted', self.language)
                )
                
                self.load_classes()
                
            except Exception as e:
                QMessageBox.critical(self, tr('error', self.language), str(e))


class ClassDialog(QDialog):
    """نافذة إضافة/تعديل الصف"""
    
    def __init__(self, language='ar', class_id=None, parent=None):
        super().__init__(parent)
        self.language = language
        self.class_id = class_id
        self.db = DatabaseManager()
        self.setup_ui()
        
        if class_id:
            self.load_class_data()
    
    def setup_ui(self):
        self.setWindowTitle(
            tr('edit_class', self.language) if self.class_id 
            else tr('add_class', self.language)
        )
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # معلومات أساسية
        basic_group = QGroupBox(tr('basic_information', self.language))
        basic_layout = QFormLayout(basic_group)
        
        # اسم الصف
        self.class_name_edit = QLineEdit()
        self.class_name_edit.setPlaceholderText(tr('enter_class_name', self.language))
        basic_layout.addRow(tr('class_name', self.language), self.class_name_edit)
        
        # الشعبة
        self.section_edit = QLineEdit()
        self.section_edit.setPlaceholderText(tr('enter_section', self.language))
        basic_layout.addRow(tr('section', self.language), self.section_edit)
        
        # السعة
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 100)
        self.capacity_spin.setValue(30)
        basic_layout.addRow(tr('capacity', self.language), self.capacity_spin)
        
        # معلم الصف
        self.teacher_combo = QComboBox()
        self.load_teachers()
        basic_layout.addRow(tr('class_teacher', self.language), self.teacher_combo)
        
        # الحالة
        self.status_combo = QComboBox()
        self.status_combo.addItem(tr('active', self.language), 'active')
        self.status_combo.addItem(tr('inactive', self.language), 'inactive')
        basic_layout.addRow(tr('status', self.language), self.status_combo)
        
        layout.addWidget(basic_group)
        
        # معلومات إضافية
        additional_group = QGroupBox(tr('additional_information', self.language))
        additional_layout = QFormLayout(additional_group)
        
        # القاعة
        self.room_edit = QLineEdit()
        self.room_edit.setPlaceholderText(tr('enter_room_number', self.language))
        additional_layout.addRow(tr('room', self.language), self.room_edit)
        
        # الطابق
        self.floor_edit = QLineEdit()
        self.floor_edit.setPlaceholderText(tr('enter_floor', self.language))
        additional_layout.addRow(tr('floor', self.language), self.floor_edit)
        
        # الوصف
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText(tr('enter_description', self.language))
        additional_layout.addRow(tr('description', self.language), self.description_edit)
        
        layout.addWidget(additional_group)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        # زر الحفظ
        save_btn = QPushButton(tr('save', self.language))
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_class)
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
    
    def load_teachers(self):
        """تحميل قائمة المعلمين"""
        self.teacher_combo.clear()
        self.teacher_combo.addItem(tr('select_teacher', self.language), None)
        
        try:
            teachers = self.db.cursor.execute("""
                SELECT id, full_name FROM teachers 
                WHERE status = 'active'
                ORDER BY full_name
            """).fetchall()
            
            for teacher in teachers:
                self.teacher_combo.addItem(teacher[1], teacher[0])
                
        except Exception as e:
            print(f"خطأ في تحميل المعلمين: {e}")
    
    def load_class_data(self):
        """تحميل بيانات الصف للتعديل"""
        try:
            class_data = self.db.cursor.execute("""
                SELECT class_name, section, capacity, class_teacher_id, 
                       status, room_number, floor, description
                FROM classes WHERE id = ?
            """, (self.class_id,)).fetchone()
            
            if class_data:
                self.class_name_edit.setText(class_data[0])
                self.section_edit.setText(class_data[1])
                self.capacity_spin.setValue(class_data[2])
                
                # تحديد المعلم
                if class_data[3]:
                    teacher_index = self.teacher_combo.findData(class_data[3])
                    if teacher_index >= 0:
                        self.teacher_combo.setCurrentIndex(teacher_index)
                
                # تحديد الحالة
                status_index = self.status_combo.findData(class_data[4])
                if status_index >= 0:
                    self.status_combo.setCurrentIndex(status_index)
                
                # معلومات إضافية
                if class_data[5]:
                    self.room_edit.setText(class_data[5])
                if class_data[6]:
                    self.floor_edit.setText(class_data[6])
                if class_data[7]:
                    self.description_edit.setPlainText(class_data[7])
                    
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
    
    def save_class(self):
        """حفظ بيانات الصف"""
        # التحقق من صحة البيانات
        if not self.class_name_edit.text().strip():
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('class_name_required', self.language)
            )
            self.class_name_edit.setFocus()
            return
        
        if not self.section_edit.text().strip():
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('section_required', self.language)
            )
            self.section_edit.setFocus()
            return
        
        # التحقق من عدم تكرار الصف والشعبة
        class_name = self.class_name_edit.text().strip()
        section = self.section_edit.text().strip()
        
        existing_class = self.db.cursor.execute("""
            SELECT id FROM classes 
            WHERE class_name = ? AND section = ? AND id != ?
        """, (class_name, section, self.class_id or 0)).fetchone()
        
        if existing_class:
            QMessageBox.warning(
                self,
                tr('warning', self.language),
                tr('class_section_exists', self.language)
            )
            return
        
        try:
            # جمع البيانات
            capacity = self.capacity_spin.value()
            teacher_id = self.teacher_combo.currentData()
            status = self.status_combo.currentData()
            room_number = self.room_edit.text().strip() or None
            floor = self.floor_edit.text().strip() or None
            description = self.description_edit.toPlainText().strip() or None
            
            if self.class_id:
                # تحديث الصف الموجود
                self.db.cursor.execute("""
                    UPDATE classes SET
                        class_name = ?, section = ?, capacity = ?,
                        class_teacher_id = ?, status = ?, room_number = ?,
                        floor = ?, description = ?
                    WHERE id = ?
                """, (class_name, section, capacity, teacher_id, status,
                      room_number, floor, description, self.class_id))
                
                message = tr('class_updated', self.language)
            else:
                # إضافة صف جديد
                self.db.cursor.execute("""
                    INSERT INTO classes 
                    (class_name, section, capacity, class_teacher_id, status,
                     room_number, floor, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (class_name, section, capacity, teacher_id, status,
                      room_number, floor, description))
                
                message = tr('class_added', self.language)
            
            self.db.connection.commit()
            
            QMessageBox.information(
                self,
                tr('success', self.language),
                message
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, tr('error', self.language), str(e))
