import time
import random
import string
from locust import HttpUser, task, between
import os
class UserSearch(HttpUser):
    wait_time = between(1,5)
    host = "http://192.168.0.111:8992"
    token = os.environ.get('365_ACCESS_TOKEN')
    @task
    def search_user(self):
        random_keyword = ''.join(random.choices(string.ascii_letters,k=3))
        self.client.get(f'/profiles/search?keywords={random_keyword}&with-realtionship=true',headers={'Authentication':f'Bearer {token}'})
