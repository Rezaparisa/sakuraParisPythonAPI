import requests
import json
import re
from entryClass import Entry
import traceback

# return [[Entry], nextPageMarker]

# q: search keyword（UTF-8 urlencode）
# dict: dictionary name（UTF-8 urlencode）
# type: (optional) search type。 0 = 前方一致, 1 = 後方一致, 2 = 完全一致。default = 0 (前方一致)
# romaji: (optional) "ローマ字変換" enable switch。0 = 無効 (disable), 1 = 有効 (enable)。default = 0
# max: (optional)　Valid range: 1-40)
# marker: (optional) Pagination marker, see above.
# page & offset:　fetch a specific word from dict.

def queryApi(word : str, dictionary : str, maxEntries = 40, type = 1, romaji = 0, marker = "", removeTags = True, removeFirstDef = True):
    url = "https://sakura-paris.org/dict/"
    params = {
        "api" : "1",
    }

    params["q"] = word
    params["dict"] = dictionary
    params["type"] = str(type)
    params["romaji"] = romaji
    params["max"] = min(maxEntries, 40)
    
    if marker != "":
        params["marker"] = marker

    result = None

    #try getting the api response and parse
    try:
        response = requests.get(url, params)

        #if response was received, parse and place in result
        if response:
            responseObj = response.json()

            if isinstance(responseObj, list):
                if removeTags or removeFirstDef:
                    cleanText(responseObj, removeTags, removeFirstDef)
                result = [convertToEntryList(responseObj), ""]

            elif isinstance(responseObj, object):
                if removeTags or removeFirstDef:
                    cleanText(responseObj["words"], removeTags, removeFirstDef)

                result = [convertToEntryList(responseObj["words"]), responseObj["nextPageMarker"]]

        #if no response do nothing 

    except Exception as e :
        print("---EXCEPTION OCCURRED IN FUNCTION sakuraParisAPI.getEntries---")
        print(traceback.format_exc())

    return result

#converts list of dictionaries into list of entries
def convertToEntryList(dicList: list[Entry]):
    result = []

    for word in dicList:
        heading = word["heading"]
        text = word["text"]
        page = ""
        offset = ""

        if "page" in word:
            page = word["page"]

        if "offset" in word:
            offset = word["offset"]

        result.append(Entry(heading, text, page, offset))

    return result

#returns output without tags
def cleanText(input: list[dict], removeTags: bool, removeFirstDef: bool):
    for _ in input:
        heading = _["heading"]
        definition = _["text"]

        if removeTags:
            heading = clearTags(_["heading"])
            definition = clearTags(_["text"])

        if removeFirstDef:
            definition = removeFirstLine(definition)

        _["heading"] = heading
        _["text"] = definition

def clearTags(s: str):
    return re.sub(r'\[.*?\]', '', s)

#removes first line of string
def removeFirstLine(s: str):
    i = 0
    while s[i] != '\n' and i < len(s):
        i += 1

    return s[i:]

a = queryApi("か", "広辞苑", 3, removeFirstDef = True)[0]

for entry in a :
    print(entry.getHeading())
    print(entry.getDefinition())
