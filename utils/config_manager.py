import os
import configparser

class ConfigManager:
    """
    配置管理类，用于管理配置文件的读取和保存。
    """
    def __init__(self, config_file="config.ini"):
        """
        初始化配置管理器。
        :param config_file: 配置文件路径，默认为 "config.ini"。
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # 如果配置文件存在，加载配置
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            print(f"配置文件 {self.config_file} 不存在，将在需要时创建新的配置文件。")

    def get(self, section, key, default_value=None):
        """
        获取指定配置项的值。
        :param section: 配置段名。
        :param key: 配置键名。
        :param default_value: 如果键不存在，则返回的默认值。
        :return: 配置值或默认值。
        """
        try:
            return self.config[section][key]
        except KeyError:
            # 如果键不存在，返回默认值
            return default_value

    def set(self, section, key, value):
        """
        设置指定配置项的值。
        :param section: 配置段名。
        :param key: 配置键名。
        :param value: 配置值。
        """
        # 如果段不存在，创建段
        if section not in self.config:
            self.config[section] = {}
        
        # 设置键值
        self.config[section][key] = value

    def save(self):
        """
        保存配置到文件。
        """
        with open(self.config_file, "w") as config_file:
            self.config.write(config_file)
        print(f"配置已保存到 {self.config_file}")


def save_browser_path_to_config(browser_path):
    """
    将浏览器路径保存到 config.ini 文件。
    """
    config = ConfigManager("config.ini")
    config.set("Settings", "BrowserPath", browser_path)
    config.save()


def load_browser_path_from_config():
    """
    从 config.ini 文件加载浏览器路径。
    """
    config = ConfigManager("config.ini")
    return config.get("Settings", "BrowserPath", "")
