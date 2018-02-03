"""
Run the Odds Portal scraping suite, processing all the present tennis league
JSON files in lexicographical order.
"""
#-*- coding: utf-8 -*

import os
import json
from os import listdir, sep, getcwd
from os.path import isfile, join
from Homelist import Homelist

# initialize, and save the default set
if os.path.isfile('set.json'):
    with open('set.json', "r") as f:
        current_set = f.read().replace("\n", "")
    current_set
    # whether the data is correct, if not, delete and reset the default,
    # read the default set
else:
    with open('set.json',"w") as f:
        default_set={"sports": "tennis",
                     "area":"australia",
                     "leagues": "burnie challenger men",
                     "urls": "http://www.oddsportal.com/",
                     "last_update": "1900"
                     }
        json.dump(default_set,f)
        current_set = default_set

# get web page address of all the country and single leagues with "ATP" and "WTA" from 2011-current day
# path_result=join(getcwd() + sep + "leagues")
league_scraper = Homelist(current_set)
league_scraper.scrape_leagues(True)

# path_temp=join(getcwd() + sep + "leagues")
# initialize_json = True
#
# for possible_file in listdir(path_temp):
#     if isfile(join(path_temp, possible_file)):
#         match_json_file = join(path_temp, possible_file)
#         with open(match_json_file, "r") as open_json_file:
#             json_str = open_json_file.read().replace("\n", "")
#             sports_scraper = Homelist(json_str, initialize_json)
#             sports_scraper.scrape_url()
#                 #             if os.path.isdir(sport_path):       #create folders
#                 #     pass
#                 # else:
#                 #     os.mkdir('E:\test')
#


tennis_match_path = "." + sep + "leagues" + sep + "tennis"

initialize_db = True
#
# for possible_file in listdir(tennis_match_path):
#     if isfile(join(tennis_match_path, possible_file)):
#         tennis_match_json_file = join(tennis_match_path, possible_file)
#         with open(tennis_match_json_file, "r") as open_json_file:
#             json_str = open_json_file.read().replace("\n", "")
#             match_scraper = Scraper(json_str, initialize_db)
#             match_scraper.scrape_all_urls(True)
#
#             if initialize_db is True:
#                 initialize_db = False
