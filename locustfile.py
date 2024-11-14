from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):
    @task
    def login(self) -> None:
        self.client.post("/login", json={"email": "juanita@gmail.com", "password": "juanita"})


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    waittime = between(1, 5)


if __name__ == "_main":
    import locust

    locust.run_single_user(WebsiteUser, run_time="10s")
