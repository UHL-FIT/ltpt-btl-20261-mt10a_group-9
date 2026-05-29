import sys
from utils.logger import setup_logger
from controllers.ctk_controller import chay_ung_dung

# Tạo đối tượng ghi log
logger = setup_logger("main")

def main() -> int:
    logger.info("Khởi động hệ thống FaceAttend ...")
    chay_ung_dung()
    return 0

if __name__ == "__main__":
    sys.exit(main())

