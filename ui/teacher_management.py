# ui/teacher_management.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDialog, QFormLayout, QMessageBox,
    QHeaderView, QAbstractItemView, QLabel, QListWidget, QListWidgetItem,
    QDialogButtonBox, QComboBox
)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from utils.translations import tr
import hashlib


class TeacherManagement(QWidget):
    """واجهة إدارة المعلمين (CRUD + إسناد مواد)."""

    def __init__(self, language="ar"):
        super().__init__()
        self.language = language
        self.db = DatabaseManager()
        self.setup_ui()
        self.load_teachers()

    # ---------- UI ----------
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # شريط الأدوات
        tb = QHBoxLayout()

        self.add_btn = QPushButton(f"➕ {tr('add_teacher', self.language)}")
        self.add_btn.setObjectName("successButton")
        self.add_btn.clicked.connect(self.show_add_dialog)
        tb.addWidget(self.add_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("search_teachers", self.language))
        self.search_input.textChanged.connect(self.search_teachers)
        self.search_input.setMaximumWidth(300)
        tb.addWidget(self.search_input)

        tb.addStretch()

        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.clicked.connect(self.refresh_table)
        tb.addWidget(refresh_btn)

        layout.addLayout(tb)

        # جدول المعلمين
        self.table = QTableWidget()
        self.init_table()
        layout.addWidget(self.table)

        # شريط المعلومات
        self.info_lbl = QLabel()
        self.info_lbl.setStyleSheet(
            "padding:10px;background:#F5F6FA;border-radius:5px;color:#7F8C8D;"
        )
        layout.addWidget(self.info_lbl)

    def init_table(self):
        headers = [
            tr("teacher_id", self.language),
            tr("full_name", self.language),
            tr("username", self.language),
            tr("email", self.language),
            tr("phone", self.language),
            tr("specialization", self.language),
            tr("hire_date", self.language),
            tr("subjects", self.language),
            tr("actions", self.language),
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

    # ---------- Data ----------
    def load_teachers(self):
        self.table.setRowCount(0)
        self.teachers = self.db.get_all_teachers()
        for t in self.teachers:
            self.add_teacher_row(t)
        self.update_info_label()

    def add_teacher_row(self, t):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # استرجاع المواد المسندة
        subjects = ", ".join(
            s["subject_name"] for s in self.db.get_all_subjects()
            if self.db.cursor.execute(
                "SELECT 1 FROM teacher_subjects WHERE teacher_id = ? AND subject_id = ?",
                (t["id"], s["id"])
            ).fetchone()
        )

        data = [
            t["teacher_id"],
            t["full_name"],
            t["username"],
            t.get("email", ""),
            t.get("phone", ""),
            t.get("specialization", ""),
            t.get("hire_date", ""),
            subjects,
        ]
        for col, val in enumerate(data):
            self.table.setItem(row, col, QTableWidgetItem(str(val)))

        # أزرار الإجراءات
        act_widget = QWidget()
        act_layout = QHBoxLayout(act_widget)
        act_layout.setContentsMargins(5, 0, 5, 0)

        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip(tr("edit", self.language))
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(lambda _, _id=t["id"]: self.show_edit_dialog(_id))
        act_layout.addWidget(edit_btn)

        del_btn = QPushButton("🗑️")
        del_btn.setToolTip(tr("delete", self.language))
        del_btn.setFixedSize(30, 30)
        del_btn.setObjectName("dangerButton")
        del_btn.clicked.connect(lambda _, _id=t["id"]: self.delete_teacher(_id))
        act_layout.addWidget(del_btn)

        assign_btn = QPushButton("📚")
        assign_btn.setToolTip(tr("assign_subjects", self.language))
        assign_btn.setFixedSize(30, 30)
        assign_btn.clicked.connect(lambda _, _id=t["id"]: self.assign_subjects(_id))
        act_layout.addWidget(assign_btn)

        self.table.setCellWidget(row, 8, act_widget)

    # ---------- CRUD ----------
    def show_add_dialog(self):
        dlg = TeacherDialog(self.language, parent=self)
        if dlg.exec():
            try:
                self.db.add_teacher(dlg.get_data())
                self.refresh_table()
                QMessageBox.information(self, tr("success", self.language),
                                        tr("teacher_added_success", self.language))
            except Exception as e:
                QMessageBox.critical(self, tr("error", self.language), str(e))

    def show_edit_dialog(self, teacher_id):
        teacher = next((t for t in self.teachers if t["id"] == teacher_id), None)
        if not teacher:
            return
        dlg = TeacherDialog(self.language, teacher, self)
        if dlg.exec():
            data = dlg.get_data()
            # تحديث بيانات جدول users و teachers معاً
            self.db.cursor.execute(
                "UPDATE users SET full_name=?, email=?, phone=? WHERE id=?",
                (data["full_name"], data["email"], data["phone"], teacher["user_id"])
            )
            self.db.cursor.execute(
                "UPDATE teachers SET full_name=?, email=?, phone=?, specialization=? "
                "WHERE id=?",
                (data["full_name"], data["email"], data["phone"],
                 data["specialization"], teacher_id)
            )
            self.db.connection.commit()
            self.refresh_table()

    def delete_teacher(self, teacher_id):
        msg = QMessageBox.question(
            self, tr("confirm_delete", self.language),
            tr("delete_teacher_confirm", self.language),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if msg == QMessageBox.StandardButton.Yes:
            # حذف من جدول teachers و users
            user_id = next(t for t in self.teachers if t["id"] == teacher_id)["user_id"]
            self.db.cursor.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
            self.db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.db.connection.commit()
            self.refresh_table()

    # ---------- Subjects ----------
    def assign_subjects(self, teacher_id):
        dlg = SubjectAssignDialog(self.language, teacher_id, self)
        dlg.exec()
        self.refresh_table()

    # ---------- Helpers ----------
    def search_teachers(self, text):
        for row in range(self.table.rowCount()):
            visible = any(
                text.lower() in (self.table.item(row, c).text().lower() if self.table.item(row, c) else "")
                for c in range(self.table.columnCount() - 1)
            )
            self.table.setRowHidden(row, not visible)

    def refresh_table(self):
        self.load_teachers()
        self.search_input.clear()

    def update_info_label(self):
        total = self.table.rowCount()
        visible = sum(1 for r in range(total) if not self.table.isRowHidden(r))
        self.info_lbl.setText(tr("showing_teachers", self.language).format(
            visible=visible, total=total))


# ------------------------------------------------------------------
class TeacherDialog(QDialog):
    """نافذة إضافة/تعديل معلم."""

    def __init__(self, language="ar", teacher_data=None, parent=None):
        super().__init__(parent)
        self.language = language
        self.teacher_data = teacher_data
        self.setup_ui()
        if teacher_data:
            self.fill_data()

    def setup_ui(self):
        self.setWindowTitle(tr("add_teacher", self.language)
                            if not self.teacher_data else tr("edit_teacher", self.language))
        self.setFixedWidth(450)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.teacher_id = QLineEdit()
        self.full_name = QLineEdit()
        self.username = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.specialization = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow(tr("teacher_id", self.language), self.teacher_id)
        form.addRow(tr("full_name", self.language), self.full_name)
        form.addRow(tr("username", self.language), self.username)
        form.addRow(tr("email", self.language), self.email)
        form.addRow(tr("phone", self.language), self.phone)
        form.addRow(tr("specialization", self.language), self.specialization)
        if not self.teacher_data:
            form.addRow(tr("password", self.language), self.password)

        layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.validate)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def fill_data(self):
        self.teacher_id.setText(self.teacher_data["teacher_id"])
        self.full_name.setText(self.teacher_data["full_name"])
        self.username.setText(self.teacher_data["username"])
        self.username.setDisabled(True)
        self.email.setText(self.teacher_data.get("email", ""))
        self.phone.setText(self.teacher_data.get("phone", ""))
        self.specialization.setText(self.teacher_data.get("specialization", ""))

    def validate(self):
        if not self.teacher_id.text() or not self.full_name.text() or not self.username.text():
            QMessageBox.warning(self, tr("warning", self.language),
                                tr("required_fields", self.language))
            return
        self.accept()

    def get_data(self):
        return {
            "teacher_id": self.teacher_id.text().strip(),
            "full_name": self.full_name.text().strip(),
            "username": self.username.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "specialization": self.specialization.text().strip(),
            "password": self.password.text().strip() or "teacher123",
        }


# ------------------------------------------------------------------
class SubjectAssignDialog(QDialog):
    """نافذة إسناد المواد إلى معلم."""

    def __init__(self, language, teacher_id, parent=None):
        super().__init__(parent)
        self.language = language
        self.teacher_id = teacher_id
        self.db = DatabaseManager()
        self.setWindowTitle(tr("assign_subjects", language))
        self.setFixedWidth(400)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.populate_subjects()
        layout.addWidget(self.list_widget)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def populate_subjects(self):
        current = {
            r["subject_id"]
            for r in self.db.cursor.execute(
                "SELECT subject_id FROM teacher_subjects WHERE teacher_id=?",
                (self.teacher_id,),
            ).fetchall()
        }
        for s in self.db.get_all_subjects():
            item = QListWidgetItem(s["subject_name"])
            item.setData(Qt.ItemDataRole.UserRole, s["id"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if s["id"] in current else Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

    def save(self):
        # حذف القديم
        self.db.cursor.execute("DELETE FROM teacher_subjects WHERE teacher_id=?", (self.teacher_id,))
        # إضافة الجديد
        for i in range(self.list_widget.count()):
            it = self.list_widget.item(i)
            if it.checkState() == Qt.CheckState.Checked:
                self.db.assign_teacher_to_subject(self.teacher_id, it.data(Qt.ItemDataRole.UserRole))
        self.db.connection.commit()
        self.accept()
