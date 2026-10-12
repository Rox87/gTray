import pystray
from PIL import Image
import win32gui,win32con
import keyboard
from pessoal.Decorador import tempo_decorrido
from pessoal.IA import IA
from pessoal.Engineer import Engineer
from pessoal.config_manager import ConfigManager
from gtray_data_manager import GTrayDataManager
import re
import subprocess
import configparser
config = configparser.ConfigParser()

# Read in the configuration file
config.read('assets/config.ini',encoding='utf-8')

def wait_hotkey_release():  
    print("Hotkey pressed, waiting for release...")

    # Wait for all keys to be released
    while keyboard.is_pressed('ctrl'):
        pass

    print("Hotkey released!")  
class Gtray:
    @staticmethod
    def extract_code_blocks(response: str, comment_char: str = "#") -> str:
        if not response:
            return ""
        matches = list(re.finditer(r'```[a-zA-Z0-9_\-\+\.]*[\r\n]+(.*?)```', response, re.DOTALL))
        if not matches:
            return response

        comment = (comment_char or "#").strip()
        if not comment:
            comment = "#"

        blocks = []
        last_end = 0
        for m in matches:
            block_content = m.group(1).strip('\r\n')
            preceding_text = response[last_end:m.start()]
            last_end = m.end()

            filename = ""
            for line in reversed(preceding_text.splitlines()):
                line_clean = line.strip()
                if line_clean:
                    words = line_clean.split()
                    if words:
                        first_word = words[0]
                        cleaned_word = re.sub(r'^[*_`"\'\(\[]+|[*_`"\'\)\]:,]+$', '', first_word).strip()
                        if cleaned_word:
                            filename = cleaned_word
                    break

            if filename:
                blocks.append(f"{comment} {filename}\n{block_content}")
            else:
                blocks.append(block_content)

        return "\n\n".join(blocks)
    processo = None
    icon = None
    shortcut = None
    def show_terminal(self):
        if self.UI:
            self.UI.show_UI()
        logger.info("Interface gráfica exibida.")
        
    def hide_terminal(self):
        if self.UI:
            self.UI.hide_UI()
        logger.info("Interface gráfica ocultada (em segundo plano).")
        
    def __init__(self,UI=None,logger_from=None):
        global logger
        logger = logger_from
        self.config = ConfigManager()
        self.data_manager = GTrayDataManager()
        self.Engineer = Engineer(logger_from)
        self.AI = None
        self.UI = UI
        self.initialize_app()
    def initialize_app(self):
        logger.info("Inicializando componentes do gTray...")
        self.sair = False
        self.prosseguir = True
        self.the_program_to_hide = win32gui.GetForegroundWindow()
        self.mode = None
        self.initialize_ui()
    def initialize_ui(self):
        logger.info("Carregando recursos visuais e ícone da bandeja...")
        from PIL import ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        icon_path = self.config.get('GTRAY', 'gtON')
        with Image.open(icon_path) as img:
            self.red_image = img.copy()
        self.menu_visible = pystray.MenuItem("Mostrar UI", self.show_terminal)
        self.menu_exit = pystray.MenuItem("Sair", self.on_exit)
        self.icon = pystray.Icon("GPTray", self.red_image, menu=pystray.Menu())
        self.build_menu()
    def start(self):
        try:
            self.register_shortcuts()
            shortcuts = {}
            if hasattr(self, 'data_manager') and self.data_manager:
                shortcuts = self.data_manager.get_shortcuts()
            if hasattr(logger, 'log_shortcuts'):
                logger.log_shortcuts(shortcuts, active_shortcut=self.shortcut)
            else:
                logger.info("Atalhos cadastrados:")
                for name, data in shortcuts.items():
                    key = data.get("key", "(nenhuma)") if isinstance(data, dict) else data
                    logger.info(f" - {name}: {key}")
                active = self.shortcut if self.shortcut else "o atalho configurado"
                logger.info(f'pressione {active} com um texto selecionado em um campo editável e aguarde...')
        except Exception as ex:
            logger.error(f"Error starting application: {str(ex)}")
    def unregister_shortcuts(self):
        shortcut_types = ['generic', 'upgrade', 'python', 'creation']
        for shortcut_type in shortcut_types:
            shortcut = self.config.get_shortcut(shortcut_type)
            try:
                keyboard.remove_hotkey(shortcut.lower())
            except:
                pass
    def register_shortcuts(self):
        self.unregister_shortcuts()
        shortcut_types = ['generic', 'upgrade', 'python', 'creation']
        handlers = {
            'generic': self.chat_handler,
            'upgrade': self.sem_rodeios_upgrade,
            'python': self.python_handler,
            'graphs': self.graficos,
            'creation': self.creation
        }
        for shortcut_type in shortcut_types:
            shortcut = self.config.get_shortcut(shortcut_type)
            if shortcut_type == 'upgrade':
                self.shortcut = shortcut

            is_enabled = True
            if hasattr(self, 'data_manager') and self.data_manager:
                sc_info = self.data_manager.get_shortcut(shortcut_type)
                if sc_info and not sc_info.get("enabled", True):
                    is_enabled = False

            if is_enabled and shortcut:
                keyboard.add_hotkey(shortcut.lower(), handlers[shortcut_type])
            
    def stop(self):
        self._is_running = False
        self.prosseguir = False
        self.unregister_shortcuts()
        try:
            if hasattr(self, 'icon') and self.icon and getattr(self.icon, '_running', False):
                self.icon.stop()
        except Exception as ex:
            logger.error(f"Error stopping icon: {str(ex)}")

    def run(self):
        if getattr(self, '_is_running', False):
            return
        self._is_running = True
        try:
            if hasattr(self.icon, 'run_detached') and not getattr(self.icon, '_running', False):
                self.icon.run_detached()
            elif not getattr(self.icon, '_running', False):
                self.icon.run()
        except Exception as ex:
            self._is_running = False
            logger.error(f"Error in main loop: {str(ex)}")
    def build_menu(self):
        self.icon.menu = pystray.Menu(self.menu_exit)
    def on_exit(self):
        logger.info("Encerrando aplicação...")
        self._is_running = False
        self.prosseguir = False
        self.unregister_shortcuts()
        try:
            if hasattr(self, 'icon') and self.icon and getattr(self.icon, '_running', False):
                self.icon.stop()
        except Exception as ex:
            logger.error(f"Erro ao parar ícone da bandeja: {str(ex)}")
        if self.UI:
            from PyQt5.QtWidgets import QApplication
            QApplication.quit()
    @tempo_decorrido
    def handle_ai_request(self, mode, prompt_modifier=""):
        try:
            logger.info(f"Processando atalho '{mode}'...")
            clipboard = self.Engineer.pre_processamento()
            if not clipboard:
                logger.info("Nenhum texto selecionado na área de transferência.")
                return
            logger.info("Consultando provedor de Inteligência Artificial...")
            resolved = self.data_manager.resolve_shortcut(mode)
            api_key = resolved.get('api_key')
            model_name = resolved.get('model_name')
            base_url = resolved.get('base_url')
            system_prompt = (resolved.get('system_prompt') or '').strip()

            system_cmd = system_prompt if system_prompt else prompt_modifier

            if self.AI is None:
                self.AI = IA(api_key or "", logger, base_url=base_url)
            else:
                self.AI.change_key(api_key, base_url=base_url)

            comment_char = resolved.get('comment_char', '#')

            if mode == 'python':
                response = self.AI.python_responder(clipboard, mode=mode, model_override=model_name, comment_char=comment_char)
            else:
                response = self.AI.responder(clipboard, system_cmd, mode=mode, model_override=model_name)
                if resolved.get('extract_blocks', False) and response:
                    response = self.extract_code_blocks(response, comment_char=comment_char)

            logger.info("Resposta da IA recebida e aplicada com sucesso.")
            self.Engineer.pos_processamento(clipboard, response)
        except Exception as ex:
            logger.error(f"Error in {mode} handler: {str(ex)}")
    @tempo_decorrido
    def python_handler(self):
        self.handle_ai_request('python')
    @tempo_decorrido
    def chat_handler(self):
        self.handle_ai_request('generic')
    @tempo_decorrido
    def sem_rodeios_upgrade(self):
        self.handle_ai_request('upgrade', "Não responda o usuario, retorne apenas, sem rodeios, a própria entrada do usuário melhorada")
    @tempo_decorrido
    def creation(self):
        try:
            subprocess.run("python code_widget.py", shell=True, capture_output=False, text=True)
        except Exception as ex:
            logger.error(f"Error launching code widget: {str(ex)}")
    @tempo_decorrido
    def graficos(self):
        try:
            subprocess.run("python graphs_widget.py", shell=True, capture_output=False, text=True)
        except Exception as ex:
            logger.error(f"Error launching graphs widget: {str(ex)}")
    def change_key(self, key, base_url=None):
        if self.AI is not None:
            self.AI.change_key(key, base_url=base_url)
        else:
            self.AI = IA(key, logger, base_url=base_url)
if __name__ == '__main__':
    app = Gtray()
    app.run()
