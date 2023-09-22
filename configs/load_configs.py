import yaml

with open('./configs.yml', 'r', encoding = 'utf8') as yfile:
    configs = yaml.safe_load(yfile)