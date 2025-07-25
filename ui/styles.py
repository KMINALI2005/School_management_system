from config import COLORS

STYLESHEET = f"""
/* النمط العام */
QWidget {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
    color: {COLORS['text']};
    background-color: {COLORS['background']};
}}

/* نافذة تسجيل الدخول */
QDialog#LoginWindow {{
    background-color: {COLORS['white']};
}}

/* الأزرار */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['secondary']};
}}

QPushButton#primaryButton {{
    background-color: {COLORS['primary']};
}}

QPushButton#successButton {{
    background-color: {COLORS['success']};
}}

QPushButton#successButton:hover {{
    background-color: #229954;
}}

QPushButton#dangerButton {{
    background-color: {COLORS['danger']};
}}

QPushButton#dangerButton:hover {{
    background-color: #C0392B;
}}

QPushButton#infoButton {{
    background-color: {COLORS['info']};
}}

/* حقول الإدخال */
QLineEdit, QTextEdit, QSpinBox, QComboBox, QDateEdit {{
    padding: 8px;
    border: 2px solid {COLORS['light']};
    border-radius: 5px;
    background-color: {COLORS['white']};
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, 
QComboBox:focus, QDateEdit:focus {{
    border-color: {COLORS['secondary']};
}}

/* الجداول */
QTableWidget {{
    background-color: {COLORS['white']};
    alternate-background-color: {COLORS['light']};
    gridline-color: {COLORS['light']};
    border: 1px solid {COLORS['light']};
    border-radius: 5px;
}}

QTableWidget::item {{
    padding: 5px;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['secondary']};
    color: {COLORS['white']};
}}

QHeaderView::section {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    padding: 10px;
    border: none;
    font-weight: bold;
}}

/* القائمة الجانبية */
QListWidget#sideMenu {{
    background-color: {COLORS['primary']};
    border: none;
    outline: none;
}}

QListWidget#sideMenu::item {{
    color: {COLORS['white']};
    padding: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}}

QListWidget#sideMenu::item:hover {{
    background-color: {COLORS['secondary']};
}}

QListWidget#sideMenu::item:selected {{
    background-color: {COLORS['secondary']};
    border-left: 4px solid {COLORS['white']};
}}

/* التسميات */
QLabel {{
    color: {COLORS['text']};
}}

QLabel#titleLabel {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS['primary']};
    padding: 10px;
}}

QLabel#statsLabel {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['white']};
}}

/* البطاقات */
QFrame#statsCard {{
    background-color: {COLORS['white']};
    border-radius: 10px;
    padding: 20px;
}}

/* شريط التقدم */
QProgressBar {{
    # ... تكملة من الكود السابق
    border: none;
    border-radius: 5px;
    background-color: {COLORS['light']};
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['success']};
    border-radius: 5px;
}}

/* التبويبات */
QTabWidget::pane {{
    border: 1px solid {COLORS['light']};
    background-color: {COLORS['white']};
    border-radius: 5px;
}}

QTabBar::tab {{
    background-color: {COLORS['light']};
    color: {COLORS['text']};
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['white']};
    border-bottom: 2px solid {COLORS['primary']};
}}

QTabBar::tab:hover {{
    background-color: {COLORS['secondary']};
    color: {COLORS['white']};
}}

/* مربعات الاختيار */
QCheckBox {{
    spacing: 10px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 3px;
    border: 2px solid {COLORS['light']};
    background-color: {COLORS['white']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['success']};
    border-color: {COLORS['success']};
}}

/* أزرار الراديو */
QRadioButton {{
    spacing: 10px;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid {COLORS['light']};
    background-color: {COLORS['white']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

/* شريط التمرير */
QScrollBar:vertical {{
    background-color: {COLORS['light']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['secondary']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['primary']};
}}

/* مربعات المجموعة */
QGroupBox {{
    font-weight: bold;
    border: 2px solid {COLORS['light']};
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    background-color: {COLORS['background']};
}}

/* القوائم المنسدلة */
QMenu {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['light']};
    border-radius: 5px;
    padding: 5px;
}}

QMenu::item {{
    padding: 8px 20px;
    border-radius: 3px;
}}

QMenu::item:selected {{
    background-color: {COLORS['secondary']};
    color: {COLORS['white']};
}}

/* رسائل التحذير */
QMessageBox {{
    background-color: {COLORS['white']};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}

/* التقويم */
QCalendarWidget {{
    background-color: {COLORS['white']};
}}

QCalendarWidget QToolButton {{
    color: {COLORS['text']};
    background-color: {COLORS['white']};
}}

QCalendarWidget QToolButton:hover {{
    background-color: {COLORS['light']};
}}

QCalendarWidget QToolButton:pressed {{
    background-color: {COLORS['secondary']};
    color: {COLORS['white']};
}}

/* شريط الأدوات */
QToolBar {{
    background-color: {COLORS['white']};
    border: none;
    padding: 5px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 5px;
    border-radius: 3px;
}}

QToolButton:hover {{
    background-color: {COLORS['light']};
}}

/* البطاقات الإحصائية */
QFrame#statCard {{
    background-color: {COLORS['white']};
    border-radius: 10px;
    padding: 20px;
    border: 1px solid {COLORS['light']};
}}

QFrame#primaryCard {{
    background-color: {COLORS['primary']};
}}

QFrame#successCard {{
    background-color: {COLORS['success']};
}}

QFrame#warningCard {{
    background-color: {COLORS['warning']};
}}

QFrame#dangerCard {{
    background-color: {COLORS['danger']};
}}

QFrame#infoCard {{
    background-color: {COLORS['info']};
}}

/* نمط خاص للغة العربية */
QWidget[direction="rtl"] {{
    direction: rtl;
}}

QWidget[direction="rtl"] QListWidget#sideMenu::item:selected {{
    border-left: none;
    border-right: 4px solid {COLORS['white']};
}}
"""

