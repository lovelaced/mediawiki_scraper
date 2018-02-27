from mediawiki import MediaWiki
from bs4 import BeautifulSoup
import json
from urllib.parse import urlencode
from urllib.request import urlopen
import mwparserfromhell
import re
import sys
import pprint
from pymongo import MongoClient

API_URL = "https://practicalplants.org/w/api.php"

def get_sections(page_title, wiki):
    section_titles = []
    wiki_page = wiki.page(page_title)
    page_html = wiki_page.html
    soup = BeautifulSoup(page_html, "html.parser")
    section_list = soup.select("div.infobox-title")
    for section in section_list:
        section_titles.append(section.get_text())
    return section_titles

def print_section_contents(section_title):
    return


def parse(title):
    data = {"action": "query", "prop": "revisions", "rvlimit": 1,
            "rvprop": "content", "format": "json", "titles": title}
    try:
        raw = urlopen(API_URL, urlencode(data).encode()).read()
    except ConnectionRefusedError:
        print("Oops, connection refused. Retrying...")
        parse(title)

    res = json.loads(raw)
    text = next(iter(res["query"]["pages"].values()))["revisions"][0]["*"]
    return mwparserfromhell.parse(text)


def get_param_dict(templates):
    param_dict = {}
    mw_template = templates[0]

    for entry in mw_template.params:
        value = None
        split_entry = entry.strip().split("=")
        if len(split_entry) < 2:
            value = None
        elif len(split_entry) > 2:
            if "{{" in mw_template.get(split_entry[0]).value and "}}" in mw_template.get(split_entry[0]):
                result = re.sub('{{(.*)}}', '', str(mw_template.get(split_entry[0]).value))
                if result:
                    value = result
        else:
            value = split_entry[1]
        param_dict[split_entry[0]] = value

    for key in param_dict.keys():
        if param_dict[key] is None:
            continue
        try:
           param_dict[key] = re.sub('{{(.*)}}', '', param_dict[key])
           param_dict[key] = re.sub('PFAF(.*[0-9])', '', param_dict[key])
        except TypeError:
            print("TypeError:", param_dict[key])
            sys.exit(1)

        templates = mwparserfromhell.parse(param_dict[key]).filter_templates()
        if templates:
            param_dict[key] = get_param_dict(templates)

        if " " not in param_dict[key] and "," in param_dict[key]:
            param_dict[key] = param_dict[key].split(",")
    return param_dict


try:
    connection = MongoClient("mongodb://localhost:27017")
    connection.database_names()
    db = connection.database
    crops = db.crops
except:
    print("MongoDB connection has failed somehow...")
    sys.exit(1)


# INFO
pp = pprint.PrettyPrinter(indent=4)
full_section_list = []
record_number_ingested = 0

# Get NUM_RESULTS mediawiki pages in specific category
# Set NUM_RESULTS to None to get all pages in category
CATEGORY = "Plant"
NUM_RESULTS = None

plantwiki = MediaWiki(url=API_URL, rate_limit=True, timeout=100)

all_plant_names = plantwiki.categorymembers(CATEGORY, results=NUM_RESULTS, subcategories=False)

for plant_name in all_plant_names:

    wikicode = parse(plant_name)
    templates = wikicode.filter_templates()
    plant_info = get_param_dict(templates)
    record_number_ingested += 1

    # INFO
    section_list = get_sections(all_plant_names[0], plantwiki)
    for section in section_list:
        if section not in full_section_list:
            full_section_list.append(section)
    # MORE INFO
    print("Name:", plant_name)
    print("MongoDB ID:", crops.insert_one(plant_info).inserted_id, "\n")
    #4print("Section list:", section_list)

# EVEN MORE INFO
print("\nList of section keys:")
pp.pprint(full_section_list)
print("Records ingested:", record_number_ingested)
