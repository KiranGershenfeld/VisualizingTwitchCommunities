import csv
import boto3
import pickle as pkl
import sys
from datetime import datetime

now = datetime.now()

#Generates a new csv file for the edge list on Gephi
def GenerateGephiData(dict):
    fileString = "Visualization/GephiData/%s" % (now.strftime("%m.%d.%Y.%H.%MEDGELIST.csv"))
    with open(fileString, 'w') as csvfile:
        writer = csv.writer(csvfile)
        #writer.writeheader()
        writer.writerow(["Source", "Target", "Weight"]) #These column headers are used in Gephi automatically
        for key, value in dict.items():
            nodeA = key
            for node, count in value.items():
                nodeB = node
                writer.writerow([nodeA, nodeB, count]) #nodeA is streamer1, nodeB is streamer2, and count is their overlapping viewers

#Generates a new csv file for the node list labels on Gephi
def GenerateGephiLabels(rawDict):
    fileString = "Visualization/GephiData/%s" % (now.strftime("%m.%d.%Y.%H.%MLABELS.csv"))
    print("Generating Labels...")
    sys.stdout.flush()
    with open(fileString, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Label", "Count"]) #These columns are used in Gephi automatically
        for key, value in rawDict.items():
            writer.writerow([key, key, len(value)]) #This data is streamer1, streamer1, and # of unique viewers for streamer1

def load_pkl_obj_s3(file_name, bucket):
    s3 = boto3.resource('s3')
    obj = pkl.loads(s3.Bucket(bucket).Object(file_name).get()['Body'].read())
    return obj

if __name__ == "__main__":
    raw_overlap_dict = load_pkl_obj_s3('September2021Overlaps.pkl', 'twitch-atlas-overlaps')
    print("finished big file")
    overlap_count_dict =  load_pkl_obj_s3('SeptemberTwitchOverlapCounts.pkl', 'twitch-atlas-overlaps')
    GenerateGephiData(overlap_count_dict)
    GenerateGephiLabels(raw_overlap_dict)