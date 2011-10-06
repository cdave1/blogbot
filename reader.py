"""
Gather together a bunch of RSS feeds into an RSS
object from the RSS.py project.
"""

import feedparser
from newsTodayClasses import BlogLink, BlogPost
import cPickle
import os
import sys
from BeautifulSoup import BeautifulSoup
import os.path
from datetime import datetime, timedelta
import urllib2
import time
import re
import htmllib
import formatter
from urlparse import urlparse

# Simply ties a link to one or more posts
linkDict = {}
BlogPosts = []
blacklist = []

oneMonthAgo = datetime.today() + timedelta(weeks=-4)
oneWeekAgo = datetime.today() + timedelta(weeks=-1)
oneDayAgo = datetime.today() + timedelta(days=-1)
oneHourAgo = datetime.today() + timedelta(hours=-1)
twoHoursAgo = datetime.today() + timedelta(hours=-2)
fourHoursAgo = datetime.today() + timedelta(hours=-4)
cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
blacklistFile = open(cwd + "/blacklist")



# To do:
# - Reject recursive links
# - Store the details of the linking post.
# - Reject links from the black list (feedburner, technorati, etc)
def writeLinks(post):
	soup = BeautifulSoup(post.htmlBlock)
	parsed = urlparse(post.url)
	
	for link in soup.findAll('a'):
		if link['href']:
			if link['href'].find(parsed[1]) > -1:
				print "Recursive link was ignored:" + link['href']
			elif isOnBlacklist(link['href']):
				print link['href'] + " is on the black list"			
			elif linkDict.has_key(link['href']):
				linkDict[link['href']].addPost(post)
			else:
				linkDict[link['href']] = BlogLink(link['href'], post)



# Black list should be made of regular expressions rather
# than root domains.		
def loadBlacklist():
	for line in blacklistFile.readlines():
		blacklist.append(line.replace('\n', ''))



def isOnBlacklist(url):
	if len(blacklist) == 0: loadBlacklist()
	for b in blacklist:
		if url.find(b) > -1: return True
	return False



# Note: encoding in utf8 seems to prevent these kinds of errors:
#
# rss python parser'ascii' codec can't encode character...
def parseEntries(url):
	try:
		d = feedparser.parse(url)
	except:
		print "could not parse url", url
		return
	for entry in d.entries:
		try:
			if datetime(*entry.date_parsed[0:7]) >= oneDayAgo:
				if entry.has_key('content'):
					for c in entry.content:
						post = BlogPost(entry.link, entry.title, d.feed.title, d.feed.link, datetime(*entry.date_parsed[0:7]), c.value)
						BlogPosts.append(post)
						writeLinks(post)
				elif entry.has_key('summary_detail'):
					post = BlogPost(entry.link, entry.title, d.feed.title, d.feed.link, datetime(*entry.date_parsed[0:7]), entry.summary_detail.value)
					BlogPosts.append(post)
					writeLinks(post)
		except:
			print "There was a fucking problem with the fucking feed"



#/for file in os.listdir("feeds"):
#/	linkDict = {}
#/	parseEntries("feeds/" + file)
#/	
#/	for key in linkDict.keys():
#/		dumpFile.write(str(linkDict[key]) + ',' + key + '\n')



# Finds the most popular links in RSS feeds in the rssFile.
def popLinks():
	# linkDict = cPickle.load(open("pickletest.txt", "r"))
	
	dumpFile = open(cwd + "/linkDump.txt", "w")
	rssFile = open(cwd + "/rssFile.txt")
	for line in rssFile.readlines():
		print line
		parseEntries(line)

	cPickle.dump(BlogPosts, open(cwd + "/readerOutput.txt", "w"))
	for key in linkDict.keys():
		dumpFile.write(linkDict[key].size() + ',' + key + '\n')

	cPickle.dump(linkDict, open(cwd + "/pickletest.txt", "w"))



