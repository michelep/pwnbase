pwnbase
=======

Inspired by the great work by CyrisXD and his Pwnagetty, i decide to make a Python script to simplify my life managing captured handshaked.

So, just plug your [Pwnagotchy](https://pwnagotchi.ai) via USB data port and run the "main.py" script: pwnbase checks for new handshakes, save them and prepare for hashcat. Simply, isn't?

![Raspberry Pi W zero](/assets/rpiw.jpg)

Dependencies
------------

sudo python -m pip install paramiko sqlite3

please note that multicapconverter.py was created by [Abdelhafidh Belalia (s77rt)](https://github.com/s77rt/multicapconverter/) and related credits


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


-----------------


Disclaimer
-----------------

Please note that the use of this code is under your OWN RESPONSABILITY.
