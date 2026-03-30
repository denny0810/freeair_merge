import json
import os
from typing import Dict, List

import yaml
from config import NODES_DIR
from logger import logger
from protocols import (
    extract_clash_meta_style,
    extract_hy1_style,
    extract_hy2_style,
    extract_mieru_style,
    extract_singbox_style,
    extract_xray_style,
)


def parse_all_nodes() -> Dict[str, List[Dict]]:
    """
    遍歷 node/ 目錄下所有協議資料夾，解析裡面的配置文件
    返回統一的 nodes_dict
    """
    # nodes_dict: Dict[str, List[Dict]] = {
    #     "vmess": [],
    #     "vless": [],
    #     "trojan": [],
    #     "ss": [],
    #     "ssr": [],
    #     "hysteria": [],
    #     "hysteria2": [],
    #     "tuic": [],
    #     "shadowsocks": [],
    #     "mieru": [],
    # }
    nodes_dict: dict[str, List[Dict]] = {}

    protocol_handlers = {
        "clash": extract_clash_meta_style,
        "clash.meta": extract_clash_meta_style,
        "xray": extract_xray_style,
        "v2ray": extract_xray_style,
        "singbox": extract_singbox_style,
        "hysteria": extract_hy1_style,
        "hysteria2": extract_hy2_style,
        "mieru": extract_mieru_style,
    }

    # 遍歷每個協議資料夾
    for folder_name in os.listdir(NODES_DIR):
        protocol_path = os.path.join(NODES_DIR, folder_name)
        if not os.path.isdir(protocol_path):
            continue

        # logger.info(f"处理节点文件夹：\{folder_name}")
        handler = protocol_handlers.get(folder_name.lower())

        for filename in os.listdir(protocol_path):
            file_path = os.path.join(protocol_path, filename)
            if not os.path.isfile(file_path):
                continue

            logger.info(f"   解析文件：\\{folder_name}\\{filename}")

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                if not content:
                    continue
                if content.startswith("{") or content.startswith("["):
                    data = json.loads(content)
                else:
                    data = yaml.safe_load(content)

                if not data:
                    continue

                if handler:
                    extracted = handler(data) or {}
                    if isinstance(extracted, dict):
                        for protocol, node_list in extracted.items():
                            if not isinstance(node_list, list):
                                continue
                            if protocol not in nodes_dict:
                                nodes_dict[protocol] = []
                            nodes_dict[protocol].extend(node_list)
                    elif isinstance(extracted, list):
                        nodes_dict[folder_name.lower()].extend(extracted)
                    else:
                        logger.warning(
                            f" ⚠️ 解析器返回类型不支持: {type(extracted).__name__}"
                        )
                else:
                    logger.warning(f" ⚠️ 未知协议文件夹 '{folder_name}'")

            except Exception as e:
                logger.error(
                    f" ❌ 解析失败 \\{folder_name}\\{filename}: {type(e).__name__} - {e}"
                )
    return nodes_dict
