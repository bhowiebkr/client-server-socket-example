# Client, Server socket example in python

A client and server python example using QtNetwork

I was dealing with some python socket communication bugs in Qt based GUI so I built this simple example of 2 apps (client and server) to test on. I have it setup to run on the same machine but the code can be easily modified to run on a local or external network. I ended up giving up on using python native socket and instead am using QtNetwork which works much better in Qt based GUI.

![Alt text](images/client_and_server_gui.jpg)

If you see mistakes or anything that could be done better let me know and do a pull request and I’ll check it out. I’ve left out static typing hints on purpose even though I believe they are beneficial but for the purpose of getting a minimal example with no extra bloat I’ve left them out.

