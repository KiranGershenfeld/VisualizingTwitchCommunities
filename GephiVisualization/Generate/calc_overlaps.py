import sqlalchemy as sql
from sqlalchemy.sql.expression import func
from datetime import datetime

class OverlapsManager:
    start_time = None
    end_time = None
    engine = None
    metadata_obj = None
    overlaps = None

    def __init__(self, *, start_time, end_time, db_url):
        self.start_time = start_time
        self.end_time = end_time
        self.engine = sql.create_engine(db_url)
        self.metadata_obj = sql.MetaData()
    
    def run(self):
    
        combinations = self.get_top_channel_combinations()
        
        overlaps = self.calc_overlaps(combinations)
        self.overlaps = overlaps

    def dump_overlaps_to_db(self):
        overlaps = self.overlaps
        overlaps_table = sql.Table("channel_overlaps", self.metadata_obj, autoload_with=self.engine)

        #Get next batch_id
        stmt = sql.select(func.max(overlaps_table.c.batch_id))
        with self.engine.connect() as conn:
            res = conn.execute(stmt).fetchall()

        prev_batch_id = res[0][0]
        print(f"Prev Batch Id: {prev_batch_id}")
        if prev_batch_id != None: #Needs to trigger if = 0
            new_batch_id = int(prev_batch_id) + 1
        else:
            new_batch_id = 0

        for overlap in overlaps:
            overlap["batch_id"] = new_batch_id
        
        chunks = [overlaps[x:x+100] for x in range(0, len(overlaps), 100)]

        with self.engine.connect() as conn:
            index = 1
            for chunk in chunks:
                print(f"INSERT PROGRESS {index}/{len(chunks)}")
                stmt = sql.insert(overlaps_table).values(chunk)            
                conn.execute(stmt)
                index += 1
                
    def get_top_channel_combinations(self):
        channels_table = sql.Table('channels', self.metadata_obj, autoload_with=self.engine)

        stmt = sql.select(channels_table.c.url_name).where(channels_table.c.is_current_top_stream == True)

        with self.engine.connect() as conn:
            res = conn.execute(stmt).fetchall()
            channels = [r for r, in res] #Flatten tuple response into a list

        combinations = {}
        for i, channel in enumerate(channels):
            combinations[channel] = channels[i+1:]

        return combinations

    def condense_chatters(self, res):
        channel_chatters = set()
        for entry in res:
            chatters = entry['chatters']
            channel_chatters |= set(chatters)

        return channel_chatters

    def get_chatters(self, chatters_table, channel):
        print(f"{channel} not found in cache, getting chatters")
        stmt = sql.select(chatters_table.c.chatters_json).where(
                        chatters_table.c.url_name == channel, 
                        chatters_table.c.log_time >= self.start_time, 
                        chatters_table.c.log_time <= self.end_time
                    )
        
        with self.engine.connect() as conn:
            res = conn.execute(stmt).fetchall()

        res = [r for r, in res]

        return self.condense_chatters(res)

    def calc_overlaps(self, channel_combinations):
        chatters_table = sql.Table('chatters', self.metadata_obj, autoload_with=self.engine)
        
        data = []
        counter = 0
        combination_count = sum([len(combinations) for c1, combinations in channel_combinations.items()])
        for c1, combinations in channel_combinations.items():
            cache = {}
            if c1 not in cache:
                cache[c1] = self.get_chatters(chatters_table, c1)

            print(f"COMPLETION PERCENTAGE: {counter / combination_count}")
            for c2 in combinations:
                counter += 1
                    
                if c2 not in cache:
                    cache[c2] = self.get_chatters(chatters_table, c2)
                
                overlap_count = len(cache[c1] & cache[c2])
                data.append({"source": c1, "target": c2, "weight": overlap_count, "log_time": datetime.utcnow()})
        
            # del cache[c1]

        return data

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    start_time = "2022-10-15 00:00:00.000"
    end_time = "2022-11-01 00:00:00.000"

    om = OverlapsManager(start_time=start_time, end_time=end_time, db_url=os.environ.get("DB_URL"))
    om.run()
    om.dump_overlaps_to_db()

