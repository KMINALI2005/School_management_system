from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFrame, QComboBox,
                           QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QIcon
from database.db_manager import DatabaseManager
from ui.styles import LOGIN_STYLE
from utils.translations import tr
import config

class LoginWindow(QDialog):
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_language = config.DEFAULT_LANGUAGE
        self.setup_ui()
        self.setStyleSheet(LOGIN_STYLE)
        
    def setup_ui(self):
        self.setWindowTitle(tr("login_title", self.current_language))
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # إطار تسجيل الدخول
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        frame_layout = QVBoxLayout(login_frame)
        frame_layout.setSpacing(20)
        
        # شعار المدرسة
        logo_label = QLabel("🏫")
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(logo_label)
        
        # عنوان النظام
        title_label = QLabel(tr("system_name", self.current_language))
        title_label.setObjectName("logoLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # اختيار اللغة
        language_layout = QHBoxLayout()
        language_label = QLabel(tr("language", self.current_language))
        self.language_combo = QComboBox()
        for code, name in config.LANGUAGES.items():
            self.language_combo.addItem(name, code)
        self.language_combo.setCurrentText(config.LANGUAGES[self.current_language])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        frame_layout.addLayout(language_layout)
        
        # حقل اسم المستخدم
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(tr("username", self.current_language))
        frame_layout.addWidget(self.username_input)
        
        # حقل كلمة المرور
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(tr("password", self.current_language))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        frame_layout.addWidget(self.password_input)
        
        # خيار تذكرني
        self.remember_checkbox = QCheckBox(tr("remember_me", self.current_language))
        frame_layout.addWidget(self.remember_checkbox)
        
        # زر تسجيل الدخول
        self.login_button = QPushButton(tr("login", self.current_language))
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        frame_layout.addWidget(self.login_button)
        
        # رسالة الخطأ
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; padding: 10px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        frame_layout.addWidget(self.error_label)
        
        # زر الإغلاق
        close_button = QPushButton("✕")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #E74C3C;
                font-size: 20px;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #E74C3C;
                color: white;
                border-radius: 15px;
            }
        """)
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # تخطيط زر الإغلاق
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(close_button)
        
        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        main_layout.addWidget(login_frame)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # تأثيرات الحركة
        self.fade_in_animation()
        
        # اختصارات لوحة المفاتيح
        self.password_input.returnPressed.connect(self.handle_login)
        
    def fade_in_animation(self):
        """تأثير الظهور التدريجي"""
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        # ... تكملة من الكود السابق
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()
    
    def change_language(self):
        """تغيير لغة الواجهة"""
        self.current_language = self.language_combo.currentData()
        self.update_ui_language()
    
    def update_ui_language(self):
        """تحديث نصوص الواجهة"""
        self.setWindowTitle(tr("login_title", self.current_language))
        self.username_input.setPlaceholderText(tr("username", self.current_language))
        self.password_input.setPlaceholderText(tr("password", self.current_language))
        self.remember_checkbox.setText(tr("remember_me", self.current_language))
        self.login_button.setText(tr("login", self.current_language))
        
        # تحديث اتجاه النص
        if self.current_language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    
    def handle_login(self):
        """معالجة عملية تسجيل الدخول"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # التحقق من الحقول الفارغة
        if not username or not password:
            self.show_error(tr("empty_fields_error", self.current_language))
            return
        
        # محاولة تسجيل الدخول
        user = self.db.authenticate_user(username, password)
        
        if user:
            # تسجيل دخول ناجح
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name'],
                'language': self.current_language
            }
            
            # تأثير الاختفاء
            self.fade_out_animation(user_data)
        else:
            # فشل تسجيل الدخول
            self.show_error(tr("invalid_credentials", self.current_language))
            self.shake_window()
    
    def show_error(self, message):
        """عرض رسالة خطأ"""
        self.error_label.setText(message)
        self.error_label.show()
        
        # إخفاء الرسالة بعد 3 ثوانٍ
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, self.error_label.hide)
    
    def shake_window(self):
        """تأثير اهتزاز النافذة عند فشل تسجيل الدخول"""
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(500)
        animation.setLoopCount(1)
        
        pos = self.pos()
        animation.setKeyValueAt(0, pos)
        animation.setKeyValueAt(0.1, pos + Qt.QPoint(-10, 0))
        animation.setKeyValueAt(0.2, pos + Qt.QPoint(10, 0))
        animation.setKeyValueAt(0.3, pos + Qt.QPoint(-10, 0))
        animation.setKeyValueAt(0.4, pos + Qt.QPoint(10, 0))
        animation.setKeyValueAt(0.5, pos + Qt.QPoint(-10, 0))
        animation.setKeyValueAt(0.6, pos + Qt.QPoint(10, 0))
        animation.setKeyValueAt(0.7, pos + Qt.QPoint(-10, 0))
        animation.setKeyValueAt(0.8, pos + Qt.QPoint(10, 0))
        animation.setKeyValueAt(0.9, pos + Qt.QPoint(-10, 0))
        animation.setKeyValueAt(1, pos)
        
        animation.start()
    
    def fade_out_animation(self, user_data):
        """تأثير الاختفاء عند نجاح تسجيل الدخول"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(lambda: self.on_login_complete(user_data))
        self.animation.start()
    
    def on_login_complete(self, user_data):
        """إكمال عملية تسجيل الدخول"""
        self.login_successful.emit(user_data)
        self.accept()
    
    def mousePressEvent(self, event):
        """تمكين سحب النافذة"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """تحريك النافذة"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
