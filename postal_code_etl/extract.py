from enum import Enum
from typing import Iterator

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed


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
        place_containers = self.driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/table/tbody/tr')
        for place in place_containers:
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


def get_all_fsa_codes() -> Iterator[str]:
    num_workers = 5
    spider = Spider()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(spider.get_fsa_codes_of_all_provinces, province) for province in list(Province)]
        for future in as_completed(futures):
            yield future.result()


def get_all_postal_codes_from_fsa_codes(all_fsa_codes: Iterator[str]) -> None:
    num_workers = 5
    spider = Spider()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(spider.get_postal_codes_of_forward_sortation_code, all_fsa_codes))
        import pdb

        pdb.set_trace()


def process_postal_codes_in_parallel(postal_codes: Iterator[str]) -> None:
    num_workers = 5

    spider = Spider()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(spider.extract_postal_code_data, postal_codes)


if __name__ == '__main__':
    # process_fsa_codes_in_parallel(Spider().get_fsa_codes_of_all_provinces())
    for all_fsa_codes in get_all_fsa_codes():
        
    all_postal_codes = get_all_postal_codes_from_fsa_codes(all_fsa_codes)
    postal_code_data = process_postal_codes_in_parallel(all_postal_codes)

    for postal_code in postal_code_data:
        import pdb

        pdb.set_trace()
        insert_postal_code_data(postal_code)
