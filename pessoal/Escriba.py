import logging
from logging.handlers import RotatingFileHandler
import os

class registrador:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Create file handler which logs even debug messages
        log_file = os.path.join(logs_dir, 'application.log')
        fh = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
        fh.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Remove existing handlers to prevent duplicates
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                try:
                    handler.close()
                except Exception:
                    pass
                self.logger.removeHandler(handler)

        # Add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        # Attach helpers
        self.logger.registrador = self
        self.logger.log_shortcuts = self.log_shortcuts

    def addHand(self):
        # No need to reinitialize since handlers are properly managed in __init__
        pass

    def get_logger(self):
        return self.logger

    def log_shortcuts(self, shortcuts=None, active_shortcut: str = None):
        """
        Escreve no log todos os atalhos cadastrados e a frase de orientação
        com a ortografia corrigida em português.
        """
        if shortcuts is None:
            try:
                from gtray_data_manager import GTrayDataManager
                dm = GTrayDataManager()
                shortcuts = dm.get_shortcuts()
            except Exception:
                shortcuts = {}

        self.logger.info("Atalhos cadastrados:")
        if isinstance(shortcuts, dict):
            for name, data in shortcuts.items():
                if isinstance(data, dict):
                    key = data.get("key", "(nenhuma)")
                    self.logger.info(f" - {name}: {key}")
                else:
                    self.logger.info(f" - {name}: {data}")

        shortcut_label = active_shortcut if active_shortcut else "o atalho configurado"
