#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Christopher Potts"
__copyright__ = "Copyright 2011, Christopher Potts"
__credits__ = []
__license__ = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License: http://creativecommons.org/licenses/by-nc-sa/3.0/"
__version__ = "1.0"
__maintainer__ = "Christopher Potts"
__email__ = "See the author's website"

######################################################################

import pickle,csv
import nltk
import codecs
import re
##import htmlentitydefs
import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from  lengthned import normalize_word
##import Classifier
from  lengthned import normalize_sentence

######################################################################

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

url = r"""http[s]?:[/]*(?:[a-zA-Z]|[0-9]|[$-_@.&#+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"""
hashtags=r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
username=r"""(?:@[\w_]+)"""
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
    username
    ,
    # Twitter hashtags:
    hashtags
    ,
    # Twitter URLs:
    url
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
STOP_WORDS_LISTS = [","]
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
":",",","'","’","!","#","$","%","&","(",")","*","+","-",".","/",":",";","<","=",">","?","@","[","]","^","_","`","{","|","}","~","…","RT"]
tweets=[]
def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
     all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

word_features = get_word_features(get_words_in_tweets(tweets))

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features


class RemoveStopWords:

    def remove(self, cstr):
        keywords_list = cstr.split()
        resarr = [i for i in keywords_list if not i in STOP_WORDS_LISTS ]

        # Return the new keyword string
        return " ".join(resarr)

######################################################################
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

ckey = 'A4KTn8xjWElewDU3WNERgg'
csecret = 'jVDgcHkmu6XRVM9ZisJkU6ctlC9EYQ3FddWn7iefQeo'
atoken = '43272816-AbpXbmYLM74pzUlO5rRF5JC0IFo6Zl5O4AAzdozZg'
asecret = 'MUDWDJpDRTOJRpmFN86ouFBEZgK4bHB8xfRSJGGZrvSMi'
tweets = []
remove = RemoveStopWords()
pkl_file = open('classifier.pkl', 'rb')
Stored_classifier = pickle.load(pkl_file)
pkl_file = open('word_features.pkl', 'rb')
word_features= pickle.load(pkl_file)
print "Classifier loaded"
class listener(StreamListener):
    
    def on_data(self, data):
        
        tweets = json.loads(data)
        s = tweets['text']
        language = tweets['lang']
        if language == 'en':
            s=s.encode('ascii','ignore')
##          print "======================================================================"
            print "original Tweet           : " + s
            s= re.sub( '\s+', ' ', s).strip()
            s= normalize_sentence(s)
##            print "normalized Tweet         : " + s
            s = remove.remove(s)
##            print "stop words removed Tweet : " + s
            
            s = re.sub(url,'',s)
#            s = re.sub(hashtags,'',s)
            s = re.sub(username,'',s)
##            print "url  hashtags usernames removed Tweet : " + s
            
            tokenized = tok.tokenize(s)
##            print "Tokens in Tweet : "
##            print "\n".join(tokenized)    
            s=''
            for token in tokenized:
                token = remove.remove(token)
                s=s+token+' '
            s= re.sub( '\s+', ' ', s).strip()
##            f.write(s+'\n');
            s = remove.remove(s)
##            print "Final Tweet : " + s
##            if 'retweeted_status' in tweets:
##                retweet_count = tweets['retweeted_status']['retweet_count']   
##            else:
##                retweet_count=0
            sentiment = Stored_classifier.classify(extract_features(s.split()))
            print "normalised Tweet           : " + s
            print sentiment
            writer.writerow((s,sentiment))
            return True
    def on_error(self, status):
        print status
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
f = codecs.open('live_classified_tweets.csv','w','utf-8')
writer = csv.writer(f)
twitterStream.filter(locations=[-117.08,32.54,-68.54,47.08])
f.close()
