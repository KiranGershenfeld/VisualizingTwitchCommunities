import csv
import sys
import pandas as pd
import os
import pickle

#Moves each column of dataframe up so that all NaN values sit at the bottom of the dataframe
def ShiftColumnsUp(df):
    return df.apply(lambda x: pd.Series(x.dropna().values))

#Storing the dataframe into a csv forces a bunch of NaN values so each column is equal length.
#This function drastically reduces processing times by getting rid of NaN values in the dictionary
def RemoveNans(dict):
    length = len(dict.items())
    newDict = {}
    print("removing nan values from " + str(length) + " entries")
    count = 0
    for key, value in dict.items():
        print(str(count) + "/" + str(length)) #Count printing to keep track of what is happening at run time
        sys.stdout.flush()
        newDict[key] = [x for x in value if str(x) != 'nan'] #Removes NaN values from list
        count+= 1
    return newDict

#Combines two dictionaries
#matching keys will have their value lists merged without duplicate values
#Comparisons to find duplicate values are done using sets for efficiency
def CombineDictionaries(dict1, dict2, repeatsAllowed):
    dict3 = {}
    set1 = set(dict1)
    set2 = set(dict2)
    print("Creating list for keys in both dictionaries...")
    sys.stdout.flush()
    print("There are " + str(len(set1 & set2)) + " keys shared")

    #For each key in both dictionaries
    for key in set1 & set2:
        print("finding viewer union for " + key + "...")
        sys.stdout.flush()
        print("extending list")
        sys.stdout.flush()
        list1 = dict1[key]
        list2 = dict2[key]
        list1.extend(list2) #Add the lists together
        sys.stdout.flush()
        if(repeatsAllowed):
            dict3[key] = list1
        else:
            dict3[key] = list(set(list1))  #Remove duplicates in the list

    print("Adding dict1 only values...")
    sys.stdout.flush()
    for key in set1 - set2: #Add key value pairs in just dict1
        dict3[key] = dict1[key]

    print("Adding dict2 only values...")
    sys.stdout.flush()
    for key in set2 - set1: #Add key value pairs in just dict 2
        dict3[key] = dict2[key]

    return dict3

#Load a pickle file with specified name
def loadPickle(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

#Save a pickle file with specified data and name
def savePickle(name, data):
    with open(name + '.pkl', 'wb') as f:
        return pickle.dump(data, f, 0)

#This method takes in a dictionary of data from twitch, combines it with the currently saved data, and writes that into a file
def UpdatePickleWithData(dict1):
    try:
        dict2 = loadPickle('DataCollection/TwitchData')
        dict = CombineDictionaries(dict1, dict2, True) #Combines the dictionaries so each key appears once, True allows duplicate viewers
    except:
        dict = dict1
    savePickle('DataCollection/TwitchData', dict)
