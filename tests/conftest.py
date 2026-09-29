import os
import sys
from types import ModuleType
import yaml

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Global test isolation fixture / setup
# ---------------------------------------------------------------------------
# 1. Stub out configs.load_configs using configs.example.yml (tracked in git)
#    so tests never depend on local configs.yml or generated configs.generated.yml.
# 2. Stub out get_accounts to avoid dependency on TWITTER_TOKEN env var.
# ---------------------------------------------------------------------------

if 'configs.load_configs' not in sys.modules:
    example_cfg_path = os.path.join(PROJECT_ROOT, 'configs.example.yml')
    with open(example_cfg_path, 'r', encoding='utf-8') as f:
        fake_configs = yaml.safe_load(f)

    fake_mod = ModuleType('configs.load_configs')
    fake_mod.configs = fake_configs
    fake_mod.FX_SETTINGS = fake_configs['embed']['built_in']['fx']
    fake_mod.IS_TRANSLATION_ENABLED = (
        fake_mod.FX_SETTINGS['auto_translation']
        if fake_configs['embed']['type'] == 'built_in'
        else fake_configs['embed']['proxy']['auto_translation']
    )
    sys.modules['configs.load_configs'] = fake_mod

import src.utils
if not hasattr(src.utils, '_original_get_accounts'):
    src.utils._original_get_accounts = src.utils.get_accounts
    src.utils.get_accounts = lambda: {'test_account': 'fake_token'}
