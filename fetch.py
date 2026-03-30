import os
import re
from urllib.parse import urlparse

import requests

# import time
from config import NODES_DIR, URL_LIST_PATH
from logger import logger


def fetch_nodes():

    if not os.path.exists(URL_LIST_PATH):
        logger.error(f" ❌ 錯誤：{URL_LIST_PATH}不存在")
        return False

    with open(URL_LIST_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        logger.error(f" ❌ 錯誤：{URL_LIST_PATH}配置无效")
        return False

    current_dir = NODES_DIR
    download_success = 0
    download_failed = 0
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )

    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            current_dir = os.path.join(NODES_DIR, line[1:-1].strip())
            if not os.path.exists(current_dir):
                os.makedirs(current_dir, exist_ok=True)
            continue

        if line.startswith("http://") or line.startswith("https://"):
            url = line
            # log_message(log_file, f"嘗試下載 → {url}")
            logger.info(f"   下载: {url}")

            try:
                resp = session.get(line, timeout=15, allow_redirects=True)
                if resp.status_code != 200:
                    # log_message(log_file, f"下載失敗 → {url} 狀態碼 {resp.status_code}")
                    logger.error(f" ❌ {url}下载失败: {resp.status_code}")
                    download_failed += 1
                    continue

                filename = None
                cd = resp.headers.get("Content-Disposition")
                if cd:
                    m = re.search(r'filename="?([^";\r\n]+)"?', cd)
                    if m:
                        filename = m.group(1)

                if not filename:
                    parsed = urlparse(url)
                    raw_name = os.path.basename(parsed.path)
                    filename = raw_name.strip() if raw_name else "nodefile"

                # 移除常见非法字符
                # safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

                base, ext = os.path.splitext(filename)
                save_path = os.path.join(current_dir, filename)

                # 文件去重逻辑
                counter = 1
                while os.path.exists(save_path):
                    new_name = f"{base}_{counter}{ext}"
                    save_path = os.path.join(current_dir, new_name)
                    counter += 1

                with open(save_path, "wb") as f:
                    f.write(resp.content)

                # log_message(log_file, f"✔ 下载成功 → {save_path}")
                logger.success(f" ✔ 下载成功: {os.path.basename(save_path)}")
                download_success += 1

            except Exception as e:
                # log_message(log_file, f"✘ 下載異常 → {url}  → {type(e).__name__}: {e}")
                logger.error(f" ❌ {url}下载异常: {str(e)}")
                download_failed += 1

    # og_message(log_file, f"=== fetch_nodes 結束，共下載 {downloaded_count} 個檔案 ===")
    logger.info(f" ✔ 下载成功: {download_success}, ❌ 下载失败: {download_failed}")
    return True
