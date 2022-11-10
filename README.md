# Visualizing Twitch Communities
## Overview
This project aims to map popular channels on Twitch.tv in a way that feels intuitive to both viewers and streamers. This is accomplished by collecting who is watching different streamers at regular intervals and using that data to create a network graph. 

New Twitch Atlas posts every month at https://twitter.com/TwitchAtlasMap!

## Reactions
This project has accumulated millions of impressions across a variety of social media platforms including YouTube, Reddit, and Twitter. A playlist of popular reaction videos is available [here](https://www.youtube.com/playlist?list=PLCgMcJdIpEnADGngmh7u7q9T8geigZkOY)

I have also written an article on Towards Data Science explaining what these graphs are, how to read them, and how they were created. You can read that (for free!) [here](https://towardsdatascience.com/insights-from-visualizing-public-data-on-twitch-a73304a1b3eb).

## Tech Stack
The newest iteration of this project is now approaching 100% automation. This is accomplished with the following architecture
![Twitch Atlas Architecture](TwitchAtlasArchitecture.drawio.png?raw=true "Title")

## Gallery of Old Atlas'
### Map 7 (September 2021)
[![Twtich Communities September](https://i.postimg.cc/CK3jx7b0/Twitch-Atlas-September-PNG.png)](https://postimg.cc/SXGXZWZ1)

### Map 6 (July 2021)
[![Twtich Communities July](https://i.postimg.cc/G3QTkdXJ/Twitch-Map-July-PNG.png)](https://postimg.cc/Z0WqmttC)

### Map 5 (June 2021)
[![Twtich Communities June](https://i.postimg.cc/Gpvh4QBV/Twitch-Atlas-June-PNG.png)](https://postimg.cc/xkTS7L33)

### Map 4 (May 2021)
[![Twtich Communities May](https://i.postimg.cc/nrvbzprR/Twitch-Communities-May-PNG5275x5965.png)](https://postimg.cc/XB7D1Mwd)

### Map 3 (Mid March - Mid April 2021)
[![Twtich Communities MarchApril](https://i.postimg.cc/ydzG4s2B/Twitch-Communities-March-April.png)](https://postimg.cc/mc8j7fb6)

### Map 2 (February 2021):
[![Twtich Communities February](https://i.postimg.cc/gJxS8fXP/T-witch-Communities-February.png)](https://postimg.cc/fthfhqfH)

### Map 1 (December 2020):
[![Twitch-Communities-March](https://i.postimg.cc/RZZmd0kD/Twitch-Communities-High-Res.png)](https://postimg.cc/2VMg8C8Q)

## Visualization Tutorial
I used a program called Gephi which while extremely powerful has many bugs, limitations, and problems. You will encounter these in your time with the program so just beware. You can download Gephi for free from their website [here](https://gephi.org/). You will also want to download the most recent data in this repository which can be done by navigating the file structure above to "Visualization/GephiData." Pick the most recent date and download the edgelist file and the labels file. 

### Importing Data
Once you have the software and data, open a new project in Gephi follow these steps:
1. Navigate to the Data Laboratory section. 
2. Click "Import Spreadsheet" and import the edgelist file. Make sure "import as" is listed as "Edges Table" and click next.
3. Click Finish on the following dialogue and make sure "Weight" is listed as a "Double". No issues should be found on the following dialogue if this is done correctly.
4. On the next screen change "Directed" to "Undirected" and change "New Workspace" to "Append to existing workspace"
5. Click ok.
6. Repeat the steps 2-5 importing the labels file instead of the edgelist. In step 2 you should make sure "import as" is listed as "Nodes Table"
7. Your data is now loaded into Gephi for you to experiment with!

### Detecting Communities
If you want to detect communities like I did follow these steps:
1. Navigate to the Overview screen.
2. On the menu on the righthand side where is says "Filters" click "Statistics". This menu has several algorithsm that you can run and I encourage anyone to research these and learn more about network analysis.
3. Next to "Modularity" click "Run"
4. In the "Resolution" Dialogue you can put in a value that best suits what you are looking for. Like the description says values lower than 1.0 yields smaller communities while values higher than 1.0 yield broader communities. For my first map I used values in the .75-1.0 range, for the second one I used a values are 0.5-0.75, and for the third map I used around 0.25. The reason for this decrease is because I think the smaller communities are generally more interesting and make the graph seem more accurate when looking at individual streamers. This process has a fair amount of randomness built in so you should run it multiple times and see what you find. 
5. In the top left "Appearance" menu click the paint pallete
6. Click "Partition" and choose "Modularity Class" in the dropdown.
7. Click the blue "Pallete" button in the bottom right of the menu and choose a pallete.
8. Click apply to color the nodes according to your detected communities!

### Laying out the nodes
Gephi has a bunch of layout algorithms built in. You can find them in the "Layout" menu in the bottom left under the "Choose a Layout" dropdown. To get the maps to look the way I did involves doing a few of the algorithms in a row, adjusting a ton of the layout algorithm settings, and a fair amount of precision. I also have some filtering of low weight edges in the "Filters" -> "Queries" menu on the right hand side and I manually move some outer clusters and nodes towards the main graph cluster to make it more cohesive. The details of this will remain a trade secret for now but anyone is capable of similar results with a bit of experimentation. 
