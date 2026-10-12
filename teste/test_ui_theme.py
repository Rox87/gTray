import unittest
from ui_theme import get_theme_stylesheet, get_status_badge_style

class TestUITheme(unittest.TestCase):
    def test_dark_stylesheet_contains_palette(self):
        qss = get_theme_stylesheet('dark')
        self.assertIn('#0F172A', qss.upper())
        self.assertIn('QPushButton', qss)
        self.assertIn('QLineEdit', qss)

    def test_light_stylesheet_contains_palette(self):
        qss = get_theme_stylesheet('light')
        self.assertIn('#F8FAFC', qss.upper())
        self.assertIn('QPushButton', qss)

    def test_fallback_to_dark_for_unknown_theme(self):
        qss = get_theme_stylesheet('unknown_theme')
        self.assertEqual(qss, get_theme_stylesheet('dark'))

    def test_status_badge_styles(self):
        active_style = get_status_badge_style(True, 'dark')
        self.assertIn('#22C55E', active_style.upper())
        inactive_style = get_status_badge_style(False, 'dark')
        self.assertTrue('#94A3B8' in inactive_style.upper() or '#EF4444' in inactive_style.upper())

if __name__ == '__main__':
    unittest.main()
