import os
from typing import Any

import yaml

from src.log import setup_logger

log = setup_logger(__name__)

_translations: dict[str, Any] = {}


def _load_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def init_i18n(lang: str = 'en') -> None:
    global _translations
    locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
    en_path = os.path.join(locales_dir, 'en.yml')
    _translations = _load_yaml(en_path)

    if lang != 'en':
        lang_path = os.path.join(locales_dir, f'{lang}.yml')
        if os.path.isfile(lang_path):
            lang_data = _load_yaml(lang_path)
            _translations = _deep_merge(_translations, lang_data)
        else:
            log.warning(f"i18n: locale file '{lang}.yml' not found, falling back to 'en'")


def t(key: str, **kwargs) -> str:
    parts = key.split('.')
    node: Any = _translations
    for part in parts:
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            log.warning(f"i18n: missing translation key '{key}'")
            return key
    if not isinstance(node, str):
        log.warning(f"i18n: key '{key}' does not resolve to a string")
        return key
    if kwargs:
        try:
            return node.format_map(kwargs)
        except KeyError as e:
            log.warning(f"i18n: missing interpolation variable {e} for key '{key}'")
            return node
    return node
