import os

import requests


def ping_healthcheck():
    url = os.getenv("HEALTHCHECKS_URL")
    requests.get(url, timeout=10)


if __name__ == "__main__":
    ping_healthcheck()
