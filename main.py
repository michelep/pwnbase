#!/usr/bin/env python
###############################
# pwnbase - fetch new peers handshake captures from pwnagotchi 
# 
# by O-Zone <o-zone@zerozone.it>
import paramiko
import sqlite3
import os

# <-- CONFIGURATION VALUES
hostname = '10.0.0.2'
port = 22
username = 'pi'
password = 'raspberry'
hshakes_r_path = '/home/pi/handshakes/'
hshakes_l_path = './handshakes/'
db_path = 'handshakes.db'
# -->

sftp = None
DB = None

# Copy peer file via SFTP
def sftp_copy(filename):
    try:
	f_remote = str(filename)
	f_local = str(hshakes_l_path+filename)
	print("GETting file %s..."%(f_remote))
	sftp.get(f_remote,f_local)
    except Exception as e:
	print('An error occurred copying handshakes from Pwnagotchi via SSH: %s: %s' % (e.__class__, e))
	return False
    return True

# Initilize peers DB
def db_init():
    try:
	db = sqlite3.connect(db_path)
	cur = db.cursor()
	result = cur.execute('''CREATE TABLE IF NOT EXISTS peers
    	    (filename  CHAR(256) PRIMARY KEY,
    	    size           INT NOT NULL,
	    addate        DATETIME,
    	    chgdate        DATETIME);''')
	db.commit()
    except Exception as e:
	print('DB init() error: %s: %s' % (e.__class__, e))
	return False

    return db

# True if need to download the file, False otherwhise
def db_checkpeer(filename,fsize):
    cur = DB.cursor()
    result = cur.execute("SELECT size FROM peers WHERE filename LIKE '%s';"%(filename))
    if result:
	row = cur.fetchone()
	if row:
	    if int(row[0]) == fsize:
		return False
    return True

# Add peer to DB
def db_addpeer(filename,fsize):
    cur = DB.cursor()
    result = cur.execute("INSERT INTO peers(filename,size,addate) VALUES('%s','%d',date('now'));"%(filename,fsize))
    print cur.lastrowid
    DB.commit()
    return True

# MAIN()
if __name__ == "__main__":
    DB = db_init()
    try:
	paramiko.util.log_to_file('paramiko.log')
	s = paramiko.SSHClient()
	s.load_system_host_keys()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	s.connect(hostname, port, username, password)

    except Exception as e:
	print('An error occurred connecting to Pwnagotchi via SSH: %s: %s' % (e.__class__, e))
	pass

    sftp = s.open_sftp()
    sftp.chdir(hshakes_r_path)

    files = sftp.listdir_attr()
    for f in files:
	print('Checking %s (%d)...'%(f.filename,f.st_size))
	if db_checkpeer(f.filename,f.st_size):
	    if sftp_copy(f.filename):
		# After successfull copy, add to DB
		db_addpeer(f.filename,f.st_size)
		# Convert to HCCAPX
		os.system('./multicapconverter.py --input handshakes/%s --export hccapx'%(f.filename))

    s.close()