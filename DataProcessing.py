import csv
import sys
import pandas as pd
import GetTwitchData



def ShiftColumnsUp(df):
    return df.apply(lambda x: pd.Series(x.dropna().values))

def GetLengthOfDictEntries(dict):
    newDict = {}
    for element in dict:
        newDict[element] = len(dict[element])
    return newDict

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

def CombineDictionaries(dict1, dict2):
    dict3 = {}

    print("Creating list for keys in both dictionaries...")
    sys.stdout.flush()
    print("There are " + str(len(set(dict1) & set(dict2))) + " keys shared")
    for key in set(dict1) & set(dict2):
        print("finding viewer union for " + key + "...")
        sys.stdout.flush()
        print("extending list")
        sys.stdout.flush()
        list1 = dict1[key]
        list2 = dict2[key]
        list1.extend(list2)
        sys.stdout.flush()
        dict3[key] = list(set(list1))

    print("Adding dict1 only values...")
    sys.stdout.flush()
    for key in set(dict1) - set(dict2):
        dict3[key] = dict1[key]

    print("Adding dict2 only values...")
    sys.stdout.flush()
    for key in set(dict2) - set(dict1):
        dict3[key] = dict2[key]

    return dict3

def UpdateTwitchData(dict1):
    #Get dict of form {streamer: viewers}
    print("Reading Dictionary from CSV...")
    sys.stdout.flush()
    readDF = pd.read_csv('C:/CodeStuff/VisualizingTwitchCommunities/TwitchData.csv')
    dict2 = readDF.to_dict('list')
    dict2 = RemoveNans(dict2)
    #if streamer matches, write union of lists to new dict with that streamer.
    print("Combining Dictionaries...")
    sys.stdout.flush()
    dict3 = CombineDictionaries(dict1, dict2)

    #Make dict into suitable dat aframe
    print("Processing dictionary to be written...")
    sys.stdout.flush()
    dataFrame = pd.DataFrame.from_dict(dict([ (k,pd.Series(v)) for k,v in dict3.items() ])) #The only reason this line is complicated is because pd wants the lists to all be the same length

    #Shift dataframe columns up
    print("Shifting dictionary columns up...")
    dataFrame = ShiftColumnsUp(dataFrame)

    #Write dataframe to csv
    print("Writing dictionary to CSV...")
    dataFrame.to_csv('C:/CodeStuff/VisualizingTwitchCommunities/TwitchData.csv', index = False)

j = GetTwitchData.GetTopStreams()
d = GetTwitchData.GetDictOfStreamersAndViewers(j)
#l = GetLengthOfDictEntries(d)
#ViewerNumbersToCSV(l)
UpdateTwitchData(d)


def testing():
    readDF = pd.read_csv('C:/CodeStuff/VisualizingTwitchCommunities/TwitchData.csv')
    dict = readDF.to_dict('list')
    for key, value in dict.items():
        list = [x for x in value if str(x) != 'nan']
        if(len(list) != len(set(list))):
            print("repeated values found")
            break
    print("No repeated values")

#testing()
