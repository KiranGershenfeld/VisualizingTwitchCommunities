import sys
import csv
import pandas as pd

#This function removes NaN values from a dictionary
def RemoveNans(dict):
    length = len(dict.items())
    newDict = {}
    print("removing nan values from " + str(length) + " entries")
    count = 0
    for key, value in dict.items():
        print(str(count) + "/" + str(length)) #Printing count so I can keep track of progress
        sys.stdout.flush()
        newDict[key] = [x for x in value if str(x) != 'nan']
        count+= 1
    return newDict

#This function reads out a csv into a dictionary without NaN valus
def ReadOutToDict(csvFile):
    print("Reading csv to dataframe...")
    sys.stdout.flush()
    df = pd.read_csv(csvFile)
    dict = df.to_dict('list')
    dict = RemoveNans(dict)
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

rawDict = ReadOutToDict("C:/CodeStuff/VisualizingTwitchCommunities/TwitchData.csv") #Read the data from csv
dict = CreateOverlapDict(rawDict) #Process data creating dictionary of {streamer1: {streamer2: overlap, streamer3: overlap}}

#Generates a new csv file for the edge list on Gephi
def GenerateGephiData(dict):
    with open("C:/CodeStuff/VisualizingTwitchCommunities/GephiDataRepository/5DayData.csv", 'w') as csvfile:
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
    print("Generating Labels...")
    sys.stdout.flush()
    with open("C:/CodeStuff/VisualizingTwitchCommunities/GephiDataRepository/5DayLabels.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Label", "Count"]) #These columns are used in Gephi automatically
        for key, value in rawDict.items():
            writer.writerow([key, key, len(value)]) #This data is streamer1, streamer1, and # of unique viewers for streamer1

#Generate Gephi data files with the dictionaries
GenerateGephiData(dict)
GenerateGephiLabels(rawDict)
