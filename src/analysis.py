import csv
import json


# Combines two dictionaries
# matching keys will have their value lists appended without duplicate values
# Comparisons to find duplicate values are done using sets for efficiency
def combine_dicts(dict1, dict2):
    dict3 = {}

    print("Creating list for keys in both dictionaries...")

    set1 = set(dict1)
    set2 = set(dict2)
    shared = set1 & set2

    print(f"There are {len(shared)} keys shared")

    # For each key in both dictionaries
    for key in shared:
        print(f"finding viewer union for {key}...")
        dict3[key] = list(set(dict1[key]) | set(dict2[key]))

    print("Adding dict1 only values...")
    for key in set1 - set2:
        dict3[key] = dict1[key]

    print("Adding dict2 only values...")
    for key in set2 - set1:
        dict3[key] = dict2[key]

    return dict3


# This is the main analysis function for the data.
# It creates a graph where edge values are number of overlapping viewers
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


# This is the main function to update the large csv with all the data in it.
# It takes in the dictionary of {streamer:[viewers]} that was just queried from Twitch,
# combines with the existing database, and writes to a csv
def update_data(current_user_data, filename):
    try:
        stored_data = read_data(filename)
        print("Combining data...")
        combined_data = combine_dicts(current_user_data, stored_data)
    except:
        print("No existing data found")
        combined_data = current_user_data

    print("Writing data to file...")
    with open(filename, 'w') as f:
        json.dump(combined_data, f)


# This function reads out a csv into a dictionary without NaN valus
def read_data(filename):
    print("Reading data from file...")
    with open(filename) as f:
        return json.load(f)


# Generates a new csv file for the edge list on Gephi
def write_gephi_data(graph, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Source", "Target", "Weight"])
        for node_a, connections in graph.items():
            for node_b, count in connections.items():
                print(f"{node_a} {node_b}")
                writer.writerow([node_a, node_b, count])


# Generates a new csv file for the node list labels on Gephi
def write_gephi_labels(viewer_data, filename):
    print("Generating Labels...")
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Label", "Count"])
        for streamer, viewers in viewer_data.items():
            writer.writerow([streamer, streamer, len(viewers)])


def export(filename, gephi_graph_name, gephi_labels_name):
    # Read the data from csv
    viewer_data = read_data(filename)

    # Process data creating dictionary of {streamer1: {streamer2: overlap, streamer3: overlap}}
    graph = compute_streamer_overlaps(viewer_data)

    # Generate Gephi data files with the dictionaries
    write_gephi_data(graph, gephi_graph_name)
    write_gephi_labels(viewer_data, gephi_labels_name)
