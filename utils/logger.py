import logging
import os
import sys

# Setup đối tượng ghi log
def setup_logger(name: str) -> logging.Logger:
    # Tạo biến lưu đối tượng ghi log
    logger = logging.getLogger(name)

    # Kiểm tra xem đối tượng này đã có đường kết nối chưa hay mới được tạo
    # handlers là list các đường kết nối của đối tượng ghi log
    if logger.handlers: return logger

    # Set message level cho đối tượng ghi log
    logger.setLevel(logging.INFO)

    # Set format cho log khi in ra:    Time       Message Level     Name       Message
    log_format = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    ''' Tạo handler kết nối đến terminal, hiển thị trên terminal đúng format 
        và gắn handler vào đối tượng ghi log '''
    terminal_handler = logging.StreamHandler(sys.stdout)
    terminal_handler.setFormatter(log_format)
    logger.addHandler(terminal_handler)

    # Tạo handler đến file, tương tự như terminal_handler
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(data_dir, "app.log"), encoding="utf-8")
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    except Exception as e: 
        logger.warning(f"Không thể tạo file handler!\nChi tiết lỗi: {e}")

    return logger

