from collections import defaultdict
from typing import Dict, List

from logger import logger

from .format import clean_node, parse_server_field


def extract_singbox_style(data: dict) -> Dict[str, List[Dict]]:
    """
    解析 sing-box 配置檔案（.json 格式）
    """
    if not isinstance(data, dict):
        logger.warning(" ⚠️ singbox解析失败: 输入数据不是字典")
        return {}

    # 使用 defaultdict 避免 KeyError
    result: Dict[str, List[Dict]] = defaultdict(list)

    outbounds = data.get("outbounds", [])
    if not isinstance(outbounds, list):
        logger.warning("  ⚠️ singbox解析失败: outbounds 不是列表")
        return dict(result)

    for outbound in outbounds:
        if not isinstance(outbound, dict):
            continue

        ob_type = str(outbound.get("type", "")).lower()
        normalized_ip, port_str = parse_server_field(outbound.get("server"))
        node_name = f"{normalized_ip}"
        final_port = str(outbound.get("server_port") or port_str or "443")
        node = None

        # ==================== TUIC 協議 ====================
        if ob_type == "tuic":
            node = {
                # "name": outbound.get("tag") or f"tuic_{len(nodes_dict['tuic']) + 1}",
                "name": node_name,
                "type": "tuic",
                "server": normalized_ip,
                "port": final_port,
                "uuid": outbound.get("uuid"),
                "password": outbound.get("password"),
                "congestion-controller": outbound.get("congestion_control", "bbr"),
                "sni": outbound.get("tls", {}).get("server_name"),
                "alpn": outbound.get("tls", {}).get("alpn", ["h3"]),
                "skip-cert-verify": outbound.get("tls", {}).get("insecure", True),
                "udp-relay-mode": "native",  # sing-box tuic 預設推薦值
            }

        # ==================== 其他常見協議（可後續擴展） ====================
        elif ob_type == "vless":
            node = {
                # "name": outbound.get("tag") or f"vless_{len(nodes_dict['vless']) + 1}",
                "name": node_name,
                "type": "vless",
                "server": normalized_ip,
                "port": final_port,
                "uuid": outbound.get("uuid"),
                "network": outbound.get("network", "tcp"),
                "tls": outbound.get("tls", {}).get("enabled", False),
                "sni": outbound.get("tls", {}).get("server_name"),
                "skip-cert-verify": outbound.get("tls", {}).get("insecure", False),
                "client-fingerprint": outbound.get("tls", {})
                .get("utls", {})
                .get("fingerprint"),
                # Reality 支持（如果有）
                "reality-opts": outbound.get("reality")
                or outbound.get("tls", {}).get("reality"),
            }

        elif ob_type == "trojan":
            node = {
                # "name": outbound.get("tag")
                # or f"trojan_{len(nodes_dict['trojan']) + 1}",
                "name": node_name,
                "type": "trojan",
                "server": normalized_ip,
                "port": final_port,
                "password": outbound.get("password"),
                "sni": outbound.get("tls", {}).get("server_name"),
                "skip-cert-verify": outbound.get("tls", {}).get("insecure", True),
            }

        elif ob_type in ["shadowsocks", "ss"]:
            node = {
                # "name": outbound.get("tag") or f"ss_{len(nodes_dict['ss']) + 1}",
                "name": node_name,
                "type": "ss",
                "server": normalized_ip,
                "port": final_port,
                "cipher": outbound.get("method") or outbound.get("cipher"),
                "password": outbound.get("password"),
            }

        elif ob_type == "hysteria":
            node = {
                "name": node_name,
                "type": "hysteria",
                "server": normalized_ip,
                "port": final_port,
                "auth-str": outbound.get("auth_str") or outbound.get("auth"),
                "up": outbound.get("up_mbps") or outbound.get("up"),
                "down": outbound.get("down_mbps") or outbound.get("down"),
                "obfs": outbound.get("obfs"),
                "sni": outbound.get("tls", {}).get("server_name"),
                "alpn": outbound.get("tls", {}).get("alpn"),
                "skip-cert-verify": outbound.get("tls", {}).get("insecure", True),
                "protocol": outbound.get("network") or "udp",
            }

        elif ob_type == "direct":
            pass
        # 可以繼續擴展 vmess、hysteria2、wireguard 等...
        else:
            if ob_type:  # 只打印有 type 的未知協議
                logger.warning(f" ⚠️ sing-box中outbounds类型: {ob_type} 未适配")

        # 清理空值並統一映射協議名稱
        if node:
            cleaned_node = clean_node(node)
            key = "ss" if ob_type in ["shadowsocks", "ss"] else ob_type
            result[key].append(cleaned_node)
            # logger.info(f"提取 sing-box {ob_type.upper()} 節點: {node_name}")

    return dict(result)
