import unittest
import sys
import os
from PyQt5.QtWidgets import QApplication, QLineEdit

class TestGTrayUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Cria a aplicação Qt em modo headless/offscreen para testes
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_theme_is_dark_and_no_toggle(self):
        from GTray import GTray_CFG_UI
        ui = GTray_CFG_UI()
        self.assertEqual(ui.current_theme, 'dark')
        self.assertFalse(hasattr(ui, 'btn_theme_toggle'))
        self.assertIn('#0F172A', ui.styleSheet().upper())
        ui.close()

    def test_api_key_visibility_toggle(self):
        from GTray import GTray_CFG_UI
        ui = GTray_CFG_UI()
        self.assertEqual(ui.input_provider_key.echoMode(), QLineEdit.Password)
        ui.toggle_apikey_visibility()
        self.assertEqual(ui.input_provider_key.echoMode(), QLineEdit.Normal)
        ui.toggle_apikey_visibility()
        self.assertEqual(ui.input_provider_key.echoMode(), QLineEdit.Password)
        ui.close()

    def test_tabs_and_crud_workflow(self):
        from GTray import GTray_CFG_UI
        ui = GTray_CFG_UI()
        
        # 3 Abas devem existir
        self.assertEqual(ui.tabs.count(), 3)
        self.assertEqual(ui.tabs.tabText(0), "⚡ Atalhos")
        self.assertEqual(ui.tabs.tabText(1), "🤖 Modelos")
        self.assertEqual(ui.tabs.tabText(2), "🔑 Provedores")

        # 1. Salvar Provedor (nome e chave)
        ui.input_provider_name.setText('groq_test')
        ui.input_provider_key.setText('gsk-test-key')
        ui.save_provider(show_msg=False)
        self.assertIn('groq_test', ui.data_manager.get_providers())

        # 2. Salvar Modelo (nome e provedor)
        ui.input_model_name.setText('llama-test')
        ui.combo_model_provider.setCurrentText('groq_test')
        ui.save_model(show_msg=False)
        self.assertIn('llama-test', ui.data_manager.get_models())
        self.assertEqual(ui.data_manager.get_model_provider('llama-test'), 'groq_test')

        # 3. Salvar Atalho (nome, tecla e modelo)
        ui.input_shortcut_name.setText('custom_test')
        ui.lbl_shortcut_key.setText('Ctrl+Alt+T')
        ui.combo_shortcut_model.setCurrentText('llama-test')
        ui.save_shortcut(show_msg=False)

        resolved = ui.data_manager.resolve_shortcut('custom_test')
        self.assertEqual(resolved['key'], 'Ctrl+Alt+T')
        self.assertEqual(resolved['model_name'], 'llama-test')
        self.assertEqual(resolved['provider_name'], 'groq_test')
        self.assertEqual(resolved['api_key'], 'gsk-test-key')
        
        # Limpa dados de teste
        ui.data_manager.delete_shortcut('custom_test')
        ui.data_manager.delete_model('llama-test')
        ui.data_manager.delete_provider('groq_test')
        test_cfg = os.path.join('assets', 'shortcut_custom_test.cfg')
        if os.path.exists(test_cfg):
            os.remove(test_cfg)

        ui.close()

if __name__ == '__main__':
    unittest.main()
