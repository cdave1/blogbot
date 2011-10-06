#!/usr/bin/env Python
"""HTML Parser and Filter

Copyright 2001-2003 by Andrew Shearer.
Dual-licensed under the Python license and MPSL 1.1.

For current version, see:

http://www.shearersoftware.com/software/developers/htmlfilter/

or contact:

mailto:ashearerw@shearersoftware.com

Version history:
1.1     2003-09-28  Minor comment cleanup of HTMLDecode
1.1b1   2003-05-26  Added hex entity decoding, expanded docstring for HTMLDecode.
1.1a1   2003-01-10  Added encoding support (Unicode)
1.0b7   2002-10-27  Python 1.5 compatibility (removed
                    string instance methods, +=)
1.0b6   2002-07-02  Minor optimizations
1.0b5   2002-05-29  Bug fix for tag.setAttribute(name, None)
1.0b4   2001-10-28  Added HTMLTag.hasAttribute() method;
                    renamed handleScript to handleScriptOrStyle

"""

__author__ = "Andrew Shearer"
__version__ = "1.1"

import re
import string

def HTMLDecode(value):
    """Decoder for strings containing HTML entities. ("&gt;" becomes ">", etc.)
    
    Parses numeric entities in hex and decimal, as well as all entities listed in
    Python's standard htmlentitydefs module.
    
    On a Unicode-capable Python, the input and output are assumed to be Unicode strings.
    (This is because Python complains when concatenating Unicode strings with
    non-Unicode strings containing characters outside 7-bit ASCII. Numeric entities
    are converted to Unicode characters, so the combination of those and 8-bit
    input strings would result in an error.)
    
    CHECK: should newlines & whitespace be collapsed? This would reduce the fidelity
    of attribute values--bad for form element preset values, where browsers tend
    to respect whitespace.
    
    """
    entityStart = string.find(value, '&')
    if entityStart != -1:   # only run bulk of code if there are entities present
        preferUnicodeToISO8859 = 1 #(outputEncoding is not 'iso-8859-1')
        prevOffset = 0
        valueParts = []
        import htmlentitydefs
        while entityStart != -1:
        
            valueParts.append(value[prevOffset:entityStart])
            entityEnd = string.find(value, ';', entityStart+1)
            
            if entityEnd == -1:
                entityEnd = entityStart
                entity = '&'
            else:
                entity = value[entityStart:entityEnd+1]
                if len(entity) < 4 or entity[1] != '#':
                    entity = htmlentitydefs.entitydefs.get(entity[1:-1],entity)
                if len(entity) == 1:
                    if preferUnicodeToISO8859 and ord(entity) > 127 and hasattr(entity, 'decode'):
                        entity = entity.decode('iso-8859-1')
                else:
                    if len(entity) >= 4 and entity[1] == '#':
                        if entity[2] in ('X','x'):
                            entityCode = int(entity[3:-1], 16)
                        else:
                            entityCode = int(entity[2:-1])
                        if entityCode > 255:
                            entity = unichr(entityCode)
                        else:
                            entity = chr(entityCode)
                            if preferUnicodeToISO8859 and hasattr(entity, 'decode'):
                                entity = entity.decode('iso-8859-1')
                valueParts.append(entity)
            prevOffset = entityEnd+1
            entityStart = string.find(value, '&', prevOffset)
        valueParts.append(value[prevOffset:])
        value = string.join(valueParts, '')
    return value

def HTMLEncode(value):
    """Encode HTML entities. Output is in Unicode only if this input is in Unicode."""
    from cgi import escape
    value = escape(value, 1)
    return value

