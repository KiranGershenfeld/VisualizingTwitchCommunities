import asyncio
import json
import sys

import aiohttp

import analysis
import twitch


async def main():
    async with aiohttp.ClientSession() as session:

        # Load our credentials
        cr = json.load(open('../credentials.json'))

        # Get the top 100 streamers on Twitch
        streamers = await twitch.get_top_streamers(session, cr, count=100)

        # Create a dictionary of {streamer:[viewers]} from those 100 streams
        data = await twitch.get_viewer_map(session, streamers)

        # Add that dictionary to the master csv
        analysis.update_twitch_data(data)


# Program Execution
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        analysis.export()
    else:
        asyncio.run(main())
