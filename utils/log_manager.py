import os
import logging
from datetime import datetime

class LogManager:
    def __init__(self, log_file="rtc.log"):
        self.log_file = log_file

        # 设置日志格式和日志等级
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, mode='a', encoding='utf-8'),
                logging.StreamHandler()  # 也可以同时输出到控制台
            ]
        )
        
    def log(self, title, message):
        """记录日志，标题作为日志的标识，内容作为日志的详细信息"""
        log_message = f"【{title}】 {message}"
        logging.info(log_message)

    def log_error(self, title, message):
        """记录错误日志，标题作为日志的标识，内容作为错误的详细信息"""
        log_message = f"【{title}】【ERROR】 {message}"
        logging.error(log_message)

    def log_warning(self, title, message):
        """记录警告日志"""
        log_message = f"【{title}】【WARNING】 {message}"
        logging.warning(log_message)
