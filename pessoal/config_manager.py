"""
pessoal/config_manager.py - Gerenciador Singleton de Arquivos de Configuração INI.

Centraliza a leitura dos parâmetros estáticos definidos em `assets/config.ini`,
como caminhos de ícones, arquivos de atalho legados, tempos de retentativa e
valores padrão de inicialização.
"""

import configparser
import os
from typing import Optional

class ConfigManager:
    """Gerenciador Singleton para leitura das configurações do assets/config.ini."""
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Carrega e analisa o arquivo assets/config.ini com codificação UTF-8."""
        self._config = configparser.ConfigParser()
        config_path = os.path.join('assets', 'config.ini')
        self._config.read(config_path, encoding='utf-8')

    def get(self, section: str, key: str) -> str:
        """Retorna o valor em formato string para a seção e chave especificadas."""
        try:
            return self._config[section][key]
        except KeyError:
            raise KeyError(f"Configuration not found for section '{section}' and key '{key}'")

    def get_int(self, section, key):
        """Get a configuration value as integer"""
        return int(self.get(section, key))

    def get_shortcut(self, shortcut_type):
        """Get a shortcut configuration"""
        env_var = f"assets/shortcut_{shortcut_type.lower()}.cfg"
        with open(env_var,'r') as f:
            value = f.read().strip()
        if not value:
            raise KeyError(f"Environment variable {env_var} not found")
        return value.strip()

    def get_model(self, shortcut_type=None):
        """Get AI model configuration, optionally for a specific shortcut"""
        if shortcut_type:
            try:
                return self.get('GTRAY', f'model_{shortcut_type.lower()}')
            except KeyError:
                pass
        return self.get('GTRAY', 'modelo')

    def get_provider(self, shortcut_type=None):
        """Get AI provider configuration, optionally for a specific shortcut"""
        if shortcut_type:
            try:
                return self.get('GTRAY', f'provider_{shortcut_type.lower()}')
            except KeyError:
                pass
        try:
            return self.get('GTRAY', 'provedor')
        except KeyError:
            return 'openai'

    def get_log_file(self):
        """Get log file path"""
        return self.get('GTRAY', 'log')

    def get_retry_attempts(self):
        """Get retry attempts configuration"""
        return self.get_int('GTRAY', 'retry_ia')

    def get_clip_retry(self):
        """Get clipboard retry attempts configuration"""
        return self.get_int('GTRAY', 'retry_clip')