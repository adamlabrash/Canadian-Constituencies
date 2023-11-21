from bs4 import BeautifulSoup

# collect constituency info displayed from Elections Canada if postal code input is valid
# example page: https://www.elections.ca/Scripts/vis/EDInfo?L=e&ED=47011&EV=99&EV_TYPE=6&PC=S7N2X5&PROV=SK&PROVID=47&QID=-1&PAGEID=21


def transform_html_to_constituency_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    import pdb

    pdb.set_trace()
    price_cells = soup.findAll('td', {'class': 'pricecell'})

    # item['MP'] = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/div[2]/p[1]').text
    # item['constituency'] = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/div[1]/p[1]').text[6:]
    # item['constituency_population'] = int(
    #     (self.driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/div[1]/p[2]').text[12:]).replace(",", "")
    # )
    # item['constituency_registered_voters'] = int(
    #     (self.driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/div[1]/p[3]').text[19:]).replace(",", "")
    # )
    # item['constituency_polling_divisions'] = int(
    #     (self.driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/div[1]/p[4]').text[29:]).replace(",", "")
    # )
    # item['MP_email'] = (
    #     item['MP'].split()[0] + "." + item['MP'].split()[1] + "@parl.gc.ca"
    # )  # each MP email is simply FirstName.LastName@parl.gc.ca
