import sqlalchemy as sql
from sqlalchemy.sql.expression import func
from datetime import datetime
import _pickle as cPickle
import logging
logging.basicConfig(filename='overlaps.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

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
    
    def run(self, gen_chatter_sets = True, calc_chatter_overlaps = True):
        logging.info("Starting Overlaps Run")

        #Get list of channels to calculate overlaps for 
        channels_table = sql.Table('channels', self.metadata_obj, autoload_with=self.engine)
        stmt = sql.select(channels_table.c.url_name).where(channels_table.c.is_current_top_stream == True)
        with self.engine.connect() as conn:
            res = conn.execute(stmt).fetchall()
            channels = [r for r, in res] #Flatten tuple response into a list

        if(gen_chatter_sets):
            #Get chatters from each channel and dump sets into pkl files for overlap calculations
            self.generate_chatter_sets(channels)

        if(calc_chatter_overlaps):
            #Get combinations of channels to calculate overlaps for, prevents duplicate calculations
            combinations = self.get_top_channel_combinations(channels)
            
            #Get number of overlaping chatters for each combinations
            overlaps = self.calc_overlaps(combinations)

            #data to be inserted into Overlaps table
            self.overlaps = overlaps

    def dump_overlaps_to_db(self):
        logging.info("Dumping overlaps to database")
        overlaps = self.overlaps
        overlaps_table = sql.Table("channel_overlaps", self.metadata_obj, autoload_with=self.engine)

        #Get next batch_id
        stmt = sql.select(func.max(overlaps_table.c.batch_id))
        with self.engine.connect() as conn:
            res = conn.execute(stmt).fetchall()

        #Calculate new batch_id
        prev_batch_id = res[0][0]
        if prev_batch_id != None: #Needs to trigger if = 0
            new_batch_id = int(prev_batch_id) + 1
        else:
            new_batch_id = 0

        logging.info(f"New batch id is: {new_batch_id}")
        for overlap in overlaps:
            overlap["batch_id"] = new_batch_id
        
        chunks = [overlaps[x:x+100] for x in range(0, len(overlaps), 100)]

        #Insert data into database in chunks to prevent absurdly long queries that can fail due to high message content
        with self.engine.connect() as conn:
            index = 1
            for chunk in chunks:
                logging.info(f"Insertion chunk progress: {index}/{len(chunks)}")
                stmt = sql.insert(overlaps_table).values(chunk)            
                conn.execute(stmt)
                index += 1

        #Delete all files in tmp directory
        self.delete_dir('./tmp')
    
    def delete_dir(self, path):
        import shutil
        shutil.rmtree(path)
                
    def get_top_channel_combinations(self, channels):
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
        
        data = []
        counter = 0
        combination_count = sum([len(combinations) for c1, combinations in channel_combinations.items()])
        for c1, combinations in channel_combinations.items():
            logging.info(f"Calculating {len(combinations)} Overlaps for Channel {c1}")

            #Load chatters from pkl object
            with open(f'tmp/channel_{c1}_set.pkl', 'rb') as handle:
                c1_set = cPickle.load(handle)

            for c2 in combinations:
                counter += 1
        
                #Load comparison chatters from pkl object
                with open(f'tmp/channel_{c2}_set', 'rb') as handle:
                    c2_set = cPickle.load(handle)
                
                #Calculate overlaps and append to result
                overlap_count = len(c1_set & c2_set)
                data.append({"source": c1, "target": c2, "weight": overlap_count, "log_time": datetime.utcnow()})
        
        return data

    def generate_chatter_sets(self, channels):
        logging.info("Generating chatter sets as pkl objects")
        chatters_table = sql.Table('chatters', self.metadata_obj, autoload_with=self.engine)

        #Get chatters within time window from each selected channel, dumping sets into individual pickle objects
        #This is done to reduce sql queries required while preserving memory usage. File I/O times are long but better than thousands of unnecesary queries from a slow database
        with self.engine.connect() as conn:
            for channel in channels:
                chatter_set = self.get_chatters(chatters_table, channel)
                with open(f'tmp/channel_{channel}_set.pkl', 'wb') as handle:
                    cPickle.dump(chatter_set, handle)
                logging.info(f"Dumped chatter set for {channel}")

        return 
                
    def calc_stats(self, batch_id):
        import networkx as nx
        overlaps_table = sql.Table("channel_overlaps", self.metadata_obj, autoload_with=self.engine)

        #Get next batch_id
        stmt = sql.select(overlaps_table.c.source, overlaps_table.c.target, overlaps_table.c.weight).where((overlaps_table.c.batch_id == batch_id) & (overlaps_table.c.weight >= 1000))
        with self.engine.connect() as conn:
            res = conn.execute(stmt).fetchall()
        
        network_data = {}
        for source, target, weight in res:
            if source in network_data:
                network_data[source][target] = {"weight": weight}
            else:
                network_data[source] = {target: {"weight": weight}}
        
        G = nx.from_dict_of_dicts(network_data)
        ec = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
        ec = sorted([(v, c) for v, c in ec.items()], key=lambda x: x[1], reverse=True)

        bc = nx.betweenness_centrality(G, weight='weight')
        bc = sorted([(v, c) for v, c in bc.items()], key=lambda x: x[1], reverse=True)

        cc = nx.closeness_centrality(G)
        cc = sorted([(v, c) for v, c in cc.items()], key=lambda x: x[1], reverse=True)

        return {
            "eigenvector_centrality": ec,
            "betweeness_centrality": bc,
            "closeness_centrality": cc
        }


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    start_time = "2022-10-10 00:00:00.000"
    end_time = "2022-11-08 00:00:00.000"

    om = OverlapsManager(start_time=start_time, end_time=end_time, db_url=os.environ.get("DB_URL"))
    om.run(gen_chatter_sets = True, calc_chatter_overlaps = True)
    om.dump_overlaps_to_db()

