from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from faker import Faker

faker = Faker()


def create_items():
    for _ in range(500):
        response = requests.post(
            "http://localhost:8080/item",
            json={
                "name": faker.word() + " " + faker.word(),
                "price": faker.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=10, max_value=1000),
            },
        )

        print(response)


def get_items():
    for _ in range(500):

        response = requests.get(
            f"http://localhost:8080/item/{faker.pyint(min_value=1, max_value=100)}",
        )
        print(response)


with ThreadPoolExecutor() as executor:
    futures = {}

    for i in range(15):
        futures[executor.submit(create_items)] = f"create-items-{i}"

    for _ in range(15):
        futures[executor.submit(get_items)] = f"get-items-{i}"

    for future in as_completed(futures):
        print(f"completed {futures[future]}")
