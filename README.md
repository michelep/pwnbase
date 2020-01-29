pwnbase
=======

Inspired by the great work by CyrisXD and his Pwnagetty, i decide to make a Python script to simplify my life managing captured handshaked.

So, just plug your [Pwnagotchy](https://pwnagotchi.ai) (anche make sure it will be reachable by the net!) and run the "main.py" script ;-)

Dependencies
------------

sudo python -m pip install paramiko sqlite3


Pre-flight checks
-----------------

Open main.py with your favourite text editor and change the lines to reflect your environment:

```
# <-- CONFIGURATION VALUES
hostname = '10.0.0.2'
port = 22
username = 'pi'
password = 'raspberry'
hshakes_r_path = '/home/pi/handshakes/'
hshakes_l_path = './handshakes/'
db_path = 'handshakes.db'
# -->
```

Please note that the use of this code is under your OWN RESPONSABILITY.
