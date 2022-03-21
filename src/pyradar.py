import os
import time
import json
import requests
import warnings
from dotenv import load_dotenv, find_dotenv

# Leave here to suppress https missing certificate validation warning
warnings.filterwarnings("ignore")

load_dotenv(find_dotenv())

INDENT = 4
VERIFY = False
BASE_URL = os.getenv("API_URL")
SEC_TOKEN = os.getenv("SEC")
HEADER = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'SEC': SEC_TOKEN
}

# Base urls for different apis
SIEM_API = BASE_URL + "/siem"


def help():
    url = BASE_URL + "help/capabilities"
    print(f"[+] GET {url}")

    res = requests.get(url, verify=VERIFY, headers=HEADER).json()
    with open("api_doc.json", "w") as f:
        f.write(json.dumps(res, indent=INDENT))


# /siem apis
def get_offenses():
    url = SIEM_API + "/offenses"

    print(f"[+] GET {url}")

    s = time.time()
    res = requests.get(url, headers=HEADER, verify=VERIFY).json()
    e = time.time()

    print(f"Served in {e - s} s")

    with open("offenses.json", "w") as f:
        f.write(json.dumps(res, indent=INDENT))


def get_offense_closing_reasons():
    url = SIEM_API + "/offense_closing_reasons"

    print(f"[+] GET {url}")

    s = time.time()
    res = requests.get(url, headers=HEADER, verify=VERIFY).json()
    e = time.time()

    print(f"[+] Served in {e - s} s")

    with open("closing_reasons.json", "w") as f:
        f.write(json.dumps(res, indent=INDENT))


if __name__ == "__main__":
    # print("[+] Configure the variables specified in config.env file")
    get_offense_closing_reasons()