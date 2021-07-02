# Visualizing Twitch Communities
## Overview
This project aims to map popular channels on Twitch.tv in a way that feels intuitive to both viewers and streamers. This is accomplished by collecting who is watching different streamers at regular intervals, comparing these lists, and turning that information into a network diagram. All code is written in python and the visualization is done using Gephi. 

I wrote an article on Towards Data Science explaining what these graphs are, how to read them, and how they were created. You can read that (for free!) [here](https://towardsdatascience.com/insights-from-visualizing-public-data-on-twitch-a73304a1b3eb).

I am trying to create these maps monthly but they do take a fair amount of work so there may be delays.

I do pay a bit out of pocket for the continous cloud compute usage from Google Cloud Platform so if this project provides you some value and you have the spare change anything I recieve will go directly to hosting costs. https://paypal.me/KiranGershenfeld?locale.x=en_US

## Results
### Map 5 (June 2021) - Most Recent
[![Twtich Communities June](https://i.postimg.cc/Gpvh4QBV/Twitch-Atlas-June-PNG.png)](https://postimg.cc/xkTS7L33)

### Map 4 (May 2021)
[![Twtich Communities May](https://i.postimg.cc/nrvbzprR/Twitch-Communities-May-PNG5275x5965.png)](https://postimg.cc/XB7D1Mwd)

### Map 3 (Mid March - Mid April 2021)
[![Twtich Communities MarchApril](https://i.postimg.cc/ydzG4s2B/Twitch-Communities-March-April.png)](https://postimg.cc/mc8j7fb6)

### Map 2 (February 2021):
[![Twtich Communities February](https://i.postimg.cc/gJxS8fXP/T-witch-Communities-February.png)](https://postimg.cc/fthfhqfH)

### Map 1 (December 2020):
[![Twitch-Communities-March](https://i.postimg.cc/RZZmd0kD/Twitch-Communities-High-Res.png)](https://postimg.cc/2VMg8C8Q)

## Making Your Own Graphs
If you want to run the project from scratch, collect your own data, and graph it please go down to the "Running The Project" section to get the code running. If you want to mess with the graph using the data I have collected than your in luck! It's super easy and requires no coding. 

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

## Running the Project
Disclaimer: I am by no means a python expert and the code I write for this project is done as a hobby.

The first map was done entirely off my personal computer. If you want something similar look at the "Local Running" section below.

All following maps are done with heavy integration with the Google Cloud Platform and their Compute Engine. If you are interesting in a more sustainable and automated approach go to the "Cloud Automation" section below. 

### Local Running
If you want to run this project locally, you can go to the "Legacy-(Local)" branch and get the code from there. That code is not as well maintained as the default branch and misses some of the big opimization improvements but it should work with some adjusting of filepaths and adding your own API credentials. You will probably need experience with python, git, and coding in general in order to get it working properly but none of it is particularly complicated. 

### Cloud Automation
For every map past the first one I have automated a lot of the data collecting using the Google Cloud Compute Engine. The code for this can be found in the default branch called "Cloud Compute." I did a lot of work debugging, experimenting, and learning to get this to work in a way that was sustainable and I cannot write out all that information here. If you are planning to set this up yourself I assume you have the skills to learn to do so. The process I used was to schedule a job using the Google Cloud Scheduler to send a message to a topic once an hour. Make a Google Cloud Function that subrscribes to that topic and calls a script on a Compute Engine virtual machine. This machine needs to be running a script that can recieve the function call. I did this by running the listener script with "nohup listenerscript.py &" which allows the vm to run the script continously even if you exit. 

The tutorial I followed to do this can be found here: https://github.com/GoogleCloudPlatform/reliable-task-scheduling-compute-engine-sample .

I dont have an intuitive understanding of how this all works so apologies if my description is inaccurate. 

## Credit
This is a hobby project done by [Kiran Gershenfeld](https://kirangershenfeld.dev/). 

Shoutout to [necauqua](https://github.com/necauqua) who gave me some inspiration for optimizing and condensing my scripts. They have a cloned version of the project on their profile with very clean code if thats your jam. 
