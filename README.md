# Canadian_Constituencies
Data scraping project mapping each postal code in Canada to its political constituency and member of parliment.

The database contains 844216 entries in total. 9960 of the postal codes do not have political information. In these instances the postal code would be for an extremely remote location, or the elections Canada website would require additional specific address input.

Project was created to increase accessibility and transparency regarding political data in Canada, and in response to general demand (see https://open.canada.ca/en/suggested-datasets/postal-codes-and-federal-ridings). Outside of politics the database is also useful as it holds all the general Canadian postal code information in one place.

Source of postal codes:
https://www.postalcodesincanada.com/

Each postal code was subsequently entered into the postal code input found here:
https://www.elections.ca/Scripts/vis/FindED?L=e&QID=-1&PAGEID=20

Information is accurate as of August 2020.

Outline format of tables

Some postal codes do not have political information regarding

The web scraper takes many days to run even when divided by province.
