"""
نظام النسخ الاحتياطي واستعادة البيانات
يدعم النسخ التلقائي والاستعادة الآمنة
"""

import sqlite3
import json
import datetime
import os
import shutil
import zipfile
import schedule
import threading
import time
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt6.QtCore import QThread, pyqtSignal
from database.db_manager import DatabaseManager
from utils.translations import tr
import logging

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

class BackupWorker(QThread):
    """خيط العمل للنسخ الاحتياطي"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, backup_path, db_path, include_files=True):
        super().__init__()
        self.backup_path = backup_path
        self.db_path = db_path
        self.include_files = include_files
    
    def run(self):
        try:
            self.status.emit("بدء النسخ الاحتياطي...")
            self.progress.emit(10)
            
            # إنشاء مجلد مؤقت
            temp_dir = f"temp_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # نسخ قاعدة البيانات
            self.status.emit("نسخ قاعدة البيانات...")
            shutil.copy2(self.db_path, os.path.join(temp_dir, 'database.db'))
            self.progress.emit(30)
            
            # إنشاء ملف معلومات النسخة الاحتياطية
            backup_info = {
                'created_at': datetime.datetime.now().isoformat(),
                'version': '1.0',
                'database_size': os.path.getsize(self.db_path),
                'backup_type': 'full' if self.include_files else 'database_only'
            }
            
            with open(os.path.join(temp_dir, 'backup_info.json'), 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            self.progress.emit(50)
            
            # نسخ الملفات الإضافية إذا كانت مطلوبة
            if self.include_files:
                self.status.emit("نسخ الملفات الإضافية...")
                
                # نسخ ملفات الإعدادات
                if os.path.exists('config.py'):
                    shutil.copy2('config.py', os.path.join(temp_dir, 'config.py'))
                
                # نسخ مجلد الموارد
                if os.path.exists('resources'):
                    shutil.copytree('resources', os.path.join(temp_dir, 'resources'))
                
                self.progress.emit(70)
            
            # ضغط النسخة الاحتياطية
            self.status.emit("ضغط الملفات...")
            with zipfile.ZipFile(self.backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_path)
            
            self.progress.emit(90)
            
            # تنظيف الملفات المؤقتة
            shutil.rmtree(temp_dir)
            
            self.progress.emit(100)
            self.finished.emit(True, "تم إنشاء النسخة الاحتياطية بنجاح")
            
        except Exception as e:
            logging.error(f"خطأ في النسخ الاحتياطي: {str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            self.finished.emit(False, f"فشل في النسخ الاحتياطي: {str(e)}")


class RestoreWorker(QThread):
    """خيط العمل لاستعادة النسخة الاحتياطية"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, backup_path, db_path):
        super().__init__()
        self.backup_path = backup_path
        self.db_path = db_path
    
    def run(self):
        try:
            self.status.emit("بدء استعادة النسخة الاحتياطية...")
            self.progress.emit(10)
            
            # إنشاء مجلد مؤقت
            temp_dir = f"temp_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # استخراج النسخة الاحتياطية
            self.status.emit("استخراج الملفات...")
            with zipfile.ZipFile(self.backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            self.progress.emit(30)
            
            # التحقق من صحة النسخة الاحتياطية
            backup_info_path = os.path.join(temp_dir, 'backup_info.json')
            if not os.path.exists(backup_info_path):
                raise Exception("ملف معلومات النسخة الاحتياطية مفقود")
            
            with open(backup_info_path, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
            
            self.progress.emit(50)
            
            # إنشاء نسخة احتياطية من قاعدة البيانات الحالية
            current_db_backup = f"{self.db_path}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, current_db_backup)
            
            # استعادة قاعدة البيانات
            self.status.emit("استعادة قاعدة البيانات...")
            restored_db_path = os.path.join(temp_dir, 'database.db')
            if os.path.exists(restored_db_path):
                shutil.copy2(restored_db_path, self.db_path)
            else:
                raise Exception("ملف قاعدة البيانات غير موجود في النسخة الاحتياطية")
            
            self.progress.emit(70)
            
            # استعادة الملفات الإضافية
            self.status.emit("استعادة الملفات الإضافية...")
            
            # استعادة ملف الإعدادات
            config_path = os.path.join(temp_dir, 'config.py')
            if os.path.exists(config_path):
                shutil.copy2(config_path, 'config.py')
            
            # استعادة مجلد الموارد
            resources_path = os.path.join(temp_dir, 'resources')
            if os.path.exists(resources_path):
                if os.path.exists('resources'):
                    shutil.rmtree('resources')
                shutil.copytree(resources_path, 'resources')
            
            self.progress.emit(90)
            
            # تنظيف الملفات المؤقتة
            shutil.rmtree(temp_dir)
            
            self.progress.emit(100)
            self.finished.emit(True, "تم استعادة النسخة الاحتياطية بنجاح")
            
        except Exception as e:
            logging.error(f"خطأ في الاستعادة: {str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            self.finished.emit(False, f"فشل في الاستعادة: {str(e)}")


class BackupManager:
    """مدير النسخ الاحتياطية"""
    
    def __init__(self, language='ar'):
        self.language = language
        self.db_manager = DatabaseManager()
        self.auto_backup_enabled = False
        self.backup_interval = 24  # ساعات
        self.backup_location = "backups"
        self.scheduler_thread = None
        
        # إنشاء مجلد النسخ الاحتياطية
        os.makedirs(self.backup_location, exist_ok=True)
        
        # تحميل الإعدادات
        self.load_settings()
    
    def load_settings(self):
        """تحميل إعدادات النسخ الاحتياطي"""
        try:
            settings = self.db_manager.cursor.execute(
                "SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'backup_%'"
            ).fetchall()
            
            for key, value in settings:
                if key == 'backup_auto_enabled':
                    self.auto_backup_enabled = value.lower() == 'true'
                elif key == 'backup_interval':
                    self.backup_interval = int(value)
                elif key == 'backup_location':
                    self.backup_location = value
                    
        except Exception as e:
            logging.warning(f"تعذر تحميل إعدادات النسخ الاحتياطي: {str(e)}")
    
    def save_settings(self):
        """حفظ إعدادات النسخ الاحتياطي"""
        try:
            settings = {
                'backup_auto_enabled': str(self.auto_backup_enabled).lower(),
                'backup_interval': str(self.backup_interval),
                'backup_location': self.backup_location
            }
            
            for key, value in settings.items():
                self.db_manager.cursor.execute(
                    "INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)",
                    (key, value)
                )
            
            self.db_manager.connection.commit()
            
        except Exception as e:
            logging.error(f"فشل في حفظ إعدادات النسخ الاحتياطي: {str(e)}")
    
    def create_backup(self, backup_path=None, include_files=True, parent=None):
        """إنشاء نسخة احتياطية"""
        if not backup_path:
            backup_path, _ = QFileDialog.getSaveFileName(
                parent,
                tr('save_backup', self.language),
                f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                "Backup Files (*.zip)"
            )
            
            if not backup_path:
                return False
        
        # إنشاء نافذة التقدم
        progress_dialog = QProgressDialog(
            tr('creating_backup', self.language),
            tr('cancel', self.language),
            0, 100,
            parent
        )
        progress_dialog.setWindowTitle(tr('backup', self.language))
        progress_dialog.setModal(True)
        progress_dialog.show()
        
        # إنشاء خيط العمل
        worker = BackupWorker(backup_path, self.db_manager.db_path, include_files)
        
        # ربط الإشارات
        worker.progress.connect(progress_dialog.setValue)
        worker.status.connect(progress_dialog.setLabelText)
        worker.finished.connect(lambda success, msg: self._on_backup_finished(
            success, msg, progress_dialog, parent
        ))
        
        # بدء العمل
        worker.start()
        
        return True
    
    def _on_backup_finished(self, success, message, progress_dialog, parent):
        """معالجة انتهاء النسخ الاحتياطي"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(
                parent,
                tr('success', self.language),
                message
            )
            logging.info(f"تم إنشاء نسخة احتياطية: {message}")
        else:
            QMessageBox.critical(
                parent,
                tr('error', self.language),
                message
            )
            logging.error(f"فشل النسخ الاحتياطي: {message}")
    
    def restore_backup(self, backup_path=None, parent=None):
        """استعادة نسخة احتياطية"""
        if not backup_path:
            backup_path, _ = QFileDialog.getOpenFileName(
                parent,
                tr('select_backup_file', self.language),
                "",
                "Backup Files (*.zip)"
            )
            
            if not backup_path:
                return False
        
        # تحذير المستخدم
        reply = QMessageBox.warning(
            parent,
            tr('warning', self.language),
            tr('backup_warning', self.language),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        # إنشاء نافذة التقدم
        progress_dialog = QProgressDialog(
            tr('restoring_backup', self.language),
            tr('cancel', self.language),
            0, 100,
            parent
        )
        progress_dialog.setWindowTitle(tr('restore_backup', self.language))
        progress_dialog.setModal(True)
        progress_dialog.show()
        
        # إنشاء خيط العمل
        worker = RestoreWorker(backup_path, self.db_manager.db_path)
        
        # ربط الإشارات
        worker.progress.connect(progress_dialog.setValue)
        worker.status.connect(progress_dialog.setLabelText)
        worker.finished.connect(lambda success, msg: self._on_restore_finished(
            success, msg, progress_dialog, parent
        ))
        
        # بدء العمل
        worker.start()
        
        return True
    
    def _on_restore_finished(self, success, message, progress_dialog, parent):
        """معالجة انتهاء الاستعادة"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(
                parent,
                tr('success', self.language),
                message + "\n" + tr('restart_required', self.language)
            )
            logging.info(f"تم استعادة النسخة الاحتياطية: {message}")
        else:
            QMessageBox.critical(
                parent,
                tr('error', self.language),
                message
            )
            logging.error(f"فشلت الاستعادة: {message}")
    
    def start_auto_backup(self):
        """بدء النسخ الاحتياطي التلقائي"""
        if not self.auto_backup_enabled:
            return
        
        # إيقاف الجدولة السابقة
        self.stop_auto_backup()
        
        # جدولة النسخ الاحتياطي
        schedule.every(self.backup_interval).hours.do(self._auto_backup_job)
        
        # بدء خيط المجدول
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logging.info(f"تم بدء النسخ الاحتياطي التلقائي كل {self.backup_interval} ساعة")
    
    def stop_auto_backup(self):
        """إيقاف النسخ الاحتياطي التلقائي"""
        schedule.clear()
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread = None
        
        logging.info("تم إيقاف النسخ الاحتياطي التلقائي")
    
    def _run_scheduler(self):
        """تشغيل المجدول"""
        while self.auto_backup_enabled:
            schedule.run_pending()
            time.sleep(60)  # فحص كل دقيقة
    
    def _auto_backup_job(self):
        """مهمة النسخ الاحتياطي التلقائي"""
        try:
            backup_filename = f"auto_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            backup_path = os.path.join(self.backup_location, backup_filename)
            
            # إنشاء النسخة الاحتياطية
            worker = BackupWorker(backup_path, self.db_manager.db_path, True)
            worker.run()  # تشغيل مباشر بدون واجهة
            
            logging.info(f"تم إنشاء نسخة احتياطية تلقائية: {backup_path}")
            
            # تنظيف النسخ القديمة
            self._cleanup_old_backups()
            
        except Exception as e:
            logging.error(f"فشل النسخ الاحتياطي التلقائي: {str(e)}")
    
    def _cleanup_old_backups(self, keep_count=10):
        """تنظيف النسخ الاحتياطية القديمة"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_location):
                if filename.startswith('auto_backup_') and filename.endswith('.zip'):
                    file_path = os.path.join(self.backup_location, filename)
                    backup_files.append((file_path, os.path.getctime(file_path)))
            
            # ترتيب حسب تاريخ الإنشاء
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # حذف النسخ الزائدة
            for file_path, _ in backup_files[keep_count:]:
                os.remove(file_path)
                logging.info(f"تم حذف النسخة الاحتياطية القديمة: {file_path}")
                
        except Exception as e:
            logging.error(f"فشل في تنظيف النسخ القديمة: {str(e)}")
    
    def get_backup_list(self):
        """الحصول على قائمة النسخ الاحتياطية"""
        backups = []
        
        try:
            for filename in os.listdir(self.backup_location):
                if filename.endswith('.zip'):
                    file_path = os.path.join(self.backup_location, filename)
                    file_stats = os.stat(file_path)
                    
                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'size': file_stats.st_size,
                        'created_at': datetime.datetime.fromtimestamp(file_stats.st_ctime),
                        'is_auto': filename.startswith('auto_backup_')
                    })
            
            # ترتيب حسب تاريخ الإنشاء
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logging.error(f"فشل في الحصول على قائمة النسخ الاحتياطية: {str(e)}")
        
        return backups
    
    def delete_backup(self, backup_path):
        """حذف نسخة احتياطية"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logging.info(f"تم حذف النسخة الاحتياطية: {backup_path}")
                return True
        except Exception as e:
            logging.error(f"فشل في حذف النسخة الاحتياطية: {str(e)}")
        
        return False
    
    def validate_backup(self, backup_path):
        """التحقق من صحة النسخة الاحتياطية"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # فحص قائمة الملفات
                file_list = zipf.namelist()
                
                # التحقق من وجود الملفات المطلوبة
                required_files = ['database.db', 'backup_info.json']
                for required_file in required_files:
                    if required_file not in file_list:
                        return False, f"الملف المطلوب مفقود: {required_file}"
                
                # فحص ملف المعلومات
                backup_info_data = zipf.read('backup_info.json')
                backup_info = json.loads(backup_info_data.decode('utf-8'))
                
                # التحقق من البيانات المطلوبة
                required_keys = ['created_at', 'version', 'backup_type']
                for key in required_keys:
                    if key not in backup_info:
                        return False, f"معلومة مفقودة في ملف المعلومات: {key}"
                
                return True, "النسخة الاحتياطية صحيحة"
                
        except zipfile.BadZipFile:
            return False, "ملف النسخة الاحتياطية تالف"
        except json.JSONDecodeError:
            return False, "ملف معلومات النسخة الاحتياطية تالف"
        except Exception as e:
            return False, f"خطأ في فحص النسخة الاحتياطية: {str(e)}"
