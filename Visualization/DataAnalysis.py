import sys
import csv
import pandas as pd
import pickle
import os
import io
from datetime import datetime
from google.cloud import storage

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="UTF-8")

def save_pickle(filename, bucketname, data):
    client = storage.Client()
    bucket = client.get_bucket(bucketname)
    blob = bucket.blob(filename)
    pickle_out = pickle.dumps(data)
    blob.upload_from_string(pickle_out)

def load_pickle(bucket_name, filename):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(filename)
    blob_string = blob.download_as_string()
    dict = pickle.loads(blob_string)
    return dict

def load_local_pickle(filename):
    dict = pickle.load(open(filename, 'rb'))
    return dict


#This is the main analysis function for the data.
#It creates a dictionary of the form {streamer1: {streamer2: overlap, streamer3: overlap}}
#This allows us to have an integer of overlapping viewers for each streamer with every other streamer
def CreateOverlapDict(dict):
    viewerOverlapDict = {}
    count = 1
    completedStreamers = [] #Save which streamers have been processed to avoid repeating
    for key in dict:
        dict[key] = set(dict[key]) #Make viewer list a set to dramatically decrease comparison time
    for key in dict:
        tempList = {}

        totalLength = len(dict.keys())
        print(str(count) + "/" + str(totalLength)) #Print progress so I can keep track

        for comparisonKey in dict: #Loop through every key again for each key in the dictionary
            if(comparisonKey != key and comparisonKey not in completedStreamers): #If its not a self comparison and the comparison hasn't already been completed
                overlapSize = len(dict[key] & dict[comparisonKey]) #Find the overlap size of the two streamers using set intersection
                if(overlapSize > 300 ):
                    tempList[comparisonKey] = overlapSize #If the size is over 300 add {comparisonStreamer: overlap} to the dictionary
        viewerOverlapDict[key] = tempList #Add this comparison dictionary to the larger dictionary for that streamer
        completedStreamers.append(key) #Add the streamer to completed as no comparisons using this streamer need to be done anymore
        count+=1
    return viewerOverlapDict

rawDict = load_pickle("visualizingtwitchcommunities.appspot.com", "4-6-2021-Merged")
dict = CreateOverlapDict(rawDict) #Process data creating dictionary of {streamer1: {streamer2: overlap, streamer3: overlap}}
#save_pickle("4-6-21ViewerOverlapDict", "visualizingtwitchcommunities.appspot.com", dict)
now = datetime.now()

#Generates a new csv file for the edge list on Gephi
def GenerateGephiData(dict):
    fileString = "VisualizingTwitchCommunities/Visualization/GephiData/%s" % (now.strftime("%m.%d.%Y.%H.%M.%SEDGELIST.csv"))
    with open(fileString, 'w') as csvfile:
        writer = csv.writer(csvfile)
        #writer.writeheader()
        writer.writerow(["Source", "Target", "Weight"]) #These column headers are used in Gephi automatically
        for key, value in dict.items():
            nodeA = key
            for node, count in value.items():
                nodeB = node
                print(nodeA + " " + nodeB)
                writer.writerow([nodeA, nodeB, count]) #nodeA is streamer1, nodeB is streamer2, and count is their overlapping viewers

#Generates a new csv file for the node list labels on Gephi
def GenerateGephiLabels(rawDict):
    fileString = "Visualization/GephiData/%s" % (now.strftime("%m.%d.%Y.%H.%M.%SLABELS.csv"))
    print("Generating Labels...")
    sys.stdout.flush()
    with open(fileString, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Label", "Count"]) #These columns are used in Gephi automatically
        for key, value in rawDict.items():
            writer.writerow([key, key, len(value)]) #This data is streamer1, streamer1, and # of unique viewers for streamer1

#Generate Gephi data files with the dictionaries
GenerateGephiData(dict)
GenerateGephiLabels(rawDict)
