import GetTwitchData
import SavingData
import Credentials as cr
import os

#Replace cr.path with the path to the VisualizingTwitchCommunities folder as a string (ex. 'C:/VisualizingTwitchCommunities')
#os.chdir(cr.path)

def main(data, context):
    json = GetTwitchData.GetTopStreams(100) #Get the top 100 streams on Twitch
    dict = GetTwitchData.GetDictOfStreamersAndViewers(json) #Create a dictionary of {streamer:[viewers]} from those 100 streams
    SavingData.UpdatePickleWithData(dict) #Add that data to 'pickle' (.pkl) which is a file type for saving data in a serialized way

if __name__ == '__main__':
    main('data', 'context')
