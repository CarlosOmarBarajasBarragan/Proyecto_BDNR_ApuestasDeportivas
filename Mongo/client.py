import requests

API_URL = "http://localhost:8000"


def print_resultado(data):
    if isinstance(data, list):
        for doc in data:
            for k, v in doc.items():
                print(f"{k}: {v}")
            print("=" * 50)
    elif isinstance(data, dict):
        for k, v in data.items():
            print(f"{k}: {v}")
        print("=" * 50)