# أنماط خاصة للأزرار مع الأيقونات
ICON_BUTTON_STYLE = f"""
QPushButton {{
    text-align: left;
    padding: 10px 15px;
    border: none;
    background-color: {COLORS['white']};
    border-radius: 5px;
}}

QPushButton:hover {{
    background-color: {COLORS['light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['secondary']};
    color: {COLORS['white']};
}}
"""

# نمط خاص للبطاقات الإحصائية
STAT_CARD_STYLE = """
QFrame {
    background-color: %s;
    border-radius: 15px;
    padding: 20px;
}

QLabel {
    color: white;
    background-color: transparent;
}

QLabel#statNumber {
    font-size: 32px;
    font-weight: bold;
}

QLabel#statTitle {
    font-size: 16px;
    color: rgba(255, 255, 255, 0.9);
}
"""

# دالة للحصول على نمط البطاقة الإحصائية بلون محدد
def get_stat_card_style(color):
    return STAT_CARD_STYLE % color

# نمط خاص لنافذة تسجيل الدخول
LOGIN_STYLE = f"""
QWidget {{
    background-color: {COLORS['background']};
}}

QFrame#loginFrame {{
    background-color: {COLORS['white']};
    border-radius: 20px;
    padding: 40px;
}}

QLabel#logoLabel {{
    font-size: 32px;
    font-weight: bold;
    color: {COLORS['primary']};
    padding: 20px;
}}

QLineEdit {{
    padding: 12px;
    font-size: 16px;
    border: 2px solid {COLORS['light']};
    border-radius: 8px;
}}

QPushButton#loginButton {{
    padding: 12px;
    font-size: 16px;
    font-weight: bold;
    background-color: {COLORS['primary']};
    color: white;
    border-radius: 8px;
}}

QPushButton#loginButton:hover {{
    background-color: {COLORS['dark']};
}}
"""

# نمط خاص للمحادثة مع AI
CHAT_STYLE = f"""
QTextEdit#chatDisplay {{
    background-color: {COLORS['light']};
    border: none;
    border-radius: 10px;
    padding: 10px;
}}

QLineEdit#chatInput {{
    padding: 12px;
    font-size: 14px;
    border: 2px solid {COLORS['light']};
    border-radius: 25px;
    background-color: {COLORS['white']};
}}

QPushButton#sendButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 18px;
}}

QPushButton#sendButton:hover {{
    background-color: {COLORS['dark']};
}}

QLabel#userMessage {{
    background-color: {COLORS['primary']};
    color: white;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px;
}}

QLabel#aiMessage {{
    background-color: {COLORS['white']};
    color: {COLORS['text']};
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px;
    border: 1px solid {COLORS['light']};
}}
"""
