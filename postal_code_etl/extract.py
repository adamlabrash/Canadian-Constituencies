from enum import Enum
from multiprocessing import Pool, Process, Queue
import multiprocessing
from typing import Any, Iterator

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Province(Enum):
    AB = 'Alberta'
    BC = 'British Columbia'
    NB = 'New Brunswick'
    NL = 'Newfoundland and Labrador'
    NT = 'Northwest Territories'
    NS = 'Nova Scotia'
    NU = 'Nunavut'
    PE = 'Prince Edward Island'
    MB = 'Manitoba'
    SK = 'Saskatchewan'
    ON = 'Ontario'
    QB = 'Quebec'


BASE_URL = 'https://www.postalcodesincanada.com'


class Spider:
    def __init__(self) -> None:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.driver = Chrome(
            options=chrome_options
        )  # we have to use selenium because website blocks non-javascript requests

    def get_fsa_codes_of_all_provinces(self) -> Iterator[str]:
        for province in Province:
            print("Extracting FSA codes for ", province.value)
            yield from self.get_fsa_codes_of_province(province)

    def get_fsa_codes_of_province(self, province: Province) -> Iterator[str]:
        url = f'{BASE_URL}/province-{province.value}/'
        self.driver.get(url)
        fsa_code_elements = self.driver.find_elements(By.XPATH, '//*[@id="pills-home"]/div/table/tbody/tr/td[1]/span/a')
        yield from [element.text for element in fsa_code_elements]

    def get_postal_codes_of_forward_sortation_code(self, fsa_code: str) -> Iterator[str]:
        self.driver.get(f'{BASE_URL}/fsa-{fsa_code}')
        max_page_nums = max(int(element.text) for element in self.driver.find_elements(By.CLASS_NAME, 'page'))

        for sub_page_num in range(1, max_page_nums + 1):
            self.driver.get(f'{BASE_URL}/fsa-{fsa_code}/?page={sub_page_num}')
            postal_elements = self.driver.find_elements(
                By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[2]/table/tbody/tr/td/span/a'
            )
            yield from [postal_data.text for postal_data in postal_elements]

    def extract_postal_code_data(self, postal_code: str) -> Iterator[dict]:
        # Example page: https://www.postalcodesincanada.com/postal-code-k1k-1v6/
        self.driver.get(f"{BASE_URL}/postal-code-{postal_code.replace(' ', '-')}/")
        import pdb

        pdb.set_trace()
        province = Province(
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table/tbody/tr[2]/td[2]/a').text
        )
        places = self.driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/table/tbody/tr')
        for place in places:
            place_attributes = place.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/table/tbody/tr/td')
            try:
                yield {
                    'postal_code': postal_code,
                    'province': province,
                    'place': place_attributes[1].text,
                    'county': place_attributes[2].text,
                }
            except Exception:  # TODO
                import pdb

                pdb.set_trace()
                return


class Worker(Process):
    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue = queue

    def run(self):
        print('Worker started')
        # do some initialization here

        print('Computing things!')
        for data in iter(self.queue.get, None):
            # Use data
            pass


if __name__ == "__main__":
    postal_code_queue = Queue()
    for _ in range(4):
        Worker(postal_code_queue).start()

    for fsa_code in Spider().get_fsa_codes_of_all_provinces():
        postal_code_queue.put(fsa_code)

    # Sentinel objects to allow clean shutdown: 1 per worker.
    for i in range(4):
        postal_code_queue.put(None)
