from typing import Any, Tuple


def parse_server_field(server_field: Any) -> Tuple[str, str]:
    """
    解析服务器字段，返回 (host: str, port: str) 元组。

    - IPv6 地址会去除方括号
    - 端口始终返回字符串
    - 支持单端口、端口范围（如 5000-6000）、逗号分隔的多端口
    """
    if not server_field:
        return "", ""

    s = str(server_field).strip()
    if not s:
        return "", ""

    # 统计冒号数量，作为第一层分流
    colon_count = s.count(":")

    # 情况 1: 冒号数量 > 1，IPv6 相关
    # IPv4 和域名最多只有 1 个冒号，因此冒号数量 > 1 必定是 IPv6
    if colon_count > 1:
        # 如果首字符不是 "["，视为纯 IPv6 地址
        # （不带 [] 的 IPv6:Port 是非法格式，无法区分，直接视为纯 IP）
        if not s.startswith("["):
            return s, ""

        # 标准格式 [IPv6]:Port，查找第一个 ']' 的位置
        close_bracket_idx = s.find("]")
        if close_bracket_idx == -1:
            # 非法格式：有开括号没闭括号，去除 '[' 后视为纯 IP
            return s[1:], ""

        # 提取 IP 部分（去除方括号）
        ip_part = s[1:close_bracket_idx]
        rest = s[close_bracket_idx + 1 :]

        # 检查 ']' 后面是否有 ':'
        # 如果有，后面全是端口；如果没有，就是纯 IP
        if rest.startswith(":"):
            return ip_part, rest[1:]
        return ip_part, ""

    # 情况 2: 冒号数量 == 1，IPv4:端口 或 域名:端口
    if colon_count == 1:
        ip_part, port_part = s.split(":", 1)
        return ip_part.strip(), port_part.strip()

    # 情况 3: 冒号数量 == 0，纯 IPv4 或纯域名
    return s, ""


def clean_node(node: dict) -> dict:
    """清理節點字典中的 None 和空字符串"""
    return {k: v for k, v in node.items() if v is not None and v != ""}
