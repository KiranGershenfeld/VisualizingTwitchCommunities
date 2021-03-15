import csv
from math import isnan

import pandas as pd


# This function removes NaN values from a dictionary
def remove_nans(data):
    length = len(data.items())
    new_dict = {}
    print("removing nan values from " + str(length) + " entries")
    count = 0
    for key, value in data.items():
        print(str(count) + "/" + str(length))  # Printing count so I can keep track of progress
        new_dict[key] = [x for x in value if not isnan(x)]
        count += 1
    return new_dict


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
def compute_streamer_overlaps(data):
    overlap = {}
    count = 1
    completed_streamers = []  # Save which streamers have been processed to avoid repeating
    for key in data:
        data[key] = set(data[key])  # Make viewer list a set to dramatically decrease comparison time
    for key in data:
        temp_list = {}

        total_length = len(data.keys())
        print(str(count) + "/" + str(total_length))  # Print progress so I can keep track

        # Loop through every key again for each key in the dictionary
        for comparisonKey in data:
            # If its not a self comparison and the comparison hasn't already been completed
            if comparisonKey != key and comparisonKey not in completed_streamers:
                # Find the overlap size of the two streamers using set intersection
                overlap_size = len(data[key] & data[comparisonKey])
                # If the size is over 300 add {comparisonStreamer: overlap} to the dictionary
                if overlap_size > 300:
                    temp_list[comparisonKey] = overlap_size
        overlap[key] = temp_list  # Add this comparison dictionary to the larger dictionary for that streamer
        # Add the streamer to completed as no comparisons using this streamer need to be done anymore
        completed_streamers.append(key)
        count += 1
    return overlap


# Generates a new csv file for the edge list on Gephi
def generate_gephi_data(data):
    with open("C:/CodeStuff/VisualizingTwitchCommunities/GephiDataRepository/5DayData.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writeheader()
        writer.writerow(["Source", "Target", "Weight"])  # These column headers are used in Gephi automatically
        for key, value in data.items():
            node_a = key
            for node, count in value.items():
                node_b = node
                print(node_a + " " + node_b)
                # node_a is streamer1, node_b is streamer2, and count is their overlapping viewers
                writer.writerow([node_a, node_b, count])


# Generates a new csv file for the node list labels on Gephi
def generate_gephi_labels(raw_dict):
    print("Generating Labels...")
    with open("C:/CodeStuff/VisualizingTwitchCommunities/GephiDataRepository/5DayLabels.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Label", "Count"])  # These columns are used in Gephi automatically
        for key, value in raw_dict.items():
            writer.writerow(
                [key, key, len(value)])  # This data is streamer1, streamer1, and # of unique viewers for streamer1


def main():
    # Read the data from csv
    raw_dict = read_data("C:/CodeStuff/VisualizingTwitchCommunities/TwitchData.csv")
    # Process data creating dictionary of {streamer1: {streamer2: overlap, streamer3: overlap}}
    data = compute_streamer_overlaps(raw_dict)
    # Generate Gephi data files with the dictionaries
    generate_gephi_data(data)
    generate_gephi_labels(raw_dict)


if __name__ == '__main__':
    main()
