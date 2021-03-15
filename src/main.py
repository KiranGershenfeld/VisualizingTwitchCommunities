import asyncio
import json
import logging
import sys

import aiohttp

import analysis
import twitch


async def main():
    with open('credentials.json') as f:
        cr = json.load(f)

    async with aiohttp.ClientSession() as session:
        streamers = await twitch.get_top_streamers(session, cr)
        viewer_map = await twitch.get_viewer_map(session, streamers)

    analysis.update_data(viewer_map, 'unique_viewer_data.json')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        # filenames should be arguments but egh oh well
        analysis.generate_gephi_graph("unique_viewer_data.json", "gephi_edges.csv", "gephi_labels.csv")
    else:
        asyncio.run(main())
