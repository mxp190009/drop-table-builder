# The drop simulator plugin was capable of doing all of the scraping on its own, but once clue scroll simulations
# were introduced, it was no longer feasible for the plugin to do all of the scraping on its own. The time taken
# to scrape the wiki was too long for anyone to enjoy the plugin. This supplementary python script scrapes the wiki
# and builds a json file for each table to be included in the plugin resources folder. The plugin will still use the
# osrs-box api for all npcs, this is just for all non-npc tables not included in the osrs-box api.
import pandas as pd
import requests
import re
from osrsbox import items_api as items


# build_clue_table builds a clue table from the osrs wiki
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

    ids_to_be_added = []  # ids of each item
    drop_types_to_be_added = []  # type of drop of each item

    my_items = items.load()

    # get the id of each item gathered from the wiki by using the osrs-box db

    for row in table.iterrows():
        for item in my_items:
            if item.name == row[1]['name']:
                print(item.name)

                if item.name == 'Coins':  # special case for coins
                    ids_to_be_added.append(995)  # specific coin id needed
                else:
                    ids_to_be_added.append(int(item.id))

                # determine the drop type
                # Determining the type for clue tables is easy:
                # If it is a clue scroll drop or bloodhound, it is tertiary
                # Everything else is a main drop

                if item.name.__contains__("Clue scroll") or item.name == 'Bloodhound':
                    drop_types_to_be_added.append('tertiary')  # tertiary
                else:
                    drop_types_to_be_added.append('')  # empty cases of this column are to be considered main drops
                break

    table['id'] = ids_to_be_added
    table['drop-type'] = drop_types_to_be_added
    return table


# build_all_clue_tables builds all clue tables from the osrs wiki and writes each table to an individual json file
def all_clue_tables_to_json():
    beginner = 'beginner_casket'
    easy = 'easy_casket'
    medium = 'medium_casket'
    hard = 'hard_casket'
    elite = 'elite_casket'
    master = 'master_casket'

    all_clues = [beginner, easy, medium, hard, elite, master]

    for clue in all_clues:  # for each clue scroll
        clue_table = build_clue_table(clue)  # builds the table
        clue_table.to_json(path_or_buf='C:/Users/Marshall/IdeaProjects/drop-simulator/src/main/resources/' + clue +
                                       '.json',
                           orient='table')


# build_non_npc_table builds a non_npc_table from the osrs wiki that is NOT a clue scroll drop table
def build_non_npc_table(drop_source):
    url = 'https://oldschool.runescape.wiki/w/' + drop_source
    response = requests.get(url)

    tables = []
    html_tables = pd.read_html(response.text)

    for table in html_tables:  # for each table on the page

        if len(table.columns) > 4:  # if there is more than one column
            if table.columns[4] == 'Price':  # if it is a table containing items
                tables.append(table)  # it is a table we want

    table = pd.concat(tables)  # join all needed tables together
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    del table['Unnamed: 0']  # delete unnamed column
    del table['Price']  # delete price column
    del table['High Alch']  # delete high alch column
    table.columns = table.columns.str.lower()  # remove capitalization from each column name
    table.columns = table.columns.str.replace("item", "name", regex=True)
    table['rarity'] = table['rarity'].apply(lambda x: '1/1' if 'Always' in x else x)  # replaces always with 1/1
    table = table[table.name != 'Cabbage']  # remove cabbage drops from tob
    table = table[table.name != 'Message (Theatre of Blood)']  # remove message drop from tob
    table = table[table.name != 'Magic potion(2)']  # remove magic potion(2) from grotesque guardians
    table = table[table.name != 'Ranging potion(2)']  # remove ranging potion(2) from grotesque guardians
    table = table[table.name != 'Bludgeon axon']  # remove bludgeon axon from unsired
    table = table[table.name != 'Bludgeon spine']  # remove bludgeon spine from unsired
    table = table[table.name != 'Ranging potion(2)']  # remove ranging potion(2) from grotesque guardians
    table['rarity'] = table['rarity'].str.replace(',', "", regex=True)  # removes commas from rarity
    table['rarity'] = table['rarity'].apply(lambda x: re.sub(r'^.*?\u00D7', "", x))  # removes rolls x from rarity
    table['rarity'] = table['rarity'].apply(lambda x: re.sub("[\[].*?[\]]", "", x))  # removes annotations [~]
    table['quantity'] = table['quantity'].apply(
        lambda x: re.sub("[\(].*?[\)]", "", str(x)).strip())  # remove (noted)
    table['quantity'] = table['quantity'].apply(
        lambda x: re.sub(u"\u2013", "-", str(x)))  # replaces en dash with regular dash
    table['quantity'] = table['quantity'].str.replace(',', "", regex=True)  # removes commas from quantity
    table['rarity'] = table['rarity'].apply(lambda x: re.sub('\u2013.*$', "", x))  # removes rarity interval from rarity
    table['rarity'] = table['rarity'].apply(pd.eval)  # evaluates each rarity as double

    # store ids in a new column gathered from the osrs-box db

    ids_to_be_added = []  # ids of each item
    drop_types_to_be_added = []  # type of drop of each item

    my_items = items.load()

    # get the id of each item gathered from the wiki by using the osrs-box db

    for row in table.iterrows():
        for item in my_items:
            if item.name == row[1]['name']:
                print(item.name)

                if item.name == 'Coins':  # special case for coins
                    ids_to_be_added.append(995)  # specific coin id needed
                else:
                    ids_to_be_added.append(int(item.id))

                if row[1]['rarity'] == 1.0:  # if 100% rarity
                    drop_types_to_be_added.append('always')
                    break;
                # determine the drop type

                if item.name.__contains__("Clue scroll") or \
                        item.name.__contains__("zik") or \
                        item.name.__contains__('Brimstone') or \
                        item.name.__contains__('Noon') or \
                        item.name.__contains__('Jar of stone'):
                    drop_types_to_be_added.append('tertiary')  # tertiary
                    # anything with 's in the name is possessive. i.e., Guthan's
                elif item.name.__contains__("'s") or \
                        item.name.__contains__('Justiciar') or \
                        item.name.__contains__('Ghrazi') or \
                        item.name.__contains__('Sanguinesti') or \
                        item.name.__contains__('Avernic') or \
                        item.name.__contains__('vitur') or \
                        item.name.__contains__('Granite') or \
                        item.name.__contains__('tourmaline'):
                    drop_types_to_be_added.append('pre-roll')  # pre-roll
                else:
                    drop_types_to_be_added.append('')  # main drop
                break

    table['id'] = ids_to_be_added
    table['drop-type'] = drop_types_to_be_added
    return table


