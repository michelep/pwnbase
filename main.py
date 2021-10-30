#!/usr/bin/env python
###############################
# pwnbase - the smart way to manage wpa handshakes collected by pwnagotchi
#
# v0.0.1 - 29.01.2020 
# * First commit
#
# v0.0.2 - 29.01.2020
# * Some minor changes committed
#
# v0.0.3 - 25.04.2020
# * Fixed an error on duplicate peer
# * Added remove option
# * Added log option
#
# v0.0.4 - 30.10.2021
# * Minor updates just to keep alive the software
#
# https://github.com/michelep/pwnbase
# 
# by O-Zone <o-zone@zerozone.it>
import paramiko
import sqlite3
import os
import sys
import subprocess
import argparse

# <-- CONFIGURATION VALUES
hostname = '10.10.0.2'
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
		if row and (int(row[0]) == fsize):
			return False
	return True

# Add or update peer on DB
def db_addpeer(filename,fsize):
	cur = DB.cursor()
	result = cur.execute("UPDATE peers SET size='%d',chgdate=date('now') WHERE filename='%s';"%(fsize,filename))
	if result:
		return True
	# add new...
	try:
		result = cur.execute("INSERT INTO peers(filename,size,addate) VALUES('%s','%d',date('now'));"%(filename,fsize))
		print(cur.lastrowid)
		DB.commit()
	except Exception as e:
		print('INSERT new peer failed with error: %s: %s' % (e.__class__, e))
		return False
	return True

# MAIN()
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='pwnbase - the smart way to manage wpa handshakes collected by pwnagotchi')
	parser.add_argument('-i','--ip', help='Pwnagotchi IP (default: %s)'%hostname,required=False)
	parser.add_argument('-p','--port', help='Pwnagotchi port (default: %d)'%port,required=False)
	parser.add_argument('-r','--remove', help='Remove peer files after download', action='store_true')
	parser.add_argument('-l','--log', help='Enable paramiko log (useful for debugging)', action='store_true')
	args = parser.parse_args()
	if args.ip:
		hostname = args.ip
	if args.port:
		port = args.port
	# Open DB
	DB = db_init()
	# Now connect via SSH
	print("# Connecting to %s:%d..."%(hostname,port))
	try:
		if args.log:
			paramiko.util.log_to_file('paramiko.log')
		s = paramiko.SSHClient()
		s.load_system_host_keys()
		s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		s.connect(hostname, port, username, password)
	except Exception as e:
		print("[!] An error occurred connecting to Pwnagotchi via SSH: %s: %s"% (e.__class__, e))
		sys.exit(-1)

	sftp = s.open_sftp()
	try:
		sftp.chdir(hshakes_r_path)	
	except Exception as e:
		print("[!] Error while fetching handshakes from %s"%(hshakes_r_path))
		sys.exit(-1)

	files = sftp.listdir_attr()
	for f in files:
		print('Checking %s (%d)...'%(f.filename,f.st_size))
		if db_checkpeer(f.filename,f.st_size):
			if sftp_copy(f.filename):
				# After successfull copy, add to DB
				db_addpeer(f.filename,f.st_size)
				# Remove downloaded peer files?
				if args.remove:
					try:
						sftp.remove(f.filename)
						print("REMOVED")
					except Exception as e:
						print("Failed removing %s: %s %s"%(f.filename,e.__class__,e))
		# Convert to HCCAPX using multicapconverter (https://github.com/s77rt/multicapconverter)
		try:
			status = subprocess.call('./multicapconverter.py --quiet --input handshakes/%s --export hccapx'%(f.filename), shell=True)
			if status < 0:
				print("Child was terminated by signal %d",status)
			else:
				print("Child returned %d"%status)
		except OSError as e:
			print("Execution failed: %s"%e)
	# Close connection
	s.close()