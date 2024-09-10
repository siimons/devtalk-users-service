import requests

new_user = {
    'email': 'bibashlep@yandex.ru',
    'password': 'gjckeifybt'
}

req = requests.post('http://localhost:8000/api/login', json=new_user)

print(req.text, req.status_code)