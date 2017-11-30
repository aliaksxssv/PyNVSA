#!/usr/bin/python
# -*- coding: utf-8 -*-

def write(data, journal):
	f = open(journal, 'a')
	f.write(data + "\n")
	f.close()
