import os
from pathlib import Path

# المسارات الأساسية
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = os.path.join(BASE_DIR, 'school_database.db')
RESOURCES_PATH = os.path.join(BASE_DIR, 'resources')

# إعدادات اللغة
LANGUAGES = {
    'ar': 'العربية',
    'en': 'English'
}
DEFAULT_LANGUAGE = 'ar'

# إعدادات الألوان والتصميم
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'success': '#27AE60',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'info': '#16A085',
    'light': '#ECF0F1',
    'dark': '#34495E',
    'white': '#FFFFFF',
    'background': '#F5F6FA',
    'text': '#2C3E50'
}

# إعدادات الذكاء الاصطناعي
AI_MODEL = "aubmindlab/bert-base-arabertv2"  # نموذج عربي للذكاء الاصطناعي
