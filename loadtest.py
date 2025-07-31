from locust import HttpUser, task, between
import random

class LoginUser(HttpUser):
    wait_time = between(0, 0)

    @task
    def login(self):
        user_id = random.randint(0, 1000)
        email = f"user{user_id}@example.com"
        password = f"123456test{user_id}"
        self.client.post("/login", json={"email": email, "password": password})