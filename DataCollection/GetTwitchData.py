import requests
import json

#Gets the numberOfStreams top streams currently live on twitch. numberOfStreams max is 100
def GetTopStreams(numberOfStreams):
    print("Getting a list of top live streams...")

    # temporary so it at least just works for me
    cr = json.load(open('../credentials.json'))

    #Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
    Headers = {'Client-ID': cr['client-id'], 'Authorization': "Bearer " + cr['access-token']}

    #Request top 100 viewed streams on twitch
    r = requests.get('https://api.twitch.tv/helix/streams?first=' + str(numberOfStreams), headers=Headers)
    raw = r.text.encode('utf-8')
    j = json.loads(raw)
    return j

#Get the a list of viewers for a given twitch channel from tmi.twitch (Not an API call)
def getCurrentViewersForChannel(channel):
    print("Getting viewers for " + channel + "...")
    r = requests.get('http://tmi.twitch.tv/group/user/'+ channel.lower() +'/chatters').json()
    if(r != ""):
        currentViewers = r['chatters']['vips'] + r['chatters']['viewers'] #List consists of users in chat tagged as viewer or VIP
        return currentViewers
    else:
        return None #If the query couldnt be completed return None (This occurs with foreign characters)

#This method looks up the viewers of each streamer in j and creates a large dictionary of {streamer: [viewers]}
def GetDictOfStreamersAndViewers(j):
    print("Creating dictionary of streamers and viewers...")
    dict = {}
    streamers = [element['user_login'] for element in j['data']] #Get just the list of streamers
    for streamer in streamers:
        #print(streamer.lower())
        viewers = getCurrentViewersForChannel(streamer.lower()) #Get viewers for a particular streamer
        if (viewers != None):
            dict[streamer] = viewers #Add streamer to dictionary with list of viewers as value
    return dict
