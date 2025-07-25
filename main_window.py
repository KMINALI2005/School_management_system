from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QStackedWidget, QListWidget, QLabel, QPushButton,
                           QFrame, QGridLayout, QSpacerItem, QSizePolicy,
                           QListWidgetItem, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QColor, QPalette
from ui.styles import STYLESHEET, get_stat_card_style
from ui.student_management import StudentManagement
from ui.teacher_management import TeacherManagement
from ui.class_management import ClassManagement
from ui.subject_management import SubjectManagement
from ui.grades_management import GradesManagement
from ui.attendance_management import AttendanceManagement
from ui.timetable_management import TimetableManagement
from ui.reports_management import ReportsManagement
from ui.notifications import NotificationsWidget
from ui.settings import SettingsWidget
from ai.assistant import AIAssistant
from database.db_manager import DatabaseManager
from utils.translations import tr
import config

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.current_language = user_data.get('language', 'ar')
        self.db = DatabaseManager()
        self.setup_ui()
        self.setStyleSheet(STYLESHEET)
        self.load_dashboard_stats()
        
    def setup_ui(self):
        self.setWindowTitle(tr("main_window_title", self.current_language))
        self.setGeometry(100, 100, 1400, 800)
        
        # تحديد اتجاه النص
        if self.current_language == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        # الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # القائمة الجانبية
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # منطقة المحتوى
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # شريط العنوان
        self.setup_titlebar()
        content_layout.addWidget(self.titlebar)
        
        # المحتوى المكدس
        self.stacked_widget = QStackedWidget()
        self.setup_pages()
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget)
        
    def setup_sidebar(self):
        """إعداد القائمة الجانبية"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {config.COLORS['primary']};
            }}
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # معلومات المستخدم
        user_info_widget = QWidget()
        user_info_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {config.COLORS['dark']};
                padding: 20px;
            }}
        """)
        user_info_layout = QVBoxLayout(user_info_widget)
        
        # أيقونة المستخدم
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 48px;")
        user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(user_icon)
        
        # اسم المستخدم
        user_name = QLabel(self.user_data.get('full_name', 'المستخدم'))
        user_name.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(user_name)
        
        # دور المستخدم
        role_text = tr(f"role_{self.user_data.get('role', 'user')}", self.current_language)
        user_role = QLabel(role_text)
        user_role.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
        """)
        user_role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info_layout.addWidget(user_role)
        
        sidebar_layout.addWidget(user_info_widget)
        
        # قائمة الصفحات
        self.menu_list = QListWidget()
        self.menu_list.setObjectName("sideMenu")
        self.menu_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # إضافة عناصر القائمة
        menu_items = [
            ("🏠", "dashboard", 0),
            ("👥", "students", 1),
            ("👨‍🏫", "teachers", 2),
            ("🏫", "classes", 3),
            ("📚", "subjects", 4),
            ("📊", "grades", 5),
            ("✓", "attendance", 6),
            ("📅", "timetable", 7),
            ("📄", "reports", 8),
            ("🔔", "notifications", 9),
            ("🤖", "ai_assistant", 10),
            ("⚙️", "settings", 11)
        ]
        
        for icon, key, index in menu_items:
            item = QListWidgetItem(f"{icon}  {tr(key, self.current_language)}")
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.menu_list.addItem(item)
        
        self.menu_list.currentRowChanged.connect(self.change_page)
        self.menu_list.setCurrentRow(0)
        
        sidebar_layout.addWidget(self.menu_list)
        
        # زر تسجيل الخروج
        logout_button = QPushButton(f"🚪  {tr('logout', self.current_language)}")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        logout_button.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_button)
        
    def setup_titlebar(self):
        """إعداد شريط العنوان"""
        self.titlebar = QFrame()
        self.titlebar.setFixedHeight(70)
        self.titlebar.setStyleSheet(f"""
            QFrame {{
                background-color: {config.COLORS['white']};
                border-bottom: 1px solid {config.COLORS['light']};
            }}
        """)
        
        titlebar_layout = QHBoxLayout(self.titlebar)
        titlebar_layout.setContentsMargins(20, 0, 20, 0)
        
        # عنوان الصفحة
        self.page_title = QLabel(tr("dashboard", self.current_language))
        self.page_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
        """)
        titlebar_layout.addWidget(self.page_title)
        
        titlebar_layout.addStretch()
        
        # أزرار الإجراءات السريعة
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(10)
        
        # زر الإشعارات
        notification_btn = QPushButton("🔔")
        notification_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F6FA;
                border: none;
                border-radius: 20px;
                padding: 10px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        notification_btn.setFixedSize(40, 40)
        quick_actions.addWidget(notification_btn)
        
        titlebar_layout.addLayout(quick_actions)
        
    def setup_pages(self):
        """إعداد الصفحات"""
        # لوحة التحكم
        self.dashboard_widget = self.create_dashboard()
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # إدارة الطلاب
        self.student_management = StudentManagement(self.current_language)
        self.stacked_widget.addWidget(self.student_management)
        
        # إدارة المعلمين
        self.teacher_management = TeacherManagement(self.current_language)
        self.stacked_widget.addWidget(self.teacher_management)
        # ... تكملة من الكود السابق
        
        # إدارة الصفوف
        self.class_management = ClassManagement(self.current_language)
        self.stacked_widget.addWidget(self.class_management)
        
        # إدارة المواد
        self.subject_management = SubjectManagement(self.current_language)
        self.stacked_widget.addWidget(self.subject_management)
        
        # إدارة الدرجات
        self.grades_management = GradesManagement(self.current_language, self.user_data)
        self.stacked_widget.addWidget(self.grades_management)
        
        # إدارة الحضور
        self.attendance_management = AttendanceManagement(self.current_language)
        self.stacked_widget.addWidget(self.attendance_management)
        
        # إدارة الجدول الدراسي
        self.timetable_management = TimetableManagement(self.current_language)
        self.stacked_widget.addWidget(self.timetable_management)
        
        # التقارير
        self.reports_management = ReportsManagement(self.current_language)
        self.stacked_widget.addWidget(self.reports_management)
        
        # الإشعارات
        self.notifications_widget = NotificationsWidget(self.current_language, self.user_data)
        self.stacked_widget.addWidget(self.notifications_widget)
        
        # مساعد الذكاء الاصطناعي
        self.ai_assistant = AIAssistant(self.current_language, self.user_data)
        self.stacked_widget.addWidget(self.ai_assistant)
        
        # الإعدادات
        self.settings_widget = SettingsWidget(self.current_language, self.user_data)
        self.stacked_widget.addWidget(self.settings_widget)
    
    def create_dashboard(self):
        """إنشاء لوحة التحكم"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان الترحيب
        welcome_label = QLabel(tr("welcome_message", self.current_language).format(
            name=self.user_data.get('full_name', '')
        ))
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 20px;
        """)
        layout.addWidget(welcome_label)
        
        # البطاقات الإحصائية
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # بطاقة الطلاب
        self.students_card = self.create_stat_card(
            "👥", tr("total_students", self.current_language), 
            "0", config.COLORS['primary']
        )
        stats_grid.addWidget(self.students_card, 0, 0)
        
        # بطاقة المعلمين
        self.teachers_card = self.create_stat_card(
            "👨‍🏫", tr("total_teachers", self.current_language), 
            "0", config.COLORS['success']
        )
        stats_grid.addWidget(self.teachers_card, 0, 1)
        
        # بطاقة الصفوف
        self.classes_card = self.create_stat_card(
            "🏫", tr("total_classes", self.current_language), 
            "0", config.COLORS['warning']
        )
        stats_grid.addWidget(self.classes_card, 0, 2)
        
        # بطاقة المواد
        self.subjects_card = self.create_stat_card(
            "📚", tr("total_subjects", self.current_language), 
            "0", config.COLORS['info']
        )
        stats_grid.addWidget(self.subjects_card, 0, 3)
        
        # بطاقة نسبة الحضور
        self.attendance_card = self.create_stat_card(
            "✓", tr("attendance_today", self.current_language), 
            "0%", config.COLORS['danger']
        )
        stats_grid.addWidget(self.attendance_card, 1, 0, 1, 2)
        
        # بطاقة الأنشطة الأخيرة
        self.activities_card = self.create_activity_card()
        stats_grid.addWidget(self.activities_card, 1, 2, 1, 2)
        
        layout.addLayout(stats_grid)
        
        # إضافة مخططات إحصائية
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # مخطط الحضور الأسبوعي
        attendance_chart = self.create_attendance_chart()
        charts_layout.addWidget(attendance_chart)
        
        # مخطط توزيع الدرجات
        grades_chart = self.create_grades_chart()
        charts_layout.addWidget(grades_chart)
        
        layout.addLayout(charts_layout)
        layout.addStretch()
        
        return dashboard
    
    def create_stat_card(self, icon, title, value, color):
        """إنشاء بطاقة إحصائية"""
        card = QFrame()
        card.setStyleSheet(get_stat_card_style(color))
        card.setFixedHeight(120)
        
        # إضافة تأثير الظل
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(card)
        
        # الأيقونة
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            font-size: 48px;
            background: transparent;
        """)
        layout.addWidget(icon_label)
        
        # المعلومات
        info_layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setObjectName("statNumber")
        info_layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        info_layout.addWidget(title_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return card
    
    def create_activity_card(self):
        """إنشاء بطاقة الأنشطة الأخيرة"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {config.COLORS['white']};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        # إضافة تأثير الظل
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        
        # العنوان
        title = QLabel(tr("recent_activities", self.current_language))
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # قائمة الأنشطة
        activities = [
            "✅ تم إضافة 5 طلاب جدد",
            "📊 تم رفع درجات الرياضيات للصف الثالث",
            "📅 تم تحديث الجدول الدراسي",
            "🔔 رسالة جديدة من المدير"
        ]
        
        for activity in activities:
            activity_label = QLabel(activity)
            activity_label.setStyleSheet("""
                padding: 8px;
                color: #7F8C8D;
                border-bottom: 1px solid #ECF0F1;
            """)
            layout.addWidget(activity_label)
        
        layout.addStretch()
        return card
    
    def create_attendance_chart(self):
        """إنشاء مخطط الحضور الأسبوعي"""
        from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis
        from PyQt6.QtGui import QPainter
        
        chart = QChart()
        chart.setTitle(tr("weekly_attendance", self.current_language))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # بيانات تجريبية
        series = QLineSeries()
        series.append(0, 92)
        series.append(1, 95)
        series.append(2, 88)
        series.append(3, 93)
        series.append(4, 90)
        
        chart.addSeries(series)
        
        # المحاور
        axis_x = QCategoryAxis()
        days = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"]
        for i, day in enumerate(days):
            axis_x.append(day, i)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setLabelFormat("%d%")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        # تخصيص المظهر
        chart.setBackgroundBrush(Qt.GlobalColor.transparent)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setStyleSheet(f"""
            background-color: {config.COLORS['white']};
            border-radius: 15px;
            padding: 10px;
        """)
        
        # إضافة تأثير الظل
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        chart_view.setGraphicsEffect(shadow)
        
        return chart_view
    
    def create_grades_chart(self):
        """إنشاء مخطط توزيع الدرجات"""
        from PyQt6.QtCharts import QChart, QChartView, QPieSeries
        from PyQt6.QtGui import QPainter
        
        chart = QChart()
        chart.setTitle(tr("grades_distribution", self.current_language))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # بيانات تجريبية
        series = QPieSeries()
        series.append("ممتاز", 45)
        series.append("جيد جداً", 30)
        series.append("جيد", 15)
        series.append("مقبول", 10)
        
        # تخصيص الألوان
        colors = [
            QColor(config.COLORS['success']),
            QColor(config.COLORS['info']),
            QColor(config.COLORS['warning']),
            QColor(config.COLORS['danger'])
        ]
        
        for i, slice in enumerate(series.slices()):
            slice.setLabelVisible(True)
            slice.setPen(QColor(Qt.GlobalColor.white))
            slice.setBrush(colors[i])
        
        chart.addSeries(series)
        chart.setBackgroundBrush(Qt.GlobalColor.transparent)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setStyleSheet(f"""
            background-color: {config.COLORS['white']};
            border-radius: 15px;
            padding: 10px;
        """)
        
        # إضافة تأثير الظل
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        chart_view.setGraphicsEffect(shadow)
        
        return chart_view
    
    def load_dashboard_stats(self):
        """تحميل إحصائيات لوحة التحكم"""
        stats = self.db.get_dashboard_stats()
        
        # تحديث البطاقات
        self.update_stat_card(self.students_card, str(stats['total_students']))
        self.update_stat_card(self.teachers_card, str(stats['total_teachers']))
        self.update_stat_card(self.classes_card, str(stats['total_classes']))
        self.update_stat_card(self.subjects_card, str(stats['total_subjects']))
        self.update_stat_card(self.attendance_card, f"{stats['attendance_rate']:.1f}%")
    
    def update_stat_card(self, card, value):
        """تحديث قيمة البطاقة الإحصائية"""
        value_label = card.findChild(QLabel, "statNumber")
        if value_label:
            value_label.setText(value)
    
    def change_page(self, index):
        """تغيير الصفحة الحالية"""
        self.stacked_widget.setCurrentIndex(index)
        
        # تحديث عنوان الصفحة
        menu_items = [
            "dashboard", "students", "teachers", "classes", 
            "subjects", "grades", "attendance", "timetable",
            "reports", "notifications", "ai_assistant", "settings"
        ]
        
        if index < len(menu_items):
            self.page_title.setText(tr(menu_items[index], self.current_language))
            
            # تأثير الانتقال
            self.animate_page_change()
    
    def animate_page_change(self):
        """تأثير حركة عند تغيير الصفحة"""
        current_widget = self.stacked_widget.currentWidget()
        
        # تأثير الظهور التدريجي
        self.fade_animation = QPropertyAnimation(current_widget, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.start()
    
    # ... تكملة من الكود السابق
    
    def logout(self):
        """تسجيل الخروج"""
        from PyQt6.QtWidgets import QMessageBox
        
        # رسالة تأكيد
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(tr("confirm_logout", self.current_language))
        msg.setText(tr("logout_message", self.current_language))
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | 
            QMessageBox.StandardButton.No
        )
        
        if self.current_language == 'ar':
            msg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            yes_button = msg.button(QMessageBox.StandardButton.Yes)
            yes_button.setText("نعم")
            no_button = msg.button(QMessageBox.StandardButton.No)
            no_button.setText("لا")
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            # إغلاق قاعدة البيانات
            self.db.close()
            
            # إغلاق النافذة الرئيسية
            self.close()
            
            # إظهار نافذة تسجيل الدخول مرة أخرى
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
    
    def closeEvent(self, event):
        """معالجة حدث إغلاق النافذة"""
        # حفظ البيانات وإغلاق الاتصالات
        self.db.close()
        event.accept()
    
    def refresh_current_page(self):
        """تحديث الصفحة الحالية"""
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 0:  # لوحة التحكم
            self.load_dashboard_stats()
        elif current_index == 1:  # الطلاب
            self.student_management.refresh_table()
        elif current_index == 2:  # المعلمين
            self.teacher_management.refresh_table()
        elif current_index == 3:  # الصفوف
            self.class_management.refresh_table()
        elif current_index == 4:  # المواد
            self.subject_management.refresh_table()
        elif current_index == 5:  # الدرجات
            self.grades_management.refresh_data()
        elif current_index == 6:  # الحضور
            self.attendance_management.refresh_data()
        elif current_index == 7:  # الجدول الدراسي
            self.timetable_management.refresh_data()
        elif current_index == 9:  # الإشعارات
            self.notifications_widget.refresh_notifications()
