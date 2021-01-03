import requests
import json
import sys
import io
import Credentials as cr

#Any instance of sys.stdout.flush() is just to force python to print at the right times so I can keep track of whats happening

#Gets the numberOfStreams top streams currently live on twitch. numberOfStreams max is 100
def GetTopStreams(numberOfStreams):
    print("Getting a list of top live streams...")
    #Change python encoding to UTF-8 because for some reason it doesnt do that by default
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="UTF-8")

    #Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
    Headers = {'Client-ID': cr.clientID, 'Authorization': "Bearer " + cr.clientSecret}

    #Request top 100 viewed streams on twitch
    r = requests.get('https://api.twitch.tv/helix/streams?first=' + str(numberOfStreams), headers=Headers)
    raw = r.text.encode('utf-8')
    j = json.loads(raw)
    return j

#Get the a list of viewers for a given twitch channel from tmi.twitch (Not an API call)
def getCurrentViewersForChannel(channel):
    print("Getting viewers for " + channel + "...")
    sys.stdout.flush()
    r = requests.get('http://tmi.twitch.tv/group/user/'+ channel.lower() +'/chatters').json()
    if(r != ""):
        currentViewers = r['chatters']['vips'] + r['chatters']['viewers'] #List consists of users in chat tagged as viewer or VIP
        return currentViewers
    else:
        return None #If the query couldnt be completed return None (This occurs with foreign characters)

#This method looks up the viewers of each streamer in j and creates a large dictionary of {streamer: [viewers]}
def GetDictOfStreamersAndViewers(j):
    print("Creating dictionary of streamers and viewers...")
    sys.stdout.flush()
    dict = {}
    streamers = [element['user_name'] for element in j['data']] #Get just the list of streamers
    for streamer in streamers:
        #print(streamer.lower())
        viewers = getCurrentViewersForChannel(streamer.lower()) #Get viewers for a particular streamer
        if (viewers != None):
            dict[streamer] = viewers #Add streamer to dictionary with list of viewers as value
    return dict
