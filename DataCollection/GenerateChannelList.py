import csv
import os

os.chdir("C:/code/VisualizingTwitchCommunities")
channel_list = []
for file in os.scandir("SullyGnomeChannelData"):
    with open(file, encoding='utf-8') as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            channel_list.append(row['Channel'])

for index, streamer in enumerate(channel_list):
    if('(' in streamer):
        startIndex = streamer.index('(') + 1
        endIndex = streamer.index(')')
        streamer = streamer[startIndex:endIndex]
        channel_list[index] = streamer


with open('ChannelList.txt', 'w', encoding='utf-8') as writeFile:
    writeFile.writelines("%s\n" % channel for channel in channel_list)
