from urllib.error import HTTPError
import requests
import math
import sqlalchemy as sql
from sqlalchemy.dialects.postgresql import insert as ps_insert
import os 
from dotenv import load_dotenv

load_dotenv()

NUM_CHANNELS = 500

def lambda_handler(event, context):
    #Get top streamers in the last 30 days
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    steps = math.ceil(NUM_CHANNELS / 100.0)

    channel_list = []
    for step in range(steps):
        start_index = step * 100

        try:
            request = requests.get(f'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/0/3/desc/{start_index}/100', headers=headers)
        except HTTPError as e:
            print(e)
            return

        if(request.status_code == 200):
            data = request.json()['data']
            channels = [{'url_name': channel['url'], 'display_name': channel['displayname'], 'is_current_top_stream': True} for channel in data]
            channel_list.extend(channels)
        else:
            print(request)
            print(f"Response returned with status code: {request.status_code}")

    channel_list = channel_list[0: NUM_CHANNELS] #List of dicts containing info about each top streamer

    #Connect to database
    engine = sql.create_engine(os.environ.get('DB_URL'))
    metadata_obj = sql.MetaData()

    channels_table = sql.Table('channels', metadata_obj, autoload_with=engine)

    #UPDATE STATEMENT SO ALL STREAMERS ARE NOT CURRENT TOP STREAMERS
    update_stmt = (
        sql.update(channels_table).
        where(channels_table.c.is_current_top_stream == True).
        values(is_current_top_stream = False)
    )

    #Upsert statement inserting new channels and updating old channels to be current top streamers
    insert_stmt = ps_insert(channels_table).values(channel_list)
    do_upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=['url_name'],
        set_ = {'is_current_top_stream': True}
    )

    with engine.connect() as conn:
        #Execute update statement
        try:
            conn.execute(update_stmt)
        except Exception as e:
            print(e)

        #Execute upsert statement
        try: 
            conn.execute(do_upsert_stmt)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    lambda_handler(None, None)