#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This code implements a basic, Twitter-aware tokenizer.

A tokenizer is a function that splits a string of text into words. In
Python terms, we map string and unicode objects into lists of unicode
objects.

There is not a single right way to do tokenizing. The best method
depends on the application.  This tokenizer is designed to be flexible
and this easy to adapt to new domains and tasks.  The basic logic is
this:

1. The tuple regex_strings defines a list of regular expression
   strings.

2. The regex_strings strings are put, in order, into a compiled
   regular expression object called word_re.

3. The tokenization is done by word_re.findall(s), where s is the
   user-supplied string, inside the tokenize() method of the class
   Tokenizer.

4. When instantiating Tokenizer objects, there is a single option:
   preserve_case.  By default, it is set to True. If it is set to
   False, then the tokenizer will downcase everything except for
   emoticons.

The __main__ method illustrates by tokenizing a few examples.

I've also included a Tokenizer method tokenize_random_tweet(). If the
twitter library is installed (http://code.google.com/p/python-twitter/)
and Twitter is cooperating, then it should tokenize a random
English-language tweet.
"""

__author__ = "Christopher Potts"
__copyright__ = "Copyright 2011, Christopher Potts"
__credits__ = []
__license__ = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License: http://creativecommons.org/licenses/by-nc-sa/3.0/"
__version__ = "1.0"
__maintainer__ = "Christopher Potts"
__email__ = "See the author's website"

######################################################################

import re
import htmlentitydefs
from  lengthned import normalize_word
from  lengthned import normalize_sentence

######################################################################
# The following strings are components in the regular expression
# that is used for tokenizing. It's important that phone_number
# appears first in the final regex (since it can contain whitespace).
# It also could matter that tags comes after emoticons, due to the
# possibility of having text like
#
#     <:| and some text >:)
#
# Most imporatantly, the final element should always be last, since it
# does a last ditch whitespace-based tokenization of whatever is left.

# This particular element is used in a couple ways, so we define it
# with a name:
emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth      
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

# The components of the tokenizer:
regex_strings = (
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?            
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?    
      \d{3}          # exchange
      [\-\s.]*   
      \d{4}          # base
    )"""
    ,
    # Emoticons:
    emoticon_string
    ,    
    # HTML tags:
     r"""<[^>]+>"""
    ,
    # Twitter username:
    r"""(?:@[\w_]+)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # Twitter URLs:
    r"""http[s]?:[/]*(?:[a-zA-Z]|[0-9]|[$-_@.&#+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"""
    ,
    # Remaining word types:
    r"""
    (?:[a-z][a-z'\-_]+[a-z])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots. 
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
    )

######################################################################
# This is the core tokenizing regex:
    
word_re = re.compile(r"""(%s)""" % "|".join(regex_strings), re.VERBOSE | re.I | re.UNICODE)

# The emoticon string gets its own regex so that we can preserve case for them as needed:
emoticon_re = re.compile(regex_strings[1], re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
html_entity_digit_re = re.compile(r"&#\d+;")
html_entity_alpha_re = re.compile(r"&\w+;")
amp = "&amp;"

######################################################################
STOP_WORDS_LIST = ["a", "about", "above", "after", "again", "against", \
"all", "am", "an", "and", "any", "are", "aren't", "as",\
"at", "be", "because", "been", "before", "being", \
"below", "between", "both", "but", "by", "can't", \
"cannot", "could", "couldn't", "did", "didn't", "do", \
"does", "doesn't", "doing", "don't", "down", "during", \
"each", "few", "for", "from", "further", "had", "hadn't", \
"has", "hasn't", "have", "haven't", "having", "he", \
"he'd", "he'll", "he's", "her", "here", "here's", "hers", \
"herself", "him", "himself", "his", "how", "how's", "i", \
"i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", \
"isn't", "it", "it's", "its", "itself", "let's", "me", \
"more", "most", "mustn't", "my", "myself", "no", "nor",\
"not", "of", "off", "on", "once", "only", "or", "other", \
"ought", "our", "ours", "ourselves", "out", "over", "own", \
"same", "shan't", "she", "she'd", "she'll", "she's", \
"should", "shouldn't", "so", "some", "such", "than", "that", \
"that's", "the", "their", "theirs", "them", "themselves", \
"then", "there", "there's", "these", "they", "they'd", \
"they'll", "they're", "they've", "this", "those", "through", \
"to", "too", "under", "until", "up", "very", "was", "wasn't", \
"we", "we'd", "we'll", "we're", "we've", "were", "weren't", \
"what", "what's", "when", "when's", "where", "where's", \
"which", "while", "who", "who's", "whom", "why", "why's", \
"with", "won't", "would", "wouldn't", "you", "you'd", \
"you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
":",",","'","!","#","$","%","&","(",")","*","+","-",".","/",":",";","<","=",">","?","@","[","]","^","_","`","{","|","}","~"]

class RemoveStopWords:

    def remove(self, cstr):
        keywords_list = cstr.split()
        resarr = [i for i in keywords_list if not i in STOP_WORDS_LIST ]

        # Return the new keyword string
        return " ".join(resarr)
    
class Tokenizer:
    def __init__(self, preserve_case=True):
        self.preserve_case = preserve_case

    def tokenize(self, s):
        """
        Argument: s -- any string or unicode object
        Value: a tokenize list of strings; conatenating this list returns the original string if preserve_case=False
        """        
        # Try to ensure unicode:
        try:
            s = unicode(s)
        except UnicodeDecodeError:
            s = str(s).encode('string_escape')
            s = unicode(s)
        # Fix HTML character entitites:
        s = self.__html2unicode(s)
        # Tokenize:
        words = word_re.findall(s)
        # Possible alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:            
            words = map((lambda x : x if emoticon_re.search(x) else x.lower()), words)
        return words

    def tokenize_random_tweet(self):
        """
        If the twitter library is installed and a twitter connection
        can be established, then tokenize a random tweet.
        """
        try:
            import twitter
        except ImportError:
            print "Apologies. The random tweet functionality requires the Python twitter library: http://code.google.com/p/python-twitter/"
        from random import shuffle
        api = twitter.Api()
        tweets = api.GetPublicTimeline()
        if tweets:
            for tweet in tweets:
                if tweet.user.lang == 'en':            
                    return self.tokenize(tweet.text)
        else:
            raise Exception("Apologies. I couldn't get Twitter to give me a public English-language tweet. Perhaps try again")

    def __html2unicode(self, s):
        """
        Internal metod that seeks to replace all the HTML entities in
        s with their corresponding unicode characters.
        """
        # First the digits:
        ents = set(html_entity_digit_re.findall(s))
        if len(ents) > 0:
            for ent in ents:
                entnum = ent[2:-1]
                try:
                    entnum = int(entnum)
                    s = s.replace(ent, unichr(entnum))	
                except:
                    pass
        # Now the alpha versions:
        ents = set(html_entity_alpha_re.findall(s))
        ents = filter((lambda x : x != amp), ents)
        for ent in ents:
            entname = ent[1:-1]
            try:            
                s = s.replace(ent, unichr(htmlentitydefs.name2codepoint[entname]))
            except:
                pass                    
            s = s.replace(amp, " and ")
        return s

###############################################################################

if __name__ == '__main__':
    tok = Tokenizer(preserve_case=True)
    remove = RemoveStopWords()
    samples = (
        u"RT @duranduran : Still need alllllll,,    Of your help .. http://dbsjcndsncjs  Join!!! us to support Typhoon relief Hearts go out to all",
        u"HTML entities &amp; other Web oddities cannnnn,,,, be an .  &aacute;cute <em class='grumpy'>pain</em> >:("
        
        )

    for s in samples:
        print "======================================================================"
        print "original Tweet           : " + s
        s= re.sub( '\s+', ' ', s).strip()
        s= normalize_sentence(s)
        print "normalized Tweet         : " + s
        s = remove.remove(s)
        print "stop words removed Tweet : " + s
        tokenized = tok.tokenize(s)
        print "Tokens in Tweet : "
        print "\n".join(tokenized)    
        s=''
        for token in tokenized:
            token = remove.remove(token)
            s=s+token+' '
        s= re.sub( '\s+', ' ', s).strip()
        s = remove.remove(s)
        print "Final Tweet : " + s
                
        


        
