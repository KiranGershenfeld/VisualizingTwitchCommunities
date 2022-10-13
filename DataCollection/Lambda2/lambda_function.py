import datetime
import json
import aiohttp
import asyncio
import sqlalchemy as sql
import os
from dotenv import load_dotenv

load_dotenv()

#Asyncio optimization makes the viewer requests almost instantaneos.

async def get_viewers_for_streamer(streamer, session):
    #Requests to tmi.twitch for the viewers in each stream
    try:
        url = f"http://tmi.twitch.tv/group/user/{streamer.lower()}/chatters"
        response = await session.get(url)
        response = await response.json()
    except json.decoder.JSONDecodeError:
        response = ""
    #viewerlist consists of the streamers vips, mods, and chatters
    viewers = response['chatters']['vips'] + response['chatters']['moderators'] + response['chatters']['viewers'] #List consists of users in chat tagged as viewer or VIP
    broadcaster_in_chat = bool(len(response['chatters']['broadcaster']))
    return ({streamer: {"chatters": viewers, "broadcaster_in_chat": broadcaster_in_chat}})

async def create_streamer_viewer_dict(channel_list):
    dict = {}
    async with aiohttp.ClientSession() as session:
        obj = await asyncio.gather(*[get_viewers_for_streamer(streamer, session) for streamer in channel_list])
    for pair in obj:
        dict.update(pair)
    return dict


def write_data(data):
    insert_data = [{"url_name": streamer, "chatters_json": {'chatters': obj['chatters']}, "broadcaster_in_chat": obj["broadcaster_in_chat"], "log_time": datetime.datetime.utcnow()} for streamer, obj in data.items()]
    
    engine = sql.create_engine(os.environ.get("DB_URL"))
    metadata_obj = sql.MetaData()
    chatters_table = sql.Table('chatters', metadata_obj, autoload_with=engine)

    insert_stmt = sql.insert(chatters_table).values(insert_data)

    with engine.connect() as conn:
        try: 
            conn.execute(insert_stmt)
        except Exception as e:
            print(e)

    return 

def lambda_handler(event, context):
    print(f"LAMBDA 2 TRIGGERED")
    print(f"EVENT: {event}")

    data = asyncio.run(create_streamer_viewer_dict(event))

    write_data(data)

if __name__ == '__main__':
    event = ['109ace','1pvcs','1win_slots','2chamcham2','39daph']
    lambda_handler(event, None)
