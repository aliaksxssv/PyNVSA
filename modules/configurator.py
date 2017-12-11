#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, yaml, logger, time
import fcntl, errno
from datetime import datetime

def get_config(cfg_name, log_path=None, debug=False):
	cfg_path = os.path.dirname(os.path.realpath(__file__)) + "/../conf.d/" + cfg_name + ".yml"
	if cfg_name == 'targets':
		while True:
			try:
				ymlfile = open(cfg_path, 'r+')
				fcntl.flock(ymlfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
				break
			except IOError as e:
				if e.errno != errno.EAGAIN:
					logger.write(str(datetime.now()) + " ERROR " + str(e) + ". New file will be created.", log_path)
					ymlfile = open(cfg_path, 'w')
					break
				else:
					if debug is True:
						logger.write(str(datetime.now()) + " DEBUG " + str(e) + ". File targets.yml is locked. Waiting ...", log_path)
					ymlfile.close()
					time.sleep(1) 
	else:
		ymlfile = open(cfg_path, 'r')
	return ymlfile


def update_config(data, ymlfile):
	ymlfile.seek(0)
	ymlfile.truncate()
	yaml.dump(data, ymlfile, default_flow_style=False)
	fcntl.flock(ymlfile, fcntl.LOCK_UN)
	ymlfile.close()

