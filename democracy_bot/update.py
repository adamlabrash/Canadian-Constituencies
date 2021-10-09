import gzip
from selenium import webdriver
from multiprocessing.pool import ThreadPool as Pool
import psycopg2

DB_USER = 'postgres'
DB_PASSWORD = '123456'
DB_NAME = 'canadapolitics2021'
DB_HOST = 'localhost'


def update_constituencies(csv_file):
    lines = get_next_line(csv_file)
    pool = Pool(processes=1, initializer=init_process)

    for line in lines:
        pool.map(process_postal_code, (line,))

    pool.close()
    pool.join()


def init_process():
    global driver  # using global for convenience because each process is independent
    global db_conn

    driver = webdriver.Chrome()
    driver.get("https://elections.ca/Scripts/vis/FindED?L=e&PAGEID=20")

    db_conn = connect_db()


def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        print('successfully connected to database')
    except Exception:
        print("unable to connect to db, terminating program...")
        exit(0)

    return conn


def insert_db(item):

    try:
        sql = """INSERT INTO canadian_constituencies(postal_code, mp_name, mp_email, constituency_name, province, county, place, 
            constituency_population, constituency_registered_voters, constituency_polling_divisions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        db_conn.cursor.execute(sql,
                               (
                                   item.get("postal_code"),
                                   item.get("MP"),
                                   item.get("MP_email"),
                                   item.get("constituency"),
                                   item.get("province"),
                                   item.get("county"),
                                   item.get("place"),
                                   item.get("constituency_population"),
                                   item.get("constituency_registered_voters"),
                                   item.get("constituency_polling_divisions")
                               )
                               )
        db_conn.commit()
        print(f"Successfully inserted {item['postal_code']} into db")

    except Exception:
        print('Error inserting item into database')
        import pdb
        pdb.set_trace()


def get_next_line(csv_file):
    with gzip.open(csv_file, 'rb') as f:
        next(f)  # skip header row

        for line in f:
            yield line.decode().strip().split(',')


# def process_postal_code(postal_code, province, county, place):
def process_postal_code(location_info):

    postal_code = location_info[0]

    try:
        searchElem = driver.find_element_by_id('CommonSearchTxt')
        searchElem.clear()
        searchElem.send_keys(postal_code)
        searchElem.submit()
    except:
        print(f"\nError searching {postal_code}\n")
        driver.back()

    driver.implicitly_wait(5)

    try:
        constituency = {}
        constituency['postal_code'] = postal_code
        constituency['province'] = location_info[4]
        constituency['county'] = location_info[5]
        constituency['place'] = location_info[6]
        constituency['MP'] = driver.find_element_by_xpath(
            '//*[@id="main"]/div[3]/div[2]/p[1]').text
        constituency['MP_email'] = constituency['MP'].split()[0] + "." + \
            constituency['MP'].split()[1] + "@parl.gc.ca"
        constituency['constituency'] = driver.find_element_by_xpath(
            '//*[@id="main"]/div[3]/div[1]/p[1]').text[6:]
        constituency['constituency_population'] = int((driver.find_element_by_xpath(
            '//*[@id="main"]/div[3]/div[1]/p[2]').text[12:]).replace(",", ""))
        constituency['constituency_registered_voters'] = int((driver.find_element_by_xpath(
            '//*[@id="main"]/div[3]/div[1]/p[3]').text[19:]).replace(",", ""))
        constituency['constituency_polling_divisions'] = int((driver.find_element_by_xpath(
            '//*[@id="main"]/div[3]/div[1]/p[4]').text[29:]).replace(",", ""))

        insert_db(constituency)
    except Exception:
        import pdb
        pdb.set_trace()
        print(f'Error processing information for {location_info}')


update_constituencies('../canadian_politics_db.csv.gz', )
