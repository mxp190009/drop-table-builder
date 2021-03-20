# The drop simulator plugin was capable of doing all of the scraping on its own, but once clue scroll simulations
# were introduced, it was no longer feasible for the plugin to do all of the scraping on its own. The time taken
# to scrape the wiki was too long for anyone to enjoy the plugin. This supplementary python script scrapes the wiki
# and builds a json file to be included in the plugin resources folder. The plugin will still use the osrs-box api for
# all npcs, this is just for all non-npc tables not included in the osrs-box api.
import pandas as pd
import requests
import re
import json
from osrsbox import items_api as items

# drop sources contains the name of each non npc table needed
drop_sources = ['beginner casket', 'easy casket', 'medium casket', 'hard casket', 'elite casket', 'master casket']


# build_clue_table  builds a clue table from the osrs wiki
def build_clue_table(drop_source):
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
    table.columns = table.columns.str.lower()  # remove capitalization from each column name
    table.columns = table.columns.str.replace("item", "name", regex=True)
    table['rarity'] = table['rarity'].apply(lambda x: '1/1' if 'Always' in x else x)  # replaces always with 1/1
    table = table[table.rarity != '1/1']  # remove all always drops
    table['rarity'] = table['rarity'].str.replace(',', "", regex=True)  # removes commas from rarity
    table['rarity'] = table['rarity'].apply(lambda x: re.sub("[\[].*?[\]]", "", x))  # removes annotations [~]
    table['quantity'] = table['quantity'].apply(
        lambda x: re.sub("[\(].*?[\)]", "", str(x)).strip())  # remove (noted)
    table['quantity'] = table['quantity'].apply(
        lambda x: re.sub(u"\u2013", "-", str(x)))  # replaces en dash with regular dash
    table['quantity'] = table['quantity'].str.replace(',', "", regex=True)  # removes commas from quantity
    table['rarity'] = table['rarity'].apply(pd.eval)  # evaluates each rarity as double

    # Special cases

    # Hard clue table contains a "Zombie head (treasure trails), but the osrsbox api has the name as "Zombie head," so
    # (treasure trails must be removed from the name

    table['name'] = table['name'].apply(
        lambda x: re.sub("[\(]Treasure Trails[\)]", "", str(x)).strip())  # remove (Treasure Trails)

    # The mega-rare hard table includes 3 rows for super att, str, and def (4). All 3 are dropped together, so to keep
    # the simulation accurate, the 3 drops are replaced with a single row of the super attack box which contains all
    # three potions in the set.

    table['name'] = table['name'].apply(lambda x: 'Super potion set' if 'Super attack(4)' in x else x)
    table = table.drop(table[table.name == 'Super strength(4)'].index)
    table = table.drop(table[table.name == 'Super defence(4)'].index)

    # store ids in a new column gathered from the osrs-box db

    ids_to_be_added = []

    my_items = items.load()

    print(drop_source)  # console printing to ensure program is running

    # get the id of each item gathered from the wiki by using the osrs-box db

    for row in table.iterrows():
        for item in my_items:
            if item.name == row[1]['name']:

                if item.name == 'Coins':  # special case for coins
                    ids_to_be_added.append(995)  # specific coin id needed
                else:
                    ids_to_be_added.append(int(item.id))

                print(item.name)  # console printing to ensure program is running
                break

    table['id'] = ids_to_be_added
    table['drop-source'] = drop_source
    return table


# build_all_clue_tables builds all clue tables from the osrs wiki
def build_all_clue_tables():
    beginner = 'Beginner casket'
    easy = 'Easy casket'
    medium = 'Medium casket'
    hard = 'Hard casket'
    elite = 'Elite casket'
    master = 'Master casket'

    all_clues = [beginner, easy, medium, hard, elite, master]
    clue_tables = []

    for clue in all_clues:  # for each clue scroll
        clue_table = build_clue_table(clue)  # builds the table
        clue_tables.append(clue_table)

    clue_table = pd.concat(clue_tables)  # concatenates all clue tables to a single table

    return clue_table


# build_all_tables builds ALL non npc tables from the osrs wiki
def build_all_tables():

    all_clue_tables = build_all_clue_tables()

    return all_clue_tables


# all_tables_to_json writes ALL tables to a json file
def all_tables_to_json():
    all_tables = build_all_tables()
    all_tables.to_json(path_or_buf='C:/Users/Marshall/IdeaProjects/drop-simulator/src/main/resources/non_npc_tables'
                                   '.json',
                       orient='table')


# all_table_names_to_json writes ALL table names to a json file
def all_table_names_to_json(drop_table_names):
    with open('C:/Users/Marshall/IdeaProjects/drop-simulator/src/main/resources/non_npc_table_names'
              '.json', 'w', encoding='utf-8') as f:
        json.dump(drop_table_names, f, ensure_ascii=False, indent=4)


def main():
    all_tables_to_json()


if __name__ == '__main__':
    main()
