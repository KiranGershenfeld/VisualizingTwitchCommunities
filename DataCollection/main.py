import asyncio
import json

import aiohttp

import CSVWriting
import GetTwitchData


async def main():
    async with aiohttp.ClientSession() as session:

        # Load our credentials
        cr = json.load(open('../credentials.json'))

        # Get the top 100 streamers on Twitch
        streamers = await GetTwitchData.get_top_streamers(session, cr, count=100)

        # Create a dictionary of {streamer:[viewers]} from those 100 streams
        data = await GetTwitchData.get_viewer_map(session, streamers)

        # Add that dictionary to the master csv
        CSVWriting.update_twitch_data(data)


# Program Execution
if __name__ == '__main__':
    asyncio.run(main())
