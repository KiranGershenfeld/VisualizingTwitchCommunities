import boto3
import pickle as pkl
import datetime
import logging
import watchtower

#Logging initialization
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TwitchAtlasLogging')
logger.addHandler(watchtower.CloudWatchLogHandler())

start_date_str = '09-01-2021_00:00'
end_date_str = '10-01-2021_00:00'
start_date = datetime.datetime.utcnow().strptime(start_date_str, '%m-%d-%Y_%H:%M')
end_date = datetime.datetime.utcnow().strptime(end_date_str, '%m-%d-%Y_%H:%M')

#S3 Helper Functions
def load_pkl_obj_s3(file_name, bucket):
    s3 = boto3.resource('s3')
    obj = pkl.loads(s3.Bucket(bucket).Object(file_name).get()['Body'].read())
    return obj

def dump_pkl_obj_s3(obj, file_name, bucket):
    s3 = boto3.resource('s3')
    pickle_obj = pkl.dumps(obj)
    response = s3.Object(bucket, file_name).put(Body=pickle_obj)
    return response['ResponseMetadata']

def see_all_files_s3(bucket):
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(bucket)
    files = []
    for obj in s3_bucket.objects.all():
        files.append(obj.key)
    return files

def combine_dictionaries(dict1, dict2):
    shared_set = dict1.keys() & dict2.keys()
    
    master_dict = {}
    for key in shared_set:
        shared_chatters = dict1[key]
        shared_chatters.extend(dict2[key])
        master_dict[key] = list(set(shared_chatters))
        del dict1[key]
        del dict2[key]

    master_dict.update(dict1)
    master_dict.update(dict2)

    return master_dict

def main():
    utility_files = ['ChannelList.pkl']
    hourly_files_with_duplicates = [file for file in see_all_files_s3('twitch-atlas') if file not in utility_files]
    hourly_files = []
    logger.info("Parsing files")
    for i in range(0,len(hourly_files_with_duplicates), 2):
        date = datetime.datetime.strptime(hourly_files_with_duplicates[i], '%m-%d-%Y_%H:%M')
        if(date > start_date and date < end_date):
            hourly_files.append(hourly_files_with_duplicates[i])

    logger.info("Starting analysis")

    master_dict = {}
    count = 0
    for file in hourly_files:
        hourly_dict = load_pkl_obj_s3(file, 'twitch-atlas')
        master_dict = combine_dictionaries(master_dict, hourly_dict)
        count += 1
        if(count % 10 == 0):
            logger.info(f'{count} / {len(hourly_files)}')

    dump_pkl_obj_s3(master_dict, 'September2021Overlaps.pkl', 'twitch-atlas-overlaps')

if __name__ == '__main__':
    main()