from calendar import c
from math import comb
import os
from dotenv import load_dotenv
import sqlalchemy as sql
import itertools
import json
from datetime import datetime

load_dotenv()
start_time = '2022-10-09 00:00:00.000'
end_time = '2022-10-12 00:00:00.000'

def get_top_channel_combinations(engine):
    channels_table = sql.Table('channels', metadata_obj, autoload_with=engine)

    stmt = sql.select(channels_table.c.url_name).where(channels_table.c.is_current_top_stream == True)

    with engine.connect() as conn:
        res = conn.execute(stmt).fetchall()
        channels = [r for r, in res] #Flatten tuple response into a list

    combinations = {}
    for i, channel in enumerate(channels):
        combinations[channel] = channels[i+1:]

    return combinations

def condense_chatters(res):
    channel_chatters = set()
    for entry in res:
        chatters = entry['chatters']
        channel_chatters |= set(chatters)

    return channel_chatters

def get_chatters(conn, chatters_table, channel, start_time, end_time):
    print(f"{channel} not found in cache, getting chatters")
    stmt = sql.select(chatters_table.c.chatters_json).where(
                    chatters_table.c.url_name == channel, 
                    chatters_table.c.log_time >= start_time, 
                    chatters_table.c.log_time <= end_time
                )

    res = conn.execute(stmt).fetchall()
    res = [r for r, in res]

    return condense_chatters(res)

def calc_overlaps(channel_combinations, engine, name_map):
    chatters_table = sql.Table('chatters', metadata_obj, autoload_with=engine)
    cache = {}
    data = []
    counter = 0
    combination_count = sum([len(combinations) for c1, combinations in channel_combinations.items()])
    for c1, combinations in channel_combinations.items():
        with engine.connect() as conn:
            if c1 not in cache:
                cache[c1] = get_chatters(conn, chatters_table, c1, start_time, end_time)

            print(f"COMPLETION PERCENTAGE: {counter / combination_count}")
            for c2 in combinations:
                counter += 1
                    
                if c2 not in cache:
                    cache[c2] = get_chatters(conn, chatters_table, c2, start_time, end_time)
                  
                overlap_count = len(cache[c1] & cache[c2])
                data.append({"source": name_map[c1], "target": name_map[c2], "weight": overlap_count, "log_time": datetime.utcnow()})
        
        del cache[c1]

    return data

if __name__ == "__main__":
    engine = sql.create_engine(os.environ.get("DB_URL"))
    metadata_obj = sql.MetaData()

    combinations = get_top_channel_combinations(engine)

    channels_table = sql.Table('channels', metadata_obj, autoload_with=engine)
    stmt = sql.select(channels_table.c.url_name, channels_table.c.display_name)

    with engine.connect() as conn:
        res = conn.execute(stmt).fetchall()
        name_map = {u: d for u,d in res}

    overlaps = calc_overlaps(combinations, engine, name_map)
    overlaps_table = sql.Table("channel_overlaps", metadata_obj, autoload_with=engine)
    stmt = sql.insert(overlaps_table).values(overlaps)

    with engine.connect() as conn:
        conn.execute(stmt)
    



