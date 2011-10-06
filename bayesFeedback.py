from __future__ import division
import feedparser
import cPickle
import os
from BeautifulSoup import BeautifulSoup
import os.path, sys
from datetime import datetime, timedelta
import time
import re
from urlparse import urlparse
from newsTodayClasses import BlogLink, BlogPost
from newsTodayUtils import stripTags, stopWords
from chunker import getChunks

cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
BlogPosts = cPickle.load(open(cwd + "/postDB_backup.txt", "r"))
readerOutput = cPickle.load(open(cwd + "/readerOutput.txt", "r"))

oneDayAgo = datetime.today() + timedelta(hours=-24)

print "Orig len: ", len(BlogPosts)

def parseEntries(cat, url):
    try:
        d = feedparser.parse(url)
    except:
        print "could not parse url", url
        return
    for entry in d.entries:
        try:
            # print datetime(*entry.date_parsed[0:7]), entry.title
            if dupeCheck(entry.link) == True:
                print "Dupe found - ignoring..."
            else:
                if datetime(*entry.date_parsed[0:7]) >= oneDayAgo:
                    if entry.has_key('content'):
                        for c in entry.content:
                            post = BlogPost(entry.link, entry.title, d.feed.title, d.feed.link, datetime(*entry.date_parsed[0:7]), findPostTextForLink(entry.link, c.value))
                            post.addCategory(cat)
                            BlogPosts.append(post)
                    elif entry.has_key('summary_detail'):
                        post = BlogPost(entry.link, entry.title, d.feed.title, d.feed.link, datetime(*entry.date_parsed[0:7]), findPostTextForLink(entry.link, entry.summary_detail.value))
                        post.addCategory(cat)
                        BlogPosts.append(post)
        except:
            print "OMG! FEED HAS GONE"



# determines if we already have an entry for the incoming link...
def dupeCheck(link):
    for p in BlogPosts: 
        if (p.url == link): return True
    return False



def findPostTextForLink(link, alt):
    chunk = getChunks(link)
    if len(chunk) == 0: return alt
    return chunk



parseEntries("entertainment", "http://www.newstoday.co.nz/Entertainment/rss")
parseEntries("travel", "http://www.newstoday.co.nz/Travel/rss")
parseEntries("tech", "http://www.newstoday.co.nz/Technology/rss")
parseEntries("sport", "http://www.newstoday.co.nz/Sport/rss")
parseEntries("politics", "http://www.newstoday.co.nz/Politics/rss")
parseEntries("business", "http://www.newstoday.co.nz/Business/rss")
parseEntries("international", "http://www.newstoday.co.nz/International/rss")
parseEntries("nz", "http://www.newstoday.co.nz/National/rss")

cPickle.dump(BlogPosts, open(cwd + "/postDB_backup2.txt", "w"))
