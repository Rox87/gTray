"""
gtray_data_manager.py - Gerenciador de Dados do gTray.
Organiza e persiste:
1. Provedor (nome e chave)
2. Modelo (nome e provedor)
3. Atalho (nome, tecla e modelo)
"""

import json
import os
from typing import Dict, Any, Optional

DEFAULT_DATA_PATH = os.path.join('assets', 'gtray_data.json')

DEFAULT_PROVIDER_BASE_URLS: Dict[str, str] = {
    'openai': 'https://api.openai.com/v1',
    'deepseek': 'https://api.deepseek.com',
    'groq': 'https://api.groq.com/openai/v1',
    'openrouter': 'https://openrouter.ai/api/v1',
    'ollama': 'http://localhost:11434/v1',
    'together': 'https://api.together.xyz/v1',
    'mistral': 'https://api.mistral.ai/v1',
    'gemini': 'https://generativelanguage.googleapis.com/v1beta/openai/',
    'google': 'https://generativelanguage.googleapis.com/v1beta/openai/',
}

class GTrayDataManager:
    def __init__(self, filepath: str = DEFAULT_DATA_PATH, sync_legacy: bool = True):
        self.filepath = filepath
        self.sync_legacy = sync_legacy
        self.data: Dict[str, Any] = {
            "providers": {},
            "models": {},
            "shortcuts": {}
        }
        self.load()

    def _init_defaults(self):
        """Inicializa configurações padrão caso o arquivo não exista."""
        # Chave padrão da OpenAI se existir k.cfg
        default_key = ""
        k_path = os.path.join('assets', 'k.cfg')
        if os.path.isfile(k_path):
            try:
                with open(k_path, 'r', encoding='utf-8') as f:
                    default_key = f.read().strip()
            except Exception:
                pass

        self.data = {
            "providers": {
                "openai": {"api_key": default_key}
            },
            "models": {
                "gpt-4o-mini": {"provider": "openai"},
                "gpt-4o": {"provider": "openai"}
            },
            "shortcuts": {
                "upgrade": {
                    "key": self._read_legacy_shortcut("upgrade", "F9"),
                    "model": "gpt-4o-mini",
                    "system_prompt": "Não responda o usuario, retorne apenas, sem rodeios, a própria entrada do usuário melhorada",
                    "extract_blocks": False,
                    "comment_char": "#",
                    "enabled": True
                },
                "generic": {
                    "key": self._read_legacy_shortcut("generic", "F7+CTRL+X"),
                    "model": "gpt-4o-mini",
                    "system_prompt": "",
                    "extract_blocks": False,
                    "comment_char": "#",
                    "enabled": True
                },
                "python": {
                    "key": self._read_legacy_shortcut("python", "F10"),
                    "model": "gpt-4o-mini",
                    "system_prompt": "",
                    "extract_blocks": False,
                    "comment_char": "#",
                    "enabled": True
                },
                "creation": {
                    "key": self._read_legacy_shortcut("creation", "F11"),
                    "model": "gpt-4o-mini",
                    "system_prompt": "",
                    "extract_blocks": False,
                    "comment_char": "#",
                    "enabled": True
                }
            }
        }
        self.save()

    def _read_legacy_shortcut(self, name: str, fallback: str) -> str:
        sc_path = os.path.join('assets', f'shortcut_{name}.cfg')
        if os.path.isfile(sc_path):
            try:
                with open(sc_path, 'r', encoding='utf-8') as f:
                    val = f.read().strip()
                    if val:
                        return val
            except Exception:
                pass
        return fallback

    def load(self):
        if os.path.isfile(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                if "providers" not in self.data:
                    self.data["providers"] = {}
                if "models" not in self.data:
                    self.data["models"] = {}
                if "shortcuts" not in self.data:
                    self.data["shortcuts"] = {}
            except Exception:
                self._init_defaults()
        else:
            self._init_defaults()

    def save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        if self.sync_legacy:
            self.sync_legacy_files()

    def sync_legacy_files(self):
        """Sincroniza arquivos legados (assets/shortcut_*.cfg e assets/k.cfg) para compatibilidade."""
        try:
            # Sincroniza atalhos legados
            for name, item in self.data.get("shortcuts", {}).items():
                sc_path = os.path.join('assets', f'shortcut_{name}.cfg')
                key_combo = item.get("key", "")
                with open(sc_path, 'w', encoding='utf-8') as f:
                    f.write(key_combo)

            # Sincroniza chave padrão da openai se existir
            openai_key = self.get_provider_key("openai")
            if openai_key is not None:
                k_path = os.path.join('assets', 'k.cfg')
                with open(k_path, 'w', encoding='utf-8') as f:
                    f.write(openai_key)
        except Exception:
            pass

    # -------------------------------------------------------------
    # 1. Provedor (nome e chave)
    # -------------------------------------------------------------
    def get_providers(self) -> Dict[str, Dict[str, str]]:
        return self.data.get("providers", {})

    def get_provider_key(self, name: str) -> Optional[str]:
        p = self.data.get("providers", {}).get(name)
        if p and "api_key" in p:
            return p["api_key"]
        return None

    def get_provider_base_url(self, name: str) -> Optional[str]:
        p = self.data.get("providers", {}).get(name)
        if p and "base_url" in p and p["base_url"]:
            return p["base_url"].strip()
        return DEFAULT_PROVIDER_BASE_URLS.get(name.lower().strip())

    def set_provider(self, name: str, api_key: str, base_url: Optional[str] = None):
        name = name.strip()
        if not name:
            return
        if "providers" not in self.data:
            self.data["providers"] = {}
        prov_dict = {"api_key": api_key.strip()}
        if base_url and base_url.strip():
            prov_dict["base_url"] = base_url.strip()
        self.data["providers"][name] = prov_dict
        self.save()

    def delete_provider(self, name: str):
        if name in self.data.get("providers", {}):
            del self.data["providers"][name]
            self.save()

    # -------------------------------------------------------------
    # 2. Modelo (nome e provedor)
    # -------------------------------------------------------------
    def get_models(self) -> Dict[str, Dict[str, str]]:
        return self.data.get("models", {})

    def get_model_provider(self, name: str) -> Optional[str]:
        m = self.data.get("models", {}).get(name)
        if m and "provider" in m:
            return m["provider"]
        return None

    def set_model(self, name: str, provider: str):
        name = name.strip()
        provider = provider.strip()
        if not name or not provider:
            return
        if "models" not in self.data:
            self.data["models"] = {}
        self.data["models"][name] = {"provider": provider}
        self.save()

    def delete_model(self, name: str):
        if name in self.data.get("models", {}):
            del self.data["models"][name]
            self.save()

    # -------------------------------------------------------------
    # 3. Atalho (nome, tecla e modelo)
    # -------------------------------------------------------------
    def get_shortcuts(self) -> Dict[str, Dict[str, str]]:
        return self.data.get("shortcuts", {})

    def get_shortcut(self, name: str) -> Optional[Dict[str, Any]]:
        sc = self.data.get("shortcuts", {}).get(name)
        if sc is not None:
            if "system_prompt" not in sc:
                if name == "upgrade":
                    sc["system_prompt"] = "Não responda o usuario, retorne apenas, sem rodeios, a própria entrada do usuário melhorada"
                else:
                    sc["system_prompt"] = ""
            if "extract_blocks" not in sc:
                sc["extract_blocks"] = False
            if "comment_char" not in sc:
                sc["comment_char"] = "#"
            if "enabled" not in sc:
                sc["enabled"] = True
        return sc

    def set_shortcut(self, name: str, key: str, model: str, system_prompt: str = "",
                     extract_blocks: bool = False, comment_char: str = "#", enabled: bool = True):
        name = name.strip()
        key = key.strip()
        model = model.strip()
        system_prompt = system_prompt.strip()
        comment_char = (comment_char or "#").strip()
        if not comment_char:
            comment_char = "#"
        if not name:
            return
        if "shortcuts" not in self.data:
            self.data["shortcuts"] = {}
        self.data["shortcuts"][name] = {
            "key": key,
            "model": model,
            "system_prompt": system_prompt,
            "extract_blocks": bool(extract_blocks),
            "comment_char": comment_char,
            "enabled": bool(enabled)
        }
        self.save()

    def delete_shortcut(self, name: str):
        if name in self.data.get("shortcuts", {}):
            del self.data["shortcuts"][name]
            self.save()

    # -------------------------------------------------------------
    # Resolução Completa da Cadeia: Atalho -> Modelo -> Provedor -> Chave
    # -------------------------------------------------------------
    def resolve_shortcut(self, shortcut_name: str) -> Dict[str, Any]:
        sc = self.get_shortcut(shortcut_name) or {}
        key = sc.get("key", "")
        model_name = sc.get("model", "")
        system_prompt = sc.get("system_prompt", "")
        extract_blocks = sc.get("extract_blocks", False)
        comment_char = sc.get("comment_char", "#")
        enabled = sc.get("enabled", True)
        
        provider_name = self.get_model_provider(model_name) or "openai"
        api_key = self.get_provider_key(provider_name) or ""
        base_url = self.get_provider_base_url(provider_name)

        return {
            "shortcut_name": shortcut_name,
            "key": key,
            "model_name": model_name,
            "provider_name": provider_name,
            "api_key": api_key,
            "base_url": base_url,
            "system_prompt": system_prompt,
            "extract_blocks": extract_blocks,
            "comment_char": comment_char,
            "enabled": enabled
        }
