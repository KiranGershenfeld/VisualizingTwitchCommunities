import asyncio
import logging

logger = logging.getLogger('twitch')


# Gets the count top streams currently live on twitch
async def get_top_streamers(session, credentials, count=100):
    """
    Gets the `count` top streams currently live on twitch.

    Maximum allowed Twitch value is 100.
    """

    logger.info('Getting top %d live streams from Twitch', count)

    # Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
    headers = {'Client-ID': credentials['client-id'], 'Authorization': f"Bearer {credentials['access-token']}"}

    # Request top `count` viewed streams on twitch
    async with session.get(f'https://api.twitch.tv/helix/streams?first={count}', headers=headers) as response:
        data = await response.json()
        # Return a list of streamers
        return [element['user_login'] for element in data['data']]


async def get_current_viewers(session, channel):
    """
    Get a list of viewers for a given twitch channel from tmi.twitch.tv (not a part of the documented API).
    """

    async with session.get(f'http://tmi.twitch.tv/group/user/{channel.lower()}/chatters') as r:
        data = await r.json()
        viewers = [viewer for group in data['chatters'].values() for viewer in group]

        logger.debug('Got %d viewers for %s', len(viewers), channel)

        return viewers


# This method looks up the viewers of each streamer and creates a dictionary of {streamer: [viewers]}
async def get_viewer_map(session, streamers):
    """
    Asynchronously gets lists of current viewers for each of the streamers in the list.
    """

    logger.info('Gathering a viewer map for %d streamers', len(streamers))

    data = {}

    async def add_viewers_task(streamer):
        data[streamer] = await get_current_viewers(session, streamer)

    # run every task in parallel and wait for the results
    await asyncio.gather(*map(add_viewers_task, streamers), return_exceptions=True)

    logger.info('Finished gathering the viewer map')

    return data
