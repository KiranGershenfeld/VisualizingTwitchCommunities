import requests
import json
import sys
import io
import Credentials as cr

def GetTopStreams():
    print("Getting a list of top live streams...")
    #Change python encoding to UTF-8 because for some reason it doesnt do that by default
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="UTF-8")

    #Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
    Headers = {'Client-ID': cr.clientID, 'Authorization': "Bearer " + cr.clientSecret}

    #Request top 100 viewed streams on twitch
    r = requests.get('https://api.twitch.tv/helix/streams?first=100', headers=Headers)
    raw = r.text.encode('utf-8')
    j = json.loads(raw)
    return j

def getCurrentViewersForChannel(channel):
    print("Getting viewers for " + channel + "...")
    sys.stdout.flush()
    r = requests.get('http://tmi.twitch.tv/group/user/'+ channel.lower() +'/chatters').json()
    if(r != ""):
        currentViewers = r['chatters']['vips'] + r['chatters']['viewers']
        return currentViewers
    else:
        return None

def GetDictOfStreamersAndViewers(j):
    print("Creating dictionary of streamers and viewers...")
    sys.stdout.flush()
    dict = {}
    streamers = [element['user_name'] for element in j['data']]
    for streamer in streamers:
        #print(streamer.lower())
        viewers = getCurrentViewersForChannel(streamer.lower())
        if (viewers != None):
            dict[streamer] = viewers
    return dict
