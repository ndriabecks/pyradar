import os
import time
import json
import requests
import warnings

# TO REMOVE
from dotenv import load_dotenv, find_dotenv

# Leave here to suppress https missing certificate validation warning
warnings.filterwarnings("ignore")

HEADER = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'SEC': "SEC_TOKEN_HERE"
}

OK = 1
KO = -1


class QRadarAPI():
    """Class exposing functions to interact with QRadar APIs.

    The class does not check for errors, you must handle them on your own.
    """

    def __init__(self, SEC, API_BASE, verify=False):

        self.api_base = API_BASE
        self.verify = verify
        self.header = HEADER
        self.header['SEC'] = SEC

    def get_help(self) -> requests.Response:
        """Retrieve the available APIs.

        Returns:
            res (requests.Response): Response object
        """

        url = self.api_base + "help/capabilities"
        print(f"[+] GET {url}")

        res = requests.get(url, verify=self.verify, headers=self.header)
        return res

    def get_offenses(self) -> requests.Response:
        """Retrieve the offenses present into QRadar.

        Returns:
            res (requests.Response): Response object.
        """

        url = self.api_base + "/siem/offenses"

        print(f"[+] GET {url}")

        s = time.time()
        res = requests.get(url, headers=HEADER, verify=self.verify)
        e = time.time()

        print(f"Served in {e - s} s")

        return res

    def get_offense_closing_reasons(self) -> requests.Response:
        """Retrieve the offenses closing reason types.

        Returns:
            res (requests.Response): Response object
        """

        url = self.api_base + "/siem/offense_closing_reasons"

        print(f"[+] GET {url}")

        s = time.time()
        res = requests.get(url, headers=HEADER, verify=self.verify)
        e = time.time()

        print(f"[+] Served in {e - s} s")

        return res

    def post_ariel_search(self,
                          query_expression: str = "") -> requests.Response:
        """Create a new ariel search with the query_expression passed in input.

        Args:
            query_expression (str, optional): Query expression written in AQL. Defaults to "".

        Returns:
            res (requests.Response): Response object
        """
        url = f"{self.api_base}/ariel/searches?query_expression={query_expression}"

        return requests.post(url, headers=self.header, verify=self.verify)

    def get_ariel_search_status(self, sid: str) -> requests.Response:
        """Look up a search's current status.

        Args:
            sid (str): The element cursor_id present in the response received by post_ariel_search()

        Returns:
            status (requests.Response): A string describing the status of the search. It is the status parameter of the response received from the server.
        """
        url = f"{self.api_base}/ariel/searches/{sid}"
        res = requests.get(url, headers=self.header, verify=self.verify)
        status = res.json()["status"]
        return status

    def get_ariel_search_results(self, sid: str) -> requests.Response:
        """Retrieve the results of a search. If the search is not completed, the response will contain a particular message describing why it is not done. For more details check out QRadar docs.

        Args:
            sid (str): The element cursor_id present in the response received by post_ariel_search()

        Returns:
            res (requests.Response): Response object
        """
        url = f"{self.api_base}/ariel/searches/{sid}/results"
        return requests.get(url, headers=self.header, verify=self.verify)

    def do_ariel_search(self,
                        query_expression: str = "",
                        debug: bool = False) -> dict:
        """This function runs a full ariel search, taking care of the async architecture of ariel. Basically it posts a search, then waits for it to complete and the retrieves the results using publicly available functions.

        Args:
            query_expression (str, optional): Query expression written in AQL. Defaults to "".

        Returns:
            dict: A dictionary containing the search results, or the error message
        """
        res = self.post_ariel_search(query_expression).json()
        try:
            sid = res['cursor_id']
        except:
            print("No cursor_id found. Here is the response received:\n")
            print(json.dumps(res, indent=4))
            return json.loads("{\"error\": \"no cursor_id\"}")

        s = time.time()
        print(f"[+] cursor_id = {sid}")

        status = self.get_ariel_search_status(sid)
        if (debug):
            print("[+] " + status)

        while status != "COMPLETED" and status != "ERROR":
            status = self.get_ariel_search_status(sid)
            time.sleep(5)

        if (debug):
            print("[+] " + status)

        if status == "ERROR":
            return json.loads("{\"error\": \"search id not found\"}")

        res = self.get_ariel_search_results(sid)
        e = time.time()
        if (debug):
            print(f"[+] Served in {e - s} s")

        return res.json()


load_dotenv(find_dotenv())
# Load .env and environment variables
SEC_TOKEN = os.getenv("SEC")
BASE_URL = os.getenv("API_URL")

if __name__ == "__main__":
    print("Pyradar is a module. Not a standalone.")
