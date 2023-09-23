import json

def get_cookies():
    with open('cookies.json') as jfile:
        cookies = json.load(jfile)        
    return cookies