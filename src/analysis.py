import csv
from pandas import isna
import pandas as pd


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
        new_dict[key] = [x for x in value if not isna(x)]
        count += 1

    return new_dict


# Moves each column of dataframe up so that all NaN values sit at the bottom of the dataframe
def shift_columns_up(df):
    return df.apply(lambda x: pd.Series(x.dropna().values))


# Combines two dictionaries
# matching keys will have their value lists appended without duplicate values
# Comparisons to find duplicate values are done using sets for efficiency
def combine_dicts(dict1, dict2):
    dict3 = {}

    print("Creating list for keys in both dictionaries...")

    set1 = set(dict1)
    set2 = set(dict2)
    shared = set1.intersection(set2)

    print(f"There are {len(shared)} keys shared")

    # For each key in both dictionaries
    for key in shared:
        print(f"finding viewer union for {key}...")
        dict3[key] = list(set(dict1[key]).union(set(dict2[key])))

    print("Adding dict1 only values...")
    for key in set1 - set2:
        dict3[key] = dict1[key]

    print("Adding dict2 only values...")
    for key in set2 - set1:
        dict3[key] = dict2[key]

    return dict3


# This is the main function to update the large csv with all the data in it.
# It takes in the dictionary of {streamer:[viewers]} that was just queried from Twitch,
# combines with the existing database, and writes to a csv
def update_twitch_data(dict1):
    # Read the csv into a dictionary and remove NaN values from it
    print("Reading Dictionary from CSV...")
    try:
        read_df = pd.read_csv('/TwitchData.csv')
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
    df.to_csv('../DataCollection/TwitchData.csv', index=False)


# This function reads out a csv into a dictionary without NaN valus
def read_data(csv_file):
    print("Reading csv to dataframe...")
    df = pd.read_csv(csv_file)
    data = df.to_dict('list')
    data = remove_nans(data)
    return data


# This is the main analysis function for the data.
# It creates a dictionary of the form {streamer1: {streamer2: overlap, streamer3: overlap}}
# This allows us to have an integer of overlapping viewers for each streamer with every other streamer
def compute_streamer_overlaps(data, threshold=300):
    overlap = {}
    count = 1

    # Save which streamers have been processed to avoid repeating
    completed_streamers = set()

    # Make viewer list a set to dramatically decrease comparison time
    for key in data:
        data[key] = set(data[key])

    for key in data:
        temp_list = {}

        total_length = len(data.keys())

        # Print progress so I can keep track
        print(f"{count}/{total_length}")

        # Loop through every key again for each key in the dictionary
        for comparisonKey in data:
            # If its not a self comparison and the comparison hasn't already been completed
            if comparisonKey != key and comparisonKey not in completed_streamers:
                # Find the overlap size of the two streamers using set intersection
                overlap_size = len(data[key] & data[comparisonKey])
                # If the size is over 300 add {comparisonStreamer: overlap} to the dictionary
                if overlap_size > threshold:
                    temp_list[comparisonKey] = overlap_size

        # Add this comparison dictionary to the larger dictionary for that streamer
        overlap[key] = temp_list

        # Add the streamer to completed as no comparisons using this streamer need to be done anymore
        completed_streamers.add(key)

        count += 1

    return overlap


# Generates a new csv file for the edge list on Gephi
def generate_gephi_data(data):
    with open("../5DayData.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)

        # These column headers are used in Gephi automatically
        writer.writerow(["Source", "Target", "Weight"])

        for key, value in data.items():
            node_a = key
            for node, count in value.items():
                node_b = node
                print(f"{node_a} {node_b}")
                # node_a is streamer1, node_b is streamer2, and count is their overlapping viewers
                writer.writerow([node_a, node_b, count])


# Generates a new csv file for the node list labels on Gephi
def generate_gephi_labels(raw_dict):
    print("Generating Labels...")
    with open("../5DayLabels.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        # These columns are used in Gephi automatically
        writer.writerow(["ID", "Label", "Count"])
        for key, value in raw_dict.items():
            # This data is streamer1, streamer1, and # of unique viewers for streamer1
            writer.writerow([key, key, len(value)])


def export():
    # Read the data from csv
    raw_dict = read_data("/TwitchData.csv")
    # Process data creating dictionary of {streamer1: {streamer2: overlap, streamer3: overlap}}
    data = compute_streamer_overlaps(raw_dict)
    # Generate Gephi data files with the dictionaries
    generate_gephi_data(data)
    generate_gephi_labels(raw_dict)
