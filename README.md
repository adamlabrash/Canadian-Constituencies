# Canadian Postal Code & Political Constituencies Database
Data scraping project mapping every postal code in Canada to its political constituency information and member of parliament. Specifically coloumns in database are as follows: postal_code, MP, MP_email, constituency, province, county, place, consituency_population, constituency_registered_voters, and constituency_polling_divisions. 

This project was created to increase accessibility and transparency regarding political data in Canada, and in response to general demand (see https://open.canada.ca/en/suggested-datasets/postal-codes-and-federal-ridings for example). Outside of politics the database is also useful as it holds all the general Canadian postal code information in one place.

The database contains 844 216 entries in total. 9960 of the postal codes do not have political information (only postal_code, province, county, and place). In these instances the postal code would be for an extremely remote location without valid political information, or the elections Canada website would require additional specific address input.

Postal codes were scrapped from https://www.postalcodesincanada.com/

Each postal code was subsequently entered into the postal code input found here:
https://www.elections.ca/Scripts/vis/FindED?L=e&QID=-1&PAGEID=20

TODO:

requirements.txt

Create script to initialize postgres db

Break larger provinces into multiple scraping spiders. Currently the entire process will take as long as Ontario takes to finish.
