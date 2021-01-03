import csv
import sys
import pandas as pd
import os

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
#matching keys will have their value lists appended without duplicate values
#Comparisons to find duplicate values are done using sets for efficiency
def CombineDictionaries(dict1, dict2):
    dict3 = {}

    print("Creating list for keys in both dictionaries...")
    sys.stdout.flush()
    print("There are " + str(len(set(dict1) & set(dict2))) + " keys shared")

    #For each key in both dictionaries
    for key in set(dict1) & set(dict2):
        print("finding viewer union for " + key + "...")
        sys.stdout.flush()
        print("extending list")
        sys.stdout.flush()
        list1 = dict1[key]
        list2 = dict2[key]
        list1.extend(list2) #Add the lists together
        sys.stdout.flush()
        dict3[key] = list(set(list1))  #Remove duplicates in the list

    print("Adding dict1 only values...")
    sys.stdout.flush()
    for key in set(dict1) - set(dict2): #Add key value pairs in just dict1
        dict3[key] = dict1[key]

    print("Adding dict2 only values...")
    sys.stdout.flush()
    for key in set(dict2) - set(dict1): #Add key value pairs in just dict 2
        dict3[key] = dict2[key]

    return dict3

#This is the main function to update the large csv with all the data in it.
#It takes in the dictionary of {streamer:[viewers]} that was just queried from Twitch, combines with the existing database, and writes to a csv
def UpdateTwitchData(dict1):

    #Read the csv into a dictionary and remove NaN values from it
    print("Reading Dictionary from CSV...")
    sys.stdout.flush()
    try:
        readDF = pd.read_csv('DataCollection/TwitchData.csv')
        dict2 = readDF.to_dict('list')
        dict2 = RemoveNans(dict2)

        #Combine new dictionary to the one just read from the csv
        print("Combining Dictionaries...")
        sys.stdout.flush()
        dict3 = CombineDictionaries(dict1, dict2)
    except:
        dict3 = dict1
    #Make dict into suitable dataframe by adding NaN values so each colunn is of matching length
    print("Processing dictionary to be written...")
    sys.stdout.flush()
    dataFrame = pd.DataFrame.from_dict(dict([ (k,pd.Series(v)) for k,v in dict3.items() ])) #The only reason this line is complicated is because pd wants the lists to all be the same length

    #Shift dataframe columns up so all NaN values sit at the bottom
    print("Shifting dictionary columns up...")
    dataFrame = ShiftColumnsUp(dataFrame)

    #Write dataframe to csv
    print("Writing dictionary to CSV...")
    dataFrame.to_csv('DataCollection/TwitchData.csv', index = False)
