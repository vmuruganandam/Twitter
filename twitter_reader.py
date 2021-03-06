__author__ = 'venkat'

from twython import *
from twitter_db_ops import TwitterDbOps
import time
import sys

class TwitterReader:

    def __init__(self, consumerKey, consumerSecret, accessKey, accessSecret):
        self.cK = consumerKey
        self.cS = consumerSecret
        self.aK = accessKey
        self.aS = accessSecret
        try:
            self.twitter = Twython(self.cK, self.cS, self.aK, self.aS)
        except TwythonAuthError:
            print "Authentication failed"
        self.dbops = TwitterDbOps("")

    def getAPI(self, auth):
        return self.twitter

    def lookup_user(self, user):
        try:
            user = self.twitter.lookup_user(screen_name=user)
            return True
        except (TwythonError, TwythonRateLimitError):
            return False

    def get_tweets_from_user(self, user, cnt=20):
        try:
            lowest_id = sys.maxint
            suser = self.twitter.show_user(screen_name=user)
            if(cnt > suser['statuses_count']):
                cnt = suser['statuses_count']
            #print suser['statuses_count']
            #3000 is the rate limit for twitter API - 15 calls in 15 minutes (200 tweets per call)
            if(cnt > 3000):
                cnt = 3000
            tweets_requested = []
            if cnt <= 200:
                timeline = self.twitter.get_user_timeline(screen_name=user, count=cnt)
                for tweet in timeline:
                    tweets_requested.append(tweet)
                    #self.dbops.createTweet(tweet['text'], self.parse_date(tweet['created_at']))
            elif cnt > 200:
                number_of_tweets = 0
                cntleft = cnt
                cntleft-=200
                timeline = self.twitter.get_user_timeline(screen_name=user, count=200)
                for tweet in timeline:
                    if tweet['id'] < lowest_id:
                        number_of_tweets+=1
                        lowest_id = tweet['id']
                        tweets_requested.append(tweet)
                    #self.dbops.createTweet(tweet['text'], self.parse_date(tweet['created_at']))
                lowest_id -= 1
                while(number_of_tweets < cnt):
                    if cntleft>200:
                        cntleft-=200
                        timeline = self.twitter.get_user_timeline(screen_name=user, count=200, max_id=lowest_id)
                    else:
                        timeline = self.twitter.get_user_timeline(screen_name=user, count=cntleft, max_id=lowest_id)
                    for tweet in timeline:
                        if tweet['id'] < lowest_id:
                            number_of_tweets+=1
                            lowest_id = tweet['id']
                            tweets_requested.append(tweet)
                        #self.dbops.createTweet(tweet['text'], self.parse_date(tweet['created_at']))
                    lowest_id -= 1
            else:
                print "something strange happened"
            return tweets_requested
        except TwythonRateLimitError:
            raise TwitterReaderException

    def parse_date(self, date):
        #print date
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y'))
        return ts

class TwitterReaderException:
    pass

consumerKey = 'jf1RuBnCqdQCNmLX0frLg'
consumerSecret = 'ThqOiemmb6u0unxovHEg9r9m4Lf0MaI30nqh3gwedI'
accessKey = '1106939719-KyTHxcGncJp0vgxTjH8P2AmaGQ13B5ert7YZR0t'
accessSecret = 'PqIuAYKTuKFfrg24CAhuwigh5R2udkl2Fls06mTaZLhXZ'

#twitter = TwitterReader(consumerKey, consumerSecret, accessKey, accessSecret)
#lookup_user = twitter.lookup_user("KingJames")
#print lookup_user
#print twitter.get_application_rate_limit_status()#['/statuses/home_timeline']
#tweets = twitter.get_tweets_from_user("KingJames", 5)
#print len(tweets)
#for tweet in tweets:
#    print tweet['entities']['hashtags']
#print len(tweets)
