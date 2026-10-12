from PyQt5.QtWidgets import (
    QDesktopWidget, QCheckBox, QLineEdit, QApplication, QWidget,
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox,
    QComboBox, QFrame, QTabWidget, QPlainTextEdit
)
from PyQt5.QtCore import Qt, QUrl, QEvent, QTimer
from PyQt5.QtGui import QPixmap, QDesktopServices, QIcon
from services.klisten import KListen
from handler import Gtray
from ui_theme import get_theme_stylesheet, get_status_badge_style
from gtray_data_manager import GTrayDataManager
import configparser
from pessoal.Escriba import registrador
import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

r = registrador()
r.addHand()
logger = r.get_logger()

# Create a new config parser object
config = configparser.ConfigParser()
config.read('assets/config.ini', encoding='utf-8')


class GTray_CFG_UI(QWidget):

    def __init__(self):
        super().__init__()

        self.gt = None
        self.kl = None
        self.visible = None
        self.autostart = False
        self.is_running = False
        self.fake_event = None
        self.lbl_shortcut_text = None
        self.button_get_shortcut_clicked = False
        self.index = 0
        self.current_theme = 'dark'
        self.data_manager = GTrayDataManager()

        self.initUI()

    def pos_left(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initUI(self):
        self.setWindowTitle('gTray')
        self.setFixedSize(400, 670)

        # Layout Principal
        self.root_layout = QVBoxLayout()
        self.root_layout.setContentsMargins(18, 18, 18, 18)
        self.root_layout.setSpacing(12)

        # ---------------------------------------------------------
        # 1. CABEÇALHO (Header)
        # ---------------------------------------------------------
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.setSpacing(10)

        # Ícone do Logo
        self.logo_label = QLabel()
        if os.path.isfile(config['GTRAY']['favicon']):
            pix = QPixmap(config['GTRAY']['favicon']).scaled(
                30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(pix)
        else:
            self.logo_label.setText("G")
        self.logo_label.setFixedSize(32, 32)
        self.logo_label.setAlignment(Qt.AlignCenter)

        # Título e Subtítulo
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self.header_title = QLabel(config['GTRAY'].get('header_title', 'gTray'))
        self.header_title.setProperty('class', 'headerTitle')
        self.header_subtitle = QLabel("Assistente IA de Bandeja")
        self.header_subtitle.setProperty('class', 'headerSubtitle')
        title_box.addWidget(self.header_title)
        title_box.addWidget(self.header_subtitle)

        # Status
        header_controls = QHBoxLayout()
        header_controls.setSpacing(8)

        self.lbl_status = QLabel("● Pausado")
        self.lbl_status.setAlignment(Qt.AlignCenter)

        header_controls.addWidget(self.lbl_status)

        header_layout.addWidget(self.logo_label)
        header_layout.addLayout(title_box, stretch=1)
        header_layout.addLayout(header_controls)
        self.root_layout.addWidget(header_frame)

        # ---------------------------------------------------------
        # 2. ABAS DE CONFIGURAÇÃO (QTabWidget)
        # ---------------------------------------------------------
        self.tabs = QTabWidget()

        # Tab 1: Atalhos (nome, tecla, modelo)
        self.tab_shortcuts = QWidget()
        self.setup_shortcuts_tab()
        self.tabs.addTab(self.tab_shortcuts, "⚡ Atalhos")

        # Tab 2: Modelos (nome, provedor)
        self.tab_models = QWidget()
        self.setup_models_tab()
        self.tabs.addTab(self.tab_models, "🤖 Modelos")

        # Tab 3: Provedores (nome, chave)
        self.tab_providers = QWidget()
        self.setup_providers_tab()
        self.tabs.addTab(self.tab_providers, "🔑 Provedores")

        self.root_layout.addWidget(self.tabs, stretch=1)

        # ---------------------------------------------------------
        # 3. PREFERÊNCIAS & CONTROLES NO RODAPÉ
        # ---------------------------------------------------------
        prefs_layout = QHBoxLayout()
        self.checkbox_visibility = QCheckBox("Manter Visível")
        self.checkbox_visibility.setChecked(True)
        self.checkbox_visibility.stateChanged.connect(self.checkbox_visibility_changed)
        prefs_layout.addWidget(self.checkbox_visibility)
        prefs_layout.addStretch(1)
        self.root_layout.addLayout(prefs_layout)

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)

        self.btn_startstop = QPushButton("Iniciar Serviço")
        self.btn_startstop.setProperty('class', 'primary')
        self.btn_startstop.setFixedHeight(38)
        self.btn_startstop.clicked.connect(self.startstop)

        self.btn_minimize = QPushButton("Minimizar")
        self.btn_minimize.setFixedHeight(38)
        self.btn_minimize.clicked.connect(self.hide_UI)

        footer_layout.addWidget(self.btn_startstop, stretch=2)
        footer_layout.addWidget(self.btn_minimize, stretch=1)
        self.root_layout.addLayout(footer_layout)

        # Mensagem Flash (no centro da parte inferior)
        self.lbl_flash_message = QLabel("")
        self.lbl_flash_message.setAlignment(Qt.AlignCenter)
        self.lbl_flash_message.setProperty('class', 'flashSuccess')
        self.lbl_flash_message.setFixedHeight(28)
        self.lbl_flash_message.hide()
        self.root_layout.addWidget(self.lbl_flash_message)

        self.setLayout(self.root_layout)

        # Inicialização do Tema e dados
        self.set_theme(self.current_theme, save_to_file=False)
        self.load_all_data()
        self.start_buttons_def()

        if os.path.isfile(config['GTRAY']['favicon']):
            self.setWindowIcon(QIcon(config['GTRAY']['favicon']))

        self.pos_left()
        self.show()

    def show_flash_message(self, message: str, msg_type: str = "success"):
        if msg_type == "success":
            icon = "✓ "
        elif msg_type == "warning":
            icon = "⚠ "
        elif msg_type == "danger":
            icon = "🗑 "
        else:
            icon = "✖ "
        self.lbl_flash_message.setText(f"{icon}{message}")
        if msg_type in ("warning", "danger", "error"):
            self.lbl_flash_message.setProperty('class', 'flashWarning')
        else:
            self.lbl_flash_message.setProperty('class', 'flashSuccess')
        self.lbl_flash_message.style().unpolish(self.lbl_flash_message)
        self.lbl_flash_message.style().polish(self.lbl_flash_message)
        self.lbl_flash_message.show()
        if not hasattr(self, 'flash_timer'):
            self.flash_timer = QTimer(self)
            self.flash_timer.setSingleShot(True)
            self.flash_timer.timeout.connect(self.lbl_flash_message.hide)
        self.flash_timer.stop()
        self.flash_timer.start(3000)

    # -------------------------------------------------------------
    # SETUP: ABA ATALHOS (Nome, Tecla e Modelo)
    # -------------------------------------------------------------
    def setup_shortcuts_tab(self):
        layout = QVBoxLayout(self.tab_shortcuts)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Seletor do Atalho + Novo
        sel_row = QHBoxLayout()
        lbl_sel = QLabel("Atalho:")
        lbl_sel.setProperty('class', 'sectionHeader')
        self.combo_shortcuts = QComboBox()
        self.combo_shortcuts.currentTextChanged.connect(self.on_shortcut_selected)

        self.btn_new_shortcut = QPushButton("+ Novo")
        self.btn_new_shortcut.clicked.connect(self.new_shortcut)

        sel_row.addWidget(lbl_sel)
        sel_row.addWidget(self.combo_shortcuts, stretch=1)
        sel_row.addWidget(self.btn_new_shortcut)
        layout.addLayout(sel_row)

        # Nome do Atalho
        name_box = QVBoxLayout()
        name_box.setSpacing(2)
        lbl_name = QLabel("Nome do Atalho:")
        lbl_name.setProperty('class', 'headerSubtitle')
        self.input_shortcut_name = QLineEdit()
        name_box.addWidget(lbl_name)
        name_box.addWidget(self.input_shortcut_name)
        layout.addLayout(name_box)

        # Tecla de Atalho
        key_box = QVBoxLayout()
        key_box.setSpacing(2)
        lbl_key = QLabel("Tecla / Combinação:")
        lbl_key.setProperty('class', 'headerSubtitle')
        key_box.addWidget(lbl_key)

        key_row = QHBoxLayout()
        self.lbl_shortcut_key = QLabel("(nenhuma)")
        self.lbl_shortcut_key.setProperty('class', 'badgeDisplay')
        self.lbl_shortcut_key.setAlignment(Qt.AlignCenter)

        self.btn_listen_key = QPushButton("Gravar Tecla")
        self.btn_listen_key.clicked.connect(self.listen_shortcut_key)

        key_row.addWidget(self.lbl_shortcut_key, stretch=1)
        key_row.addWidget(self.btn_listen_key)
        key_box.addLayout(key_row)
        layout.addLayout(key_box)

        # Modelo Associado
        model_box = QVBoxLayout()
        model_box.setSpacing(2)
        lbl_model = QLabel("Modelo de IA Associado:")
        lbl_model.setProperty('class', 'headerSubtitle')
        self.combo_shortcut_model = QComboBox()
        model_box.addWidget(lbl_model)
        model_box.addWidget(self.combo_shortcut_model)
        layout.addLayout(model_box)

        # Pré-comando / Mensagem do Sistema
        prompt_box = QVBoxLayout()
        prompt_box.setSpacing(2)
        lbl_prompt = QLabel("Pré-comando / Mensagem do Sistema:")
        lbl_prompt.setProperty('class', 'headerSubtitle')
        self.input_shortcut_system_prompt = QPlainTextEdit()
        self.input_shortcut_system_prompt.setPlaceholderText("Instrução ou papel da IA (ex: Responda apenas com o texto melhorado, sem rodeios)")
        self.input_shortcut_system_prompt.setFixedHeight(70)
        prompt_box.addWidget(lbl_prompt)
        prompt_box.addWidget(self.input_shortcut_system_prompt)
        layout.addLayout(prompt_box)

        # Extração de Blocos de Código
        extract_box = QVBoxLayout()
        extract_box.setSpacing(4)
        extract_row = QHBoxLayout()
        self.checkbox_extract_blocks = QCheckBox("Conteúdo de blocos apenas")
        self.checkbox_extract_blocks.setChecked(False)

        lbl_comment = QLabel("Comentário:")
        lbl_comment.setProperty('class', 'headerSubtitle')
        self.input_comment_char = QLineEdit()
        self.input_comment_char.setText("#")
        self.input_comment_char.setPlaceholderText("#")
        self.input_comment_char.setFixedWidth(50)

        extract_row.addWidget(self.checkbox_extract_blocks, stretch=1)
        extract_row.addWidget(lbl_comment)
        extract_row.addWidget(self.input_comment_char)
        extract_box.addLayout(extract_row)
        layout.addLayout(extract_box)

        # Botões de Ação
        btn_row = QHBoxLayout()
        self.btn_save_shortcut = QPushButton("Salvar Atalho")
        self.btn_save_shortcut.setProperty('class', 'primary')
        self.btn_save_shortcut.clicked.connect(lambda: self.save_shortcut(show_msg=True))

        self.btn_del_shortcut = QPushButton("Excluir")
        self.btn_del_shortcut.setProperty('class', 'danger')
        self.btn_del_shortcut.clicked.connect(self.delete_shortcut)

        btn_row.addWidget(self.btn_save_shortcut, stretch=2)
        btn_row.addWidget(self.btn_del_shortcut, stretch=1)
        layout.addLayout(btn_row)

        layout.addStretch(1)

        # Aliases para retrocompatibilidade
        self.shortcut_type_combo = self.combo_shortcuts
        self.lbl_shortcut = self.lbl_shortcut_key
        self.btn_shortcut = self.btn_listen_key

    # -------------------------------------------------------------
    # SETUP: ABA MODELOS (Nome e Provedor)
    # -------------------------------------------------------------
    def setup_models_tab(self):
        layout = QVBoxLayout(self.tab_models)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Seletor de Modelo + Novo
        sel_row = QHBoxLayout()
        lbl_sel = QLabel("Modelo:")
        lbl_sel.setProperty('class', 'sectionHeader')
        self.combo_models = QComboBox()
        self.combo_models.currentTextChanged.connect(self.on_model_selected)

        self.btn_new_model = QPushButton("+ Novo")
        self.btn_new_model.clicked.connect(self.new_model)

        sel_row.addWidget(lbl_sel)
        sel_row.addWidget(self.combo_models, stretch=1)
        sel_row.addWidget(self.btn_new_model)
        layout.addLayout(sel_row)

        # Nome do Modelo
        name_box = QVBoxLayout()
        name_box.setSpacing(2)
        lbl_name = QLabel("Nome do Modelo:")
        lbl_name.setProperty('class', 'headerSubtitle')
        self.input_model_name = QLineEdit()
        self.input_model_name.setPlaceholderText("ex: gpt-4o-mini, claude-3-5-sonnet")
        name_box.addWidget(lbl_name)
        name_box.addWidget(self.input_model_name)
        layout.addLayout(name_box)

        # Provedor do Modelo
        prov_box = QVBoxLayout()
        prov_box.setSpacing(2)
        lbl_prov = QLabel("Provedor Associado:")
        lbl_prov.setProperty('class', 'headerSubtitle')
        self.combo_model_provider = QComboBox()
        prov_box.addWidget(lbl_prov)
        prov_box.addWidget(self.combo_model_provider)
        layout.addLayout(prov_box)

        # Botões de Ação
        btn_row = QHBoxLayout()
        self.btn_save_model = QPushButton("Salvar Modelo")
        self.btn_save_model.setProperty('class', 'primary')
        self.btn_save_model.clicked.connect(lambda: self.save_model(show_msg=True))

        self.btn_del_model = QPushButton("Excluir")
        self.btn_del_model.setProperty('class', 'danger')
        self.btn_del_model.clicked.connect(self.delete_model)

        btn_row.addWidget(self.btn_save_model, stretch=2)
        btn_row.addWidget(self.btn_del_model, stretch=1)
        layout.addLayout(btn_row)

        layout.addStretch(1)

        # Aliases para retrocompatibilidade
        self.input_model = self.input_model_name

    # -------------------------------------------------------------
    # SETUP: ABA PROVEDORES (Nome e Chave)
    # -------------------------------------------------------------
    def setup_providers_tab(self):
        layout = QVBoxLayout(self.tab_providers)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Seletor de Provedor + Novo
        sel_row = QHBoxLayout()
        lbl_sel = QLabel("Provedor:")
        lbl_sel.setProperty('class', 'sectionHeader')
        self.combo_providers = QComboBox()
        self.combo_providers.currentTextChanged.connect(self.on_provider_selected)

        self.btn_new_provider = QPushButton("+ Novo")
        self.btn_new_provider.clicked.connect(self.new_provider)

        sel_row.addWidget(lbl_sel)
        sel_row.addWidget(self.combo_providers, stretch=1)
        sel_row.addWidget(self.btn_new_provider)
        layout.addLayout(sel_row)

        # Nome do Provedor
        name_box = QVBoxLayout()
        name_box.setSpacing(2)
        lbl_name = QLabel("Nome do Provedor:")
        lbl_name.setProperty('class', 'headerSubtitle')
        self.input_provider_name = QLineEdit()
        self.input_provider_name.setPlaceholderText("ex: openai, anthropic, groq")
        name_box.addWidget(lbl_name)
        name_box.addWidget(self.input_provider_name)
        layout.addLayout(name_box)

        # Chave da API
        key_box = QVBoxLayout()
        key_box.setSpacing(2)
        lbl_key = QLabel("Chave de API:")
        lbl_key.setProperty('class', 'headerSubtitle')
        key_box.addWidget(lbl_key)

        key_row = QHBoxLayout()
        self.input_provider_key = QLineEdit()
        self.input_provider_key.setEchoMode(QLineEdit.Password)
        self.input_provider_key.setPlaceholderText("sk-...")

        self.btn_show_provider_key = QPushButton("👁")
        self.btn_show_provider_key.setProperty('class', 'iconBtn')
        self.btn_show_provider_key.setFixedSize(32, 32)
        self.btn_show_provider_key.setToolTip("Visualizar / Ocultar Chave")
        self.btn_show_provider_key.clicked.connect(self.toggle_apikey_visibility)

        key_row.addWidget(self.input_provider_key, stretch=1)
        key_row.addWidget(self.btn_show_provider_key)
        key_box.addLayout(key_row)
        layout.addLayout(key_box)

        # URL Base (Opcional)
        url_box = QVBoxLayout()
        url_box.setSpacing(2)
        lbl_url = QLabel("URL Base da API (opcional):")
        lbl_url.setProperty('class', 'headerSubtitle')
        self.input_provider_url = QLineEdit()
        self.input_provider_url.setPlaceholderText("ex: https://api.deepseek.com (automático se conhecido)")
        url_box.addWidget(lbl_url)
        url_box.addWidget(self.input_provider_url)
        layout.addLayout(url_box)

        # Botões de Ação
        btn_row = QHBoxLayout()
        self.btn_save_provider = QPushButton("Salvar Provedor")
        self.btn_save_provider.setProperty('class', 'primary')
        self.btn_save_provider.clicked.connect(lambda: self.save_provider(show_msg=True))

        self.btn_del_provider = QPushButton("Excluir")
        self.btn_del_provider.setProperty('class', 'danger')
        self.btn_del_provider.clicked.connect(self.delete_provider)

        btn_row.addWidget(self.btn_save_provider, stretch=2)
        btn_row.addWidget(self.btn_del_provider, stretch=1)
        layout.addLayout(btn_row)

        layout.addStretch(1)

        # Aliases para retrocompatibilidade
        self.input_apikey = self.input_provider_key
        self.input_provider = self.input_provider_name

    # -------------------------------------------------------------
    # CARREGAMENTO E SINCRONIZAÇÃO DE DADOS
    # -------------------------------------------------------------
    def load_all_data(self):
        self.refresh_providers_dropdown()
        self.refresh_models_dropdown()
        self.refresh_shortcuts_dropdown()

    def refresh_providers_dropdown(self):
        providers = list(self.data_manager.get_providers().keys())
        current = self.combo_providers.currentText()
        self.combo_providers.blockSignals(True)
        self.combo_providers.clear()
        self.combo_providers.addItems(providers)
        self.combo_model_provider.blockSignals(True)
        self.combo_model_provider.clear()
        self.combo_model_provider.addItems(providers)
        self.combo_providers.blockSignals(False)
        self.combo_model_provider.blockSignals(False)

        if current in providers:
            self.combo_providers.setCurrentText(current)
        elif providers:
            self.combo_providers.setCurrentIndex(0)
        self.on_provider_selected(self.combo_providers.currentText())

    def refresh_models_dropdown(self):
        models = list(self.data_manager.get_models().keys())
        current = self.combo_models.currentText()
        self.combo_models.blockSignals(True)
        self.combo_models.clear()
        self.combo_models.addItems(models)
        self.combo_shortcut_model.blockSignals(True)
        self.combo_shortcut_model.clear()
        self.combo_shortcut_model.addItems(models)
        self.combo_models.blockSignals(False)
        self.combo_shortcut_model.blockSignals(False)

        if current in models:
            self.combo_models.setCurrentText(current)
        elif models:
            self.combo_models.setCurrentIndex(0)
        self.on_model_selected(self.combo_models.currentText())

    def refresh_shortcuts_dropdown(self):
        shortcuts = list(self.data_manager.get_shortcuts().keys())
        current = self.combo_shortcuts.currentText()
        self.combo_shortcuts.blockSignals(True)
        self.combo_shortcuts.clear()
        self.combo_shortcuts.addItems(shortcuts)
        self.combo_shortcuts.blockSignals(False)

        if current in shortcuts:
            self.combo_shortcuts.setCurrentText(current)
        elif shortcuts:
            self.combo_shortcuts.setCurrentIndex(0)
        self.on_shortcut_selected(self.combo_shortcuts.currentText())

    # Handlers da Aba Provedores
    def on_provider_selected(self, name):
        if not name:
            self.input_provider_name.clear()
            self.input_provider_key.clear()
            self.input_provider_url.clear()
            return
        key = self.data_manager.get_provider_key(name) or ""
        url = self.data_manager.get_providers().get(name, {}).get("base_url", "")
        self.input_provider_name.setText(name)
        self.input_provider_key.setText(key)
        self.input_provider_url.setText(url)

    def new_provider(self):
        self.input_provider_name.clear()
        self.input_provider_key.clear()
        self.input_provider_url.clear()
        self.input_provider_name.setFocus()

    def save_provider(self, *args, show_msg: bool = True):
        name = self.input_provider_name.text().strip()
        key = self.input_provider_key.text().strip()
        url = self.input_provider_url.text().strip() or None
        if not name:
            if show_msg:
                self.show_flash_message("Informe o nome do provedor para salvar.", "warning")
            return
        try:
            self.data_manager.set_provider(name, key, base_url=url)
            self.refresh_providers_dropdown()
            self.combo_providers.setCurrentText(name)
            if show_msg:
                self.show_flash_message(f"Provedor '{name}' salvo com sucesso!", "success")
        except Exception as e:
            if show_msg:
                self.show_flash_message(f"Falha ao salvar provedor: {str(e)}", "danger")

    def delete_provider(self, *args):
        name = self.input_provider_name.text().strip()
        if not name:
            self.show_flash_message("Selecione um provedor para excluir.", "warning")
            return
        confirm = QMessageBox.question(
            self, "Confirmar", f"Deseja excluir o provedor '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                self.data_manager.delete_provider(name)
                self.refresh_providers_dropdown()
                self.show_flash_message(f"Provedor '{name}' excluído com sucesso!", "danger")
            except Exception as e:
                self.show_flash_message(f"Falha ao excluir provedor: {str(e)}", "danger")

    # Handlers da Aba Modelos
    def on_model_selected(self, name):
        if not name:
            self.input_model_name.clear()
            return
        provider = self.data_manager.get_model_provider(name) or ""
        self.input_model_name.setText(name)
        if provider:
            self.combo_model_provider.setCurrentText(provider)

    def new_model(self):
        self.input_model_name.clear()
        self.input_model_name.setFocus()

    def save_model(self, *args, show_msg: bool = True):
        name = self.input_model_name.text().strip()
        provider = self.combo_model_provider.currentText().strip()
        if not name:
            if show_msg:
                self.show_flash_message("Informe o nome do modelo para salvar.", "warning")
            return
        if not provider:
            if show_msg:
                self.show_flash_message("Cadastre e selecione um provedor associado ao modelo.", "warning")
            return
        try:
            self.data_manager.set_model(name, provider)
            self.refresh_models_dropdown()
            self.combo_models.setCurrentText(name)
            if show_msg:
                self.show_flash_message(f"Modelo '{name}' salvo com sucesso!", "success")
        except Exception as e:
            if show_msg:
                self.show_flash_message(f"Falha ao salvar modelo: {str(e)}", "danger")

    def delete_model(self, *args):
        name = self.input_model_name.text().strip()
        if not name:
            self.show_flash_message("Selecione um modelo para excluir.", "warning")
            return
        confirm = QMessageBox.question(
            self, "Confirmar", f"Deseja excluir o modelo '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                self.data_manager.delete_model(name)
                self.refresh_models_dropdown()
                self.show_flash_message(f"Modelo '{name}' excluído com sucesso!", "danger")
            except Exception as e:
                self.show_flash_message(f"Falha ao excluir modelo: {str(e)}", "danger")

    # Handlers da Aba Atalhos
    def on_shortcut_selected(self, name):
        if not name:
            self.input_shortcut_name.clear()
            self.lbl_shortcut_key.setText("(nenhuma)")
            self.input_shortcut_system_prompt.clear()
            self.checkbox_extract_blocks.setChecked(False)
            self.input_comment_char.setText("#")
            return
        sc = self.data_manager.get_shortcut(name) or {}
        key = sc.get("key", "")
        model = sc.get("model", "")
        system_prompt = sc.get("system_prompt", "")
        extract_blocks = sc.get("extract_blocks", False)
        comment_char = sc.get("comment_char", "#")

        self.input_shortcut_name.setText(name)
        self.lbl_shortcut_key.setText(key if key else "(nenhuma)")
        if model:
            self.combo_shortcut_model.setCurrentText(model)
        self.input_shortcut_system_prompt.setPlainText(system_prompt)
        self.checkbox_extract_blocks.setChecked(bool(extract_blocks))
        self.input_comment_char.setText(comment_char if comment_char else "#")

    def new_shortcut(self):
        self.input_shortcut_name.clear()
        self.lbl_shortcut_key.setText("(nenhuma)")
        self.input_shortcut_system_prompt.clear()
        self.checkbox_extract_blocks.setChecked(False)
        self.input_comment_char.setText("#")
        self.input_shortcut_name.setFocus()

    def save_shortcut(self, *args, show_msg: bool = True):
        name = self.input_shortcut_name.text().strip()
        key = self.lbl_shortcut_key.text().strip()
        if key == "(nenhuma)":
            key = ""
        model = self.combo_shortcut_model.currentText().strip()
        system_prompt = self.input_shortcut_system_prompt.toPlainText().strip()
        extract_blocks = self.checkbox_extract_blocks.isChecked()
        comment_char = self.input_comment_char.text().strip() or "#"
        if not name:
            if show_msg:
                self.show_flash_message("Informe o nome do atalho para salvar.", "warning")
            return
        try:
            self.data_manager.set_shortcut(
                name, key, model,
                system_prompt=system_prompt,
                extract_blocks=extract_blocks,
                comment_char=comment_char
            )
            self.refresh_shortcuts_dropdown()
            self.combo_shortcuts.setCurrentText(name)
            if show_msg:
                self.show_flash_message(f"Atalho '{name}' salvo com sucesso!", "success")
        except Exception as e:
            if show_msg:
                self.show_flash_message(f"Falha ao salvar atalho: {str(e)}", "danger")

    def delete_shortcut(self, *args):
        name = self.input_shortcut_name.text().strip()
        if not name:
            self.show_flash_message("Selecione um atalho para excluir.", "warning")
            return
        confirm = QMessageBox.question(
            self, "Confirmar", f"Deseja excluir o atalho '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                self.data_manager.delete_shortcut(name)
                self.refresh_shortcuts_dropdown()
                self.show_flash_message(f"Atalho '{name}' excluído com sucesso!", "danger")
            except Exception as e:
                self.show_flash_message(f"Falha ao excluir atalho: {str(e)}", "danger")

    def listen_shortcut_key(self):
        name = self.input_shortcut_name.text().strip() or "upgrade"
        self.button_get_shortcut_clicked = True
        self.lbl_shortcut_key.setText(config['GTRAY'].get('lbl_shortcut_state_rec', 'Pressione teclas...'))
        QApplication.processEvents()

        if hasattr(self.kl, 'kl'):
            self.kl.__init__(combo=name)
        else:
            self.kl = KListen(combo=name)
        self.kl.run()
        self.kl.set_activated(False)

        # Lê tecla capturada
        sc_file = os.path.join('assets', f'shortcut_{name}.cfg')
        captured_key = ""
        if os.path.isfile(sc_file):
            try:
                with open(sc_file, 'r', encoding='utf-8') as f:
                    captured_key = f.read().strip()
            except Exception:
                pass

        if captured_key:
            self.lbl_shortcut_key.setText(captured_key)
            model = self.combo_shortcut_model.currentText().strip()
            self.data_manager.set_shortcut(name, captured_key, model)
        else:
            self.lbl_shortcut_key.setText("(nenhuma)")

    # -------------------------------------------------------------
    # GERENCIAMENTO DE TEMA E STATUS
    # -------------------------------------------------------------
    def set_theme(self, theme_name: str = 'dark', save_to_file: bool = False):
        self.current_theme = 'dark'
        self.setStyleSheet(get_theme_stylesheet('dark'))
        self.update_status_badge()

    def update_status_badge(self):
        if getattr(self, 'is_running', False):
            self.lbl_status.setText("● Ativo")
            self.lbl_status.setStyleSheet(get_status_badge_style(True, 'dark'))
        else:
            self.lbl_status.setText("● Pausado")
            self.lbl_status.setStyleSheet(get_status_badge_style(False, 'dark'))

    def toggle_apikey_visibility(self):
        if self.input_provider_key.echoMode() == QLineEdit.Password:
            self.input_provider_key.setEchoMode(QLineEdit.Normal)
        else:
            self.input_provider_key.setEchoMode(QLineEdit.Password)

    def start_buttons_def(self):
        self.is_running = False
        self.btn_startstop.setText('Iniciar Serviço')
        self.btn_startstop.setProperty('class', 'primary')
        self.btn_startstop.style().unpolish(self.btn_startstop)
        self.btn_startstop.style().polish(self.btn_startstop)
        self.update_status_badge()

    def stop_buttons_def(self):
        self.is_running = True
        self.btn_startstop.setText('Pausar Serviço')
        self.btn_startstop.setProperty('class', 'danger')
        self.btn_startstop.style().unpolish(self.btn_startstop)
        self.btn_startstop.style().polish(self.btn_startstop)
        self.update_status_badge()

    def checkbox_visibility_changed(self, state):
        if state != 2:
            self.visible = False
            self.start_buttons_def()
        else:
            self.visible = True
            self.show()

    def start_service(self):
        if not hasattr(self.gt, 'UI') or self.gt is None:
            self.gt = Gtray(self, logger)
        file_path = config['GTRAY']['k']
        if not os.path.isfile(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('')
        with open(file_path, 'r', encoding='utf-8') as f:
            self.apikey = f.read().strip()
            self.gt.change_key(self.apikey)

        self.stop_buttons_def()
        self.gt.start()
        self.autostart = False
        self.gt.run()

    def stop_service(self):
        self.start_buttons_def()
        if self.gt is not None:
            self.gt.stop()
            del self.gt
            self.gt = None
        self.autostart = True

    def startstop(self):
        if self.checkbox_visibility.isChecked():
            self.show()
        else:
            self.hide()

        if self.autostart is True:
            self.start_service()
        else:
            self.stop_service()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                self.setWindowState(Qt.WindowNoState)
                self.hide_UI()
                event.ignore()
                return
        super().changeEvent(event)

    def closeEvent(self, event):
        if self.gt is not None:
            self.gt.on_exit()
        event.accept()

    def hide_UI(self):
        logger.info('app no plano de fundo')
        self.hide()
        if not getattr(self, 'is_running', False):
            self.start_service()

    def show_UI(self):
        logger.info('app visivel')
        self.show()

    def cmd_start(self):
        self.startstop()


if __name__ == '__main__':
    pid = os.getpid()
    lastpid_path = 'cmd/lastpid.txt'
    if os.path.exists(lastpid_path):
        with open(lastpid_path, 'r', encoding='utf-8') as file:
            pid2 = file.read().strip()
        if pid2:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call(f'taskkill /f /FI "PID eq {pid2}"', creationflags=CREATE_NO_WINDOW)

    os.makedirs('cmd', exist_ok=True)
    with open(lastpid_path, 'w', encoding='utf-8') as file:
        file.write(f'{pid}')

    app = QApplication(sys.argv)
    ex = GTray_CFG_UI()
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "1":
            logger.info(f'main > {sys.argv[1]}')
            ex.visible = True
            ex.autostart = True
            ex.startstop()
            sys.exit(app.exec_())
        elif len(sys.argv) > 1 and sys.argv[1] == "2":
            logger.info(f'main > {sys.argv[1]}')
            ex.visible = False
            ex.autostart = True
            ex.checkbox_visibility.setChecked(ex.visible)
            ex.hide()
            ex.startstop()
            ex.gt.run()
        else:
            raise Exception
    except Exception:
        logger.info('main > UI')
        ex.visible = True
        ex.autostart = False
        ex.startstop()
        sys.exit(app.exec_())
    sys.exit(0)
