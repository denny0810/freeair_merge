from typing import Any, Tuple


def parse_server_field(server_field: Any) -> Tuple[str, str]:
    """
    返回 (normalized_ip: str, port_str: str)
    - IPv6 去掉 []
    - port 永遠返回字符串
    - 支援單端口、純範圍（如 5000-6000）、帶逗號的多端口
    """
    if not server_field:
        return "", ""

    s = str(server_field).strip()
    if not s:
        return "", ""

    # 统计冒号数量，作为第一层分流
    colon_count = s.count(":")

    # ---------------------------------------------------------
    # 情况 1: 冒号数量 > 1
    # 肯定是 IPv6 相关（因为 IPv4 和域名最多只有 1 个冒号）
    # ---------------------------------------------------------
    if colon_count > 1 or "::" in s:
        # 1. 如果首字符不是 "["，肯定是纯 IPv6 地址
        #    (因为不带 [] 的 IPv6:Port 是非法的，无法区分，直接视为纯 IP)
        if not s.startswith("["):
            # return normalize_ip(s), ""
            return s, ""

        # 2. 如果首字符是 "["，则是标准格式 [IPv6]:Port
        #    查找第一个 ']' 的位置
        close_bracket_idx = s.find("]")
        if close_bracket_idx == -1:
            # 非法格式：有开括号没闭括号，视为纯 IP
            # return normalize_ip(s[1:]), ""
            return s[1:], ""

        # 提取 IP 部分（重新规范化）
        # normalized_ip = f"[{s[1:close_bracket_idx]}]"
        normalized_ip = s[1:close_bracket_idx]
        # 检查 ']' 后面是否有 ':'
        # 如果有，后面全是端口；如果没有，就是纯 IP
        if close_bracket_idx + 1 < len(s) and s[close_bracket_idx + 1] == ":":
            port_str = s[close_bracket_idx + 2 :]  # 截取 ']:' 之后的部分
            return normalized_ip, port_str
        else:
            return normalized_ip, ""

    # ---------------------------------------------------------
    # 情况 2: 冒号数量 == 1
    # 肯定是 IPv4:端口 或 域名:端口
    # ---------------------------------------------------------
    elif colon_count == 1:
        ip_part, port_part = s.split(":", 1)
        # return normalize_ip(ip_part.strip()), port_part.strip()
        return ip_part.strip(), port_part.strip()
    # ---------------------------------------------------------
    # 情况 3: 冒号数量 == 0
    # 肯定是纯 IPv4 或 纯域名
    # ---------------------------------------------------------
    else:
        # return normalize_ip(s), ""
        return s, ""


# def normalize_ip(ip: str) -> str:
#     """
#     规范化 IP：
#     - IPv6 去掉 []
#     - IPv4/域名 保持不变
#     """
#     s = str(ip).strip()
#     if not s:
#         return ""

#     # 如果已经包裹了，直接返回
#     if s.startswith("[") and s.endswith("]"):
#         return s[1:-1]

#     # 判断是否为 IPv6 (冒号数量 >= 2 或者 包含 ::)
#     # 注意：::1 只有一个冒号，所以必须检查 ::
#     if s.count(":") >= 2 or "::" in s:
#         return f"[{s}]"

#     return s


def clean_node(node: dict) -> dict:
    """清理節點字典中的 None 和空字符串"""
    return {k: v for k, v in node.items() if v is not None and v != ""}
