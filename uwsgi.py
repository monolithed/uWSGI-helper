# -*- coding: utf-8; indent-tabs-mode: nil; tab-width: 4; c-basic-offset: 4; -*-

'''
- UWSGI process helper
-
- uwsgi.py  [ --test ] | [ --stop ] | [ --start ] | [ --reload ] |
-           [ --kill ] | [ --info ] | [ --state ] | [ --version ] |
-             --path |     --name
-
_
- uwsgi.py --path='/usr/local/etc/uwsgi/uwsgi.yaml' --name='example.com' --test
-
- # uwsgi.yaml
-
- default: &options
-     path    : /usr/local/bin/uwsgi
-
- example.com:
-    path    : /usr/local/bin/uwsgi
-    pid     : /var/run/uwsgi/example.com.uwsgi.pid
-    config  : /home/www/example.com/uwsgi.yaml
-
-
- @author Alexander Guinness <monolithed@gmail.com>
- @version 0.0.2
- @license: MIT
- @date: Jul 24 06:53:00 2013
'''


import yaml

import sys
import os
import subprocess
# import time



class uWSGI(object):
	def __init__(self, options):
		self.options = options.__dict__
		self.params = self.__params()

		self.__run()


	def __exec(self, command):
		try:
			process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

			# while process.poll() is None:
			# 	time.sleep(.2)
			#
			# if process.returncode is not 0:
			# 	self.__log('there was an error starting the server', True)

			output, error = process.communicate()

			return output.decode('utf-8')

		except OSError as error:
			self.__log('Execution failed: \n%s' % error, True)


	def __launch(self, value, text=''):
		output = self.__exec('%s %s' % (self.params.get('path'), value))

		if text:
			self.__log('%s...' % text)

		else:
			self.__log(output)


	def __parse_config(self, name, file, data=''):
		try:
			data = yaml.load(file, Loader=yaml.Loader)

			if self.options.get('test'):
				self.__log('the configuration file %s syntax is ok' % name)

		except yaml.YAMLError as error:
			sys.exit(error)

		return data


	def __get_config(self, name):
		try:
			with open(name, 'r', encoding='utf-8') as file:
				return self.__parse_config(name, file)

		except IOError:
			self.__log('%s is not found' % name, True)


	def __log(self, name, exit=''):
		print('[%s]%s %s' % (self.__class__.__name__,
			exit and ' error:', name))

		if exit:
			sys.exit(1)


	def __params(self):
		path = self.options.get('path')
		data = self.__get_config(path)

		if not data:
			self.__log('the configuration file %s is not found' %
				path, True)

		name = self.options.get('name')
		data = data[name]

		if not data:
			self.__log('there is no the project settings in file %s' %
				path, True)

		return data


	def __run(self):
		base = ('name', 'path')

		for key, value in self.options.items():
			if value and key not in base:
				return self.__getattribute__(key)()


	def required(self):
		required = {'path', 'config'}

		result = required <= set(self.params)

		if not result:
			self.__log('please see required options: \n %s' %
				required, True)

		return result


	def test(method):
		return lambda self: \
			self.__get_config(self.params.get('config')) and \
			self.required() and method(self)


	def pid(self):
		file = self.params.get('config')
		uwsgi = self.__get_config(file).get('uwsgi')

		if 'pidfile' in uwsgi:
			return uwsgi.get('pidfile')

		else:
			self.__log('pidfile is empty: \n %s' % file, True)


	@test
	def start(self):
		self.__launch('--yaml %s' %  self.params.get('config'), 'starting')


	@test
	def stop(self):
		self.__launch('--stop %s' % self.pid(), 'stopping')


	@test
	def reload(self):
		self.__launch('--reload %s' % self.pid(), 'reloading')


	def info(self):
		self.__launch('--help')


	def version(self):
		self.__launch('--version')


	def kill(self):
		output = self.__exec('killall -%s uwsgi' %
			self.options.get('kill'))

		if not output:
			file = os.path.basename(self.params.get('config'))
			output = self.__exec('ps aux | grep %s | grep -v grep' % file)

			if not output:
				self.__log('killed')

			else:
				self.__log('the process is still working!')


	def state(self):
		command = \
			'''ps axw -o pid,user,%cpu,%mem,command | {
				awk "NR == 1 || /uwsgi/" | grep -vE "awk|--info" ;
			}'''

		output = self.__exec(command)
		self.__log(output)



if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='UWSGI')

	params = [
		'test', 'stop', 'start', 'reload',
		'info', 'version', 'state'
	]

	for key in params:
		parser.add_argument('--%s' % key, action='store_true')

	parser.add_argument('--kill', help =
		'A process can be sent POSIX-signals like '
		'SIGHUP, SIGTERM or SIGKILL: See: <man signal>'
	)

	parser.add_argument('--path', default='/opt/local/etc/uwsgi/uwsgi.yaml')
	parser.add_argument('--name', required=True)

	options = parser.parse_args()
	uWSGI(options)
