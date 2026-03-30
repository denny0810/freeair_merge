from collections import defaultdict
from typing import Dict, List

from logger import logger

from .format import parse_server_field


def extract_clash_meta_style(data: dict) -> Dict[str, List[Dict]]:
    """
    解析 Clash Meta / Mihomo 格式的 proxies 列表
    """
    proxies = data.get("proxies") or data.get("Proxy") or data.get("proxies-list") or []

    if not isinstance(proxies, list):
        logger.warning(" ⚠️ clash.meta解析失败: 输入数据不是字典")
        return {}

    # 使用 defaultdict 避免 KeyError
    result: Dict[str, List[Dict]] = defaultdict(list)

    for proxy in proxies:
        if not isinstance(proxy, dict):
            continue

        ptype = str(proxy.get("type", "")).lower().strip()

        if "server" in proxy:
            normalized_ip, port_str = parse_server_field(proxy["server"])
            proxy["server"] = normalized_ip

            final_port = str(
                proxy.get("port") or proxy.get("ports") or port_str or "443"
            )
            proxy["port"] = final_port

        # 規範化協議名稱，統一存入對應的 key
        if ptype == "tuic":
            result["tuic"].append(proxy)
        elif ptype == "hysteria":
            result["hysteria"].append(proxy)
        elif ptype == "hysteria2":
            result["hysteria2"].append(proxy)
        elif ptype in ["vless", "vmess", "trojan", "ss", "ssr", "mieru", "wireguard"]:
            result[ptype].append(proxy)
        elif ptype in ["shadowsocks", "ss"]:
            result["ss"].append(proxy)
        else:
            # 未知類型
            logger.warning(f" ⚠️ 未知节点类型: {ptype}，已忽略")
            continue

    return dict(result)
