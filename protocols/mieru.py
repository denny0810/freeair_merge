from collections import defaultdict
from typing import Dict, List

from logger import logger

from .format import clean_node, parse_server_field


def extract_mieru_style(data: dict) -> Dict[str, List[Dict]]:
    """
    解析 Mieru 協議配置文件（.json 格式）
    （支援多 profiles，但只提取 activeProfile）
    """
    if not isinstance(data, dict):
        logger.warning(" ⚠️ mieru解析失败: 输入数据不是字典")
        return {}

    # 使用 defaultdict 避免 KeyError
    result: Dict[str, List[Dict]] = defaultdict(list)

    # 獲取活躍配置
    active_profile_name = data.get("activeProfile", "default")
    profiles = data.get("profiles", [])

    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        if profile.get("profileName") != active_profile_name:
            continue

        # 提取 user 資訊
        user = profile.get("user", {})
        username = user.get("name", "")
        password = user.get("password", "")

        # 提取 servers（通常只有一個）
        servers = profile.get("servers", [])
        for server in servers:
            if not isinstance(server, dict):
                continue

            ip = server.get("ipAddress") or server.get("domainName")
            if not ip:
                continue

            normalized_ip, port_str = parse_server_field(ip)

            # portBindings 通常只有一項
            port_bindings = server.get("portBindings")
            if not port_bindings:
                continue

            final_port = str(port_bindings[0].get("port") or port_str)
            transport = port_bindings[0].get("protocol", "TCP").upper()
            node_name = f"{normalized_ip}"

            # 構建 mihomo 兼容的 Mieru 節點格式
            node = {
                # "name": f"mieru_{len(nodes_dict['mieru']) + 1}",
                "name": node_name,
                "type": "mieru",
                "server": normalized_ip,
                "port": final_port,
                "username": username,
                "password": password,
                # "protocol": protocol,
                "mtu": profile.get("mtu", 1400),
                # Mieru 常用額外參數（可根據實際需要調整）
                "transport": transport,
                "skip-cert-verify": True,  # Mieru 通常不需要驗證
            }

            # 清理空值
            cleaned_node = clean_node(node)
            result["mieru"].append(cleaned_node)

        # 通常一個配置文件只處理一個 activeProfile，處理完即可跳出
        break

    return dict(result)
