"""
Function that finds the most wordy chunk of text on a webpage.

It makes the assumption that this is location of the main block of content, and
spits out the inner text as plain text.
"""
import re
import sys
from BeautifulSoup import BeautifulSoup, SoupStrainer
from parseUtils import loadURL
from bayesCalcer import getProbableCategory
from newsTodayClasses import BlogLink, BlogPost



def getChunks(url):
    try:
        soup = BeautifulSoup(loadURL(url))
    except:
        # print "Page load failed, probably because the web page could not be reached."
        return ""
    
    tags =  soup.find('div')
    if tags == None: return ""
    tags = tags.findAllNext('div')
    tags = [str(''.join(map(str, t.contents))) for t in tags if len(t.contents) > 0]
    tags.sort(longer)
    return stripTags(tags[0])



# Spits out xml representation of the selected page, its main "content chunk",
# url, title, etc...
def getPageInfo(url):
    info = {}
    try:
        soup = BeautifulSoup(loadURL(url))
    except:
        # print "Page load failed, probably because the web page could not be reached."
        return ""
    # info['images'] = soup.findAll('img')
    tags =  soup.find('div')
    desc = ""
    if tags == None: 
        tags = []
        tags.append(soup.find('body'))
        desc = stripTags(str(soup.find('body')))
    else: 
        tags = tags.findAllNext('div')
        tags = [str(''.join(map(str, t.contents))) for t in tags if len(t.contents) > 0]
        tags.sort(longer)
        desc = stripTags(tags[0])

    try:
        tmp = BlogPost(url, soup.html.head.title.string, "", "", 0, desc)
    except:
        tmp = BlogPost(url, url, "", "", 0, desc)
    
    category = getProbableCategory(tmp)

    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<category>'
    print '<title><![CDATA[' + tmp.title.encode('utf-8') + ']]></title>'
    print '<item>'
    print '<url><![CDATA[' + url + ']]></url>'
    if len(category) > 0: print '<cat>' + category + '</cat>'
    print '<title><![CDATA[' + tmp.title.encode('utf-8') + ']]></title>'
    print '<description>'
    print '<![CDATA[' + desc + ']]>'
    print '</description>'
    print '</item>'
    print '</category>'



# Given an HTML block of any length, determine the average
# length of each uninterrupted string in the block. Return 0 if the sentences
# contain no sentences between HTML tags.
def AvgSentenceLength(htmlBlock):
    if len(htmlBlock) == 0: return 0
    stopTags = re.compile(r"<[\/]*\s*(p|strong|em|i|b|u|br|li|ul|h1|h2|h3|a)\s*>", re.M|re.I|re.S)
    remove_img = re.compile(r"<\s*(a|img).*?\s*>", re.M|re.I|re.S)
    htmlBlock = stopTags.sub(" ", htmlBlock)
    strs = re.split(r"<[^>]+>|\n", htmlBlock)
    return sum(map(len, strs)) / len(strs)



# Strips unwanted tags from a block of HTML
def stripTags(str):
	# matches multiline <script ...</script> tags.
	js = re.compile(r"<\s*(script|form).*?<\s*\/\s*(script|form)\s*>", re.M|re.I|re.S)
	r = re.compile(r"<[^>]+>|\n", re.I)
	ws = re.compile(r"\s+")
	str = js.sub("", str)
	str = r.sub(" ", str)
	return ws.sub(" ", str)



# print tags
def longer(a,b):
    try:
        if AvgSentenceLength(a) < AvgSentenceLength(b): return 1
        if AvgSentenceLength(a) == AvgSentenceLength(b): return 0
        return -1
    except:
        return 0


