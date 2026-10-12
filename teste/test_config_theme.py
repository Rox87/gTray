import unittest
import configparser
import os
import tempfile

class TestConfigTheme(unittest.TestCase):
    def test_theme_fallback_when_absent(self):
        cp = configparser.ConfigParser()
        cp.read_string("[GTRAY]\nheader_title=GTray\n")
        theme = cp.get('GTRAY', 'tema', fallback='dark')
        self.assertEqual(theme, 'dark')

    def test_theme_read_and_write(self):
        with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.ini', encoding='utf-8') as f:
            f.write("[GTRAY]\nheader_title=GTray\ntema=light\n")
            temp_path = f.name
        try:
            cp = configparser.ConfigParser()
            cp.read(temp_path, encoding='utf-8')
            self.assertEqual(cp.get('GTRAY', 'tema'), 'light')
            
            cp.set('GTRAY', 'tema', 'dark')
            with open(temp_path, 'w', encoding='utf-8') as f:
                cp.write(f)
                
            cp2 = configparser.ConfigParser()
            cp2.read(temp_path, encoding='utf-8')
            self.assertEqual(cp2.get('GTRAY', 'tema'), 'dark')
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
