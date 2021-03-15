import CSVWriting
import GetTwitchData


def main():
    # Get the top 100 streams on Twitch
    json = GetTwitchData.get_top_streams(100)
    # Create a dictionary of {streamer:[viewers]} from those 100 streams
    data = GetTwitchData.get_viewers(json)
    # Add that dictionary to the master csv
    CSVWriting.update_twitch_data(data)


# Program Execution
if __name__ == '__main__':
    main()
