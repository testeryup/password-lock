# services/log_service.py
import json
import os
from datetime import datetime
from state_manager import StateManager

class LogService:
    def __init__(self, state_manager=None, log_file="door_access.log"):
        self.state_manager = state_manager or StateManager()
        self.log_file = log_file
        
        # Đảm bảo file log tồn tại
        if not os.path.exists(log_file):
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("# Nhật ký truy cập hệ thống khoá cửa\n")
    
    def log_entry(self, action, details=""):
        """Thêm một bản ghi vào nhật ký"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details,
        }
        
        # Thêm vào state manager
        self.state_manager.access_log.append(log_entry)
        
        # Ghi vào file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {action} | {details}\n")
        
        return log_entry
    
    def get_recent_logs(self, limit=10):
        """Lấy các bản ghi gần đây nhất"""
        return self.state_manager.access_log[-limit:] if self.state_manager.access_log else []
    
    def clear_logs(self):
        """Xóa toàn bộ nhật ký (chỉ dành cho admin)"""
        self.state_manager.access_log = []
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("# Nhật ký truy cập hệ thống khoá cửa\n")
        
        return {"status": "success", "message": "Đã xóa toàn bộ nhật ký"}