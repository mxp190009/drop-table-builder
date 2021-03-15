# The drop simulator plugin was capable of doing all of the scraping on its own, but once clue scroll simulations
# were introduced, it was no longer feasible for the plugin to do all of the scraping on its own. The time taken
# to scrape the wiki was too long for anyone to enjoy the plugin. This supplementary python script scrapes the wiki
# and builds a simple relational database .txt file to be included in the plugin resources folder. The plugin will
# still use the osrs-box api for all npcs, this is just for all non-npc tables not included in the osrs-box api.

import requests
from bs4 import BeautifulSoup


def build_table_from_wiki(drop_source):

    url = 'https://oldschool.runescape.wiki/w/' + drop_source
    response = requests.get(url)
    page_content = BeautifulSoup(response.content, 'html.parser')
    print(page_content)


def main():
    build_table_from_wiki('Reward casket (beginner)')
    build_table_from_wiki('Reward casket (easy)')
    build_table_from_wiki('Reward casket (medium)')
    build_table_from_wiki('Reward casket (hard)')
    build_table_from_wiki('Reward casket (elite)')
    build_table_from_wiki('Reward casket (master)')


if __name__ == '__main__':
    main()
