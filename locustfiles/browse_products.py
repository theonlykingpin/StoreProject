from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task(2)
    def view_product(self):
        print("view product")
        collection_id = randint(1, 1000)
        self.client.get("/store/products/?collection_id=%d" % collection_id, name="/store/products/")

    @task(4)
    def view_product(self):
        print("view product detail")
        product_id = randint(1, 1000)
        self.client.get("/store/products/%d/" % product_id, name="/store/products/:id")

    @task(1)
    def add_to_cart(self):
        print("add to cart")
        product_id = randint(1, 1000)
        self.client.get("/store/carts/%s/items/" % self.cart_id, name="/store/carts/items", json={"product_id": product_id, "quantity": 1})

    def on_start(self):
        result = self.client.post("/store/carts/").json()
        self.cart_id = result["id"]


    @task
    def say_hello(self):
        self.client.get("/playgroundapplication/hello/")
