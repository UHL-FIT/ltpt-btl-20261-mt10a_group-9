import sys
from utils.logger import setup_logger

logger = setup_logger("main")

def main() -> int:
    logger.info("Khởi động SmartAttend (Face Attendance - CTk) ...")
    # Lazy import để giảm thời gian load + entrypoint chỉ điều phối.
    from controllers.ctk_controller import chay_ung_dung
    chay_ung_dung()
    return 0

if __name__ == "__main__":
    sys.exit(main())

