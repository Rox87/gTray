import unittest
from unittest.mock import MagicMock, patch
from handler import Gtray
from pessoal.IA import IA

class TestSystemPromptIntegration(unittest.TestCase):
    @patch('handler.Image.open')
    @patch('handler.pystray.Icon')
    @patch('handler.win32gui.GetForegroundWindow', return_value=123)
    def test_handler_uses_system_prompt_from_shortcut(self, mock_fg, mock_icon, mock_img):
        gtray = Gtray(logger_from=MagicMock())
        gtray.Engineer = MagicMock()
        gtray.Engineer.pre_processamento.return_value = "Texto selecionado pelo usuario"
        gtray.AI = MagicMock()
        gtray.AI.responder.return_value = "Texto processado"

        # Mock resolve_shortcut com system_prompt customizado
        gtray.data_manager = MagicMock()
        gtray.data_manager.resolve_shortcut.return_value = {
            'api_key': 'test_key',
            'model_name': 'test_model',
            'base_url': None,
            'system_prompt': 'Traduza para espanhol'
        }

        gtray.handle_ai_request('custom_shortcut')

        gtray.AI.responder.assert_called_once_with(
            "Texto selecionado pelo usuario",
            "Traduza para espanhol",
            mode="custom_shortcut",
            model_override="test_model"
        )
        gtray.Engineer.pos_processamento.assert_called_once_with(
            "Texto selecionado pelo usuario",
            "Texto processado"
        )

    @patch('handler.Image.open')
    @patch('handler.pystray.Icon')
    @patch('handler.win32gui.GetForegroundWindow', return_value=123)
    def test_handler_falls_back_to_prompt_modifier_when_empty(self, mock_fg, mock_icon, mock_img):
        gtray = Gtray(logger_from=MagicMock())
        gtray.Engineer = MagicMock()
        gtray.Engineer.pre_processamento.return_value = "Texto"
        gtray.AI = MagicMock()
        gtray.AI.responder.return_value = "Resp"

        gtray.data_manager = MagicMock()
        gtray.data_manager.resolve_shortcut.return_value = {
            'api_key': 'key',
            'model_name': 'model',
            'base_url': None,
            'system_prompt': ''
        }

        gtray.handle_ai_request('upgrade', prompt_modifier="Modificador padrao")

        gtray.AI.responder.assert_called_once_with(
            "Texto",
            "Modificador padrao",
            mode="upgrade",
            model_override="model"
        )

    @patch('pessoal.IA.OpenAI')
    def test_ia_responder_builds_messages_correctly(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message.content = "Resposta da IA"
        mock_client.chat.completions.create.return_value = mock_resp

        logger_mock = MagicMock()
        ia = IA(key="test", logger_from=logger_mock)
        ia.client = mock_client

        # Chamada com system prompt
        res = ia.responder("Meu texto", cmd="Instrução do sistema", model_override="gpt-4o")
        self.assertEqual(res, "Resposta da IA")
        called_messages = mock_client.chat.completions.create.call_args[1]['messages']
        self.assertEqual(len(called_messages), 2)
        self.assertEqual(called_messages[0], {"role": "system", "content": "Instrução do sistema"})
        self.assertEqual(called_messages[1], {"role": "user", "content": "Meu texto"})

        # Chamada sem system prompt
        ia.responder("Meu texto", cmd="", model_override="gpt-4o")
        called_messages_empty = mock_client.chat.completions.create.call_args[1]['messages']
        self.assertEqual(len(called_messages_empty), 1)
        self.assertEqual(called_messages_empty[0], {"role": "user", "content": "Meu texto"})

if __name__ == '__main__':
    unittest.main()
