import asyncio


# Gets the count top streams currently live on twitch. numberOfStreams max is 100
async def get_top_streamers(session, credentials, count):
    print("Getting a list of top live streams...")

    # Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
    headers = {'Client-ID': credentials['client-id'], 'Authorization': f"Bearer {credentials['access-token']}"}

    # Request top `count` viewed streams on twitch
    async with session.get(f'https://api.twitch.tv/helix/streams?first={count}', headers=headers) as response:
        data = await response.json()
        # return a list of streamers
        return [element['user_login'] for element in data['data']]


# Get the a list of viewers for a given twitch channel from tmi.twitch (Not an API call)
async def get_current_viewers(session, channel):
    print(f"Getting viewers for {channel}...")

    async with session.get(f'http://tmi.twitch.tv/group/user/{channel.lower()}/chatters') as r:
        data = await r.json()
        # List consists of users in chat tagged as viewer or VIP
        viewers = data['chatters']['vips'] + data['chatters']['viewers']
        print(f"Got {len(viewers)} viewers for {channel}...")
        return viewers


# This method looks up the viewers of each streamer and creates a dictionary of {streamer: [viewers]}
async def get_viewer_map(session, streamers):
    print("Creating dictionary of streamers and viewers...")

    data = {}

    async def add_viewers_task(streamer):
        data[streamer] = await get_current_viewers(session, streamer)

    # run every task in parallel and wait for the results
    await asyncio.gather(*map(add_viewers_task, streamers), return_exceptions=True)

    return data
