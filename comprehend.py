from twitter import *
import boto3
import json
from sys import argv


# Add your credentials below and uncomment.
# Warning: DO NOT CHECK ANY CODE WHICH CONTAINS CREDENTIALS INTO GITHUB
#access_key=
#secret_key=

comprehend = boto3.client(service_name='comprehend', region_name='us-west-2', aws_access_key_id=access_key,
    aws_secret_access_key=secret_key)


# Update the next line with your Twitter developer credentials.
t = Twitter(
    auth=OAuth(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET))


# Dallas Latitude and Longitude
#latitude = 32.7767
#longitude = -96.7970
#max_range = 50

# Los Angeles Latitude and Longitude
latitude = 34.0522
longitude = -118.2437
max_range = 50

searchTerm = "Amazon"
numberOfTweets = 100

# We retrieve the search results from Twitter.
results = t.search.tweets(q=searchTerm, geocode="%f,%f,%dkm" % (latitude, longitude, max_range), count=numberOfTweets, tweet_mode="extended");


averageNegativeSentiment = 0;
count = 0
mostNegativeTweet = ""
mostNegativeTweetConfidence = 0

# In the following loop, we go through each of our results from Twitter and analyze them with Comprehend.
while (count < numberOfTweets):
    #print 'The count is:', count
    text = results['statuses'][count]['full_text']
    print(text)

    json_data = comprehend.detect_sentiment(Text=text, LanguageCode='en');

    print(json_data["Sentiment"]);
    print("Mixed confidence:"+str(json_data["SentimentScore"]["Mixed"])+
          "; Negative confidence:"+str(json_data["SentimentScore"]["Negative"])+
          "; Neutral confidence:"+str(json_data["SentimentScore"]["Neutral"])+
          "; Positive confidence:" + str(json_data["SentimentScore"]["Positive"]))

    json_entities = comprehend.detect_entities(Text=text, LanguageCode='en')

    averageNegativeSentiment += json_data["SentimentScore"]["Negative"]

    if(json_data["SentimentScore"]["Negative"] > mostNegativeTweetConfidence):
        mostNegativeTweet = text
        mostNegativeTweetConfidence = json_data["SentimentScore"]["Negative"]

    print("\nKey entities:")

    for entity in json_entities["Entities"]:
        print(entity["Text"]+" is a "+entity["Type"])

    print("**********************************\n")
    count = count + 1

print("Average negative sentiment is "+str(averageNegativeSentiment/numberOfTweets))
print("The winner of most negative tweet was:\n")
print(mostNegativeTweet)
print("Negative confidence:"+str(mostNegativeTweetConfidence))
