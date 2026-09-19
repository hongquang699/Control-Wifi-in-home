"""
Hệ thống Đa ngôn ngữ (i18n / Internationalization): Tiếng Việt (vi) & Tiếng Anh (en).
Được module hóa tách biệt từ điển và bộ quản lý ngôn ngữ.
"""

import json
import os
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal

from core.i18n.locales.vi import VI_TRANSLATIONS
from core.i18n.locales.en import EN_TRANSLATIONS

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "vi": VI_TRANSLATIONS,
    "en": EN_TRANSLATIONS,
}

class TranslationManager(QObject):
    language_changed = Signal(str)
    _instance: Optional["TranslationManager"] = None

    def __init__(self):
        super().__init__()
        self.current_lang = "vi"
        self._load_saved_language()

    @classmethod
    def get_instance(cls) -> "TranslationManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_config_path(self) -> str:
        if os.path.exists("config/config.json"):
            return "config/config.json"
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target = os.path.join(app_root, "config", "config.json")
        if os.path.exists(target):
            return target
        return "config/config.json"

    def _load_saved_language(self):
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.current_lang = cfg.get("ui", {}).get("language", "vi")
            except Exception:
                self.current_lang = "vi"

    def set_language(self, lang: str):
        if lang in ("vi", "en") and lang != self.current_lang:
            self.current_lang = lang
            try:
                config_path = self._get_config_path()
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    cfg.setdefault("ui", {})["language"] = lang
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            self.language_changed.emit(self.current_lang)

    def translate(self, key: str, **kwargs) -> str:
        dict_lang = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["vi"])
        text = dict_lang.get(key, TRANSLATIONS["vi"].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

# Singleton instance & shorthand function
i18n = TranslationManager.get_instance()

def t(key: str, **kwargs) -> str:
    return i18n.translate(key, **kwargs)

__all__ = ["TRANSLATIONS", "TranslationManager", "i18n", "t"]