# completes a relative url.
def urlComplete(url, href):
	ignore = re.compile(r"^(http://|mailto:|ftp://)")
	if ignore.match(href):
		return href
	else:
		parsed = urlparse(url)
		return parsed[0] + "://" + parsed[1] + href
		


# Goes to the URL and tries to find an RSS feed.
# 
# Writes the first available RSS feed out to file.
def findRSS(url):
	soup = BeautifulSoup(loadURL(url))
	
	if soup == None: 
		print url + ": page not found"
		return
	for rss in soup.findAll('link'):
		try:
			if rss['type'].upper().find('RSS') != -1:
				rssFile.write(urlComplete(url, rss['href']) + '\n')
				break
			elif rss['type'].upper().find('ATOM') != -1:
				rssFile.write(urlComplete(url, rss['href']) + '\n')
				break
		except:
			print "could not find rss feed in", url







popLinks()




# Goes off and gets all the RSS feeds from a list of sites

#/findRSS("http://actoncampus.blogspot.com/")
#/findRSS("http://andrewfalloon.blogspot.com/")
#/findRSS("http://bzp.blogspot.com/")
#/findRSS("http://big-news.blogspot.com/")
#/findRSS("http://brooklynblue.blogzone.co.nz")
#/findRSS("http://asianinvasion2006.blogspot.com/")
#/findRSS("http://chaucey.blogspot.com/index.html")
#/findRSS("http://clintheine.blogspot.com/")
#/findRSS("http://www.cloudsofheaven.org")
#/findRSS("http://craigfoss.co.nz/")
#/findRSS("http://www.darntonvsclark.org")
#/findRSS("http://davegee.blogspot.com/")
#/findRSS("http://www.ellisnz.com/")
#/findRSS("http://theeverlastingman.blogspot.com/")
#/findRSS("http://generation-xy.blogspot.com/")
#/findRSS("http://geniusnz.blogspot.com/index.html")
#/findRSS("http://gmaninc.blogspot.com/")
#/findRSS("http://gonzofreakpower.blogspot.com/")
#/findRSS("http://rupahu.blogspot.com/")
#/findRSS("http://craigmranapia.blogspot.com/")
#/findRSS("http://hittingmetalwithahammer.wordpress.com")
#/findRSS("http://billenglish.co.nz/")
#/findRSS("http://mikeenz.blogspot.com/")
#/findRSS("http://insolentprick.blogspot.com/")
#/findRSS("http://jwatson.kol.co.nz/index.html")
#/findRSS("http://kearney.blogspot.com/")
#/findRSS("http://latitude45south.blogspot.com/index.html")
#/findRSS("http://libfront.blogspot.com/")
#/findRSS("http://libertyscott.blogspot.com/")
#/findRSS("http://lindsaymitchell.blogspot.com/")
#/findRSS("http://mandmandmandm.blogspot.com/index.html")
#/findRSS("http://metcalph.blogspot.com/index.html")
#/findRSS("http://blairmulholland.typepad.com/mulholland_drive/")
#/findRSS("http://multipledispatch.blogspot.com/")
#/findRSS("http://newzeal.blogspot.com/")
#/findRSS("http://nicholasokane.wordpress.com")
#/findRSS("http://pc.blogspot.com/")
#/findRSS("http://nzmediabias.blogspot.com/")
#/findRSS("http://nzconservative.blogspot.com/")
#/findRSS("http://mikeheine.blogspot.com/")
#/findRSS("http://oswaldbastable.blogspot.com/")
#/findRSS("http://pacificempire.org.nz")
#/findRSS("http://www.porkpie.co.nz/")
#/findRSS("http://auntiesworld.blogspot.com/index.html")
#/findRSS("http://peteremcc.wordpress.com")
#/findRSS("http://puntiki.blogspot.com/")
#/findRSS("http://hosking.blogspot.com/index.html")
#/findRSS("http://www.rodneyhide.com/index.php/weblog/index/")
#/findRSS("http://sagenz.typepad.com/sagenz/")
#/findRSS("http://scottkennedy.blogspot.com/")
#/findRSS("http://www.freespeech.org.nz/section14")
#/findRSS("http://section59.blogspot.com/")
#/findRSS("http://setcond1.blogspot.com/index.html")
#/findRSS("http://silentrunning.tv")
#/findRSS("http://www.sirhumphreys.com")
#/findRSS("http://socialistfree.blogspot.com/")
#/findRSS("http://halfdone.wordpress.com")
#/findRSS("http://76spirit.blogspot.com/index.html")
#/findRSS("http://www.spitting-llama.info/")
#/findRSS("http://www.stephenfranks.co.nz")
#/findRSS("http://studentchoice.blogspot.com/")
#/findRSS("http://briefingroom.typepad.com/the_briefing_room/")
#/findRSS("http://www.tbr.cc")
#/findRSS("http://thisischristchurch.blogspot.com/")
#/findRSS("http://bluewattledcrow.blogspot.com/")
#/findRSS("http://www.whaleoil.co.nz")
#/findRSS("http://thewhig.typepad.com/the_whig/")
#/findRSS("http://zealandwhinge.blogspot.com/")
#/findRSS("http://www.swoboda.net.nz/zen/")
#/findRSS("http://cog.org.nz")
#/findRSS("http://garethrobinson.net.nz")
#/findRSS("http://www.holdenrepublic.org.nz/")
#/findRSS("http://hot-topic.co.nz")
#/findRSS("http://laws179.blogspot.com/")
#/findRSS("http://lawswatch.blogspot.com/")
#/findRSS("http://ngakorero.blogspot.com/index.html")
#/findRSS("http://newzealandconservative.blogspot.com/")
#/findRSS("http://nzhumanrightslawyer.blogspot.com/")
#/findRSS("http://plaguehouse.blogspot.com/")
#/findRSS("http://billwilmot.blogspot.com/")
#/findRSS("http://tamakiblog.blogspot.com/index.html")
#/findRSS("http://finsec.wordpress.com")
#/findRSS("http://aboutown.blogspot.com/")
#/findRSS("http://anarchafairy.wordpress.com")
#/findRSS("http://anarchia.wordpress.com")
#/findRSS("http://aucklanderatlarge.blogspot.com/")
#/findRSS("http://blog.myspace.com/julianblanchard")
#/findRSS("http://bloggreen.wordpress.com")
#/findRSS("http://capitalismbad.blogspot.com/")
#/findRSS("http://contradiction.wordpress.com")
#/findRSS("http://fightingtalk.blogspot.com/")
#/findRSS("http://blog.greens.org.nz")
#/findRSS("http://fundypost.blogspot.com/")
#/findRSS("http://tonymilne.blogs.com/i_see_red/")
#/findRSS("http://joehendren.blogspot.com/")
#/findRSS("http://jtc.blogs.com/just_left/")
#/findRSS("http://liberation.typepad.com/liberation/")
#/findRSS("http://memorypocket.wordpress.com")
#/findRSS("http://norightturn.blogspot.com/")
#/findRSS("http://observationz.blogspot.com/")
#/findRSS("http://parrotonpolitics.blogspot.com/")
#/findRSS("http://redbears.blogspot.com/")
#/findRSS("http://pixnaps.blogspot.com/")
#/findRSS("http://prayingmantis.blogtown.co.nz")
#/findRSS("http://www.publicaddress.net/")
#/findRSS("http://redconfectionery.blogspot.com/")
#/findRSS("http://woodm.blogspot.com/2007/01/new-blogger.html")
#/findRSS("http://singlemaltsocialdemocrat.blogspot.com/")
#/findRSS("http://sleeponpolitics.blogspot.com/")
#/findRSS("http://spanblather.blogspot.com/")
#/findRSS("http://greengeneration.blogspot.com/")
#/findRSS("http://thorndon.blogspot.com/")
#/findRSS("http://tumeke.blogspot.com/")
#/findRSS("http://uncensored.co.nz")
#/findRSS("http://unityaotearoa.blogspot.com/")
#/findRSS("http://whoar.co.nz")
#/findRSS("http://www.nznews.org.nz/")
#/findRSS("http://aardvark.co.nz/")
#/findRSS("http://bramcohen.livejournal.com/")
#/findRSS("http://chocnvodka.blogware.com/blog")
#/findRSS("http://icannblog.org")
#/findRSS("http://www.cre8d-design.com")
#/findRSS("http://daniel.expdev.net")
#/findRSS("https://www.tuanz.org.nz/blog/e379f711-b2b6-4423-9e32-4a8bf9f301db.html")
#/findRSS("http://weblog.johnlevine.com")
#/findRSS("http://frasertalk.blogspot.com/")
#/findRSS("http://community.canada.com/geekboutique")
#/findRSS("http://www.geekzone.co.nz/tonyhughes")
#/findRSS("http://griffinsgadgets.blogspot.com/")
#/findRSS("http://blog.lextext.com/blog")
#/findRSS("http://blog.internetnz.net.nz")
#/findRSS("http://www.mattb.net.nz/blog")
#/findRSS("http://www.geekzone.co.nz/freitasm")
#/findRSS("http://www.ibiblio.org/ahkitj/diaries/tph/")
#/findRSS("http://www.byte.org/blog")
#/findRSS("http://www.readwriteweb.com/")
#/findRSS("http://www.hydro.gen.nz/blog")
#/findRSS("http://sorryexcuse.com")
#/findRSS("http://thespamdiaries.blogspot.com/")
#/findRSS("http://stevesramblings.com/")
#/findRSS("http://scrawford.blogware.com/blog")
#/findRSS("http://www.geekzone.co.nz/juha")
#/findRSS("http://till.co.nz/tillnet")
#/findRSS("http://writedisability.blogspot.com/")
#/findRSS("http://www.kiwibohemian.com/")
#/findRSS("http://alastairamerica.blogspot.com/")
#/findRSS("http://www.apricotflan.com")
#/findRSS("http://onceuponatime.blog.com/")
#/findRSS("http://athomewithrose.blogspot.com/")
#/findRSS("http://thebackyard.blogspot.com/")
#/findRSS("http://barzoomian.blogspot.com/")
#/findRSS("http://www.stonesoup.co.nz/ecoqueer/")
#/findRSS("http://blogithowitis.blogspot.com/index.html")
#/findRSS("http://thebonnieandclydeshow.blogspot.com/")
#/findRSS("http://brainstab.blogspot.com/")
#/findRSS("http://my-breakfast-at-tiffanys.blogspot.com/index.html")
#/findRSS("http://brightcopperkettles.blogspot.com/")
#/findRSS("http://benkepes.wordpress.com")
#/findRSS("http://miramarmike.blogspot.com/")
#/findRSS("http://toscie.blogspot.com/")
#/findRSS("http://frothmouthedlefty.blogspot.com/")
#/findRSS("http://deadkiwis.blogspot.com/index.html")
#/findRSS("http://dubdotdash.blogspot.com/")
#/findRSS("http://duckenvy.blogspot.com/")
#/findRSS("http://jimdonovan.net.nz")
#/findRSS("http://enragedandamused.blogspot.com/")
#/findRSS("http://fearandloathinginwangavegasv2.blogspot.com/index.html")
#/findRSS("http://eleanorpulpit.blogspot.com/")
#/findRSS("http://grosslyexcessive.blogspot.com/index.html")
#/findRSS("http://halfpie.net/")
#/findRSS("http://hkham.wordpress.com")
#/findRSS("http://aarontck.spaces.live.com/")
#/findRSS("http://timandmegan.babbage.tv/")
#/findRSS("http://idlevice.blogspot.com/")
#/findRSS("http://jaggylioness.blogspot.com/index.html")
#/findRSS("http://jimmyjangles.blogspot.com/")
#/findRSS("http://macilree.blogspot.com/")
#/findRSS("http://nbr.co.nz/smythe/index.html")
#/findRSS("http://jothespoiltbrat.blogspot.com/")
#/findRSS("http://thekiwiadventurer.blogspot.com/")
#/findRSS("http://flying0kiwi.blogspot.com/")
#/findRSS("http://kiwiherald.blogspot.com/")
#/findRSS("http://kiwilog.blogspot.com/index.html")
#/findRSS("http://kiwitrader.blogspot.com/")
#/findRSS("http://kiwigirl28.blogspot.com/")
#/findRSS("http://krimsonlake.blogspot.com/")
#/findRSS("http://oharg.blogspot.com/")
#/findRSS("http://jeronamo1.blogspot.com/")
#/findRSS("http://lisaland.blog.com/")
#/findRSS("http://mariavontrapp.blogspot.com/")
#/findRSS("http://m2v.blogspot.com/index.html")
#/findRSS("http://argantemiscellany.blogspot.com/index.html")
#/findRSS("http://blog.morph.net.nz")
#/findRSS("http://nathanaelbaker.blogspot.com/")
#/findRSS("http://neilsanderson.com")
#/findRSS("http://nzart-lizzie-l.blogspot.com/")
#/findRSS("http://nzaid.blogspot.com/")
#/findRSS("http://www.nzbc.net.nz/")
#/findRSS("http://objectdart.wordpress.com")
#/findRSS("http://officegirlnz.blogspot.com/index.html")
#/findRSS("http://uroskin.blogspot.com/")
#/findRSS("http://leslyfinnsart.blogspot.com/")
#/findRSS("http://petone.blogspot.com/index.html")
#/findRSS("http://phrenicphilosophy.blogspot.com/index.html")
#/findRSS("http://pmofnz.blogspot.com/")
#/findRSS("http://www.ponoko.com/blog")
#/findRSS("http://contributionz.blogspot.com/")
#/findRSS("http://rattusnorvegus.blogspot.com/")
#/findRSS("http://razork.blogspot.com/")
#/findRSS("http://www.realbeer.co.nz/blog/blog.html")
#/findRSS("http://reinventingtvnz.blogspot.com/index.html")
#/findRSS("http://restarea300.blogspot.com/")
#/findRSS("http://rcd.typepad.com/personal/")
#/findRSS("http://secretpassage.livejournal.com/")
#/findRSS("http://www.drury.net.nz")
#/findRSS("http://www.salient.org.nz")
#/findRSS("http://2seek.wordpress.com")
#/findRSS("http://shadowfoot.com/footprints")
#/findRSS("http://www.shes-sassy.net/journal/")
#/findRSS("http://somewherealongtheway.net")
#/findRSS("http://www.spareroom.co.nz")
#/findRSS("http://vital.org.nz/blog")
#/findRSS("http://sportreviewnz.blogspot.com/")
#/findRSS("http://suchsmallportions.blogspot.com/index.html")
#/findRSS("http://sunnyo.blogspot.com/")
#/findRSS("http://susifookes.com")
#/findRSS("http://systemcrashnovel.blogspot.com/index.html")
#/findRSS("http://www.this-chick.com/")
#/findRSS("http://trekkingwithtigers.blogspot.com/")
#/findRSS("http://unpclesbian.blogspot.com/")
#/findRSS("http://urbancast.blogspot.com/index.html")
#/findRSS("http://satsumasalad.livejournal.com/")
#/findRSS("http://wandaharland.blogspot.com/")
#/findRSS("http://ahwellhereiam.blogspot.com/index.html")
#/findRSS("http://wellingtonista.com")
#/findRSS("http://westportnz.blogspot.com/")
#/findRSS("http://wildebeestasylum.blogspot.com/")
#/findRSS("http://windycitygirl06.blogspot.com/")
#/findRSS("http://thewinewanker.blogspot.com/")
#/findRSS("http://www.xero.com/blog/")
