import json

import requests


# Gets the count top streams currently live on twitch. numberOfStreams max is 100
def get_top_streams(count):
    print("Getting a list of top live streams...")

    # temporary so it at least just works for me
    cr = json.load(open('../credentials.json'))

    # Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
    headers = {'Client-ID': cr['client-id'], 'Authorization': "Bearer " + cr['access-token']}

    # Request top 100 viewed streams on twitch
    r = requests.get('https://api.twitch.tv/helix/streams?first=' + str(count), headers=headers)
    raw = r.text.encode('utf-8')
    j = json.loads(raw)
    return j


# Get the a list of viewers for a given twitch channel from tmi.twitch (Not an API call)
def get_current_viewers(channel):
    print("Getting viewers for " + channel + "...")
    r = requests.get('http://tmi.twitch.tv/group/user/' + channel.lower() + '/chatters').json()

    # If the query couldnt be completed return None (This occurs with foreign characters)
    if r == "":
        return None

    # List consists of users in chat tagged as viewer or VIP
    current_viewers = r['chatters']['vips'] + r['chatters']['viewers']
    return current_viewers


# This method looks up the viewers of each streamer in j and creates a large dictionary of {streamer: [viewers]}
def get_viewers(j):
    print("Creating dictionary of streamers and viewers...")
    data = {}
    streamers = [element['user_login'] for element in j['data']]  # Get just the list of streamers
    for streamer in streamers:
        viewers = get_current_viewers(streamer.lower())  # Get viewers for a particular streamer
        if viewers is not None:
            data[streamer] = viewers  # Add streamer to dictionary with list of viewers as value
    return data
