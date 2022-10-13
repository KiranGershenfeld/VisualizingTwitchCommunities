from json import load
from urllib.error import HTTPError
import math
import sqlalchemy as sql
import os
from dotenv import load_dotenv
import boto3
import json

load_dotenv()

BATCH_SIZE = 100
FUNCTION_NAME = os.environ.get('FUNCTION_ARN')

def lambda_handler(event, context):
    """
    Reads NUM_CHANNELS channels from database, splits channels into batches, and triggers several instances of a 
    separate lambda function to get viewers from each channel
    """
    print(f"LAMBDA 1 TRIGGERED")

    channel_batches = get_channel_batches()

    client = boto3.client(
        'lambda',
    )
    
    #Call lambda with channel_batch
    for batch in channel_batches:
        client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType='Event',
            Payload=json.dumps(batch),
        )


def get_channel_batches():
    engine = sql.create_engine(os.environ.get('DB_URL'))
    metadata_obj = sql.MetaData()

    channels_table = sql.Table('channels', metadata_obj, autoload_with=engine)
    query = sql.select(channels_table.c.url_name).filter(channels_table.c.is_current_top_stream == True)

    with engine.connect() as conn:
        try: 
            result_proxy = conn.execute(query)
            channel_set = result_proxy.fetchall()
        except Exception as e:
            exit(0)

    channels = [tup[0] for tup in channel_set]

    #Batch channels into BATCH_SIZE chunks
    channel_batches = [channels[i:i + BATCH_SIZE] for i in range(0, len(channels), BATCH_SIZE)]

    return channel_batches


if __name__ == '__main__':
    lambda_handler(None, None)
