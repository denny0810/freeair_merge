from collections import defaultdict
from typing import Dict, List

from logger import logger

from .format import clean_node, parse_server_field


def extract_hy1_style(data: dict) -> Dict[str, List[Dict]]:
    """
    解析 Hysteria 1 協議配置文件（.json 格式）
    """
    # Hysteria 1 的單節點配置通常是整個 dict 本身就是一個節點
    if not isinstance(data, dict):
        logger.warning(" ⚠️ hysteria解析失败: 输入数据不是字典")
        return {}

    # 檢查是否包含 Hysteria 1 關鍵字段
    # if "server" not in data or "auth_str" not in data:
    #     return

    result: Dict[str, List[Dict]] = defaultdict(list)

    # 轉換成 mihomo (Clash Meta) 兼容的 hysteria 節點格式
    server_raw = data.get("server")
    normalized_ip, port_str = parse_server_field(server_raw)
    node_name = f"{normalized_ip}"
    final_port = str(data.get("port") or data.get("ports") or port_str or "443")
    node = {
        # "name": f"hysteria_{len(nodes_dict['hysteria']) + 1}",  # 自動生成名稱
        "name": node_name,
        "type": "hysteria",
        "server": normalized_ip,
        # "port": final_port,
        "auth_str": data.get("auth_str"),
        "sni": data.get("server_name"),
        "skip-cert-verify": data.get("insecure", True),
        "alpn": [data.get("alpn")]
        if isinstance(data.get("alpn"), str)
        else data.get("alpn"),
        "protocol": data.get("protocol", "udp"),
        "up": f"{data.get('up_mbps', 10)} Mbps",
        "down": f"{data.get('down_mbps', 50)} Mbps",
        # 可選字段
        "recv-window-conn": data.get("recv_window_conn"),
        "recv-window": data.get("recv_window"),
        "disable-mtu-discovery": data.get("disable_mtu_discovery"),
    }
    if "," in final_port or "-" in final_port:
        node["ports"] = final_port
    else:
        node["port"] = final_port
    # 清理 None 值
    cleaned_node = clean_node(node)
    result["hysteria"].append(cleaned_node)
    return dict(result)


def extract_hy2_style(data: dict) -> Dict[str, List[Dict]]:
    """
    解析 Hysteria2 協議配置文件（.json 格式）
    """
    if not isinstance(data, dict):
        logger.warning(" ⚠️ hysteria2解析失败: 输入数据不是字典")
        return {}

    # 關鍵字段檢查
    # if "server" not in data or "auth" not in data:
    #     return

    # 使用 defaultdict 避免 KeyError
    result: Dict[str, List[Dict]] = defaultdict(list)
    # server_raw = str(data.get("server", "")).strip()
    server_raw = data.get("server")
    normalized_ip, port_str = parse_server_field(server_raw)
    # 如果原始配置有獨立 port 字段，優先使用它
    final_port = str(data.get("port") or data.get("ports") or port_str or "443")
    node_name = f"{normalized_ip}"
    # 構建標準 mihomo Hysteria2 節點
    node = {
        # "name": f"hysteria2_{len(nodes_dict['hysteria2']) + 1}",
        "name": node_name,
        "type": "hysteria2",
        "server": normalized_ip,
        # "port": final_port,
        "password": data.get("auth"),
        "sni": data.get("tls", {}).get("sni"),
        "skip-cert-verify": data.get("tls", {}).get("insecure", True),
        "alpn": ["h3"],
        "up": data.get("bandwidth", {}).get("up", "10 Mbps"),
        "down": data.get("bandwidth", {}).get("down", "50 Mbps"),
    }
    if "," in final_port or "-" in final_port:
        node["ports"] = final_port
    else:
        node["port"] = final_port
    # 可選字段
    if "obfs" in data and data.get("obfs"):
        node["obfs"] = data.get("obfs")
    if "quic" in data:
        node["quic"] = data.get("quic")

    # 清理空值
    cleaned_node = clean_node(node)
    result["hysteria2"].append(cleaned_node)
    return dict(result)
