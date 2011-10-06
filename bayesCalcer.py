from __future__ import division
import cPickle
import re
import os, sys
from newsTodayClasses import BlogLink, BlogPost
from newsTodayUtils import stripTags, stopWords

cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
categs = cPickle.load(open(cwd + "/postDB_backup2.txt", "r"))
corpus = cPickle.load(open(cwd + "/readerOutput.txt", "r"))
reToken = re.compile(r"[^A-Za-z0-9']*", re.I)



tempCats = {}
finalCats = {}

for c in categs:
	for cat in c.GetCategoriesList():
		try:
			if tempCats.has_key(cat.lower()) == False:
				tempCats[cat.lower()] = cPickle.load(open(cwd + "/bayesCats/" + cat.lower() + ".txt", "r"))
			if finalCats.has_key(cat.lower()) == False:
				finalCats[cat.lower()] = []
		except:
			pass # print "No file found for", cat



# tokenise a post, and then calculate the pcatw for each token
#
# Returns a list of all categories and the probability that the
# supplied post belongs to that category.
def GetCategoryProbabilities(post, tempCats):
    results = {}
    allTokens = cPickle.load(open(cwd + "/bayesCats/allTokens.txt", "r"))

    if len(tempCats) == 0: tempCats = getTempCats()
    for category in tempCats.keys():
        catTokens = tempCats[category]
        words = stripTags(post.htmlBlock) + ", " + post.title.encode("ascii", "ignore") # + ", " + post.title.encode("utf8")
        #probs = {}
	instancesCat = {}
	instancesAll = {}

	# strip and lower all the words
	wordsList = map((lambda s: s.lower()), map((lambda s: s.strip()), words.split(" ")))

        for token in wordsList:
            #if reToken.sub("", token).strip().lower() in stopWords:
            #    pass
            #else:
            if token.isalnum() == False:
                token = reToken.sub("", token)

            if catTokens.has_key(token): instancesCat[token] = catTokens[token]
	    else: instancesCat[token] = 1

	    if allTokens.has_key(token): instancesAll[token] = allTokens[token]
            else: instancesAll[token] = 1
	
        valuesCat = instancesCat.values()
	valuesAll = instancesAll.values()
        valuesCat.sort()
	valuesAll.sort()
	
	pcat = 1.0
        pwcat = 1.0
        pw = 1.0
		
        for i in range(min(15, len(valuesCat))):
            pwcat = (valuesCat[i]) * pwcat
        for i in range(min(15, len(valuesAll))):
            pw = (valuesAll[i]) * pw
		
        if pw == 0:
            results[category] = 0
        else:
            results[category] = (pcat * pwcat)/pw

    return results



# temp cats are go!
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



def getFinalCats():
    f = {}
    f["Uncategorised"] = []
    for c in categs:
    	for cat in c.GetCategoriesList():
    		if f.has_key(cat.lower()) == False:
    			f[cat.lower()] = []
    return f



# Get the probability list for each post, and then
# add the post into the dictionary with the highest 
# probability that matches a category.
def doBayes(b):
    tempCats = getTempCats()
    finalCats = getFinalCats()
    for c in corpus:
        results = GetCategoryProbabilities(c, tempCats)
        keys = results.keys()
        keys.sort()
        highestCat = 0
        highestCatKey = "Uncategorised" 
        if len(c.htmlBlock) > 500:
            print ""
            #for key in keys:
                # print key[0:6], '\t', "%1.3f" % results[key]
                #if results[key] > 0.20 and results[key] > highestCat:
                #   highestCat = results[key]
                #   highestCatKey = key
            if len(highestCatKey) > 0:
                print c.title.encode('utf8'), '\t', highestCat, highestCatKey
                finalCats[highestCatKey].append(c)
    
    
    
    # outputs all the posts into different category html files.
    keys = finalCats.keys()
    keys.sort()
    for k in keys:
        f = open('/home/starterbase/subdomains/admin/httpdocs/' + k + '.xml', 'w')
        #f = open(cwd + "/postOutput/" + k + '.xml', 'w')
    	
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<category>\n')
        f.write("<title>" + k.capitalize() + "</title>\n")
        for post in finalCats[k]:
            f.write("<item>\n")
            f.write("<url>" + post.url.encode('utf8') + "</url>")
            f.write("<title>" + post.title.encode('utf8', 'ignore') + "</title>")
            f.write("<date>" + str(post.date) + "</date>")
            f.write("<description><![CDATA[\n")
            f.write(post.htmlBlock.encode('utf8', 'ignore'))
            f.write("]]></description>\n")
            f.write("</item>\n")
        f.write("</category>\n")
        f.close()
        


# Finds the most likely category for the post.
def getProbableCategory(post):
    results = GetCategoryProbabilities(post, {})
    keys = results.keys()
    keys.sort()
    highestCat = 0
    highestCatKey = "" 
    
    for key in keys:
        if results[key] > highestCat and key != 'u':
            highestCat = results[key]
            highestCatKey = key
    
    return highestCatKey
    

doBayes(1) #sys.argv[1])
	

