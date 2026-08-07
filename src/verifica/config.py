from platformdirs import user_config_dir
from importlib.metadata import version, PackageNotFoundError
from colorama import init
from time import time
import json
import sys
import os

def setup_colors():
    if not sys.stdout.isatty():
        init(strip=True, convert=False)
        return False
    
    init(autoreset=True)
    return True

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.enviroment_supports_colors = setup_colors()

        config_dir = user_config_dir("verifica")
        os.makedirs(config_dir, exist_ok=True)

        self.config_dir = config_dir
        self.config_path = os.path.join(config_dir, "config.toml")
        self.__check_config_state()

    def __save_keys(self, data: dict):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def __read_keys(self) -> dict:
        if not self.config_path or not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return {}

    def __check_config_state(self):
        try:
            current_version = version("verifica")
        except PackageNotFoundError:
            current_version = f"indev-{time()}"

        defaultConfig = {
            "version": current_version,
            "url": "https://raw.githubusercontent.com",
            "answers_file_name": "correcao.json"
        }

        current_config = self.__read_keys()
        if len(current_config) == 0:
            self.__save_keys(defaultConfig)
        else:
            if current_config.get("version") != defaultConfig.get("version"):
                self.update_config(defaultConfig, defaultConfig.get("version"))

    def update_config(self, new_data: dict, version: str = None):
        current_config = self.__read_keys()
        if version:
            current_config["version"] = version
        new_data.update(current_config)
        self.__save_keys(new_data)

    def get_config(self, key: str = None) -> dict:
        config = self.__read_keys()
        if key:
            return config.get(key, "")
        return config

    def set_config(self, key: str, value):
        config = self.__read_keys()
        config[key] = value
        self.update_config(config)

settings = Config()