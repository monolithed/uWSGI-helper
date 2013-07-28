# -*- coding: utf-8; indent-tabs-mode: nil; tab-width: 4; c-basic-offset: 4; -*-

'''
- UWSGI process helper
-
- uwsgi.py  [ --test ] | [ --stop ] | [ --start ] | [ --reload ] |
-           [ --kill ] | [ --info ] | [ --state ] | [ --version ] |
-             --path |     --name
-
_
- uwsgi --path='/usr/local/etc/uwsgi/uwsgi.yaml' --name='example.com' --test
-
- # uwsgi.yaml
- example.com:
-    path    : /usr/local/bin/uwsgi
-    pid     : /var/run/uwsgi/example.com.uwsgi.pid
-    config  : /home/www/example.com/uwsgi.yaml
-
-
- @author Alexander Guinness <monolithed@gmail.com>
- @version 0.0.1
- @license: MIT
- @date: Jul 24 06:53:00 2013
'''


import yaml

import sys
import os
import subprocess


class uWSGI(object):
	def __init__(self, options):
		self.options = options.__dict__
		self.uwsgi = self.__data()
		self.__router()


	def __router(self):
		base = ('name', 'path')

		for key, value in self.options.items():
			if value and key not in base:
				return self.__getattribute__(key)()


	def __test(method):
		return lambda self: \
			self.test() and method(self)


	def __exec(self, command):
		return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)


	def __output(self, command):
		return subprocess.getoutput(command)


	def __launch(self, option, value = '', text = ''):
		if value:
			self.__log('%s...' % text)

		self.__exec('%s --%s %s' %
			(self.uwsgi.get('path'), option, self.uwsgi.get(value, '')))


	def __load(self, name, file, data = ''):
		try:
			data = yaml.load(file, Loader=yaml.Loader)
			self.__log(name, 'syntax is ok')

		except yaml.YAMLError as error:
			sys.exit(error);

		else:
			self.__log(name, 'is found')

		return data;


	def __log(self, name, text = ''):
		if self.options.get('test'):
			print('[uWSGI] the configuration file %s %s' % (name, text))

		elif not text:
			print('[uWSGI] %s' % name)


	def __open(self, name):
		try:
			with open(name, 'r', encoding='utf-8') as file:
				return self.__load(name, file)

		except IOError:
			self.__log(name, 'is not found')


	def __data(self):
		path = self.options.get('path')
		data = self.__open(path)

		if not data:
			self.__log('the configuration file %s is not found' % path)

		name = self.options.get('name')
		data = data[name]

		if not data:
			self.__log('there is no the project settings in file %s' % path)

		return data


	def name(self):
		pass

	def test(self):
		return self.__open(self.uwsgi.get('config'))


	@__test
	def start(self):
		self.__launch('yaml', 'config', 'starting')


	@__test
	def stop(self):
		self.__launch('stop', 'pid', 'stopping')


	@__test
	def reload(self):
		self.__launch('reload', 'pid', 'reloading')


	def info(self):
		self.__launch('help')


	def version(self):
		return self.__launch('version')


	def kill(self):
		process = self.__exec('killall -%s uwsgi' %
			self.options.get('kill'))

		output, error = process.communicate()

		if not output:
			file = os.path.basename(self.uwsgi.get('config'))
			output = self.__output('ps aux | grep %s | grep -v grep' % file)

			if not output:
				self.__log('killed')

			else:
				self.__log('the process is still working!')

		elif error:
			self.__log('something wrong, please try again!')


	def state(self):
		command = \
			'''ps axw -o pid,user,%cpu,%mem,command | {
				awk "NR == 1 || /uwsgi/" | grep -vE "awk|--info" ;
			}'''

		output = self.__output(command)
		self.__log(output)



if __name__ ==  '__main__':
	import argparse

	parser = argparse.ArgumentParser(description ='UWSGI')

	params = [
		'test', 'stop', 'start', 'reload',
		'info', 'version', 'state'
	]

	for key in params:
		parser.add_argument('--%s' % key, action = 'store_true')

	parser.add_argument('--kill', help =
		'A process can be sent POSIX-signals like '
		'SIGHUP, SIGTERM or SIGKILL: See: <man signal>'
	)

	parser.add_argument('--path', default = '/opt/local/etc/uwsgi/uwsgi.yaml')
	parser.add_argument('--name', required = True)

	options = parser.parse_args()
	uWSGI(options)
