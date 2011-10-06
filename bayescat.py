# A small command line app that allows a human to 
# categorise an existing corpus of blog posts
# for later user by a Bayesian filter.

import cPickle
import re
import sys
from newsTodayClasses import BlogLink, BlogPost

	

corpus = cPickle.load(open("postDB.txt", "r"))
#newbies = cPickle.load(open("postDB3.txt", "r"))
cats = {}
topTenCats = []



def CatReplace(old, new):
	for c in corpus:
		for i in range(len(c.GetCategoriesList())):
			if old.lower() == c.GetCategoriesList()[i].lower():
				c.GetCategoriesList()[i] = new



# CatReplace("China", "International")
# CatReplace("UK", "International")
# CatReplace("Russia", "International")
# CatReplace("Middle East", "International")
# CatReplace("Chuck Norris", "Entertainment")
# CatReplace("Christchurch", "Local")
# CatReplace("Wellington", "Local")
# CatReplace("Auckland", "Local")
# CatReplace("Dunedin", "Local")
# CatReplace("Theatre", "Entertainment")
# CatReplace("Film", "Entertainment")
# CatReplace("Beer", "Food")
# CatReplace("Property", "Money")
# CatReplace("images", "imgvideo")
# CatReplace("video", "imgvideo")
# CatReplace("Journalists", "Opinion")

#for n in newbies:
#	corpus.append(n)
#cPickle.dump(corpus, open("postDB_4.txt", "w"))

for c in corpus:
	for cat in c.GetCategoriesList():
		if cats.has_key(cat.lower()):
			cats[cat.lower()] += 1
		else:
			cats[cat.lower()] = 1

print [[k, cats[k]] for k in cats.keys() if cats[k] > 35]
print ""
print cats
#
def CountCategories():
	count = 0
	for c in corpus:
		if c.hasCategories(): count += 1
	return count
#
#
#
#def CountDubiousCats():
#	count = 0
#	for c in corpus:
#		if len(c.GetCategoriesList()) > 1: count += 1
#	return count



def BayesCat():
	for c in corpus:
		
		if len(c.GetCategoriesList()) == 0:
			print "___________________________________"
			print CountCategories(), "/", len(corpus), " posts have been categorised (", (CountCategories() * 100) / len(corpus), "% )"
			print "TITLE:", c.title.encode("utf8")
			print "SOURCE:", c.channelTitle
			print "CATS:", c.categories
			try:
				print "TEXT:", c.htmlBlock
			except:
				print "TEXT:", unicode(c.htmlBlock, "utf8")
			
			cmd = sys.stdin.readline()
			
			if cmd[0:-1] == "quit": break
			if cmd[0:-1] == "cats":
				for c in cats:
					print c, ","
				cPickle.dump(corpus, open("postDB.txt", "w"))
				BayesCat()
			num = re.compile(r"[0-9]")
			if num.match(cmd[0:-1]):
				s = c.categories[int(cmd[0:-1])]
				c.removeAllCategories()
				c.addCategory(s.strip())
			elif len(cmd[0:-1]) == 0:
				print "first"
				s = c.categories[0]
				c.removeAllCategories()
				c.addCategory(s.strip())			
			else:
				c.removeAllCategories()
				for cat in cmd[0:-1].split(","):
					c.addCategory(cat.strip())
			cPickle.dump(corpus, open("postDB.txt", "w"))
			cPickle.dump(corpus, open("dbBackup.txt", "w"))



#BayesCat()



#CatReplace("Asia", "International")
#CatReplace("Japan", "International")
#CatReplace("Zimbabwe", "International")
#CatReplace("Australia", "International")
#CatReplace("Cuba", "International")
#CatReplace("south america", "International")
#CatReplace("Linux", "Tech")
#CatReplace("Bloggers", "Opinion")
#CatReplace("Religion", "Opinion")
#/CatReplace("Unknown", "u")
#/CatReplace("Freance", "France")
#/CatReplace("Travel'", "Travel")
#/CatReplace("Business. NZ", "Business")
#/CatReplace("Book Reviews", "Books")
#/CatReplace("Religiion", "Religion")
#/CatReplace("Gu", "u")
#/CatReplace("New Zealand", "nz")
#/CatReplace("Bookes", "Books")
#/CatReplace("Book", "Books")
#/CatReplace("Historyu", "History")
#/CatReplace("Job", "Jobs")
#/CatReplace("Politics\\", "Politics")
#/CatReplace("Tec", "Tech")
#/CatReplace("Ignore", "u")
#/CatReplace("Motoring", "u")
#/CatReplace("Busines", "Business")
#/CatReplace("Linkspam", "u")
#/CatReplace("Scam", "Scams")
#/CatReplace("Technology", "Tech")
#/CatReplace("Religion. NZ", "Religion")
#/CatReplace("Gree", "Green")
#/CatReplace("Privacy", "Security")
#/CatReplace("Internation", "International")
#/CatReplace("Russa", "Russia")
#/CatReplace("Gamees", "Games")
#/CatReplace("Wather", "Weather")
#/CatReplace("Expat", "Expats")
#/CatReplace("Phillipines\\", "Phillipines")
#/CatReplace("Internationl", "International")
#/CatReplace("Questions", "Bloggers")
#/CatReplace("Israel'", "Israel")
#/CatReplace("Philipines", "Phillipines")
#/CatReplace("Blogger", "Bloggers")
#/CatReplace("MZ", "NZ")
#/CatReplace("ZN", "NZ")
#/CatReplace("broadband", "Tech")
#/CatReplace("egypt", "Africa")
#/CatReplace("charity", "money")
#/CatReplace("sweden", "europe")
#/CatReplace("italy", "europe")
#/CatReplace("vietnam", "Asia")
#/CatReplace("space", "science")
#/CatReplace("poltics", "politics")
#/CatReplace("movies", "film")
#/CatReplace("syria", "middle east")
#/CatReplace("programming", "tech")
#/CatReplace("culture", "NZ")
#/CatReplace("indonesia", "Asia")
#/CatReplace("Macau", "Asia")
#/CatReplace("Hong Kong", "China")
#/CatReplace("Phillipines", "Asia")
#/CatReplace("Belgium", "Europe")
#/CatReplace("london", "Europe")
#/CatReplace("world", "u")
#/CatReplace("roading", "Travel")
#/CatReplace("finance", "Money")
#/CatReplace("Antwerp", "Europe")
#/CatReplace("Denmark", "Europe")
#/CatReplace("new york", "USA")
#/CatReplace("somalia", "Africa")
#/CatReplace("south africa", "Africa")
#/CatReplace("India", "Asia")
#/CatReplace("waikato", "u")
#/CatReplace("tonga", "Pacific")
#/CatReplace("fiji", "Pacific")
#/CatReplace("reviews", "books")
#/CatReplace("welfare", "Money")
#/CatReplace("iran", "middle east")
#/CatReplace("", "u")
#/CatReplace("islam", "religion")
#/CatReplace("national", "Politics")
#/CatReplace("labour", "Politics")
#/CatReplace("new york", "USA")
#/CatReplace("scotland", "UK")
#/CatReplace("advice", "u")
