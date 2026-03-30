from collections import defaultdict
from typing import Dict, List

from logger import logger

from .format import clean_node, parse_server_field


def extract_xray_style(data: dict) -> Dict[str, List[Dict]]:
    """
    解析 Xray / V2Ray 完整配置文件（.json 格式）
    """
    if not isinstance(data, dict):
        logger.warning(" ⚠️ xray解析失败: 输入数据不是字典")
        return {}

    # 使用 defaultdict 避免 KeyError
    result: Dict[str, List[Dict]] = defaultdict(list)

    outbounds = data.get("outbounds", [])
    if not isinstance(outbounds, list):
        logger.warning("  ⚠️ xray解析失败: outbounds 不是列表")
        return dict(result)

    for outbound in outbounds:
        if not isinstance(outbound, dict):
            continue

        protocol = str(outbound.get("protocol", "")).lower()
        tag = outbound.get("tag", "")
        node = None
        # ==================== VLESS (Reality + xhttp) ====================
        if protocol == "vless":
            settings = outbound.get("settings", {})
            vnext = settings.get("vnext", [])

            for v in vnext:
                if not isinstance(v, dict):
                    continue

                users = v.get("users", [])
                for user in users:
                    if not isinstance(user, dict):
                        continue

                    # node_name = tag or f"vless_{len(nodes_dict['vless']) + 1}"
                    normalized_ip, port_str = parse_server_field(v.get("address"))
                    final_port = str(v.get("port") or port_str or "443")
                    node_name = f"{normalized_ip}"
                    node = {
                        "name": node_name,
                        "type": "vless",
                        "server": normalized_ip,
                        "port": final_port,
                        "uuid": user.get("id"),
                        "flow": user.get("flow"),  # xtls-rprx-vision 等
                        "network": outbound.get("streamSettings", {}).get(
                            "network", "tcp"
                        ),
                        "security": outbound.get("streamSettings", {}).get(
                            "security", "none"
                        ),
                        "sni": outbound.get("streamSettings", {})
                        .get("realitySettings", {})
                        .get("serverName")
                        or outbound.get("streamSettings", {})
                        .get("tlsSettings", {})
                        .get("serverName"),
                        "skip-cert-verify": True,  # Reality 通常設為 true
                        "client-fingerprint": outbound.get("streamSettings", {})
                        .get("realitySettings", {})
                        .get("fingerprint")
                        or "chrome",
                        "reality-opts": {
                            "public-key": outbound.get("streamSettings", {})
                            .get("realitySettings", {})
                            .get("publicKey"),
                            "short-id": outbound.get("streamSettings", {})
                            .get("realitySettings", {})
                            .get("shortId"),
                        }
                        if outbound.get("streamSettings", {}).get("security")
                        == "reality"
                        else None,
                        "xhttp-opts": {
                            "path": outbound.get("streamSettings", {})
                            .get("xhttpSettings", {})
                            .get("path"),
                            "mode": outbound.get("streamSettings", {})
                            .get("xhttpSettings", {})
                            .get("mode", "auto"),
                        }
                        if outbound.get("streamSettings", {}).get("network") == "xhttp"
                        else None,
                    }
        # ==================== Hysteria 1 / 2 ====================
        elif protocol == "hysteria":
            settings = outbound.get("settings", {})
            stream_settings = outbound.get("streamSettings", {})
            hy_settings = stream_settings.get("hysteriaSettings", {})
            tls_settings = stream_settings.get("tlsSettings", {})

            # 判定版本
            version = settings.get("version") or hy_settings.get("version")

            normalized_ip, port_str = parse_server_field(settings.get("address"))
            final_port = str(
                settings.get("port") or settings.get("ports") or port_str or "443"
            )
            node_name = f"{normalized_ip}"

            if version == 2:
                node = {
                    "name": node_name,
                    "type": "hysteria2",
                    "server": normalized_ip,
                    # "port": final_port,
                    "password": hy_settings.get("auth"),
                    "sni": tls_settings.get("serverName"),
                    "skip-cert-verify": tls_settings.get("insecure", True),
                    "alpn": ["h3"],
                    "client-fingerprint": tls_settings.get("fingerprint"),
                    "up": hy_settings.get("up_mbps"),  # 如果配置中有带宽限制
                    "down": hy_settings.get("down_mbps"),
                }
            elif version == 1:
                # Hysteria 1 逻辑
                node = {
                    "name": node_name,
                    "type": "hysteria",
                    "server": normalized_ip,
                    # "port": final_port,
                    "auth_str": hy_settings.get("auth"),
                    "up": hy_settings.get("up_mbps"),
                    "down": hy_settings.get("down_mbps"),
                    "sni": tls_settings.get("serverName"),
                    "alpn": tls_settings.get("alpn", ["h3"]),
                    "protocol": hy_settings.get("protocol", "udp"),
                }
            else:
                logger.warning(f" ⚠️ Xray中协议: {protocol}版本未知 - {version}")
                continue

            if "," in final_port or "-" in final_port:
                node["ports"] = final_port
            else:
                node["port"] = final_port
        # ==================== VMess (如果未來有樣本可擴展) ====================
        # elif protocol == "vmess":
        #     pass

        # ==================== Trojan (如果未來有樣本可擴展) ====================
        # elif protocol == "trojan":
        #     pass
        else:
            if protocol and protocol not in ["freedom", "blackhole", "dns", "loopback"]:
                logger.warning(f" ⚠️ Xray中协议: {protocol} (tag: {tag}) 未适配")

        # 清理空值並統一映射協議名稱
        if node:
            cleaned_node = clean_node(node)
            key = node.get("type", protocol)
            if key in ["shadowsocks", "ss"]:
                key = "ss"
            result[key].append(cleaned_node)
            # logger.info(f"  提取 Xray 节点: {node_name}")

    return dict(result)
