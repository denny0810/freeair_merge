import os

# ==================== 路径定义 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LOG_DIR    = os.path.join(BASE_DIR, "log")
NODES_DIR = os.path.join(BASE_DIR, "nodes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMPLATE_PATH = os.path.join(BASE_DIR, "clash_template.yaml")
URL_LIST_PATH = os.path.join(BASE_DIR, "url_list.cfg")
