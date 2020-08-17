import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.chrome.options import Options
from democracy_bot.items import ConstituencyItem

#GLOBAL URLS
BASE_URL = "https://www.postalcodesincanada.com"
ELECTION_URL = "https://elections.ca/Scripts/vis/FindED?L=e&PAGEID=20"


class PostalSpider(scrapy.Spider):

    handle_httpstatus_list = [301, 302]
    name = 'politics'
    allowed_domains = ['postalcodesincanada.com', 'elections.ca']

    def __init__(self, url):

        self.start_urls = url

        #reduce verbosity of spider and driver output
        logging.getLogger('scrapy').setLevel(logging.WARNING) #spider
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        LOGGER.setLevel(logging.WARNING) #driver

        #run selenium without open web browser
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        #initialize webdriver
        self.driver = webdriver.Chrome(executable_path="path/to/chromedriver", options=chrome_options)


    #start spider on provided urls
    def start_requests(self):
        urls = [self.start_urls]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    #follow each FSA link for given province
    #example page: https://www.postalcodesincanada.com/province-ontario/
    def parse(self, response):
        self.driver.get(ELECTION_URL)
        for selection in response.xpath('//*[@id="pills-home"]/div/table/tbody/tr//td/span/a/@href').extract():
            yield scrapy.Request(BASE_URL+selection, callback=self.parse_attr, meta={'loop_condition':True, 'first_link': selection})
        

    #parse the given FSA link and follow each specific postal code link (including those on subsequent pages)
    #example page: https://www.postalcodesincanada.com/fsa-k1k/
    def parse_attr(self, response):
        loop_condition = response.meta['loop_condition']
        first_link = response.meta['first_link']

        #follow each postal code area on the given page
        for selection in response.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/table/tbody//tr//td/span/a/@href').extract():
            yield scrapy.Request(BASE_URL+selection, callback=self.parse_final)


        #this loop should only be run once on the first page to get the number of subpages, hence the loop_condition
        if loop_condition == True and len(response.xpath('/html/body/div[2]/div[2]/div[1]/div[3]/table/tbody/tr//*[@class="page"]/text()').extract())>0:
            total_pages = int(response.xpath('/html/body/div[2]/div[2]/div[1]/div[3]/table/tbody/tr//*[@class="page"]/text()').extract()[-1]) #get highest page number on bottom of page
            
            for page in range(2, total_pages+1): #use number defined above to visit all other pages in range but do not redo this loop
                yield scrapy.Request(BASE_URL+first_link+f"?page={page}", callback=self.parse_attr, meta={'loop_condition':False, 'first_link':first_link})


    #final parse collects information from last postal code page and inputs it into Elections Canada
    def parse_final(self, response):


        #Spider extracts individual postal code info from given page
        #Example page: https://www.postalcodesincanada.com/postal-code-k1k-1v6/
        try:
            item = ConstituencyItem()
            item['postal_code'] = response.xpath('/html/body/div[2]/div/div[2]/div[3]/table/tbody/tr/td[4]/text()').extract()[0]
            item['province'] = response.xpath('/html/body/div[2]/div/div[2]/div[1]/table/tbody/tr[2]/td[2]/a/text()').extract()[0]
            item['county'] = response.xpath('/html/body/div[2]/div/div[2]/div[3]/table/tbody/tr/td[3]/a/text()').extract()[0]
            item['place'] = response.xpath('/html/body/div[2]/div/div[2]/div[3]/table/tbody/tr/td[2]/a/text()').extract()[0]
        except:
            print("\nError extracting postal info\n")
            return

        self.driver.implicitly_wait(10)


        #engage webdriver to enter the collected postal code into the Elections Canada website. Note that the webdriver does this while the spider remains on postalcodescanada.com
        #Webpage: https://www.elections.ca/Scripts/vis/FindED?L=e&QID=-1&PAGEID=20
        try:
            searchElem = self.driver.find_element_by_id('CommonSearchTxt')
            searchElem.clear()
            searchElem.send_keys(item['postal_code'])
            searchElem.submit()
        except:
            print(f"\nError searching {item['postal_code']}\n")
            self.driver.back()
            return item

        self.driver.implicitly_wait(10)


        #collect constituency info displayed from Elections Canada if postal code input is valid
        #example page: https://www.elections.ca/Scripts/vis/EDInfo?L=e&ED=47011&EV=99&EV_TYPE=6&PC=S7N2X5&PROV=SK&PROVID=47&QID=-1&PAGEID=21
        try:
            item['MP'] = self.driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[2]/p[1]').text
            item['constituency'] = self.driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[1]/p[1]').text[6:]
            item['constituency_population'] = int((self.driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[1]/p[2]').text[12:]).replace(",", ""))
            item['constituency_registered_voters'] = int((self.driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[1]/p[3]').text[19:]).replace(",", ""))
            item['constituency_polling_divisions'] = int((self.driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[1]/p[4]').text[29:]).replace(",", ""))
            item['MP_email'] = item['MP'].split()[0] + "." + item['MP'].split()[1] + "@parl.gc.ca" #each MP email is simply FirstName.LastName@parl.gc.ca
        except:
            print(f"\nNo valid information for {item['postal_code']}") #Some postal codes require more info or are too obscure
            self.driver.back()
            return item
        
        self.driver.back() #return to search page on Elections Canada
        self.driver.implicitly_wait(10)

        print(f"\nSuccessfully extracted info for {item['postal_code']}\n")

        return item


#run each province with co-currently with its own spider
process = CrawlerProcess()
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-prince-edward-Island/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-newfoundland-and-labrador/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-nova-scotia/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-new-brunswick/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-quebec/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-ontario/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-manitoba/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-saskatchewan/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-alberta/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-british-columbia/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-nunavut/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-northwest-territories/")
process.crawl(PostalSpider, "https://www.postalcodesincanada.com/province-yukon/")
process.start()