# Replaces strings in Latin extended with ASCII equivalents.
#
# This is for handling web servers with FUCKED UP encodings.
#
# Oh yeah, this is a big fat hack.
def ReplaceLatinExtended(s):
	s = s.replace("&#8211;", "-")
	s = s.replace("&#8212;", "-")
	s = s.replace("&#8216;", "\'")
	s = s.replace("&#8217;", "\'")
	s = s.replace("&#8218;", ",")
	s = s.replace("&#8220;", "\"")
	s = s.replace("&#8221;", "\"")
	s = s.replace("&#8222;", "\"")
	s = s.replace("&#8226;", "&bull;")
	s = s.replace("&#8230;", "...")
	s = s.replace("&#8364;", "&euro;")
	
	# TODO: http://www.ascii.cl/htmlcodes.htm
	# 	&#8224;
	# 	&#8225;
	# 	&#8240;
	# 	&#8482;
	return s



class BlogLink:
	def __init__(self, url, post):
		self.url = url
		self.posts = []
		self.categories = []
		self.posts.append(post)
	
	
	
	def addPost(self, post):
		self.posts.append(post)
		
		
		
	def size(self):
		return len(self.posts)



class BlogPost:
	def __init__(self, url, title, channelTitle, channelURL, date, htmlBlock):
		self.url = url
		try:
			self.title = ReplaceLatinExtended(title)
		except:
			self.title = title.encode('utf8', 'ignore')
		self.channelTitle = channelTitle
		self.channelURL = channelURL
		self.date = date
		try:
			self.htmlBlock = ReplaceLatinExtended(htmlBlock)
		except:
			self.htmlBlock = htmlBlock.encode('utf8', 'ignore')
			
		self.categories = []
	
	
	

	
	
		
	def GetCategoriesString(self):
		try:
			s = ""
			for c in self.categories:
				s += c + " "
			return s
		except:
			return ""
	
	
	
	def GetCategoriesList(self):
		try:
			return self.categories
		except:
			return []
			
			
			
	def HasCategory(self, catName):
		for c in self.categories:
			if c.lower() == catName.lower(): return True
		return False
	


	
	def hasCategories(self):
		return len(self.GetCategoriesList()) > 0


	
	def addCategory(self, category):
		try:
			self.categories.append(category)
		except:
			self.categories = []
			self.addCategory(category)
			
	def removeAllCategories(self):
		self.categories = []