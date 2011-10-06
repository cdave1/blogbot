import cPickle
from newsTodayClasses import BlogLink, BlogPost


postListLoaded = cPickle.load(open("pickletest.txt", "r"))


for link in postListLoaded.values():
	print "<a href='%s'>%s</a>" % (link.url, link.url)
	print "<br><br><ul>"
	for post in link.posts:
		print "<li><a href='%s'>%s</a> on %s<br />" % (post.url.encode('utf8'), post.title.encode('utf8'), post.date)
		# print post.htmlBlock.decode('iso-8859-1')
	print "</ul>"

