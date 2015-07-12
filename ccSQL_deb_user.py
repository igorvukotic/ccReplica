#!/usr/bin/env python
# -*- coding:utf-8 -*-
import ConfigParser,paramiko,os
import os.path,sys,string,io

LocalConfig		='/root/skripte/cc.conf'


def ReadConfig(LocalConfig):
	if os.path.isfile(LocalConfig):
		m_poruka('  OK  ','konfiguraciski fajl prisutan',LocalConfig)
		try:
			config = ConfigParser.RawConfigParser(allow_no_value=False)
			config.read(LocalConfig)
			c_db_user = config.get('slave','db-user')
			c_db_pass = config.get('slave','db-pass')
			c_db_conf = config.get('slave','sql-conf')
			m_ssh_user = config.get('master','ssh-user')
			m_ssh_pass = config.get('master','ssh-pass')
			m_host = config.get('master','host')
			m_db_conf = config.get('master','sql-conf')
			return c_db_user,c_db_pass,c_db_conf,m_ssh_user,m_ssh_pass,m_host,m_db_conf
		except Exception, e:
			m_poruka('GREŠKA', 'nepotpuni configuraciski podaci', str(e))
			return '','','','','','',''
	else:
		m_poruka('  GREŠKA  ','konfiguraciski nije fajl prisutan',LocalConfig)

def MasterDebianConfRead():
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(master_hostname, username=master_ssh_user, password=master_ssh_pass) 
		ftp = ssh.open_sftp()
		file=ftp.file(master_sql_konf, "r", -1)
		data=file.read()
		ftp.close()
		config = ConfigParser.RawConfigParser(allow_no_value=True)
		config.readfp(io.BytesIO(data))
		aPASS = config.get('client','password')
		bPASS = config.get('mysql_upgrade','password')
		m_poruka('  OK  ','MASTER/SFTP','podaci pročitani')
		return aPASS,bPASS
	except Exception, e:
		m_poruka('GREŠKA', 'E1 MASTER/sftp', str(e))
		return '',''

def SlaveDebianConfRead():
	try:
		config = ConfigParser.RawConfigParser()
		config.read(slave_sql_konf)
		aPASS = config.get('client', 'password')
		bPASS = config.get('mysql_upgrade', 'password')
		m_poruka('  OK  ','SLAVE/file ', 'podaci pročitani')
		return aPASS, bPASS
	except Exception, e:
		m_poruka('GREŠKA', 'E2 SLAVE/file open', str(e))
		return '',''

def SlaveDebianConfWrite(aPASS,bPASS,slave_sql_konf):
	config = ConfigParser.RawConfigParser()
	config.read(slave_sql_konf)
	config.set('client', 'password', aPASS)
	config.set('mysql_upgrade', 'password', bPASS)
	try:
		with open(slave_sql_konf, 'wb') as configfile:
			config.write(configfile)

		return 0

	except Exception, e:
		m_poruka('GREŠKA','E3 SLAVE/file write', str(e))
		return 1

def MasterSlaveDebianConfCheck():
	MasterKonfigPass = MasterDebianConfRead()
	SlaveKonfigPass = SlaveDebianConfRead()
	newClientPass = ''
	newMyUpgradePass = ''
	stat_noviPass = 0

	if not MasterKonfigPass[0]:
		m_poruka('GREŠKA','E1.1 MASTER/sftp','readError - STOP');sys.exit(1)
	if not SlaveKonfigPass[0]:
		m_poruka('GREŠKA','E3.1 SLAVE','readError - STOP');sys.exit(1)
	if not MasterKonfigPass[1]:
		m_poruka('GREŠKA','E1.2 MASTER/sftp','readError - STOP');sys.exit(1)
	if not SlaveKonfigPass[1]:
		m_poruka('GREŠKA','E3.2 SLAVE','readError - STOP');sys.exit(1)

	if MasterKonfigPass[0] == SlaveKonfigPass[0]:
		m_poruka(' INFO ','client pass','ISTI')
	else:
		m_poruka(' INFO ','client pass','RAZLIČIT!')
		newClientPass = MasterKonfigPass[0]

	if MasterKonfigPass[1] == SlaveKonfigPass[1]:
		m_poruka(' INFO ','mysql_upgrade pass','ISTI')
	else:
		m_poruka(' INFO ','mysql_upgrade pass','RAZLIČIT!')
		newMyUpgradePass = MasterKonfigPass[1]

	if not newClientPass:
		stat_noviPass = 1;newClientPass = MasterKonfigPass[0]

	if not newMyUpgradePass:
		stat_noviPass += 1;newMyUpgradePass = MasterKonfigPass[1]

	if stat_noviPass ==2:
		m_poruka(' INFO ','nije potrebna izmjena','PASS')
	elif stat_noviPass <2:
		m_poruka(' INFO ','potrebna izmjena','PASS')
		if SlaveDebianConfWrite(newClientPass,newMyUpgradePass,debConfo) == 0:
			m_poruka(' INFO ','Izmjena upisana','PASS')
		else:
			m_poruka('GREŠKA','SLAVE','izmjena nije upisana')
	
	#print newClientPass,newMyUpgradePass

def m_poruka(stat,m1,m2):
	print (('|')+(' ' * 5)+('-[ %s ]- %s,%s')) % (stat,m1,m2)
def m_line1(): 						# -
	print ('|'+('-' * 78)+'|')
def m_line2(): 						# .
	print ('|'+('.' * 78)+'|')
def m_line3():						# =
	print ('|'+('=' * 78)+'|')
def m_line4():						# #
	print ('|'+('#' * 78)+'|')
def MenuHead():
	print ('\n' * 3)
	m_line1()
	print ('|' + (' ' * 2) + '>CloudCentar<' + (' ' * 4) + 'ccSQL Master-Slave Debian.cnf tools v.1' + (' '* 4) + ' by Igor V.' + (' ' * 5 )+ '|')
	m_line1()
	print ('|' + (' ' * 78)+'|')

MenuHead()
Konf = ReadConfig(LocalConfig)
#return c_db_user,	c_db_pass,	c_db_conf,	m_ssh_user,	m_ssh_pass,	m_host,	m_db_conf
master_sql_konf		=Konf[6]
master_hostname 	=Konf[5]
master_ssh_user		=Konf[3]
master_ssh_pass 	=Konf[4]
slave_sql_konf		=Konf[2]
slave_db_user		=Konf[0]
slave_db_pass		=Konf[1]
#
MasterSlaveDebianConfCheck()
m_line1()
print ('\n' * 2)

