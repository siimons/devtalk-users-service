import requests

new_user = {
    'username': 'Finn',
    'email': 'adventuretime@yandex.ru',
    'password': 'gfdsaqz'
}

user_update = {
    'id': 3,
    'username': 'Jake',
    'email': 'adventuretime@yandex.ru'
}

comment_create = {
    'user_id': 3,
    'article_id': 2,
    'content': 'Сool bro!'
}

r = requests.post('http://localhost:8000/api/user/', json=new_user)

print(r.text, r.status_code)