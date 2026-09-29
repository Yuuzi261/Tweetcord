import os
import re
import yaml
import unittest
import sys

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.i18n import init_i18n, t

LOCALES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locales'))
BASE_LOCALE = 'en.yml'

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def collect_keys_with_vars(data, prefix=''):
    """Recursively collect all keys and their format variables."""
    items = {}
    for k, v in data.items():
        full_key = f'{prefix}.{k}' if prefix else k
        if isinstance(v, dict):
            items.update(collect_keys_with_vars(v, full_key))
        elif isinstance(v, str):
            # Find all {variable} patterns
            vars_found = set(re.findall(r'\{(\w+)\}', v))
            items[full_key] = vars_found
    return items

class TestI18n(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.join(LOCALES_DIR, BASE_LOCALE)
        cls.base_data = load_yaml(cls.base_path)
        cls.base_keys_map = collect_keys_with_vars(cls.base_data)
        
        # Get all other locale files
        cls.target_files = [
            f for f in os.listdir(LOCALES_DIR) 
            if f.endswith('.yml') and f != BASE_LOCALE
        ]

    def test_all_locales_parity(self):
        """Check all locale files for key parity and variable consistency against en.yml."""
        for filename in self.target_files:
            with self.subTest(locale=filename):
                target_path = os.path.join(LOCALES_DIR, filename)
                target_data = load_yaml(target_path)
                target_keys_map = collect_keys_with_vars(target_data)

                # Key Parity Check
                missing_keys = set(self.base_keys_map.keys()) - set(target_keys_map.keys())
                extra_keys = set(target_keys_map.keys()) - set(self.base_keys_map.keys())

                msg = []
                if missing_keys:
                    msg.append(f"\n  Missing keys in {filename}: {sorted(list(missing_keys))}")
                if extra_keys:
                    msg.append(f"\n  Redundant keys in {filename}: {sorted(list(extra_keys))}")

                # Variable Consistency Check
                for key in set(self.base_keys_map.keys()) & set(target_keys_map.keys()):
                    base_vars = self.base_keys_map[key]
                    target_vars = target_keys_map[key]
                    if base_vars != target_vars:
                        msg.append(
                            f"\n  Variable mismatch at '{key}' in {filename}: "
                            f"Base has {base_vars or 'none'}, Target has {target_vars or 'none'}"
                        )

                if msg:
                    self.fail("".join(msg))

    def test_interpolation_logic(self):
        """Verify that the t() function handles interpolation correctly."""
        init_i18n('en')
        result = t('list.footer', page=1, total=99)
        self.assertEqual(result, 'Page 1 of 99')

    def test_fallback_logic(self):
        """Verify fallback to English when a locale file is missing."""
        with self.assertLogs('src.i18n', level='INFO') as cm:
            init_i18n('nonexistent')
            self.assertTrue(len(t('display.action.tweeted')) > 0)
        
        self.assertIn("falling back to 'en'", cm.output[0])


if __name__ == '__main__':
    unittest.main()
