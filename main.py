# school_management_system/main.py

import sys
from PyQt6.QtWidgets import QApplication
from database.db_manager import init_db
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    """
    الدالة الرئيسية لتشغيل التطبيق.
    """
    # تهيئة قاعدة البيانات وإنشاء الجداول إذا لم تكن موجودة
    init_db()

    app = QApplication(sys.argv)

    # عرض نافذة تسجيل الدخول
    login_window = LoginWindow()

    # التحقق من نجاح تسجيل الدخول
    if login_window.exec() == 1:  # 1 يعني أن تسجيل الدخول نجح
        user_role = login_window.user_role
        main_win = MainWindow(user_role)
        main_win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
