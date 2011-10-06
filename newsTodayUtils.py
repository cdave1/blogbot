import re

# Common words that can be ignored.
stopWords = ['a', 'about', 'all', 'also', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'but', 'by', 
'can', "can't", 'cannot', 'did', 'do', 'does', "doesn't", "don't", 'done', 'else', 'even', 'for', 'from', 'get', 'go', 
'got', 'had', 'has', 'have', 'he', 'her', 'here', 'hers', 'him', 'his', 'how', "i", "i'm", 'if', 'in', 'is', 'it', 
"it's", 'its', 'like', 'lot', 'many', 'me', 'much', 'my', 'no', 'not', 'now', 'of', 'off', 'on', 'only', 'or', 'our', 'ours', 'out', 'she', 'so', 
'some', 'than', 'that', "that's", 'the', 'their', 'them', 'then', 'there', 'these', "there's", 'theres', 'they', "they're", 
'this', 'those', 'to', 'too', 'use', 'us', 'was', 'we', 'what', 'when', 'where', 'which', 'will', 'with', 'yet', 'you']

def stripTags(str):
	# matches multiline <script ...</script> tags.
	js = re.compile(r"<\s*script.*?<\s*\/\s*script\s*>", re.M|re.I|re.S) 
	r = re.compile(r"<[^>]+>|\n", re.I)
	ws = re.compile(r"\s+")
	str = js.sub("", str)
	str = r.sub(" ", str)
	return ws.sub(" ", str)