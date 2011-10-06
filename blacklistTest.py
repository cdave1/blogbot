blacklist = []
blacklistFile = open("blacklist")








links = ["http://www.google.com", "www.stuff.co.nz", "www.nzherald.co.nz", "mailto:t@m.com"]





loadBlacklist()
for link in links:
	print blackListCheck(link)