# build_all_non_npc_tables_to_json builds all non_npc_tables from the osrs wiki and writes each table to an individual
# json file
def all_non_npc_tables_to_json():
    barrows = 'barrows_chest'
    tob = 'theatre'
    unsired = 'unsired'
    guardians = 'grotesque_guardians'

    all_non_npc_tables = [barrows, tob, unsired, guardians]

    for table in all_non_npc_tables:
        non_npc_table = build_non_npc_table(table)
        non_npc_table.to_json(path_or_buf='C:/Users/Marshall/IdeaProjects/drop-simulator/src/main/resources/' + table +
                                          '.json',
                              orient='table')


# cox_table_to_json builds the tob table from the osrs wiki and writes the table to an individual json file
# cox needs its own table because it is unique, no other drop source is rolled like cox
def cox_table_to_json():
    url = 'https://oldschool.runescape.wiki/w/chambers of xeric'
    response = requests.get(url)

    tables = []
    html_tables = pd.read_html(response.text)

    for table in html_tables:  # for each table on the page

        if len(table.columns) > 1:
            if table.columns[1] == 'Item.1':  # if it is the pre-roll mess of a table on the wiki
                del table['Item']  # delete the item column
                del table['GE Price']  # delete ge price column
                table.insert(1, 'quantity', str(1))
                table.columns = ['name', 'quantity', 'rarity']
                table['rarity'] = table['rarity'].apply(
                    lambda x: re.sub(r'^.*?\(', "", x))  # removes everything before ( from rarity
                table['rarity'] = table['rarity'].str.replace('%', "", regex=True)  # removes % from rarity
                table['rarity'] = table['rarity'].str.replace(')', "", regex=True)  # removes ) from rarity
                tables.append(table)
        if len(table.columns) == 6:  # if there is more than four columns
            if table.columns[4] == 'Price':  # if it is a table containing prices
                del table['Unnamed: 0']  # delete unnamed column
                del table['Price']  # delete price column
                del table['High Alch']  # delete high alch column
                table.columns = table.columns.str.lower()  # remove capitalization from each column name
                table.columns = table.columns.str.replace("item", "name", regex=True)
                tables.append(table)  # it is a table we want

    table = pd.concat(tables)
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    table['rarity'] = table['rarity'].apply(lambda x: '1/1' if 'Always' in x else x)  # replaces always with 1/1
    table = table[table.rarity != '1/1']  # remove all always drops
    table = table[table.name != 'Twisted ancestral colour kit']  # remove challenge mode only drop
    table = table[table.name != 'Metamorphic dust']  # remove challenge mode only drop
    table = table[table.name != 'Ancient tablet']  # remove ancient tablet drop
    table['rarity'] = table['rarity'].str.replace(',', "", regex=True)  # removes commas from rarity
    table['rarity'] = table['rarity'].apply(lambda x: re.sub(r'^.*?\u00D7', "", x))  # removes rolls x from rarity
    table['rarity'] = table['rarity'].apply(lambda x: re.sub("[\[].*?[\]]", "", x))  # removes annotations [~]
    table['quantity'] = table['quantity'].apply(
        lambda x: re.sub("[\(].*?[\)]", "", str(x)).strip())  # remove (noted)
    table['quantity'] = table['quantity'].apply(
        lambda x: re.sub(u"\u2013", "-", str(x)))  # replaces en dash with regular dash
    table['quantity'] = table['quantity'].str.replace(',', "", regex=True)  # removes commas from quantity
    table['rarity'] = table['rarity'].apply(lambda x: re.sub('\u2013.*$', "", x))  # removes -1/6500 from rarity
    table['rarity'] = table['rarity'].apply(pd.eval)  # evaluates each rarity as double
    table['rarity'] = table['rarity'].apply(lambda x: x - 0.01 if x == 2.90 else x)  # subtracts 0.01 from mega rares
    table['rarity'] = table['rarity'].apply(lambda x: x * .01 if x > 1 else x)  # converts to decimal

    # store ids in a new column gathered from the osrs-box db

    ids_to_be_added = []  # ids of each item
    drop_types_to_be_added = []  # type of drop of each item

    my_items = items.load()

    # translate assumed value of each quantity to rolled quantity at 30k points
    table.loc[table.name == 'Death rune', 'quantity'] = "833"
    table.loc[table.name == 'Blood rune', 'quantity'] = "937"
    table.loc[table.name == 'Soul rune', 'quantity'] = "1500"
    table.loc[table.name == 'Rune arrow', 'quantity'] = "2142"
    table.loc[table.name == 'Dragon arrow', 'quantity'] = "148"
    table.loc[table.name == 'Grimy ranarr weed', 'quantity'] = "38"
    table.loc[table.name == 'Grimy toadflax', 'quantity'] = "57"
    table.loc[table.name == 'Grimy irit leaf', 'quantity'] = "185"
    table.loc[table.name == 'Grimy avantoe', 'quantity'] = "92"
    table.loc[table.name == 'Grimy kwuarm', 'quantity'] = "79"
    table.loc[table.name == 'Grimy snapdragon', 'quantity'] = "23"
    table.loc[table.name == 'Grimy cadantine', 'quantity'] = "90"
    table.loc[table.name == 'Grimy lantadyme', 'quantity'] = "120"
    table.loc[table.name == 'Grimy dwarf weed', 'quantity'] = "150"
    table.loc[table.name == 'Grimy torstol', 'quantity'] = "37"
    table.loc[table.name == 'Silver ore', 'quantity'] = "1500"
    table.loc[table.name == 'Coal', 'quantity'] = "1500"
    table.loc[table.name == 'Gold ore', 'quantity'] = "681"
    table.loc[table.name == 'Mithril ore', 'quantity'] = "937"
    table.loc[table.name == 'Adamantite ore', 'quantity'] = "180"
    table.loc[table.name == 'Runite ore', 'quantity'] = "15"
    table.loc[table.name == 'Uncut sapphire', 'quantity'] = "159"
    table.loc[table.name == 'Uncut emerald', 'quantity'] = "211"
    table.loc[table.name == 'Uncut ruby', 'quantity'] = "123"
    table.loc[table.name == 'Uncut diamond', 'quantity'] = "59"
    table.loc[table.name == 'Lizardman fang', 'quantity'] = "1071"
    table.loc[table.name == 'Pure essence', 'quantity'] = "15000"
    table.loc[table.name == 'Saltpetre', 'quantity'] = "1250"
    table.loc[table.name == 'Teak plank', 'quantity'] = "312"
    table.loc[table.name == 'Mahogany plank', 'quantity'] = "126"
    table.loc[table.name == 'Dynamite', 'quantity'] = "555"

    # get the id of each item gathered from the wiki by using the osrs-box db

    for row in table.iterrows():
        for item in my_items:
            if item.name == row[1]['name']:
                print(item.name)

                ids_to_be_added.append(int(item.id))

                # determine the drop type
                # Determining the type for clue tables is easy:
                # If it is a clue scroll drop or bloodhound, it is tertiary
                # Everything else is a main drop

                if item.name.__contains__("Clue scroll") or item.name.__contains__("Olmlet"):
                    drop_types_to_be_added.append('tertiary')  # tertiary
                elif item.name.__contains__("Twisted") \
                        or item.name.__contains__("Ancestral") \
                        or item.name.__contains__("Dexterous") \
                        or item.name.__contains__("Arcane") \
                        or item.name.__contains__("claws") \
                        or item.name.__contains__("hunter") \
                        or item.name.__contains__("Dinh's") \
                        or item.name.__contains__("Elder") \
                        or item.name.__contains__("Kodai"):
                    drop_types_to_be_added.append('pre-roll')  # pre-roll
                else:
                    drop_types_to_be_added.append('')  # main drop

                break

    table['id'] = ids_to_be_added
    table['drop-type'] = drop_types_to_be_added
    print(table)

    table.to_json(path_or_buf='C:/Users/Marshall/IdeaProjects/drop-simulator/src/main/resources/chambers.json',
                  orient='table')


# all_tables_to_json writes ALL tables to their own individual json file
def all_tables_to_json():
    all_clue_tables_to_json()
    all_non_npc_tables_to_json()
    cox_table_to_json()


def main():
    all_tables_to_json()


if __name__ == '__main__':
    main()
