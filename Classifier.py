import nltk,os,csv
import pickle
neg=[]
pos=[]
neu=[]

os.chdir("C:\Python27\SMMProject2")
##lines = open('Wordsentimentlist.txt').read().splitlines()

##for line in lines:
##        line1 = line.split()
##        if line1[1] == 'negative':
##                neg.append(line1)
##        elif line1[1] == 'positive':
##                pos.append(line1)
##        else:
##                neu.append(line1)
##print "file loaded"            

tweets = []
##
##for (words, sentiment) in pos + neg + neu:
##
##    words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
##
##    tweets.append((words_filtered, sentiment))

##pos_tweets = [('This view is love amazing', 'positive'),
##              ('I love great this morning', 'positive'),
####              ('love','positive'),
####              (':)','positive'),
##              ('I am so excited about the concert', 'positive'),
##              ('He is my best friend', 'positive')]
##neg_tweets = [('not love this car :)', 'negative'),
##              ('This view is horrible ', 'negative'),
##              ('feel tired this ', 'negative'),
##              ('I am not looking forward to the concert', 'negative'),
##              ('He is my enemy', 'negative')]
i=1
with open('Final_training_set.txt', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, dialect="excel-tab")
        for (words, sentiment) in spamreader:
                print i
                print  words + sentiment
                i=i+1
                words_filtered = [e.lower() for e in words.split()]
                tweets.append((words_filtered, sentiment))

print "words filtered"

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
print "feature extracted"

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

training_set = nltk.classify.apply_features(extract_features, tweets)
print "got training set"
classifier1 = nltk.NaiveBayesClassifier.train(training_set)
print "classifier built"
tweet = ':)'
output = open('classifier.pkl', 'wb')
pickle.dump(classifier1, output)
output.close()
pkl_file = open('classifier.pkl', 'rb')
Stored_classifier = pickle.load(pkl_file)
print Stored_classifier.classify(extract_features(tweet.split()))
