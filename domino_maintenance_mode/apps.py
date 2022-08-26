import os
import requests

def fetch_apps():
    api_key = os.environ["DOMINO_API_KEY"]
    hostname = os.environ["DOMINO_HOSTNAME"]

    result = requests.get(f"{hostname}/v4/modelProducts", headers={"Content-Type":"application/json"})
    print(result.text)
