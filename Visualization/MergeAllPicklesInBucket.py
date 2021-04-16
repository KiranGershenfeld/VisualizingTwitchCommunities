#This file is built to merge to pickle dictionaries
import os
import pickle
import sys
from google.cloud import storage

def combine_dictionaries(dict1, dict2):
    set1 = set(dict1)
    set2 = set(dict2)
    shared_set = set1 & set2
    set1 = set1 - shared_set
    set2 = set2 - shared_set
    
    master_dict = {}
    for key in shared_set:
        shared_chatters = dict1[key]
        shared_chatters.extend(dict2[key])
        master_dict[key] = list(set(shared_chatters))
        dict1.pop(key, None)
        dict2.pop(key, None)

    master_dict.update(dict1)
    master_dict.update(dict2)

    return master_dict

def save_pickle(filename, bucketname, data):
    client = storage.Client()
    bucket = client.get_bucket(bucketname)
    blob = bucket.blob(filename)
    pickle_out = pickle.dumps(data)
    blob.upload_from_string(pickle_out)

def process_data_bucket(bucket_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob_list = bucket.list_blobs()
    length = len(list(blob_list))
    count = 1
    dict={}
    for blob in blob_list:
        content = blob.download_as_string()
        loaded_dict = pickle.loads(content)
        print(f"Currently merging master dict with {blob.name}. {count}/{length}")
        dict = combine_dictionaries(dict, loaded_dict)
        count += 1
    save_pickle("4-6-2021-Merged", bucket_name, dict)

if __name__ == "__main__":
    process_data_bucket("visualizingtwitchcommunities.appspot.com")
