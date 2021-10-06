import boto3
import pickle as pkl
import csv
import sys
import io
import logging
import watchtower

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="UTF-8")

#Logging initialization
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TwitchAtlasLogging')
logger.addHandler(watchtower.CloudWatchLogHandler())

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
    objects = boto3.client('s3').list_objects_v2(Bucket=bucket)['Contents']
    files = []
    for obj in objects:
        files.append(obj['Key'])
    return files

def create_overlap_dict(dict):
    viewerOverlapDict = {}
    count = 1
    completedStreamers = [] #Save which streamers have been processed to avoid repeating
    for key in dict:
        dict[key] = set(dict[key]) #Make viewer list a set to dramatically decrease comparison time
    for key in dict:
        tempList = {}

        totalLength = len(dict.keys())
        logger.info(str(count) + "/" + str(totalLength)) #Print progress so I can keep track

        for comparisonKey in dict: #Loop through every key again for each key in the dictionary
            if(comparisonKey != key and comparisonKey not in completedStreamers): #If its not a self comparison and the comparison hasn't already been completed
                overlapSize = len(dict[key] & dict[comparisonKey]) #Find the overlap size of the two streamers using set intersection
                if(overlapSize > 500 ):
                    tempList[comparisonKey] = overlapSize #If the size is over 300 add {comparisonStreamer: overlap} to the dictionary
        viewerOverlapDict[key] = tempList #Add this comparison dictionary to the larger dictionary for that streamer
        completedStreamers.append(key) #Add the streamer to completed as no comparisons using this streamer need to be done anymore
        count+=1
    return viewerOverlapDict

if __name__ == '__main__':
    raw_dict = load_pkl_obj_s3('September2021Overlaps.pkl', 'twitch-atlas-overlaps')
    overlap_dict = create_overlap_dict(raw_dict)
    dump_pkl_obj_s3(overlap_dict, 'SeptemberTwitchOverlapCounts.pkl', 'twitch-atlas-overlaps')
