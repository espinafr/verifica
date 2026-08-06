from config import settings

class Fetcher:
    def __init__(self, path, url=settings.get_config("url")):
        self.url = f"{url}{path}"

    def fetch(self):
        # Logic to fetch data from the URL
        pass