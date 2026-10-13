"""
preview_comboboxes.py - Demonstração visual interativa das 3 opções de ComboBox para o gTray.
Gera os ícones de chevron necessários e renderiza a janela de comparação.
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QFrame, QPushButton
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QPoint

def generate_chevron_icons():
    """Gera os ícones PNG de chevron na pasta assets/."""
    os.makedirs('assets', exist_ok=True)
    
    configs = [
        ('assets/chevron_neutral.png', '#94A3B8'),
        ('assets/chevron_cyan.png', '#38BDF8'),
        ('assets/chevron_white.png', '#F8FAFC')
    ]
    
    for path, hex_col in configs:
        pix = QPixmap(16, 16)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(hex_col), 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(QPoint(4, 6), QPoint(8, 10))
        p.drawLine(QPoint(8, 10), QPoint(12, 6))
        p.end()
        pix.save(path, 'PNG')

# Estilos QSS para as 3 opções
STYLE_BASE = """
QWidget {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    font-size: 13px;
}
QFrame[card="true"] {
    background-color: #162032;
    border: 1px solid #293548;
    border-radius: 10px;
    padding: 14px;
}
QLabel[class="title"] {
    font-size: 14px;
    font-weight: bold;
    color: #F8FAFC;
}
QLabel[class="subtitle"] {
    font-size: 11px;
    color: #94A3B8;
}
QLabel[class="badge"] {
    font-size: 10px;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
}
QLineEdit {
    background-color: #0B1120;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 12px;
    color: #94A3B8;
    font-size: 12px;
}
"""

STYLE_OPT1 = """
QComboBox#opt1 {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 34px 7px 12px;
    color: #F8FAFC;
    font-size: 12px;
    font-weight: 500;
}
QComboBox#opt1:hover {
    background-color: #273549;
    border: 1px solid #3B82F6;
}
QComboBox#opt1:focus, QComboBox#opt1:on {
    border: 1px solid #38BDF8;
}
QComboBox#opt1::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: none;
}
QComboBox#opt1::down-arrow {
    image: url(assets/chevron_neutral.png);
    width: 12px;
    height: 12px;
}
QComboBox#opt1 QAbstractItemView {
    background-color: #1E293B;
    border: 1px solid #334155;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    color: #F8FAFC;
    padding: 4px;
}
"""

STYLE_OPT2 = """
QComboBox#opt2 {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 7px 38px 7px 12px;
    color: #F8FAFC;
    font-size: 12px;
    font-weight: 600;
}
QComboBox#opt2:hover {
    background-color: #243044;
    border: 1px solid #64748B;
}
QComboBox#opt2:focus, QComboBox#opt2:on {
    border: 1px solid #2563EB;
}
QComboBox#opt2::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid #334155;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background-color: rgba(255, 255, 255, 0.03);
}
QComboBox#opt2::drop-down:hover {
    background-color: rgba(255, 255, 255, 0.08);
}
QComboBox#opt2::down-arrow {
    image: url(assets/chevron_white.png);
    width: 12px;
    height: 12px;
}
QComboBox#opt2 QAbstractItemView {
    background-color: #1E293B;
    border: 1px solid #475569;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    color: #F8FAFC;
    padding: 4px;
}
"""

STYLE_OPT3 = """
QComboBox#opt3 {
    background-color: #0B1120;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 34px 7px 12px;
    color: #F8FAFC;
    font-size: 12px;
}
QComboBox#opt3:hover {
    border: 1px solid #38BDF8;
    background-color: #10192A;
}
QComboBox#opt3:focus, QComboBox#opt3:on {
    border: 1px solid #38BDF8;
    background-color: #0B1120;
}
QComboBox#opt3::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: none;
}
QComboBox#opt3::down-arrow {
    image: url(assets/chevron_cyan.png);
    width: 12px;
    height: 12px;
}
QComboBox#opt3 QAbstractItemView {
    background-color: #0B1120;
    border: 1px solid #38BDF8;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    color: #F8FAFC;
    padding: 4px;
}
"""

class PreviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("gTray - Comparativo de ComboBoxes")
        self.setFixedWidth(640)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Cabeçalho
        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        lbl_h = QLabel("Comparativo Visual de ComboBoxes")
        lbl_h.setProperty("class", "title")
        lbl_sub = QLabel("Passe o mouse e clique para testar o comportamento de cada opção:")
        lbl_sub.setProperty("class", "subtitle")
        header_box.addWidget(lbl_h)
        header_box.addWidget(lbl_sub)
        layout.addLayout(header_box)

        # Itens de exemplo
        models = ["deepseek-flash", "gpt-4o-mini", "claude-3-5-sonnet", "llama-3.1-70b"]

        # Card Opção 1
        card1 = QFrame()
        card1.setProperty("card", "true")
        l1 = QVBoxLayout(card1)
        l1.setSpacing(8)
        
        h1 = QHBoxLayout()
        t1 = QLabel("Opção 1: Moderno com Chevron Suave (Recomendada)")
        t1.setStyleSheet("font-weight: bold; color: #38BDF8;")
        b1 = QLabel("RECOMENDADA")
        b1.setProperty("class", "badge")
        b1.setStyleSheet("background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; font-weight: bold; border-radius: 4px; padding: 2px 6px;")
        h1.addWidget(t1)
        h1.addStretch()
        h1.addWidget(b1)
        l1.addLayout(h1)

        desc1 = QLabel("Fundo de superfície (#1E293B) distinguindo-o de inputs, chevron sutil e hover azul.")
        desc1.setProperty("class", "subtitle")
        l1.addWidget(desc1)

        row1 = QHBoxLayout()
        row1.setSpacing(12)
        cb1 = QComboBox()
        cb1.setObjectName("opt1")
        cb1.addItems(models)
        cb1.setCursor(Qt.PointingHandCursor)
        txt1 = QLineEdit("Texto comum (input)")
        txt1.setReadOnly(True)
        row1.addWidget(cb1, stretch=3)
        row1.addWidget(txt1, stretch=2)
        l1.addLayout(row1)
        layout.addWidget(card1)

        # Card Opção 2
        card2 = QFrame()
        card2.setProperty("card", "true")
        l2 = QVBoxLayout(card2)
        l2.setSpacing(8)
        
        h2 = QHBoxLayout()
        t2 = QLabel("Opção 2: Botão Seletor com Divisor Lateral")
        t2.setStyleSheet("font-weight: bold; color: #F1F5F9;")
        b2 = QLabel("ESTILO BOTÃO")
        b2.setStyleSheet("background-color: rgba(148, 163, 184, 0.15); color: #94A3B8; font-weight: bold; border-radius: 4px; padding: 2px 6px;")
        h2.addWidget(t2)
        h2.addStretch()
        h2.addWidget(b2)
        l2.addLayout(h2)

        desc2 = QLabel("Aparência de botão com linha divisória lateral explícita na área do chevron.")
        desc2.setProperty("class", "subtitle")
        l2.addWidget(desc2)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        cb2 = QComboBox()
        cb2.setObjectName("opt2")
        cb2.addItems(models)
        cb2.setCursor(Qt.PointingHandCursor)
        txt2 = QLineEdit("Texto comum (input)")
        txt2.setReadOnly(True)
        row2.addWidget(cb2, stretch=3)
        row2.addWidget(txt2, stretch=2)
        l2.addLayout(row2)
        layout.addWidget(card2)

        # Card Opção 3
        card3 = QFrame()
        card3.setProperty("card", "true")
        l3 = QVBoxLayout(card3)
        l3.setSpacing(8)
        
        h3 = QHBoxLayout()
        t3 = QLabel("Opção 3: Minimalista com Chevron Ciano Neon")
        t3.setStyleSheet("font-weight: bold; color: #22D3EE;")
        b3 = QLabel("NEON / ACENTO")
        b3.setStyleSheet("background-color: rgba(34, 211, 238, 0.15); color: #22D3EE; font-weight: bold; border-radius: 4px; padding: 2px 6px;")
        h3.addWidget(t3)
        h3.addStretch()
        h3.addWidget(b3)
        l3.addLayout(h3)

        desc3 = QLabel("Mantém o fundo escuro original (#0B1120), destacando o chevron em ciano neon.")
        desc3.setProperty("class", "subtitle")
        l3.addWidget(desc3)

        row3 = QHBoxLayout()
        row3.setSpacing(12)
        cb3 = QComboBox()
        cb3.setObjectName("opt3")
        cb3.addItems(models)
        cb3.setCursor(Qt.PointingHandCursor)
        txt3 = QLineEdit("Texto comum (input)")
        txt3.setReadOnly(True)
        row3.addWidget(cb3, stretch=3)
        row3.addWidget(txt3, stretch=2)
        l3.addLayout(row3)
        layout.addWidget(card3)

        self.setStyleSheet(STYLE_BASE + STYLE_OPT1 + STYLE_OPT2 + STYLE_OPT3)

def capture_preview_image(output_path):
    """Renderiza a janela e salva uma imagem em alta resolução."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    generate_chevron_icons()
    win = PreviewWindow()
    win.adjustSize()
    win.show()
    app.processEvents()
    pix = win.grab()
    pix.save(output_path, 'PNG')
    win.close()
    return output_path

if __name__ == '__main__':
    # Inicializa o QApplication antes de criar recursos gráficos e a janela
    app = QApplication(sys.argv)
    generate_chevron_icons()
    win = PreviewWindow()
    win.show()
    sys.exit(app.exec_())