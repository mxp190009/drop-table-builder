# The drop simulator plugin was capable of doing all of the scraping on its own, but once clue scroll simulations
# were introduced, it was no longer feasible for the plugin to do all of the scraping on its own. The time taken
# to scrape the wiki was too long for anyone to enjoy the plugin. This supplementary python script scrapes the wiki
# and builds a json file to be included in the plugin resources folder. The plugin will still use the osrs-box api for
# all npcs, this is just for all non-npc tables not included in the osrs-box api.
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup


def build_clue_table_from_wiki(drop_source):
    url = 'https://oldschool.runescape.wiki/w/' + drop_source
    response = requests.get(url)

    tables = []
    html_tables = pd.read_html(response.text)

    for table in html_tables:  # for each table on the page

        if table.columns[1] == 'Item':  # if it is a table containing items
            if table.Rarity[0] != 'Common':  # if it is NOT the mimic reward table
                tables.append(table)  # it is a table we want

    table = pd.concat(tables)  # join all needed tables together
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    del table['Unnamed: 0']  # delete unnamed column
    del table['Price']  # delete price column
    del table['High Alch']  # delete high alch column
    table['Rarity'] = table['Rarity'].apply(lambda x: '1/1' if 'Always' in x else x)  # replaces always with 1/1
    table = table[table.Rarity != '1/1']  # remove all always drops
    table['Rarity'] = table['Rarity'].str.replace(',', "", regex=True)  # removes commas from rarity
    table['Rarity'] = table['Rarity'].apply(lambda x: re.sub("[\[].*?[\]]", "", x))  # removes annotations [~]
    table['Quantity'] = table['Quantity'].apply(
        lambda x: re.sub("[\(].*?[\)]", "", str(x)).strip())  # remove (noted)
    table['Quantity'] = table['Quantity'].apply(
        lambda x: re.sub(u"\u2013", "-", str(x)))  # replaces en dash with regular dash
    table['Quantity'] = table['Quantity'].str.replace(',', "", regex=True)  # removes commas from quantity
    table['Rarity'] = table['Rarity'].apply(pd.eval)  # evaluates each rarity as double

    # Special case regarding super potion sets
    # The mega-rare hard table includes 3 rows for super att, str, and def (4). All 3 are dropped together, so to keep
    # the simulation accurate, the 3 drops are replaced with a single row of the super attack box which contains all
    # three potions in the set.

    ids_to_be_added = []

    for row in table.iterrows():

        url = 'https://oldschool.runescape.wiki/w/' + row[1]['Item']
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        soup2 = soup.find('div', attrs={'class': 'realtimePrices'})

        # Items with multiple IDs will return a type error using the
        # above search. So, if a type error is caught, a different method is used
        # to acquire the id.

        try:

            item_id = soup2['data-itemid']  # try normal fetch

        except TypeError:  # if type error

            temp_id = soup.find(string='Item ID').next.text  # unique fetch

            if ',' in temp_id:  # if the temp id contains a comma, the wiki provided all IDs of the item
                item_id = temp_id.split(',')[0]  # gets first id

            else:
                item_id = temp_id  # gets the id

        ids_to_be_added.append(int(item_id))
        print(item_id)

    table['ID'] = ids_to_be_added
    table['Drop-source'] = drop_source
    return table


def main():

    beginner = 'Beginner casket'
    easy = 'Easy casket'
    medium = 'Medium casket'
    hard = 'Hard casket'
    elite = 'Elite casket'
    master = 'Master casket'

    all_clues = [beginner, easy, medium, hard, elite, master]
    clue_tables = []

    for clue in all_clues:  # for each clue scroll
        clue_table = build_clue_table_from_wiki(clue)  # builds the table
        clue_tables.append(clue_table)

    clue_table = pd.concat(clue_tables)

    clue_table.to_json(path_or_buf='C:/Users/Marshall/IdeaProjects/drop-simulator/src/main/resources/non_npc_tables'
                                   '.json',
                       orient='table')



if __name__ == '__main__':
    main()
