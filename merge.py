import os
import shutil
import sys
from typing import Dict, List

import yaml
from config import NODES_DIR, OUTPUT_DIR, TEMPLATE_PATH
from fetch import fetch_nodes
from logger import logger
from parse import parse_all_nodes


def normalize_node_names(nodes_dict: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    為所有節點名稱加上協議縮寫前綴，避免名稱衝突
    """
    seen = set()  # 用來記錄已經出現過的名稱

    prefix_map = {
        "vmess": "vmess",
        "vless": "vless",
        "trojan": "trojan",
        "ss": "ss",
        "hysteria": "hy",
        "hysteria2": "hy2",
        "tuic": "tuic",
        "mieru": "mieru",
        "shadowsocks": "ss",
    }

    for protocol, node_list in nodes_dict.items():
        prefix = prefix_map.get(protocol, protocol[:4])

        for i, node in enumerate(node_list):
            original_name = str(node.get("name", "")).strip()

            if not original_name or original_name == "None":
                base_name = f"{prefix}_{i + 1}"
            else:
                # 清理不合法字符並加上前綴
                # clean_name = re.sub(r'[\[\]\/\\:;*?"<>|]', "_", original_name)
                # new_name = f"{prefix}_{clean_name}"
                base_name = f"{prefix}_{original_name}"
            new_name = base_name
            counter = 1
            while new_name in seen:
                new_name = f"{base_name}_{counter}"
                counter += 1

            node["name"] = new_name
            seen.add(new_name)

    return nodes_dict


def deduplicate_nodes(nodes_dict: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    對所有節點進行去重，判斷依據：server + port
    返回去重後的 nodes_dict
    """
    seen = set()
    deduped: Dict[str, List[Dict]] = {k: [] for k in nodes_dict.keys()}

    total_count = 0
    duplicate_count = 0

    for protocol, node_list in nodes_dict.items():
        for node in node_list:
            total_count += 1

            server = str(node.get("server", "")).strip()
            port = str(node.get("port", "")).strip()

            # 去重鍵：server:port
            key = f"{server}:{port}"

            if key in seen:
                duplicate_count += 1
                continue

            seen.add(key)
            deduped[protocol].append(node)

    logger.success(
        f"去重完成！原始節點數: {total_count}，重複節點數: {duplicate_count}，去重後: {total_count - duplicate_count}"
    )
    return deduped


def merge_to_yaml(nodes_dict: Dict[str, List[Dict]]):
    """
    讀取 clash_template.yaml，將節點正確合併
    """
    if not os.path.exists(TEMPLATE_PATH):
        logger.error(f" ❌ 錯誤：模板檔案不存在 → {TEMPLATE_PATH}")
        raise FileNotFoundError(f"模板檔案不存在：{TEMPLATE_PATH}")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = yaml.safe_load(f)

    # 收集所有去重後的節點
    all_proxies = []
    for protocol_nodes in nodes_dict.values():
        all_proxies.extend(protocol_nodes)

    # 1. 處理 proxies 字段（完整節點）
    if "proxies" not in template or template["proxies"] is None:
        template["proxies"] = []
    # template["proxies"].clear()  # 清空模板中原有的示例節點
    template["proxies"].extend(all_proxies)

    # 2. 處理 proxy-groups 中的 "自动选择" 組（只放名稱）
    for group in template.get("proxy-groups", []):
        if group.get("name") == "自动选择" and group.get("type") in [
            "url-test",
            "fallback",
            "select",
        ]:
            # 只保留節點名稱
            group["proxies"] = [
                node.get("name") for node in all_proxies if node.get("name")
            ]

    output_path = os.path.join(OUTPUT_DIR, "merged_config.yaml")

    # 寫入 YAML
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            template,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        )

    # 建立時間戳空檔案
    # timestamp_file = datetime.now().strftime("%Y-%m-%d-%H%M") + ".txt"
    # open(os.path.join(OUTPUT_DIR, timestamp_file), "w").close()

    logger.success(f" ✅ 完成输出！最終有效節點數：{len(all_proxies)}")

    return


def clear_dirs():
    """
    清空文件夹
    """
    for d in [NODES_DIR, OUTPUT_DIR]:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(f"清除 {d} 失敗：{e}")
                return
        os.makedirs(d, exist_ok=True)
    return


def main():
    clear_dirs()
    if not fetch_nodes():
        logger.error(" ❌ 节点文件下载失败，终止")
        sys.exit(1)

    extred_nodes = parse_all_nodes()
    deduped_nodes = deduplicate_nodes(extred_nodes)
    normalized_nodes = normalize_node_names(deduped_nodes)
    merge_to_yaml(normalized_nodes)


if __name__ == "__main__":
    main()
