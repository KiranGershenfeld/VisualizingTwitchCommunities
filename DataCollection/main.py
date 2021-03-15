import CSVWriting
import GetTwitchData


def main():
    # Get the top 100 streamers on Twitch
    streamers = GetTwitchData.get_top_streamers(100)
    # Create a dictionary of {streamer:[viewers]} from those 100 streams
    data = GetTwitchData.get_viewer_map(streamers)
    # Add that dictionary to the master csv
    CSVWriting.update_twitch_data(data)


# Program Execution
if __name__ == '__main__':
    main()
