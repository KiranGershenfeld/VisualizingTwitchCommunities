import requests
import json
import sys
import io
import Credentials as cr

#Any instance of sys.stdout.flush() is just to force python to print at the right times so I can keep track of whats happening

#Header auth values taken from twitchtokengenerator.com
Headers = {'Client-ID': cr.clientID, 'Authorization': "Bearer " + cr.clientSecret}

#Gets the numberOfStreams top streams currently live on twitch. numberOfStreams max is 100
def GetTopStreams(numberOfStreams):
    print("Getting a list of top live streams...")
    #Change python encoding to UTF-8 because for some reason it doesnt do that by default
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="UTF-8")

    #Request top 100 viewed streams on twitch
    r = requests.get('https://api.twitch.tv/helix/streams?first=' + str(numberOfStreams), headers=Headers)
    raw = r.text.encode('utf-8')
    j = json.loads(raw)
    return j

#This method looks up the viewers of each streamer in j and creates a large dictionary of {streamer: [viewers]}
def GetDictOfStreamersAndViewers(j):
    print("Creating dictionary of streamers and viewers...")
    sys.stdout.flush()
    dict = {}
    for element in j['data']: #This iterates through each of the top 100 streams

        streamer = element['user_name'] #This is the streamers display name
        print("getting viewers for " + streamer)
        sys.stdout.flush()

        #Requests to tmi.twitch for the viewers in each stream
        r = requests.get('http://tmi.twitch.tv/group/user/'+ streamer.lower() +'/chatters').json()

        #If the stream was not found (this happens in the case of asian characters in name), make an extra api call to get the accounts login name which can then be queried for the same viewer list
        if(r == ""):
            loginNameRequest = requests.get('https://api.twitch.tv/helix/users?id=' + element['user_id'], headers=Headers).json()
            loginName = loginNameRequest['data'][0]['login']
            r = requests.get('http://tmi.twitch.tv/group/user/'+ loginName.lower() +'/chatters').json()

        #viewerlist consists of the streamers vips, mods, and chatters
        viewers = r['chatters']['vips'] + r['chatters']['moderators'] + r['chatters']['viewers'] #List consists of users in chat tagged as viewer or VIP

        #This is failsafe, should never happen
        if (viewers != None):
            dict[streamer] = viewers #Add streamer to dictionary with list of viewers as value

    return dict #Return dictionary of {streamer: [viewers]}