class HTMLFilter:
    """Parse an HTML 4 document, for subclasses to pass through or modify.
    
    Subclasses can output an exact replica of the original or modify
    specific elements or attributes.
    
    Normally, a user of this class would create a subclass that did
    some specific filtering, call feedString(originalHTML), then call close().
    
    The subclass would override the handleXXX methods to perform the
    filtering, and override collectHTML() if it wanted to store the generated
    data. Subclasses that only wanted to read the file and not output
    a modified version wouldn't need to override collectHTML().
    
    The handleXXX methods are overridden through subclassing the main
    HTMLFilter class, rather than implementing some kind of HTMLHandler
    interface, so that new handleXXX methods can be added to this base class
    with default implementations that provide backwards compatibility.
    (+++: could split off HTMLHandler class if it were used as a base class.)
    
    Data flow through HTMLFilter methods:
    
    feedString(originalHTML)
        -> multiple calls to handle[Text|Tag|Script|Comment|...](tag...)
           (subclasses will override to observe or modify the HTML code)
            -> collectHTML(html)
               (subclasses can store the pieces of the final HTML code)
    
    Has partial support of server-side scripting tags (ASP, PHP, JSP)-- 
    they work anywhere an HTML tag would work, but HTML tags with
    embedded code may not be parseable (for instance, if a tag
    contains ASP code inside an attribute value, subclasses can only
    reliably pass the whole tag through unmodified, not read or modify
    the attributes).
    
    Does not support SGML short tag forms (which aren't normally used
    or parsed in HTML anyway, and the HTML RFC warns about this).
    
    If a subclass doesn't override a handleXXX method, the default
    implementations will pass the data to collectHTML() so that the original
    HTML code is preserved. New handleXXX methods added in the future will
    therefore be backwards compatible with older sublcasses, so that file
    filters never lose text.
    """
    
    # regexps from sgmllib
    tagfind = re.compile('[a-zA-Z][-.a-zA-Z0-9]*')
    lineterminatorfind = re.compile('\\n|\\r\\n?')

    class HTMLTag:
        """Represents an HTML tag, allowing attribute retrieval and
        modification. After modification, getHTML() returns
        the complete new tag.
        
        Parsing within the tag is done lazily on the first call to
        getAttribute or setAttribute, so this class is very lightweight
        if all you need is getName or getHTML.
        
        Attributes and tag names are case-insensitive but
        case-preserving. In fact, this class does all it can
        to avoid changing the case and whitespace in the tag.
        When changing an existing attribute value, though,
        this class always encloses the new value in double quotes
        (even if the original value had single or no quotes). 
        
        Attribute storage:
        Each attribute is stored as a tuple of offsets into the main
        self.attrsText string.
        (attributeStart, equalsStart, valueStart, valueLimit, attributeLimit)
        attributeStart points to whitespace, and there is no whitespace
        directly preceding attributeLimit. In other words, whitespace between
        attributes, or between the tag name and first attribute, belongs to
        the beginning of the trailing attribute. This ensures that deleting
        attributes won't leave any extra whitespace before the closing >.
        If the attribute value is quoted, attributeLimit == valueLimit + 1.
        If there is no value, valueStart == valueLimit == attributeLimit.
        If there is no equals sign either (common for boolean attributes),
        equalsStart == attributeLimit.
        
        TODO: is whitespace required between quoted attributes?
        Implement dictionary methods for len(), items(), values(), keys()
        
        """
        
        attrfind = re.compile(
            '[%s]*([a-zA-Z_][-.a-zA-Z_0-9]*)' % string.whitespace
            + ('([%s]*=[%s]*' % (string.whitespace, string.whitespace))
            + r'(\'[^\']*\'|"[^"]*"|[-a-zA-Z0-9./:+*%?!\(\)_#=~]*))?')
        
        def __init__(self, tagName, tagAttrs = ''): # example: tagName='input', tagAttrs=' type="text"'
            self.name = tagName
            self.attrsText = tagAttrs
            self._attributeCache = None
        
        def getName(self):
            """Return the name of the tag, for instance, 'BODY' or 'p'."""
            return self.name
        
        def setName(self, name):
            """Change the name of the tag.
            
            Use getHTML() to return the text of the changed tag."""
            self.name = name
        
        def getHTML(self):
            """Reconstruct the complete tag, including any changed attributes."""
            return '<' + self.name + self.attrsText + '>'
        
        def hasAttribute(self, name):
            """Return 1 if the named attribute exists, None if it does not.
            
            An attribute value of the empty string is still treated as
            existent.
            
            """
            textRange = self._readAttributeCache(name)
            if textRange:
                return 1
            else:
                return None
            
        def getAttribute(self, name, htmldecode = 1):
            """Return the value of the indicated tag attribute.
            
            If the attribute doesn't exist, return None.
            
            The value is HTML entity-decoded by default, which is recommended
            if the value will be processed before being put back into another
            attribute (for example, when modifying a URL, the &amp; entities
            must be decoded first).
            
            For boolean attributes, the "expanded" value is returned:
            <input type="checkbox" checked> returns 'checked' as the
            value of the 'checked' attribute.
            """
            textRange = self._readAttributeCache(name)
            if textRange:
                (attributeStart, equalsStart, valueStart,
                    valueLimit, attributeLimit) = textRange
                if equalsStart != attributeLimit:
                    # has equals sign and therefore a value
                    value = self.attrsText[valueStart:valueLimit]
                    # strip leading & trailing whitespace, per RFC,
                    # and run very simple entity decoder
                    if htmldecode: value = string.strip(HTMLDecode(value))
                else:
                    # no equals sign; expand boolean default value shorthand
                    # (per RFC); <input type="checkbox" CHECKED> returns
                    # 'checked' as the value of the 'checked' attr
                    # Note: the case of the original attribute is not preserved,
                    # since this method only knows the case requested
                    value = name
            else:
                # attribute not found, return None
                value = None
            return value
        
        def __getitem__(self, name):
            """Redirect Python's [] operator to call getAttribute().
            
            HTML entities in the value are decoded before being returned.
            
            Example: value = tag['bgcolor']
            
            """
            return self.getAttribute(name)
            # +++ error if not found?
        
        def __setitem__(self, name, value):
            """Redirect assignment through [] to call setAttribute().
            
            The value is HTML entity-encoded before being inserted.
            
            Example: tag['bgcolor'] = '#FFFFFF'
            
            """
            return self.setAttribute(name, value)
        
        def __delitem__(self, name):
            """Redirect deletion to call deleteAttribute().
            
            Example: del tag['bgcolor']
            
            """
            return self.deleteAttribute(name)
        
        def setBooleanAttribute(self, name, bool):
            """Set a boolean attribute to true or false.
            This controls whether the attribute exists, and the value and
            equals sign are always omitted.
            
            Example: <option selected> has a true 'selected' attribute,
            and <option> has a false 'selected' attribute.
            
            (Really, the DTD treats the first case as SGML shorthand
            for <option selected="selected">, but says that browsers
            often require this shorthand form.)
            
            """
            if not bool:
                # setting boolean attr to false means removing it
                self.deleteAttribute(name)
            else:
                # setting boolean attr to true means leaving its name
                # with no equals sign or value
                textRange = self._readAttributeCache(name)
                if textRange:
                    # the attr is already there; make sure it has
                    # no equals sign or value
                    (attributeStart, equalsStart, valueStart,
                        valueLimit, attributeLimit) = textRange
                    if equalsStart != attributeLimit:
                        self._replaceText(equalsStart, attributeLimit, '')
                        valueStart = valueLimit = attributeLimit = equalsStart
                        self._attributeCache[string.lower(name)] = (attributeStart,
                             equalsStart, valueStart, valueLimit, attributeLimit)
                else:
                    # create the attr
                    attributeStart = len(self.attrsText)
                    self.attrsText = self.attrsText + " " + name
                    equalsStart = valueStart = valueLimit \
                        = attributeLimit = len(self.attrsText)
                    self._attributeCache[string.lower(name)] = (attributeStart,
                        equalsStart, valueStart, valueLimit, attributeLimit)
        
        def _replaceText(self, startOffset, endOffset, replacementText):
            """Replace a range of text from attrsText with another.
            If the lengths are different, the offsets of all following
            attributes are adjusted to compensate.
            (Don't touch attributes actually containing the affected
            range; the caller will take care of that).
            
            """
            if endOffset == len(self.attrsText):
                # optimization for changes at end of string, since
                # we won't have to move any attributes
                self.attrsText = (self.attrsText[:startOffset]
                    + replacementText)
            else:
                self.attrsText = (self.attrsText[:startOffset]
                    + replacementText
                    + self.attrsText[endOffset:])
                lengthChange = len(replacementText) - (endOffset - startOffset)
                if lengthChange != 0:
                    for testAttr, testOffset in self._attributeCache.items():
                        if testOffset[0] >= endOffset:
                            (attributeStart, equalsStart, valueStart,
                                valueLimit, attributeLimit) = testOffset
                            self._attributeCache[testAttr] = (
                                attributeStart + lengthChange,
                                equalsStart + lengthChange,
                                valueStart + lengthChange,
                                valueLimit + lengthChange,
                                attributeLimit + lengthChange)
        
        def _readAttributeCache(self, name):
            if self._attributeCache == None: self._readHTMLTagAttrs()
            textRange = self._attributeCache.get(string.lower(name))
            return textRange            
        
        def deleteAttribute(self, name):
            textRange = self._readAttributeCache(name)
            if textRange:
                (attributeStart, equalsStart, valueStart,
                    valueLimit, attributeLimit) = textRange
                del self._attributeCache[string.lower(name)]
                self._replaceText(attributeStart, attributeLimit, '')       
                
        def setAttribute(self, name, value, htmlencode = 1):
            if value is None:   # delete the attr, for None symmetry with get
                self.deleteAttribute(name)
            else:
                textRange = self._readAttributeCache(name)
                if htmlencode:
                    value = HTMLEncode(value)
                if textRange:
                    (attributeStart, equalsStart, valueStart,
                        valueLimit, attributeLimit) = textRange
                    # set up replace text and range & update valueStart
                    if valueLimit + 1 == attributeLimit:
                        # old value already quoted (' or ")
                        replaceStart = valueStart - 1
                        replaceLimit = valueLimit + 1
                        replaceText = '"' + value + '"'
                    elif equalsStart == attributeLimit:
                        # no equals sign
                        replaceStart = equalsStart
                        replaceLimit = attributeLimit
                        replaceText = '="' + value + '"'
                        valueStart = valueStart + 2 # account for equals and quote
                    else:
                        # no quotes
                        replaceStart = valueStart
                        replaceLimit = valueLimit
                        replaceText = '"' + value + '"'
                        valueStart = valueStart + 1 # account for inserted quote
                    valueLimit = valueStart + len(value)
                    attributeLimit = valueLimit + 1 # account for quote
                else:
                    # new attribute; append to end
                    #lastAttribute = self._attributeCache[
                    attributeStart = len(self.attrsText)
                    replaceText = " " + name + '="' + value + '"'
                    equalsStart = attributeStart + 1 + len(name)
                    valueStart = equalsStart + 2
                    valueLimit = valueStart + len(value)
                    attributeLimit = valueLimit + 1
                    replaceStart = replaceLimit = attributeStart
                self._attributeCache[string.lower(name)] = (attributeStart,
                    equalsStart, valueStart, valueLimit, attributeLimit)
                self._replaceText(replaceStart, replaceLimit, replaceText)
                    #((attrBegin, attrEnd), (attrEnd - len(value) - 3, attrEnd), (attrEnd - len(value) - 2, attrEnd - 1)
                
        def _readHTMLTagAttrs(self):    # self.attrsText contains only the attributes portion of the tag
            attrs = {}
            i = 0
            rawtext = self.attrsText
            length = len(rawtext)
            while i < length:
                match = self.attrfind.match(rawtext, i)
                if not match: break
                # !!! this means attrs after ASP tags or other invalid
                # syntax won't be reached
                attrname, rest, attrvalue = match.group(1, 2, 3)
                attributeStart, attributeLimit = match.span(0)
                if not rest:    # no equals sign
                    equalsStart = valueStart = valueLimit = attributeLimit
                elif (attrvalue[:1] == '\'' == attrvalue[-1:] or 
                      attrvalue[:1] == '"' == attrvalue[-1:]):
                    equalsStart = match.start(2)
                    valueStart = match.start(3)+1
                    valueLimit = match.end(3)-1
                else:
                    equalsStart = match.start(2)
                    valueStart, valueLimit = match.span(3)
                attrs[string.lower(attrname)] = (attributeStart,
                    equalsStart, valueStart, valueLimit, attributeLimit)
                i = attributeLimit
            self._attributeCache = attrs
    
    def __init__(self, inputEncoding = 'iso-8859-1'):
        self.inputEncoding = inputEncoding
    
    def collectHTML(self, html):
        """All the filtered bits of HTML are ultimately sent to this method.
        Subclasses are expected to replace this method and store the HTML code.
        
        """
        pass
    
    def handleText(self, text):
        self.collectHTML(text)
    
    def handleTag(self, tag):
        if string.lower(tag.getName()) == 'meta' \
            and string.lower(tag.getAttribute('name') or '') == 'content-type':
            contentType = tag.getAttribute('value') or ''
            if contentType: self.handleContentType(contentType)
        self.collectHTML(tag.getHTML()) # default pass-through implementation
        
    def setInputEncoding(self, encoding):
        self.inputEncoding = encoding
    
    def handleContentType(self, contentType):
        # sent in addition to handleTag(), if a tag triggered the content type.
        import cgi
        mimeType, params = cgi.parse_header(contentType)
        if params.has_key('encoding'):
            self.setInputEncoding(params['encoding'])
    
    def handleScriptOrStyle(self, startTag, content, endTag):
        """Handle a complete script or style element (overridable)."""
        self.handleTag(startTag)
        self.collectHTML(content)
        self.handleTag(endTag)
    
    def handleComment(self, startText, content, endText):
        """Handle an HTML comment (overridable)."""
        self.collectHTML(startText + content + endText)
    
    def handlePI(self, startText, content, endText):
        """Handle an HTML processing instruction (overridable).
        
        Example for <?php content ?>:
        startText -- '<?php'
        content -- ' content '
        endText -- '?>'
        
        """
        self.collectHTML(startText + content + endText)
        
    def tagIsInteresting(self, tagName):
        """Should tag be passed to handleXXX method? (overridable).
        
        Is passed the name of the tag, or the special illegal tag names
        '--' (comment) and '%', '?',  or '!' (ASP tags, PHP tags, or SGML processing instructions).
        Returns a true value if the tag is to be passed to the special
        handleTag/Script/Comment/etc. methods, or
        false if it's to be passed as part of a raw text block to collectHTML.
        
        """
        return 1
    
    def handleUnterminatedScript(self, scriptTagStartIndex, scriptTagEndIndex):
        """Error handler, called when a script tag isn't closed by EOF
        (overridable)"""
        pass
    
    def handleUnterminatedComment(self, commentTagStartIndex):
        """Error handler, called when a comment isn't closed by EOF
        (overridable)"""
        pass
    
    def handleInvalidTag(self, tagStartIndex):
        """Error handler, called when a tag isn't parseable
        (overridable)"""
        pass
    
    def getCurrentLineNumber(self):
        return self.currentLineNumber
    
    if hasattr('','decode'):    # only support encodings if Python does (e.g. Python >= 1.6)
        def decode(self, inputstring):
            return inputstring.decode(self.inputEncoding)
    else:
        def decode(self, inputstring):
            return inputstring
    
    #tagRE = re.compile("<(/?[A-Za-z][-.A-Za-z_0-9]*)([^>]*)>", re.DOTALL)
    tagMatchRE = re.compile("<(/?[A-Za-z][-.A-Za-z_0-9]*)([^>]*)(>).*", re.DOTALL)
    #itemBeginSearchRE = re.compile("<[/A-Za-z%?]")
    itemBeginSearchRE = re.compile("<")
    commentBeginMatchRE = re.compile("(<!--).*", re.DOTALL)
    #commentBeginLength = 4
    commentEndSearchRE = re.compile("--[%s]*>" % string.whitespace)
    #aspTagSearchRE = re.compile("<([%?]).*\\1>", re.DOTALL)
    scriptEndSearchRE = re.compile("<(/script)([^>]*)>", re.IGNORECASE + re.DOTALL) # the RFC says the end-tag doesn't have to contain "script"--it can just be less-than and slash--but browsers tend to require /script, and some scripts rely on this
    styleEndSearchRE = re.compile("<(/style)([^>]*)>", re.IGNORECASE + re.DOTALL)   # the RFC says the end-tag doesn't have to contain "script"--it can just be less-than and slash--but browsers tend to require /script, and some scripts rely on this
    piMatchRE = re.compile("<([%\?])(.*?)(\\1>).*", re.DOTALL)  # "processing instruction", such as <?...?> or <%...%> ASP & PHP tags
    sgmlMatchRE = re.compile("<(!)([^>]+)(>).*", re.DOTALL) 

    def feedString(self, template):
        """Pass input to the HTML parser.
        
        Similar to Python's htmllib/sgmllib feed() method, but it currently
        can't be called repeatedly (because tags and special elements such as
        scripts can't be split across two calls to feedString).  A user
        of this class would create the HTMLFilter, call feedString passing
        in the raw HTML code, then call close().
        """
        pos = 0
        startTextSave = 0
        self.currentLineNumber = 1
    
        # walk the HTML template file, stopping at interesting items
        # (including tags, script elements, and comments). +++ Should interpret entities too.
        while (pos < len(template)):
            # Stage 1. Measure.
            # Find the next item (HTML tag/script/comment/etc.) & divide into 4 parts:
            #   start of tag, start of interior, end of interior, end of tag
            # The "interior" is empty for a regular HTML tag, but exists for scripts and comments.
            # (The script element is special because it can't contain other HTML tags.)
            # Unterminated scripts/comments are passed through as raw tags/text
            #  unless error handlers are overridden by subclasses to report an HTML error instead
            # Subclasses can override:
            #       handleTag(HTMLTag)
            #       handleScriptOrStyle(startTag, scriptContent, endTag)
            #       handleComment(startText, comment, endText)  # startText and endText are the comment delimiters
            #       handleText(text)
            #       collectHTML(html)
            #       tagIsInteresting(tagname)   # if method returns false, the tag will eventually be passed to collectHTML instead of handleTag/Script/Comment
            #   ...and the error handling functions (no-ops by default):
            #       handleUnterminatedScript(scriptTagStartIndex, scriptTagEndIndex)
            #       handleUnterminatedComment(commentTagStartIndex)
            #       handleInvalidTag(tagStartIndex)
            itemMatch = HTMLFilter.itemBeginSearchRE.search(template, pos)
            if not itemMatch: break
            itemBegin = itemMatch.start(0)
            itemLimit = interiorBegin = interiorLimit = itemMatch.end(0)    # ensure we go forward at least one char in case of a bad tag
            tagMatch = self.tagMatchRE.match(template, itemMatch.start(0))
            isPI = isScriptOrStyle = isComment = 0
            self.currentLineNumber = self.currentLineNumber + \
                len(HTMLFilter.lineterminatorfind.findall(template[pos:itemBegin]))
            #print 'Line %d.' % self.currentLineNumber
            if tagMatch:
                tagName, attrtext = tagMatch.group(1, 2)
                itemLimit = interiorBegin = interiorLimit = tagMatch.end(3)
                endContainerRE = None
                if string.lower(tagName) == "script":
                    endContainerRE = HTMLFilter.scriptEndSearchRE
                elif string.lower(tagName) == "style":
                    endContainerRE = HTMLFilter.styleEndSearchRE
                
                if endContainerRE:
                    endTagMatch = endContainerRE.search(template, interiorBegin)
                    if endTagMatch:
                        isScriptOrStyle = 1
                        interiorLimit = endTagMatch.start(0)
                        itemLimit = endTagMatch.end(0)
                        endTagName, endTagAttrText = endTagMatch.group(1, 2)
                        scriptEndTag = self.HTMLTag(endTagName, self.decode(endTagAttrText))
                    else:
                        self.handleUnterminatedScript(itemBegin, interiorBegin)
                        # Handler could throw error. If it does nothing, rest of code will call regular tag handler (for <script>) then raw text handler (for interior)
            else:
                commentBeginMatch = self.commentBeginMatchRE.match(template, itemBegin)
                if commentBeginMatch:
                    endTagMatch = self.commentEndSearchRE.search(template, commentBeginMatch.end(1))
                    # +++ not fully RFC compliant; doesn't check <!-- in comment -- -- in other comment --> for correctness
                    # (though it does the right thing for correct HTML)
                    if endTagMatch:
                        isComment = 1
                        tagName = "--"
                        interiorBegin = commentBeginMatch.end(1)
                        interiorLimit = endTagMatch.start(0)
                        itemLimit = endTagMatch.end(0)
                    else:
                        self.handleUnterminatedComment(itemBegin)
                        # Handler could throw error. If it does nothing, comment item will be sent as raw text
                else:
                    piTagMatch = self.piMatchRE.match(template, itemBegin) or self.sgmlMatchRE.match(template, itemBegin)
                    if piTagMatch:
                        isPI = 1
                        tagName = piTagMatch.group(1)
                        interiorBegin = piTagMatch.start(2)
                        interiorLimit = piTagMatch.start(3)
                        itemLimit = piTagMatch.end(3)
                        #print "PI %s: itembegin %d, intbegin %d, intlimit %d, end %d" % (tagName, itemBegin, interiorBegin, interiorLimit, itemLimit)
                    else:
                        #print "SGML didn't match: " + template[itemBegin:itemBegin:70]
                        self.handleInvalidTag(itemBegin)
                    # Handler could throw error: invalid tag. If it does nothing, item will be sent as raw text

            # Stage 2. Dispatch the item to the appropriate method.
            # --but only if it's a valid tag that we're interested in. Otherwise,
            # it will be treated as raw text on a subsequent pass through the loop.
            if (tagMatch or isComment or isPI) and self.tagIsInteresting(tagName):
                if itemBegin > startTextSave:   # flush accumulated text
                    self.handleText(self.decode(template[startTextSave:itemBegin]))
                
                if tagMatch:
                    tag = self.HTMLTag(tagName, self.decode(attrtext))
                    if isScriptOrStyle:
                        self.handleScriptOrStyle(tag, self.decode(template[interiorBegin:interiorLimit]), scriptEndTag)
                    else:
                        self.handleTag(tag)
                elif isComment:
                    self.handleComment(template[itemBegin:interiorBegin], self.decode(template[interiorBegin:interiorLimit]), template[interiorLimit:itemLimit])
                elif isPI:
                    self.handlePI(template[itemBegin:interiorBegin], self.decode(template[interiorBegin:interiorLimit]), template[interiorLimit:itemLimit])
                # start accumulating text again after the item we just handled
                startTextSave = itemLimit
            
            self.currentLineNumber = self.currentLineNumber + \
                len(HTMLFilter.lineterminatorfind.findall(template[itemBegin:itemLimit]))
            pos = itemLimit     # on next search, pick up after where we left off
                
                        
        # no more interesting items--flush any remaining raw text
        if pos > startTextSave:
            self.handleText(self.decode(template[startTextSave:pos]))
    
    def close(self):
        """HTML input is done. (overridable)
        
        After calling feedString(), call close() so subclasses know there
        will be no more input."""
        pass


