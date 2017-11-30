#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, yaml, logger
from datetime import datetime

def get_config(cfg_name, log_path=None):
	try:
		with open(os.path.dirname(os.path.realpath(__file__)) + "/../conf.d/" + cfg_name + ".yml", "r") as ymlfile:
			cfg = yaml.load(ymlfile)
	except Exception as e:
		logger.write(str(datetime.now()) + " ERROR File " + str(cfg_name) + ".yml does not exist. Details: %s" % str(e), log_path)
		cfg = {}
	return cfg

def update_config(data, config_path):
	with open(config_path, 'w') as outfile:
		yaml.dump(data, outfile, default_flow_style=False)

