import json

def get_cookies():
    with open('cookies.json', 'r', encoding='utf8') as jfile:
        cookies = json.load(jfile)        
    return cookies