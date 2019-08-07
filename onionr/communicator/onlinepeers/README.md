# Online Peers

Manages a pool of peers to perform actions with. Since Onionr does not maintain socket connections, it holds a list of peers.


## Files

* \_\_init\_\_.py: exposes some functions to interact with the pool
* clearofflinepeer.py: Pop the oldest peer in the offline list
* onlinepeers.py: communicator timer to add new peers to the pool randomly
* pickonlinepeers.py: returns a random peer from the online pool
* removeonlinepeer.py: removes a specified peer from the online pool