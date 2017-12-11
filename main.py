#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, ssl, yaml, json, getopt
from modules import configurator, logger, nessus
from datetime import datetime


def getReport():

	cfgFile = configurator.get_config("general")
	cfg = yaml.load(cfgFile)
	cfgFile.close()

	conn = nessus.api()	
	scan = nessus.scan()
	report = nessus.report()

	dir_path = os.path.dirname(os.path.realpath(__file__))

	targetsFile = configurator.get_config("targets", dir_path + cfg['logger']['log'], cfg['logger']['debug'])
	try:
		targets = yaml.load(targetsFile)
	except Exception as e:
		logger.write(str(datetime.now()) + " ERROR " + str(e) + ". Can not load targets list. Exiting.", dir_path + cfg['logger']['log'])
		sys.exit()

	for folder in targets:
		scan.folder = folder
		scan.getFolderID()
		for ip in targets[folder]:
			if ( (('scan' in targets[folder][ip]) and ((datetime.now() - datetime.strptime(targets[folder][ip]['scan'], "%Y-%m-%d")).days >= cfg['nessus']['scan_ttl'])) or ('scan' not in targets[folder][ip]) ):
				for host in targets[folder][ip]['hosts']:
					if (datetime.now() - datetime.strptime(str(targets[folder][ip]['hosts'][host]['date']), "%Y-%m-%d")).days <= cfg['nessus']['host_ttl']:
						scan.name = host
						scan.getID()
						scan.getStatus()
						if scan.ID == '':
							scan.target = ip
							scan.create()
							scan.launch()
						elif scan.status == 'completed':
							scan.launch()
						targets[folder][ip]['scan'] = datetime.now().strftime("%Y-%m-%d")
						if cfg['logger']['debug'] is True:
							logger.write(str(datetime.now()) + " DEBUG Scan will be lauched for folder = " + str(folder)  + ", ip = " + str(ip) + ", host = " + str(host), dir_path + cfg['logger']['log'])
						break
			elif ((('report' in targets[folder][ip]) and (datetime.strptime(targets[folder][ip]['report'], "%Y-%m-%d") < datetime.strptime(targets[folder][ip]['scan'], "%Y-%m-%d"))) or ('report' not in targets[folder][ip])):	
				for host in targets[folder][ip]['hosts']:
					if (datetime.now() - datetime.strptime(str(targets[folder][ip]['hosts'][host]['date']), "%Y-%m-%d")).days <= cfg['nessus']['host_ttl']:
						scan.name = host
						scan.getStatus()
						if scan.status == 'completed':
							scan.getID()
							scan.getHistoryID()
							report.getReportID(scan.ID, scan.historyID)
							report.getReport(scan.ID)
							report.downloadReport(host, dir_path + cfg['logger']['report'])
							targets[folder][ip]['report'] = datetime.now().strftime("%Y-%m-%d")
							if cfg['logger']['debug'] is True:
								logger.write(str(datetime.now()) + " DEBUG Report will be exported for folder = " + str(folder)  + ", ip = " + str(ip) + ", host = " + str(host), dir_path + cfg['logger']['log'])
							break
			else:
				if cfg['logger']['debug'] is True:
					logger.write(str(datetime.now()) + " DEBUG Scan and Report are actual for folder = " + str(folder)  + ", ip = " + str(ip), dir_path + cfg['logger']['log'])

	configurator.update_config(targets, targetsFile)			

	sys.exit()


def addTarget():
	global folder

	cfgFile = configurator.get_config("general")
	cfg = yaml.load(cfgFile)
	cfgFile.close()

	dir_path = os.path.dirname(os.path.realpath(__file__))

	if folder == None:
		folder = cfg['nessus']['folder']['default']
		folder_pattern = host.split(cfg['nessus']['folder']['delimiter'])[cfg['nessus']['folder']['position']]
		if folder_pattern in cfg['nessus']['folders']:
			folder = cfg['nessus']['folders'][folder_pattern]

	targetsFile = configurator.get_config("targets", dir_path + cfg['logger']['log'], cfg['logger']['debug'])
	try:
		targets = yaml.load(targetsFile)
	except Exception as e:
		if cfg['logger']['debug'] is True:
			logger.write(str(datetime.now()) + " DEDUG " + str(e) + ". New list of targets will be created.", dir_path + cfg['logger']['log'])
		targets = {}


	if cfg['logger']['debug'] is True:
		event = str(datetime.now()) + " DEBUG Target's config will be updated: folder = " + str(folder) + ", ip = " + str(ip) + ", host = " + str(host)
		logger.write(event, dir_path + cfg['logger']['log'])

	try:
		targets[str(folder)][str(ip)]['hosts'][str(host)] = {'date': datetime.now().strftime("%Y-%m-%d")}
	except Exception as e:
		try:
			targets[str(folder)][str(ip)] = {'hosts':{str(host):{'date': datetime.now().strftime("%Y-%m-%d")}}}
		except Exception as e:
			try:
				targets[str(folder)] = {str(ip):{'hosts':{str(host):{'date': datetime.now().strftime("%Y-%m-%d")}}}}
			except Exception as e:
				logger.write(str(datetime.now()) + " " + str(targets), dir_path + cfg['logger']['log'])
				logger.write(str(datetime.now()) + " ERROR Can not update targets.yml configuration file. Details: folder = " + str(folder) + ", ip = " + str(ip) + ", host = " + str(host) + ". Exception: %s" % str(e), dir_path + cfg['logger']['log'])
				sys.exit()

	configurator.update_config(targets, targetsFile)

	sys.exit()


def main(argv):

	global host
	global ip
	global folder

	folder = None

	try:
		opts, args = getopt.getopt(argv,"a:",["host=", "ip=", "folder="])
	except getopt.GetoptError:
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-a':
			action = arg
		elif opt in ("--folder"):
			folder = arg
		elif opt in ("--ip"):
			ip = arg
		elif opt in ("--host"):
			host = arg

	if action == "addTarget":
		addTarget()
	elif action == "getReport":
		getReport()

	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
