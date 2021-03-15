import json

import requests


# Gets the count top streams currently live on twitch. numberOfStreams max is 100
def get_top_streamers(count):
    print("Getting a list of top live streams...")

    # temporary so it at least just works for me
    cr = json.load(open('../credentials.json'))

    # Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
    headers = {'Client-ID': cr['client-id'], 'Authorization': f"Bearer {cr['access-token']}"}

    # Request top `count` viewed streams on twitch
    data = requests.get(f'https://api.twitch.tv/helix/streams?first={count}', headers=headers).json()

    # return a list of streamers
    return [element['user_login'] for element in data['data']]


# Get the a list of viewers for a given twitch channel from tmi.twitch (Not an API call)
def get_current_viewers(channel):
    print(f"Getting viewers for {channel}...")

    try:
        r = requests.get(f'http://tmi.twitch.tv/group/user/{channel.lower()}/chatters').json()
    except:
        # If the query couldnt be completed return None
        return None

    # List consists of users in chat tagged as viewer or VIP
    current_viewers = r['chatters']['vips'] + r['chatters']['viewers']
    return current_viewers


# This method looks up the viewers of each streamer in j and creates a large dictionary of {streamer: [viewers]}
def get_viewer_map(streamers):
    print("Creating dictionary of streamers and viewers...")
    data = {}
    for streamer in streamers:
        if viewers := get_current_viewers(streamer):
            data[streamer] = viewers
    return data
