import GetTwitchData
import CSVWriting


def main():
    j = GetTwitchData.GetTopStreams() #Get the top 100 streams on Twitch
    d = GetTwitchData.GetDictOfStreamersAndViewers(j) #Create a dictionary of {streamer:[viewers]} from those 100 streams
    CSVWriting.UpdateTwitchData(d) #Add that dictionary to the master csv




#Program Execution
if __name__ == '__main__':
    main()
