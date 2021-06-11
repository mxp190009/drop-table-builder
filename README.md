# Drop Table Builder

Builds Drop Tables in .json format from [The OSRS Wiki](https://oldschool.runescape.wiki/). The [osrsbox api](https://api.osrsbox.com/index.html) also does not contain drop tables for non NPC entities such as raids, clues, barrows, etc. The primary purpose of this application is to build tables for non NPC entities.

## Drop Tables

[OSRS Drop Tables](https://oldschool.runescape.wiki/w/Drop_table) are not as simple as each NPC having a list of items to be dropped upon death. Each NPC actually has multiple drop tables.

- **Pre-roll table**
- **100% Table**
- **Main Table**
- **Tertiary Table**
- **Rare Drop Table**
- **Wilderness Slayer Tertiary Table**
- **Catacombs Tertiary Table**

The [osrsbox api](https://api.osrsbox.com/index.html) contains all of the drop data of all of the monsters in OSRS, but does not differentiate which table described above that the drop belongs too. Simulating drops from this data is not possible because the total probability of dropped items is greater than one, because tertiary, pre-roll drops, etc. are not differentiated from main drops. Therefore, the [RuneLite Drop Simulator](https://github.com/mxp190009/drop-simulator) gathers the drop data, and checks each drop against the wiki to determine which drop the table belongs too. This extra check against the wiki adds a LOT of unnecessary time to the simulation. An added benefit of the drop-table-builder is to gather the data from the wiki while including the type of table each drop belongs too in order to simulate drops as accurately as possible while saving the Drop Simulator the time of checking against the wiki.

## Building Tables
Optimally, the Drop Table Builder would build the tables for all NPCs in the game, but RuneLite plugins have a file limit, and to include a .json file for all NPCs would likely exceed the limit. Therefore, the Drop Table Builder only builds tables for non NPC entities and most bosses. Non NPC entities because they do not exist in the api data, and most bosses because bosses are the most frequently simulated NPCs. By creating boss tables, their simulation times are sped up drastically (essentially instant for any number of trials less than 1,000,000!).

- Initially the Drop Table Builder built the tables using [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), but because the only data being gathered exists in tables, [Pandas](https://pandas.pydata.org/) seems like a more viable alternative.

1. Pandas gets all of the tables on the OSRS wiki page for a specified entity
2. Not each table on the page is a drop table, so only tables with drop data columns are saved

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![tertiary_table](https://user-images.githubusercontent.com/78482082/121637104-86a2ad00-ca4e-11eb-887a-dcccd2d72b93.png)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Example of a table with drop data*

4. The data in the saved tables is then cleaned up and translated into a format usable by the RuneLite Drop Simulator
5. The table is then written to a .json file titled with the name of the entity

- In the future, the Drop Table Builder may scrape the wiki pages for all NPCs and host its data to an AWS database. The Drop Simulator would then access this database and not have to pair drops against the wiki to determine their drop types.