def test():
    """HTMLTag test suite."""
    # +++ add HTMLTag.hasAttribute() test
    tag = HTMLFilter.HTMLTag('option')
    print tag.getHTML(), tag.getHTML() == '<option>'
    tag['value'] = '"This & that"'
    print tag.getHTML(), tag.getHTML() == '<option value="&quot;This &amp; that&quot;">'
    print tag['value'], tag['value'] == '"This & that"'
    tag.setBooleanAttribute('selected', 1)
    print tag.getHTML(), tag.getHTML() == '<option value="&quot;This &amp; that&quot;" selected>'
    print tag['selected'], tag['selected'] == 'selected'
    tag.setBooleanAttribute('Selected', 0)
    print tag.getHTML(), tag.getHTML() == '<option value="&quot;This &amp; that&quot;">'
    print tag['selected'], tag['selected'] == None
    tag.setBooleanAttribute('selected', 1)
    print tag.getHTML(), tag.getHTML() == '<option value="&quot;This &amp; that&quot;" selected>'
    del tag['VaLUE']
    print tag.getHTML(), tag.getHTML() == '<option selected>'
    print tag['value'], tag['value'] == None
    print tag['selected'], tag['selected'] == 'selected'
    tag.setName('select')
    print tag.getHTML(), tag.getHTML() == '<select selected>'
    print tag.getName(), tag.getName() == 'select'
    del tag['selected']
    print tag.getHTML(), tag.getHTML() == '<select>'
    #testtag = '<Input  type = radio value =  \'Maybe \' ALT=" test"  >'
    tag = HTMLFilter.HTMLTag('Input','  Type = radio value =  \'Maybe \' cheCked ALT=" test"  ')
    print tag.getHTML(), tag.getHTML() == '<Input  Type = radio value =  \'Maybe \' cheCked ALT=" test"  >'
    print tag.getName(), tag.getName() == 'Input'
    print tag['TYPE'], tag['TYPE'] == 'radio'
    print tag['radio'], tag['radio'] == None
    print tag['Value'], tag['Value'] == 'Maybe'
    print tag['Checked'], tag['Checked'] == 'Checked'
    print tag['alt'], tag['alt'] == 'test'
    tag.setBooleanAttribute('checked', 1)
    print tag.getHTML(), tag.getHTML() == '<Input  Type = radio value =  \'Maybe \' cheCked ALT=" test"  >'
    tag['tyPe'] = 'checkbox'
    print tag.getHTML(), tag.getHTML() == '<Input  Type = "checkbox" value =  \'Maybe \' cheCked ALT=" test"  >'
    print tag['type'], tag['type'] == 'checkbox'
    del tag['type']
    print tag.getHTML(), tag.getHTML() == '<Input value =  \'Maybe \' cheCked ALT=" test"  >'
    tag['valUe'] = ' Not &'
    print tag.getHTML(), tag.getHTML() == '<Input value =  " Not &amp;" cheCked ALT=" test"  >'
    print tag['Value'], tag['Value'] == 'Not &'
    print tag['alt'], tag['alt'] == 'test'
    tag['checked'] = "maybe"
    print tag.getHTML(), tag.getHTML() == '<Input value =  " Not &amp;" cheCked="maybe" ALT=" test"  >'
    print tag['checked'], tag['checked'] == 'maybe'
    print tag['alt'], tag['alt'] == 'test'
    del tag['alt']
    print tag.getHTML(), tag.getHTML() == '<Input value =  " Not &amp;" cheCked="maybe"  >'
    tag['Alt'] = 'back again'
    print tag.getHTML(), tag.getHTML() == '<Input value =  " Not &amp;" cheCked="maybe" Alt="back again"  >'
    print tag['alt'], tag['alt'] == 'back again'
    tag.setBooleanAttribute('checked', 1)
    print tag.getHTML(), tag.getHTML() == '<Input value =  " Not &amp;" cheCked Alt="back again"  >'
    print tag['checked'], tag['checked'] == 'checked'
    print tag['alt'], tag['alt'] == 'back again'
    tag.setBooleanAttribute('checked2', 1)
    print tag.getHTML(), tag.getHTML() == '<Input value =  " Not &amp;" cheCked Alt="back again" checked2  >'
    print tag['checked'], tag['checked'] == 'checked'
    print tag['checked2'], tag['checked2'] == 'checked2'
    print tag['alt'], tag['alt'] == 'back again'
    # +++ what about tag['']? fix.

    print repr(HTMLDecode('&#8221;')), HTMLDecode('&#8221;') == unichr(8221)
    print repr(HTMLDecode('one&#8221;two&#8221;')), HTMLDecode('one&#8221;two&#8221;') == "one" + unichr(8221) + "two" + unichr(8221)
if __name__ == '__main__':
    test()

