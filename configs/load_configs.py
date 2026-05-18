import yaml

with open('configs/configs.generated.yml', 'r', encoding='utf-8') as f:
    configs = yaml.safe_load(f)
    
FX_SETTINGS: dict = configs['embed']['built_in']['fx']
IS_TRANSLATION_ENABLED: bool = FX_SETTINGS['auto_translation'] if configs['embed']['type'] == 'built_in' else configs['embed']['proxy']['auto_translation']
