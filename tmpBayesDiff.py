import cPickle
import re
import os, sys
from newsTodayClasses import BlogLink, BlogPost
from newsTodayUtils import stripTags, stopWords

cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
categs = cPickle.load(open(cwd + "/postDB_backup2.txt", "r"))

# Makes sure words in one category are not also included in the business category
#
# TODO: refactor me, making me part of a re-usable library (or something)
def getTempCats():
    t = {}
    for c in categs:
        for cat in c.GetCategoriesList():
            try:
                if t.has_key(cat.lower()) == False:
                    t[cat.lower()] = cPickle.load(open(cwd + "/bayesCats/" + cat.lower() + ".txt", "r"))
            except:
    	        pass
    return t

tempCats = {}
if len(tempCats) == 0: tempCats = getTempCats()

list = []
for c in tempCats["business"]:
    if c in tempCats["politics"]: list.append(c)

for l in list: del tempCats["business"][l]

cPickle.dump(tempCats["business"], open(cwd + "/bayesCats/business.txt", "w"))

