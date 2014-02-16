import nltk,os,csv
import pickle
neg=[]
pos=[]
neu=[]

os.chdir("C:\Python27\SMMProject2")       
tweets = []
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
output = open('classifier.pkl', 'wb')
pickle.dump(classifier1, output)
output.close()
output = open('word_features.pkl', 'wb')
pickle.dump(word_features, output)
output.close()
pkl_file = open('classifier.pkl', 'rb')
Stored_classifier = pickle.load(pkl_file)
pkl_file = open('word_features.pkl', 'rb')
word_features = pickle.load(pkl_file)
Test_tweet = 'I love cars'
print Stored_classifier.classify(extract_features(Test_tweet.split()))
