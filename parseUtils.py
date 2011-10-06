import urllib2
import time
import re
import os
from BeautifulSoup import BeautifulSoup
import os.path
import htmllib
import formatter
from urlparse import urlparse

# Loads a url
def loadURL(url):
	# Cookie stuff from: 
	# http://www.voidspace.org.uk/python/articles/cookielib.shtml
	
	COOKIEFILE = '/var/www/vhosts/davesblogbot/cookies.lwp' #/home/virtual/site1/fst/home/newstoday/BayesBlogBot/cookies.lwp'
	
	cj = None
	ClientCookie = None
	cookielib = None
	
	# Let's see if cookielib is available
	try:
	    import cookielib
	except ImportError:
	    try:
	        import ClientCookie
	    except ImportError:
	        urlopen = urllib2.urlopen
	        Request = urllib2.Request
	    else:
	        urlopen = ClientCookie.urlopen
	        Request = ClientCookie.Request
	        cj = ClientCookie.LWPCookieJar()
	
	else:
	    urlopen = urllib2.urlopen
	    Request = urllib2.Request
	    cj = cookielib.LWPCookieJar()
	    
	if cj is not None:
	    if os.path.isfile(COOKIEFILE):
	        cj.load(COOKIEFILE)
	    if cookielib is not None:
	        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	        urllib2.install_opener(opener)
	    else:
	        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
	        ClientCookie.install_opener(opener)
	
	txdata = None
	# if we were making a POST type request,
	# we could encode a dictionary of values here,
	# using urllib.urlencode(somedict)
	
	txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT)'}
	
	try:
	    req = Request(url, txdata, txheaders)
	    handle = urlopen(req)
	except IOError, e:
	    print 'Failed to open "%s".' % url
	    if hasattr(e, 'code'):
	        print 'Failed with error code - %s.' % e.code
	    elif hasattr(e, 'reason'):
	        print "Reason: %s" % e.reason
	    return None
	except:
		return None
	
	print
	if cj is None:
	    print "No cookies available."
	else:
	    #print 'These are the cookies we have received so far :'
	    # for index, cookie in enumerate(cj):
	    #    print index, '  :  ', cookie
	    try:
	    	cj.save(COOKIEFILE)
	    except:
	    	pass
	
	return handle.read()
