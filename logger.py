import os
from datetime import datetime

from config import OUTPUT_DIR


class Logger:
    def __init__(self, name: str = "mihomo"):
        """
        初始化日志器
        - 自動在 log/ 目錄下創建以時間戳命名的日志檔案
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(OUTPUT_DIR, f"{name}_{timestamp}.log")
        self.name = name
        self._console = True  # 是否同時打印到控制台

        self.info(f"日志系統初始化完成 → {self.log_file}")

    def log(self, message: str, level: str = "INFO"):
        """核心日志方法"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"

        # 輸出到控制台
        if self._console:
            print(line)

        # 寫入日志檔案
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            print(f"[ERROR] 寫入日志失敗: {e}")

    # 常用快捷方法
    def info(self, message: str):
        self.log(message, "INFO")

    def success(self, message: str):
        self.log(message, "SUCCESS")

    def warning(self, message: str):
        self.log(message, "WARNING")

    def error(self, message: str):
        self.log(message, "ERROR")

    def debug(self, message: str):
        self.log(message, "DEBUG")

    def disable_console(self):
        """禁用控制台輸出（僅寫檔案）"""
        self._console = False

    def enable_console(self):
        """啟用控制台輸出"""
        self._console = True


# ====================== 全局實例 ======================
# 在整個專案中統一使用這個 logger
logger = Logger(name="mihomo")
