from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.common.by import By
from transform import transform_html_to_constituency_data

ELECTION_URL = "https://elections.ca/Scripts/vis/FindED?L=e&PAGEID=20"


class PoliticalConstituencies:
    def __init__(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = Chrome(options=chrome_options)
        self.driver.get(ELECTION_URL)

    def extract_constituency_data(self, postal_code: str) -> None:
        # self.driver.implicitly_wait(10)

        # engage webdriver to enter the collected postal code into the Elections Canada website. Note that the webdriver does this while the spider remains on postalcodescanada.com
        # Webpage: https://www.elections.ca/Scripts/vis/FindED?L=e&QID=-1&PAGEID=20
        try:
            searchElem = self.driver.find_element(By.ID, 'CommonSearchTxt')
            searchElem.clear()
            searchElem.send_keys(postal_code)
            searchElem.submit()
            self.driver.implicitly_wait(10)

            constituency = transform_html_to_constituency_data(self.driver.page_source)

            # TODO insert into db
            db.insert_constituency(constituency)

            print(f"\nSuccessfully extracted info for {postal_code}\n")

        except Exception:  # TODO
            print(f"\nError searching {postal_code}\n")

        self.driver.back()  # return to search page on Elections Canada
