import requests

payload = {
    'email':'',
    'code':958073
}
respond = requests.post('http://72.62.165.221:80/auth/verify-code',json=payload)
assert respond.status_code ==200 , respond.json()