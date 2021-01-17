import csv
import sys
import os
import pickle
from google.cloud import storage

#Combines two dictionaries
#matching keys will have their value lists merged without duplicate values
#Comparisons to find duplicate values are done using sets for efficiency
def CombineDictionaries(dict1, dict2, repeatsAllowed):
    dict3 = {}
    set1 = set(dict1)
    set2 = set(dict2)
    print("Creating list for keys in both dictionaries...")
    print("There are " + str(len(set1 & set2)) + " keys shared")

    #For each key in both dictionaries
    for key in set1 & set2:
        print("finding viewer union for " + key + "...")
        print("extending list")
        list1 = dict1[key]
        list2 = dict2[key]
        list1.extend(list2) #Add the lists together
        if(repeatsAllowed):
            dict3[key] = list1
        else:
            dict3[key] = list(set(list1))  #Remove duplicates in the list

    print("Adding dict1 only values...")
    for key in set1 - set2: #Add key value pairs in just dict1
        dict3[key] = dict1[key]

    print("Adding dict2 only values...")
    for key in set2 - set1: #Add key value pairs in just dict 2
        dict3[key] = dict2[key]

    return dict3

#Load a pickle file with specified name
def loadPickle(name):

    client = storage.Client()

    bucket = client.get_bucket('visualizingtwitchcommunities.appspot.com')
    blob = bucket.blob(name)
    content = blob.download_as_string()
    return pickle.loads(content)

#Save a pickle file with specified data and name
def savePickle(name, data):
    client = storage.Client()

    bucket = client.get_bucket('visualizingtwitchcommunities.appspot.com')
    blob = bucket.blob(name)
    pickle_out = pickle.dumps(data)
    blob.upload_from_string(pickle_out)


#This method takes in a dictionary of data from twitch, combines it with the currently saved data, and writes that into a file
def UpdatePickleWithData(dict1):
    print("Saving Data...")
    try:
        dict2 = loadPickle('TwitchData.pkl')
        dict = CombineDictionaries(dict1, dict2, True) #Combines the dictionaries so each key appears once, True allows duplicate viewers
        print("Dictionaries Combined")
    except:
        dict = dict1
    
    savePickle('TwitchData.pkl', dict)
