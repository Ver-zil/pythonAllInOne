import os
from datetime import datetime


def init_log_file(log_path):
    """初始化日志文件（如果不存在则创建）"""
    if not os.path.exists(log_path):
        with open(log_path, mode="w", encoding="utf-8") as file:
            file.write("Log File Created at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        print(f"文件 {log_path} 不存在，已创建空文件。")


def log(log_path, msg):
    """记录日志"""
    with open(log_path, mode="a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] {msg}\n")


def is_file_processed(log_path, filename):
    """检查某个文件名是否已被记录（转化）"""
    if not os.path.exists(log_path):
        return False  # 如果日志文件不存在，说明文件未被处理过

    with open(log_path, mode="r", encoding="utf-8") as file:
        for line in file:
            if filename in line:
                return True  # 如果文件名在日志中，说明已被处理
    return False  # 如果未找到文件名，说明未被处理
