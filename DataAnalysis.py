import sys
import csv
import pandas as pd

#Helper functions to read csv into a processed dictionary
def RemoveNans(dict):
    length = len(dict.items())
    newDict = {}
    print("removing nan values from " + str(length) + " entries")
    count = 0
    for key, value in dict.items():
        print(str(count) + "/" + str(length))
        sys.stdout.flush()
        newDict[key] = [x for x in value if str(x) != 'nan']
        count+= 1
    return newDict
def ReadOutToDict(csvFile):
    print("Reading csv to dataframe...")
    sys.stdout.flush()
    df = pd.read_csv(csvFile)
    dict = df.to_dict('list')
    dict = RemoveNans(dict)
    return dict


def CreateOverlapDict(dict):
    #Lets build a sample dictionary that might be useful
    viewerOverlapDict = {}
    count = 1
    completedStreamers = []
    for key in dict:
        dict[key] = set(dict[key])
    for key in dict:
        tempList = {}
        totalLength = len(dict.keys())
        print(str(count) + "/" + str(totalLength))
        for comparisonKey in dict:
            if(comparisonKey != key and comparisonKey not in completedStreamers):
                overlapSize = len(dict[key] & dict[comparisonKey])
                if(overlapSize > 300 ):
                    tempList[comparisonKey] = overlapSize
        viewerOverlapDict[key] = tempList
        completedStreamers.append(key)
        count+=1
    return viewerOverlapDict

rawDict = ReadOutToDict("C:/CodeStuff/VisualizingTwitchCommunities/TwitchData.csv")
dict = CreateOverlapDict(rawDict)

def GenerateGephiData(dict):
    with open("C:/CodeStuff/VisualizingTwitchCommunities/GephiDataRepository/5DayData.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        #writer.writeheader()
        writer.writerow(["Source", "Target", "Weight"])
        for key, value in dict.items():
            nodeA = key
            for node, count in value.items():
                nodeB = node
                print(nodeA + " " + nodeB)
                writer.writerow([nodeA, nodeB, count])

def GenerateGephiLabels(rawDict):
    print("Generating Labels...")
    sys.stdout.flush()
    with open("C:/CodeStuff/VisualizingTwitchCommunities/GephiDataRepository/5DayLabels.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Label", "Count"])
        for key, value in rawDict.items():
            writer.writerow([key, key, len(value)])

GenerateGephiData(dict)
GenerateGephiLabels(rawDict)
