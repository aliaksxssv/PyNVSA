#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, urllib2, ssl, json, yaml
import configurator, logger


class scan():

	def __init__(self):
		self.folder=''
		self.folderID = ''
		self.name = ''
		self.ID = ''
		self.status = ''
		self.target = ''

		__conn = api()
		__conn.url = '/scans'
		__conn.data = ''
		self.config = __conn.sendRequest()


	def getID(self):
		self.ID = ''
		for i in range(len(self.config['scans'])):
			if self.folderID == self.config['scans'][i]['folder_id'] and self.name == self.config['scans'][i]['name']:
				self.ID = self.config['scans'][i]['id']
				
	def getStatus(self):
		self.status = ''
		for i in range(len(self.config['scans'])):
			if self.folderID == self.config['scans'][i]['folder_id'] and self.name == self.config['scans'][i]['name']:
				self.status = self.config['scans'][i]['status']

	def getFolderID(self):
		self.folderID = ''
		for i in range(len(self.config['folders'])):
			if self.folder == self.config['folders'][i]['name']:
				self.folderID = self.config['folders'][i]['id']

		if self.folderID == '':
			conn = api()
			conn.url = '/folders'
			conn.data = '{\"name\":\"' + self.folder + '\"}'
			self.folderID = conn.sendRequest()


	def getHistoryID(self):
		conn = api()
		conn.url = '/scans/' + str(self.ID)
		history = conn.sendRequest()["history"]
		self.historyID = history[len(history)-1]["history_id"]


	def create(self):
		cfgFile = configurator.get_config("general")
		cfg = yaml.load(cfgFile)
		cfgFile.close()

		conn = api()
		conn.url = '/scans'
		conn.data = '{ \"uuid\": \"' + cfg['nessus']['scan_template_uuid'] + '\", \"settings\": { \"name\": \"' + str(self.name) + '\", \"enabled\": true, \"folder_id\": ' + str(self.folderID)  + ', \"scanner_id\": 1, \"policy_id\": ' + cfg['nessus']['scan_policy_id'] + ', \"text_targets\": \"' + str(self.target)  + '\" }}'
		self.ID = conn.sendRequest()["scan"]["id"]

		
	def launch(self):
		conn = api()
		conn.url = '/scans/' + str(self.ID) + '/launch'
		conn.data = '{}'
		conn.sendRequest()

class report():

	def __init__(self):
		self.reportID = ''
		self.report = ''

	def getReportID(self, scanID, scanHistoryID):
		conn = api()
		conn.url = '/scans/' + str(scanID) + '/export?history_id=' + str(scanHistoryID)
		conn.data = '{"format": "csv"}'
		self.reportID = conn.sendRequest()['file']
                   
	def getReport(self, scanID):
		conn = api()
		conn.url = '/scans/' + str(scanID) + '/export/' + str(self.reportID) + '/download'
		self.report = conn.sendRequest()

	def downloadReport(self, host, reportPath):
		if not os.path.exists(reportPath):
			os.makedirs(reportPath)
		logger.write(self.report.replace('\n"','\n"' + host + '","'), reportPath + "/" + str(self.reportID) + '.csv')

class api():
	
	def __init__(self):
		self.url = '/'
		self.data = ''

	def sendRequest(self):
		cfgFile = configurator.get_config("general")
		cfg = yaml.load(cfgFile)
		cfgFile.close()

		ctx = ssl.create_default_context()
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
		opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx))
		if self.data == '':
			request = urllib2.Request('https://' + cfg["nessus"]["server"]  + ':8834' + str(self.url))
		else:
			request = urllib2.Request('https://' + cfg["nessus"]["server"]  + ':8834' + str(self.url), data=self.data)
		request.add_header('X-ApiKeys', 'accessKey=' + str(cfg["nessus"]["accessKey"]) + '; secretKey=' + str(cfg["nessus"]["secretKey"]))
		request.add_header('Content-Type', 'application/json')
		reply = opener.open(request).read().decode('utf8')
		self.data = ''
		try:
			return json.loads(reply)
		except:
			return reply
