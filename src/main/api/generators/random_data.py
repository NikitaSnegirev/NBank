import random
from faker import Faker

faker = Faker()

class RandomData:
    @staticmethod
    def get_username(length=random.randint(3, 15)) -> str:
        return ''.join(faker.random_letters(length))

    @staticmethod
    def get_password() -> str:
        upper = [letter.upper() for letter in faker.random_letters(length=3)]
        lower = [letter.lower() for letter in faker.random_letters(length=3)]
        digits = [str(faker.random_digit()) for _ in range(3)]
        special = [random.choice('!@#$%^&')]
        password = upper + lower + digits + special
        random.shuffle(password)
        return ''.join(password)

    @staticmethod
    def get_random_number_float(min_cents: int, max_cents: int) -> float:
        return random.randint(min_cents, max_cents) / 100
