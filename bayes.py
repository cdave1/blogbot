from __future__ import division
import cPickle
import re
import os, sys
import codecs
from newsTodayClasses import BlogLink, BlogPost
from newsTodayUtils import stripTags, stopWords


cwd = os.path.dirname(os.path.abspath(sys.argv[0]))

corpus = cPickle.load(open(cwd + "/postDB_backup2.txt", "r"))

# Problem with this is that it does not ignore
# quote marks at the start or end of tokens.
reToken = re.compile(r"[^A-Za-z0-9']*", re.I)

# HACK HACK HACK
#
# Put in the try/catch because I am getting encoding 
# problems from certain characters, and I simply don't have
# time to understand the python encoding libraries to get this
# right...
def TokeniseAll():
	all = {}
	for post in corpus:
		try:
			h = unicode(post.htmlBlock, "utf-8", errors='ignore')
			t = post.title.encode("utf-8", 'ignore')
			words = stripTags(h.encode("utf-8")) + ", " + t
			countTokens(words, all)
		except:
			print "FUCK! encoding problem!!!"
	return all



# tokenises the post - checks if the post
# is part of the supplied category. If it
# is, that post is also tokenised.
#
# HACK HACK HACK:
# The title is included twice as the words in the title
# contain (potentially) more important words.
def toke(catName, post, catTokens):
	try:
		h = unicode(post.htmlBlock, "utf-8", errors='ignore')
		t = post.title.encode("utf-8", 'ignore')
		words = stripTags(h.encode("utf-8")) + ", " + t
	except:
		#print "mutherfuckin shitty post"
		words = ""
		#words = post.htmlBlock.decode("utf-8", 'ignore')

	if post.HasCategory(catName):
		countTokens(words, catTokens)
		return True
	else:
		return False



def countTokens(words, dict):
	for token in words.split(" "):
		if reToken.sub("", token).strip().lower() in stopWords:
			pass
		else:
			if token.isalnum() == False:
				token = reToken.sub("", token)
			if dict.has_key(token.strip().lower()):
				dict[token.strip().lower()] += 1
			else:
				dict[token.strip().lower()] = 1



# Commented out - need some of the funtions below.
#
# Probability that a word indicates that particular category.
def probWord(catTokens, allTokens, NumPostsInCat):
	# print catPosts, len(corpus)
	probs = {}
	if NumPostsInCat < 35: return {}
	for w in catTokens.keys():
		rc = min(1, 10 * (catTokens[w]/NumPostsInCat))
		ra = min(1, allTokens[w]/len(corpus))
		pcatw = max(0.01, min(0.99, ra/(rc+ra)))
		
		if len(w) > 4: probs[w] = pcatw

#	for w in catTokens.keys():
	#	pwcat = 1/NumPostsInCat
	#	if catTokens.has_key(w): pwcat = min(1, catTokens[w]/NumPostsInCat)

	#	pcat = NumPostsInCat/len(corpus)
	#	pw = allTokens[w]/len(allTokens)
	#	pcatw = max(0.01, (pwcat*pcat)/pw)
#		if len(w) > 4: probs[w] = catTokens[w]
	return probs


def catBayesProbability(category, allTokens):
	NumPosts = 0
	catTokens = {}
	instanceCounts = {}
	for c in corpus:
		if len(c.htmlBlock) > 200:
			if toke(category, c, catTokens):
				NumPosts += 1
	print category, NumPosts
	
	if NumPosts < 35: return {}
	
	for w in catTokens.keys():
		if len(w) > 4: instanceCounts[w] = catTokens[w]
	return instanceCounts
	# return probWord(catTokens, allTokens, NumPosts)



def doBayes():
	tempCats = {}
	for c in corpus:
		for cat in c.GetCategoriesList():
			if tempCats.has_key(cat.lower()):
				tempCats[cat.lower()] += 1
			else:
				tempCats[cat.lower()] = 1
	
	allTokens = TokeniseAll()
				
	for category in tempCats.keys():
		d = catBayesProbability(category, allTokens)
		if len(d) > 0: cPickle.dump(d, open(cwd + "/bayesCats/" + category + ".txt", "w"))
	cPickle.dump(allTokens, open(cwd + "/bayesCats/allTokens.txt", "w"))



def doCatReplace():
    for c in corpus:
        if c.HasCategory("business") or c.HasCategory("money"): # and c.HasCategory("politics"):
            print c.title, c.categories
            #c.removeAllCategories()
            #c.addCategory("politics")
    allTokens = TokeniseAll()
    poli = catBayesProbability("politics", allTokens)
    if len(poli) > 0: cPickle.dump(poli, open(cwd + "/bayesCats/politics.txt", "w"))

    bus = catBayesProbability("business", allTokens)
    if len(bus) > 0: cPickle.dump(bus, open(cwd + "/bayesCats/business.txt", "w"))


print doBayes()



