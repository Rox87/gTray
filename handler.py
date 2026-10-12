import pystray
from PIL import Image
import win32gui,win32con
import keyboard
from pessoal.Decorador import tempo_decorrido
from pessoal.IA import IA
from pessoal.Engineer import Engineer
from pessoal.config_manager import ConfigManager
from gtray_data_manager import GTrayDataManager
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
    processo = None
    icon = None
    shortcut = None
    def show_terminal(self):
        if self.UI:
            self.UI.show_UI()
        logger.info("showing UI")
        
    def hide_terminal(self):
        if self.UI:
            self.UI.hide_UI()
        logger.info("hiding UI")
        
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
        logger.info('preparando...')
        self.sair = False
        self.prosseguir = True
        self.the_program_to_hide = win32gui.GetForegroundWindow()
        self.mode = None
        self.initialize_ui()
    def initialize_ui(self):
        logger.info('carregando icones')
        self.red_image = Image.open(self.config.get('GTRAY', 'gtON'))
        self.menu_visible = pystray.MenuItem("Mostrar UI", self.show_terminal)
        self.menu_exit = pystray.MenuItem("Sair", self.on_exit)
        self.icon = pystray.Icon("GPTray", self.red_image, menu=pystray.Menu())
        self.build_menu()
    def start(self):
        try:
            self.register_shortcuts()
            logger.info(f'precione {self.shortcut} com um texto selecionado em um campo editavel e aguarde...')
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
            keyboard.add_hotkey(shortcut.lower(), handlers[shortcut_type])
            
    def stop(self):
        self.prosseguir = False
        try:
            self.icon.stop()
        except Exception as ex:
            logger.error(f"Error stopping icon: {str(ex)}")

    def run(self):
        while self.prosseguir:
            try:
                self.icon.run()
            except Exception as ex:
                logger.error(f"Error in main loop: {str(ex)}")
    def build_menu(self):
        self.icon.menu = pystray.Menu(self.menu_exit)
    def on_exit(self):
        logger.info("saindo da aplicação")
        self.prosseguir = False
        try:
            self.icon.stop()
        except Exception as ex:
            logger.error(f"Error stopping icon: {str(ex)}")
    @tempo_decorrido
    def handle_ai_request(self, mode, prompt_modifier=""):
        try:
            logger.info(f'mode {mode}')
            logger.info('preparando dados')
            clipboard = self.Engineer.pre_processamento()
            if not clipboard:
                return
            logger.info('perguntando a inteligência artificial')
            resolved = self.data_manager.resolve_shortcut(mode)
            api_key = resolved.get('api_key')
            model_name = resolved.get('model_name')
            if api_key and self.AI:
                self.AI.change_key(api_key)

            if mode == 'python':
                response = self.AI.python_responder(clipboard, mode=mode, model_override=model_name)
            else:
                response = self.AI.responder(clipboard, prompt_modifier, mode=mode, model_override=model_name)
            logger.info('entregando resposta')
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
    def change_key(self, key):
        if self.AI is not None:
            del self.AI
        self.AI = IA(key, logger)
if __name__ == '__main__':
    app = Gtray()
    app.run()
