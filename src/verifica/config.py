from platformdirs import user_config_dir
from importlib.metadata import version, PackageNotFoundError
from time import time
import logging
import json
import os

logger = logging.getLogger(__name__)

class Config:
    """Classe de configurações compartilhadas

    Returns:
        _type_: True se a instância foi criada, False caso contrário
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Gerador de instância, impede que Config seja iniciado mais de uma vez

        Returns:
            bool: True se a instância foi criada, False caso contrário
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Inicializa a classe
        """
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        config_dir = user_config_dir("verifica")
        os.makedirs(config_dir, exist_ok=True)

        self.config_dir = config_dir
        self.config_path = os.path.join(config_dir, "config.toml")
        self.__check_config_state()
        logger.info("Configurações inicializadas.")

    def __save_keys(self, data: dict):
        """Salva as configurações da memória para o arquivo de configuração

        Args:
            data (dict): Configurações a serem salvas
        """
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def __read_keys(self) -> dict:
        """Lê o arquivo de configurações

        Returns:
            dict: Configurações lidas do arquivo
        """
        if not self.config_path or not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return {}

    def __check_config_state(self):
        """Checa se o arquivo de configurações está com conteúdo e atualizado
        """
        defaultConfig = {
            "version": self.get_version(),
            "url": "https://raw.githubusercontent.com",
            "answers_file_name": "correcao.json"
        }

        current_config = self.__read_keys()
        if len(current_config) == 0:
            self.__save_keys(defaultConfig)
        else:
            if current_config.get("version") != defaultConfig.get("version"):
                self.update_config(defaultConfig, defaultConfig.get("version"))
        logger.info("Configurações verificadas e atualizadas.")

    def get_version(self):
        """Obtém a versão da aplicação

        Returns:
            str: Versão da aplicação
        """
        try:
            __version__  = version("verifica")
        except PackageNotFoundError:
            __version__  = f"indev-{time()}"
        return __version__

    def update_config(self, new_data: dict, version: str = None):
        """Atualiza uma configuração específica

        Args:
            new_data (dict): Dicionário contendo configurações a serem salvas
            version (str, optional): Versão da aplicação. O padrão é None.
        """
        current_config = self.__read_keys()
        if version:
            current_config["version"] = version
        new_data.update(current_config)
        self.__save_keys(new_data)

    def get_config(self, key: str = None) -> dict:
        """Pega uma configuração específica do arquivo de configurações, ou todas as configurações se nenhuma chave for passada

        Args:
            key (str, optional): Configuração desejada. O padrão é None.

        Returns:
            dict: Configurações lidas do arquivo
        """
        config = self.__read_keys()
        if key:
            logger.info(f"Configuração {key} obtida.")
            return config.get(key, "")
        logger.info(f"Obtendo todas as configurações.")
        return config

    def set_config(self, key: str, value):
        """Altera uma configuração

        Args:
            key (str): Configuração a ser alterada
            value: Valor novo
        """
        config = self.__read_keys()
        config[key] = value
        self.update_config(config)

settings = Config()