import asyncio
import json
import sys

import aiohttp

import analysis
import twitch


async def main():
    with open('credentials.json') as f:
        cr = json.load(f)

    async with aiohttp.ClientSession() as session:
        streamers = await twitch.get_top_streamers(session, cr, count=100)
        viewer_map = await twitch.get_viewer_map(session, streamers)

    analysis.update_data(viewer_map, 'twitch_data.json')


# Program Execution
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        analysis.export("twitch_data.json", "5DayData.csv", "5DayLabels.csv")
    else:
        asyncio.run(main())
