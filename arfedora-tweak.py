#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  arfedora-tweak.py
#  
#  Copyright 2017 yucef sourani <youssef.m.sourani@gmail.com>
#
#  www.arfedora.blogspot.com
#
#  www.arfedora.com
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import subprocess
import sys
import os
import yaml
import time

def init_check():
	if not sys.version.startswith("3"):
		sys.exit("Use Python 3 Try run python3 arfedora-tweak.py")
init_check()

def get_distro_name():
	result=""
	if not os.path.isfile("/etc/os-release"):
		return None
	with open("/etc/os-release","r") as myfile:
		for l in myfile.readlines():
			if l.startswith("ID"):
				result=l.split("=")[1].strip()
	if result.startswith("\"") and result.endswith("\""):
		return result[1:-1]
	elif result.startswith("\'") and result.endswith("\'"):
		return result[1:-1]
	return result

distro_name = get_distro_name()
home=os.getenv("HOME")
dirname=os.path.abspath(os.path.dirname(__file__))
plugins_location = dirname+"/Plugins"
os.makedirs(plugins_location,exist_ok=True)

if os.getuid() == 0:
	user_id = "root"
else:
	user_id = "user"

if os.uname().machine == "x86_64":
	arch = "64bit"
else:
	arch = "32bit"
	
programs = {}
finally_programs = {}
speed = 1

def to_check(files):
	for f in files:
		if not os.path.exists( os.path.expanduser(f)):
			return "(Install)"

	return "(Installed)"




def read_all_plugins():
	for f in os.listdir(plugins_location):
		plugin_location = plugins_location+"/{}".format(f)
		if f.endswith(".arfedora") and os.path.isfile(plugin_location):
			plugin = yaml.load(open(plugin_location))['arfedora']
			programs.update(plugin)
read_all_plugins()	



def f_p():
	count = 1
	global finally_programs
	global distor_name
	for k,v in programs.items():
		if v[3] == "all":
			v[3] = arch
		if v[4] == "all":
			v[4] = user_id
		if "all" in v[5]:
			v[5]=[distro_name]
			
		if v[3] == arch and v[4] == user_id and distro_name in v[5]:
			finally_programs[str(count)]=[v[0] , v[1] , to_check(v[2])]
			count+=1
f_p()

def reload_():
	global programs
	global finally_programs
	programs.clear()
	finally_programs.clear()
	read_all_plugins()
	f_p()
	return main()
	
def y_o_n(m):
	while True:
		subprocess.call("clear")
		print()
		print (m)
		print("\nY To Continue || N To Back || Q To Quit : \n-",end="")
		y_n=input().strip()
		if y_n=="Y" or y_n=="y":
			break
		elif y_n=="N" or y_n=="n":
			return main()
		elif y_n=="q" or y_n=="Q":
			sys.exit("\nBye...\n")


def main(msg=""):
	while True:
		subprocess.call("clear")
		print ("Choice Task || q To Quit || r To Reload Plugins.\n")
		for number in range(len(finally_programs.items())):
			print ( "{}-{} {}.\n".format(str(number+1),finally_programs[str(number+1)][0].title(),finally_programs[str(number+1)][2]) )
			

		
		if len(msg) != 0:
			print (msg)
		msg=""
		answer=input("-").strip()
		if answer == "q" or answer == "Q":
			sys.exit("\nbye...")
		elif answer == "r" or answer == "R":
			return reload_()
			
		elif answer in finally_programs.keys():
			program = finally_programs[answer]
			if program[2] != "(Installed)":
				for command in program[1]:
					print (program[0])
					y_o_n(program[0])
					check = subprocess.call(command,shell=True)
					if check != 0:
						return main("\nTask ( {} ) Fail.".format(program[0]))
					time.sleep(1)
				if check == 0:
					main("\nTask ( {} ) Sucess.".format(program[0]))
					
			else:
				return main("\nNothing To Do.\n".format(program[0]))
if __name__ == "__main__":
	main()
