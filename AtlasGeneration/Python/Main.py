from CalculateOverlaps import OverlapsManager
import sqlalchemy as sql
from sqlalchemy.sql.expression import func
import os
from dotenv import load_dotenv
import datetime
from py4j.java_gateway import JavaGateway
import logging
logging.basicConfig(filename='.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)


RECALC_OVERLAPS = False
POST_IMAGE_TO_TWITTER = False

def main():

    #Calculate overlaps of all channels marked as top stream
    if RECALC_OVERLAPS:
        start_time = datetime.date.today()
        end_time = start_time - datetime.timedelta(days=30)

        OM = OverlapsManager(start_time=start_time, end_time=end_time, db_url=os.environ.get("DB_URL"))
        OM.run()
        OM.dump_overlaps_to_db()

    #Get newest batch_id
    engine = sql.create_engine(os.environ.get("DB_URL"))
    metadata_obj = sql.MetaData()
    overlaps_table = sql.Table("channel_overlaps", metadata_obj, autoload_with=engine)
    
    stmt = sql.select(func.max(overlaps_table.c.batch_id))

    with engine.connect() as conn:
        res = conn.execute(stmt).fetchall()

    batch_id = res[0][0]
    print(batch_id)

    #Connect to Java program with access to GephiToolkit to create the Twitch Atlas image
    gateway = JavaGateway()  

    try:                      
        gateway.entry_point.Run(batch_id)  
    except Exception as e:
        logger.error(e)

    #Post image to TwitchAtlas Twitter account using Twitter API
    if POST_IMAGE_TO_TWITTER:
        pass

    return


if __name__ == "__main__":
    # exit(0)
    load_dotenv()
    main()