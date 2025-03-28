# config.py
# Cấu hình tổng quát cho hệ thống

# Cấu hình GPIO
GPIO_CONFIG = {
    "LED_LOCKED": 17,      # Đèn đỏ (cửa đóng)
    "LED_UNLOCKED": 27,    # Đèn xanh (cửa mở)
    "RELAY_PIN": 5,        # Relay điều khiển khoá
    "BUZZER_PIN": 22,      # Buzzer cảnh báo
    "REED_PIN": 4,         # Cảm biến cửa từ
    "KEYPAD_ROWS": [6, 13, 19, 26],  # Hàng của keypad
    "KEYPAD_COLS": [12, 16, 20, 21]  # Cột của keypad
}

# Cấu hình hệ thống
SYSTEM_CONFIG = {
    "PASSWORD": "1234",            # Mật khẩu mặc định
    "AUTO_LOCK_TIMEOUT": 20,       # Thời gian tự động khoá (giây)
    "MAX_ATTEMPTS": 3,             # Số lần nhập sai tối đa
    "LOCKOUT_DURATION": 30,        # Thời gian khoá sau khi nhập sai (giây)
    "LOG_FILE": "door_access.log", # File lưu nhật ký
    "WEB_PORT": 8000               # Port cho web app
}

# Cấu hình giao diện
UI_CONFIG = {
    "APP_TITLE": "Hệ Thống Khoá Cửa Thông Minh",
    "APP_WIDTH": 1000,
    "APP_HEIGHT": 800,
    "APP_BG_COLOR": (240, 240, 245),
    "REFRESH_RATE": 30    # FPS
}