import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
ckey = 'A4KTn8xjWElewDU3WNERgg'
csecret = 'jVDgcHkmu6XRVM9ZisJkU6ctlC9EYQ3FddWn7iefQeo'
atoken = '43272816-AbpXbmYLM74pzUlO5rRF5JC0IFo6Zl5O4AAzdozZg'
asecret = 'MUDWDJpDRTOJRpmFN86ouFBEZgK4bHB8xfRSJGGZrvSMi'
tweets = []
class listener(StreamListener):
    def on_data(self, data):
        tweets = json.loads(data)
        print tweets['text'] , "\n"
        return True
    def on_error(self, status):
        print status
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
twitterStream.filter(track=["#Haiyan"])
