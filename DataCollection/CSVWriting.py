import pandas as pd
from math import isnan


# Moves each column of dataframe up so that all NaN values sit at the bottom of the dataframe
def shift_columns_up(df):
    return df.apply(lambda x: pd.Series(x.dropna().values))


# Storing the dataframe into a csv forces a bunch of NaN values so each column is equal length.
# This function drastically reduces processing times by getting rid of NaN values in the dictionary
def remove_nans(data):
    length = len(data.items())
    new_dict = {}
    print(f"removing nan values from {length} entries")
    count = 0
    for key, value in data.items():
        # Count printing to keep track of what is happening at run time
        print(f"{count}/{length}")
        # Removes NaN values from list
        new_dict[key] = [x for x in value if not isnan(x)]
        count += 1

    return new_dict


# Combines two dictionaries
# matching keys will have their value lists appended without duplicate values
# Comparisons to find duplicate values are done using sets for efficiency
def combine_dicts(dict1, dict2):
    dict3 = {}

    print("Creating list for keys in both dictionaries...")
    print(f"There are {len(set(dict1) & set(dict2))} keys shared")

    # For each key in both dictionaries
    for key in set(dict1) & set(dict2):
        print(f"finding viewer union for {key}...")
        print("extending list")
        list1 = dict1[key]
        list2 = dict2[key]
        # Add the lists together
        list1.extend(list2)
        # Remove duplicates in the list
        dict3[key] = list(set(list1))

    print("Adding dict1 only values...")
    # Add key value pairs in just dict1
    for key in set(dict1) - set(dict2):
        dict3[key] = dict1[key]

    print("Adding dict2 only values...")
    # Add key value pairs in just dict 2
    for key in set(dict2) - set(dict1):
        dict3[key] = dict2[key]

    return dict3


# This is the main function to update the large csv with all the data in it.
# It takes in the dictionary of {streamer:[viewers]} that was just queried from Twitch,
# combines with the existing database, and writes to a csv
def update_twitch_data(dict1):
    # Read the csv into a dictionary and remove NaN values from it
    print("Reading Dictionary from CSV...")
    try:
        read_df = pd.read_csv('DataCollection/TwitchData.csv')
        dict2 = read_df.to_dict('list')
        dict2 = remove_nans(dict2)

        # Combine new dictionary to the one just read from the csv
        print("Combining Dictionaries...")
        dict3 = combine_dicts(dict1, dict2)
    except:
        dict3 = dict1

    # Make dict into suitable dataframe by adding NaN values so each colunn is of matching length
    print("Processing dictionary to be written...")

    # The only reason this line is complicated is because pd wants the lists to all be the same length
    df = pd.DataFrame.from_dict(dict([(k, pd.Series(v)) for k, v in dict3.items()]))

    # Shift dataframe columns up so all NaN values sit at the bottom
    print("Shifting dictionary columns up...")
    df = shift_columns_up(df)

    # Write dataframe to csv
    print("Writing dictionary to CSV...")
    df.to_csv('DataCollection/TwitchData.csv', index=False)
