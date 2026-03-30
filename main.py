import os
import shutil
import sys

from config import LOG_DIR, NODES_DIR, OUTPUT_DIR

# import time
from fetch import fetch_nodes

# ------------------------------
# 日誌相關設定與函式
# ------------------------------


# ==================== 清空文件夹 ====================
def clear_dirs(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"清除 {path} 失敗：{e}")
            return
    os.makedirs(path, exist_ok=True)
    return


if __name__ == "__main__":
    # 清空历史文件夹
    print("清除资料夹...")
    for d in [LOG_DIR, NODES_DIR, OUTPUT_DIR]:
        clear_dirs(d)

    if not fetch_nodes():
        sys.exit(0)
