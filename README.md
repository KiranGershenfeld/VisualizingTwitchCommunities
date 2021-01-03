# VisualizingTwitchCommunities
Visualizing communities on Twitch.tv based on viewership overlap

## Results
[![Twitch-Communities-High-Res.png](https://i.postimg.cc/RZZmd0kD/Twitch-Communities-High-Res.png)](https://postimg.cc/2VMg8C8Q)

Write up here: https://towardsdatascience.com/insights-from-visualizing-public-data-on-twitch-a73304a1b3eb . If your curious about how to read this graph and why I made it please read the article.

## How can I mess with the graph?
I made the graph in a free data visualization tool called Gephi. [Download it here](https://gephi.org/)
The data set is in Visulization/GephiData . In gephi go to laboratory and import the edge file as an edgelist. Then import the label file as a node list. From there you can go to  overview and run a modularity analysis on the nodes to detect communities.

## How can I collect more data?
The DataCollection folder has a script called main that can be ran to collect the top 100 streams and all their viewers and save it to a csv. You can use the windows task scheduler to run this task at any time interval you like and build up data over long periods of time. 
