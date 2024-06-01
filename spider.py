import csv
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, wait

import requests
from loguru import logger
from pydantic import BaseModel, Field, ValidationError
from requests import Response

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class Constituency(BaseModel):
    postal_code: str
    first_name: str = Field(validation_alias='firstName')
    last_name: str = Field(validation_alias='lastName')
    constituency: str = Field(validation_alias='constituencyNameEn')
    province: str = Field(validation_alias='provinceNameEn')
    caucus: str = Field(validation_alias='caucusShortNameEn')
    phone: str = Field(validation_alias='currentPhone')

    @property
    def MP_email(self) -> str:
        return f"{self.first_name}.{self.last_name}@parl.gc.ca"


def run_multithreaded_spider() -> None:
    with ThreadPoolExecutor() as executor:
        res = [
            executor.submit(extract_constiuency_data_from_postal_code, sortation_station_code)
            for sortation_station_code in get_postal_codes_from_txt()
        ]
        wait(res)
        constituencies = [f.result() for f in res if f.result() is not None]
        write_constituency_data_to_csv(constituencies)


def get_postal_codes_from_txt() -> set[str]:
    unique_codes = set()
    with open('CA_postal_codes.txt') as source_file:
        for line in source_file.readlines():
            unique_codes.add(line.split('\t')[1].split(' ')[0])
    return unique_codes


def extract_constiuency_data_from_postal_code(postal_code: str) -> Constituency | None:
    logger.info(f'Extracting constituency data for postal code: {postal_code}')
    resp = send_post_request_to_ourcommons(postal_code)
    constituency_data = validate_constituency_data_from_resp(resp, postal_code)
    time.sleep(1)  # throttle spider
    return constituency_data


def send_post_request_to_ourcommons(postal_code: str) -> Response:
    resp = requests.post(
        'https://www.ourcommons.ca/Members/search/members',
        verify=False,
        json={'searchText': postal_code},
    )
    resp.raise_for_status()
    return resp


def validate_constituency_data_from_resp(resp: Response, postal_code: str) -> Constituency | None:
    try:
        constituency_data = {"postal_code": postal_code} | resp.json()['currentMembers'][0]
        return Constituency.model_validate(constituency_data)
    except ValidationError as e:
        logger.warning(f'Unable to validate constituency data from resp: {resp.url} | {e}')
    except KeyError as e:
        logger.warning(f'Key missing in resp json. Unable to validate resp: {resp.url} | {e}')

    return None


def write_constituency_data_to_csv(constituencies: list[Constituency]) -> None:
    with open('canadian_constituencies.csv', 'a') as csvfile:

        # initialize headers
        writer = csv.writer(csvfile)
        writer.writerow([key for key in Constituency.model_fields.keys()] + ['MP_email'])

        for constituency in constituencies:
            values = [val for val in constituency.model_dump().values()] + [constituency.MP_email]
            writer.writerow(values)


if __name__ == '__main__':
    run_multithreaded_spider()
