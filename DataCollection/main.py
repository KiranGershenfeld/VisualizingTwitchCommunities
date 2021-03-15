import GetTwitchData
import CSVWriting


def main():
    json = GetTwitchData.GetTopStreams(100) #Get the top 100 streams on Twitch
    dict = GetTwitchData.GetDictOfStreamersAndViewers(json) #Create a dictionary of {streamer:[viewers]} from those 100 streams
    CSVWriting.UpdateTwitchData(dict) #Add that dictionary to the master csv


#Program Execution
if __name__ == '__main__':
    main()
