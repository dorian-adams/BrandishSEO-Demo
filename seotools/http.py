import requests


class HttpClient:
    def __init__(self):
        self.session = requests.Session()

    def get(self, url):
        r = self.session.get(url, timeout=15)
        r.raise_for_status()
        return r


http_client = HttpClient()
