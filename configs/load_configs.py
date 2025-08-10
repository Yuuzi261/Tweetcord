import yaml

with open('configs/configs.generated.yml', 'r', encoding='utf-8') as f:
    configs = yaml.safe_load(f)
