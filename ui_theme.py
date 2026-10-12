"""
ui_theme.py - Módulo de tema e estilo QSS escuro para o gTray.
Fornece paleta Dark e folha de estilo moderna.
"""

from typing import Dict, Any

PALETTES: Dict[str, Dict[str, str]] = {
    'dark': {
        'window_bg': '#0F172A',
        'card_bg': '#1E293B',
        'inner_bg': '#0B1120',
        'border': '#334155',
        'border_focus': '#3B82F6',
        'text_primary': '#F8FAFC',
        'text_secondary': '#94A3B8',
        'btn_primary_bg': '#2563EB',
        'btn_primary_hover': '#1D4ED8',
        'btn_primary_text': '#FFFFFF',
        'btn_danger_bg': '#DC2626',
        'btn_danger_hover': '#B91C1C',
        'btn_danger_text': '#FFFFFF',
        'btn_neutral_bg': '#1E293B',
        'btn_neutral_hover': '#334155',
        'btn_neutral_text': '#F1F5F9',
        'input_bg': '#0B1120',
        'input_disabled_bg': '#161F30',
        'input_text': '#F8FAFC',
        'status_active_bg': 'rgba(34, 197, 94, 0.15)',
        'status_active_text': '#22C55E',
        'status_inactive_bg': 'rgba(239, 68, 68, 0.15)',
        'status_inactive_text': '#EF4444',
        'accent': '#38BDF8',
    }
}

def get_theme_stylesheet(theme_name: str = 'dark') -> str:
    """Retorna a folha de estilo QSS para o tema escuro."""
    p = PALETTES['dark']
    
    return f"""
    /* Janela e Base */
    QWidget {{
        background-color: {p['window_bg']};
        color: {p['text_primary']};
        font-family: 'Segoe UI', -apple-system, sans-serif;
        font-size: 13px;
    }}

    /* Tabs (QTabWidget e QTabBar) */
    QTabWidget::pane {{
        border: 1px solid {p['border']};
        background-color: {p['card_bg']};
        border-radius: 8px;
        padding: 6px;
    }}

    QTabBar::tab {{
        background-color: transparent;
        color: {p['text_secondary']};
        padding: 6px 12px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-weight: 600;
        font-size: 11px;
    }}

    QTabBar::tab:selected {{
        color: {p['text_primary']};
        background-color: {p['card_bg']};
        border-top: 2px solid {p['btn_primary_bg']};
    }}

    QTabBar::tab:hover {{
        color: {p['text_primary']};
    }}

    /* Cards e Containers */
    QFrame[card="true"] {{
        background-color: {p['card_bg']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 12px;
    }}

    /* Labels e Tipografia */
    QLabel {{
        background-color: transparent;
        color: {p['text_primary']};
    }}

    QLabel[class="headerTitle"] {{
        font-size: 16px;
        font-weight: bold;
        color: {p['text_primary']};
    }}

    QLabel[class="headerSubtitle"] {{
        font-size: 11px;
        color: {p['text_secondary']};
    }}

    QLabel[class="sectionHeader"] {{
        font-size: 11px;
        font-weight: 600;
        color: {p['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    QLabel[class="badgeDisplay"] {{
        background-color: {p['inner_bg']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 6px 10px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-weight: bold;
        font-size: 12px;
        color: {p['accent']};
    }}

    QLabel[class="flashSuccess"] {{
        background-color: rgba(34, 197, 94, 0.18);
        border: 1px solid #22C55E;
        border-radius: 6px;
        padding: 4px 10px;
        font-weight: 600;
        font-size: 12px;
        color: #4ADE80;
    }}

    QLabel[class="flashWarning"] {{
        background-color: rgba(239, 68, 68, 0.18);
        border: 1px solid #EF4444;
        border-radius: 6px;
        padding: 4px 10px;
        font-weight: 600;
        font-size: 12px;
        color: #F87171;
    }}

    /* Campos de Entrada (QLineEdit, QPlainTextEdit, QTextEdit) */
    QLineEdit, QPlainTextEdit, QTextEdit {{
        background-color: {p['input_bg']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 6px 10px;
        color: {p['input_text']};
        font-size: 12px;
        selection-background-color: {p['btn_primary_bg']};
    }}

    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
        border: 1px solid {p['border_focus']};
    }}

    QLineEdit:disabled, QPlainTextEdit:disabled, QTextEdit:disabled {{
        background-color: {p['input_disabled_bg']};
        color: {p['text_secondary']};
        border: 1px solid {p['border']};
    }}

    /* ComboBox */
    QComboBox {{
        background-color: {p['input_bg']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 5px 10px;
        color: {p['text_primary']};
        font-size: 12px;
    }}

    QComboBox:focus {{
        border: 1px solid {p['border_focus']};
    }}

    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: none;
    }}

    QComboBox QAbstractItemView {{
        background-color: {p['card_bg']};
        border: 1px solid {p['border']};
        selection-background-color: {p['btn_primary_bg']};
        selection-color: #FFFFFF;
        color: {p['text_primary']};
        padding: 4px;
    }}

    /* Botões */
    QPushButton {{
        background-color: {p['btn_neutral_bg']};
        color: {p['btn_neutral_text']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {p['btn_neutral_hover']};
    }}

    QPushButton:pressed {{
        background-color: {p['border']};
    }}

    QPushButton[class="primary"] {{
        background-color: {p['btn_primary_bg']};
        color: {p['btn_primary_text']};
        border: none;
        font-weight: 600;
    }}

    QPushButton[class="primary"]:hover {{
        background-color: {p['btn_primary_hover']};
    }}

    QPushButton[class="danger"] {{
        background-color: {p['btn_danger_bg']};
        color: {p['btn_danger_text']};
        border: none;
        font-weight: 600;
    }}

    QPushButton[class="danger"]:hover {{
        background-color: {p['btn_danger_hover']};
    }}

    QPushButton[class="iconBtn"] {{
        padding: 4px 8px;
        font-size: 13px;
    }}

    /* CheckBox */
    QCheckBox {{
        background-color: transparent;
        color: {p['text_secondary']};
        font-size: 11px;
        spacing: 6px;
    }}

    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border-radius: 3px;
        border: 1px solid {p['border']};
        background-color: {p['input_bg']};
    }}

    QCheckBox::indicator:checked {{
        background-color: {p['btn_primary_bg']};
        border-color: {p['btn_primary_bg']};
    }}
    """

def get_status_badge_style(is_active: bool, theme_name: str = 'dark') -> str:
    """Retorna o estilo inline para a badge de status (Ativo / Pausado)."""
    p = PALETTES['dark']
    
    if is_active:
        return f"""
        background-color: {p['status_active_bg']};
        color: {p['status_active_text']};
        border-radius: 10px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: bold;
        """
    else:
        return f"""
        background-color: {p['status_inactive_bg']};
        color: {p['status_inactive_text']};
        border-radius: 10px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: bold;
        """
