import requests
from bs4 import BeautifulSoup
import os

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]

BASE_URL = "https://api.mycaptain.co.in"
LOGIN_URL = f"{BASE_URL}/users/sign_in"
DATA_URL = f"{BASE_URL}/operations/kickstarter_transactions"


def run():
    session = requests.Session()
    approved_count = 0

    try:
        # LOGIN PAGE
        login_page = session.get(LOGIN_URL)
        soup = BeautifulSoup(login_page.text, "html.parser")
        form_token = soup.find("input", {"name": "authenticity_token"})["value"]

        # LOGIN
        payload = {
            "authenticity_token": form_token,
            "user[email]": EMAIL,
            "user[password]": PASSWORD
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": LOGIN_URL
        }

        session.post(LOGIN_URL, data=payload, headers=headers)

        # LOAD TRANSACTIONS
        page = session.get(DATA_URL)
        soup = BeautifulSoup(page.text, "html.parser")

        meta_token = soup.find("meta", {"name": "csrf-token"})["content"]

        rows = soup.select("table tbody tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) < 17:
                continue

            status = cols[2].text.strip().lower()
            mode = cols[16].text.strip().lower()

            if status == "created" and "free" in mode:
                approve_link = row.select_one("a[href*='approve']")

                if approve_link:
                    approve_url = BASE_URL + approve_link["href"]

                    approve_headers = {
                        "User-Agent": "Mozilla/5.0",
                        "Referer": DATA_URL,
                        "Origin": BASE_URL,
                        "X-CSRF-Token": meta_token,
                        "X-Requested-With": "XMLHttpRequest"
                    }

                    response = session.post(
                        approve_url,
                        headers=approve_headers
                    )

                    if response.status_code in [200, 302]:
                        approved_count += 1
                        print(f"✅ Approved: {approve_url}")
                    else:
                        print(f"❌ Failed: {response.status_code}")

        print(f"🚀 Total Approved: {approved_count}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    run()
