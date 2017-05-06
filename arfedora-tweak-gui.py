#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import threading
import multiprocessing
import gettext
import gi
import time
gi.require_version("Gtk","3.0")
from gi.repository import Gtk,GLib,GdkPixbuf

project_location=os.path.dirname(os.path.abspath(__file__))

############################################################################
program_name        = "arfedora-tweak"
############################################################################



locale=project_location+"/locale"
gettext.install(program_name,locale)
#gettext.install(program_name)



############################################################################
program_version     = "0.1"
program_copyright   = _("Copyright © 2017 Youssef Sourani")
program_comment     = _("arfedora-tweak is a simple tool for install programs")
program_authors     = ["Youssef Sourani <youssef.m.sourani@gmail.com>"]
program_translators = "translator-credits"
#program_translators = "yucef\nhareth"
website             = "http://www.arfedora.blogspot.com"
#icon                = ""
icon                = project_location+"/icon/arfedora-tweak.png"
exec__              = "pkexec"
program_width       = 600
program_height      = 400
############################################################################

file_to_run = "/tmp/{}_run".format(program_name)


class NInfo(Gtk.MessageDialog):
	def __init__(self,message,parent=None):
		Gtk.MessageDialog.__init__(self,parent,1,Gtk.MessageType.INFO,Gtk.ButtonsType.OK,message)
		self.parent=parent
		if self.parent != None:
			self.set_transient_for(self.parent)
			self.set_modal(True)
			self.parent.set_sensitive(False)
		else:
			self.set_position(Gtk.WindowPosition.CENTER)
		self.run()
		if self.parent != None:
			self.parent.set_sensitive(True)
		self.destroy()
		
		
def init_check():
	if not sys.version.startswith("3"):
		NInfo(_("Use Python 3 Try run python3 %s"%__file__))
		sys.exit()
	
	with open(file_to_run,"w") as myfile:
		pass
	if oct(os.stat(file_to_run).st_mode)[-3:]!="755":
		check = subprocess.call("{} chmod 755 {}".format(exec__,file_to_run),shell=True)
		if check != 0:
			NInfo(_("Error"))
			sys.exit()
	
init_check()



import yaml



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
dirname=os.path.abspath(os.path.dirname(__file__))
plugins_location = dirname+"/Plugins"
os.makedirs(plugins_location,exist_ok=True)



if os.uname().machine == "x86_64":
	arch = "64bit"
else:
	arch = "32bit"
	
programs = {}
finally_programs = {}
speed = 1
status=multiprocessing.Value("i",2)


		
class WWait(threading.Thread):
	def __init__(self,status,msg="",title="",speed=100,parent=None,box=None):
		threading.Thread.__init__(self)
		self.msg=msg
		self.status = status
		self.speed = speed
		self.title=title
		self.box=box
		self.parent = parent
		self.parent.set_sensitive(False)

		self.p=Gtk.ProgressBar()
		if len(self.msg)!=0 and len(self.title)!=0:
			self.p.set_text(self.msg)
			self.p.set_show_text(self.msg)
		self.box.pack_start(self.p,True,True,0)
		
	def __pulse(self):
		if self.status.value !=2:
			self.parent.set_sensitive(True)
			self.p.set_fraction(0.0)
			self.p.hide()
			return False
		else:
			self.p.pulse()
			return True

	def __loading_progressbar(self):
		self.source_id = GLib.timeout_add(self.speed, self.__pulse)

	def run(self):
		self.p.show()
		self.__loading_progressbar()
		
		
		

		
		
def to_check(files):
	for f in files:
		if not os.path.exists( os.path.expanduser(f)):
			return _("Install")

	return _("Installed")




def read_all_plugins():
	for f in os.listdir(plugins_location):
		plugin_location = plugins_location+"/{}".format(f)
		if f.endswith(".Plugins") and os.path.isfile(plugin_location):
			plugin = yaml.load(open(plugin_location))['plugins']
			programs.update(plugin)
read_all_plugins()	



def f_p():
	count = 1
	global finally_programs
	global distor_name
	for k,v in programs.items():
		if v[3] == "all":
			v[3] = arch
		if "all" in v[5]:
			v[5]=[distro_name]

		if v[3]=="32bitonly" :
			if arch!="64bit" and distro_name in v[5]:
				finally_programs[str(count)]=[v[0] , v[1] , to_check(v[2]),v[4]]
				count+=1

		else:
			if arch=="64bit":
				if  distro_name in v[5]:
					finally_programs[str(count)]=[v[0] , v[1] , to_check(v[2]),v[4]]
					count+=1
					
			
	
			else:
				if v[3] == arch and distro_name in v[5]:
					finally_programs[str(count)]=[v[0] , v[1] , to_check(v[2]),v[4]]
					count+=1
					
f_p()



def reload_(button,win):
	global programs
	global finally_programs
	programs.clear()
	finally_programs.clear()
	read_all_plugins()
	f_p()
	win.destroy()
	return main_gui(True)


				
class CT(threading.Thread):
	def __init__(self,command,status,button,data):
		threading.Thread.__init__(self)
		self.command=command
		self.status = status
		self.button=button
		self.status_label=data[3]
		self.task=data[4]
		
	def run(self):
		check = subprocess.call(self.command,shell=True)
		if check == 0:
			self.button.set_label(_("Installed"))
			self.status_label.set_text(_("Status : Task ( {} ) Sucess.".format(self.task)))
			self.status.value = 3
		else:
			self.status_label.set_text(_("Status : Task ( {} ) Fail.".format(self.task)))
			self.status.value = 4
		

		
		
		
def installed(button,window):
	return NInfo(_("Nothing To Do"),window)
	
	
def check_if_done(window):
	if status.value == 3:
		NInfo("Done",window)
		status.value=2
		return False
	elif status.value == 4:
		NInfo("Fail",window)
		status.value=2
		return False
	return True
	
def install(button,data):
	command = "set -e\n"
	for c in data[0]:
		command+=repr(r"""{}""".format(c))[1:-1]+"\n"
	with open(file_to_run,"w") as myfile:
		myfile.write(command)
	if data[5]=="root":
		t1 = CT("{} bash  {}".format(exec__,file_to_run),status,button,data)
	else:
		t1 = CT("bash  {}".format(file_to_run),status,button,data)
	t2 = WWait(msg="",status=status,title="",speed=50,parent=data[1],box=data[2])
	t1.start()
	t2.start()
	
	GLib.idle_add(check_if_done,data[1])


def about_(button,parent):
	authors = program_authors
	about = Gtk.AboutDialog()
	about.set_transient_for(parent)
	about.set_program_name(program_name)
	about.set_version(program_version)
	about.set_copyright(program_copyright)
	about.set_comments(program_comment)
	about.set_website(website)
	about.set_website_label(_('My Website'))
	if len(icon)!=0:
		about.set_logo(GdkPixbuf.Pixbuf.new_from_file(icon))
	about.set_authors(authors)
	about.set_license_type(Gtk.License.GPL_3_0)
	translators = program_translators
	if translators != "translator-credits":
		about.set_translator_credits(translators)
	about.run()
	about.destroy()

def main_gui(reset=False):
	w=Gtk.Window()
	w.set_title(program_name)
	w.set_default_size(program_width,program_height)
	w.set_resizable(False)
	w.connect("delete-event",Gtk.main_quit)
	sw=Gtk.ScrolledWindow()
	sw.set_border_width(10)
	main_vbox=Gtk.VBox(spacing=10)
	w.add(main_vbox)
	main_vbox.pack_start(sw,True,True,0)
	vbox=Gtk.VBox(spacing=10)
	sw.add(vbox)
	vbox1=Gtk.VBox(spacing=5)
	if reset:
		status_label=Gtk.Label(_("Status : Reset Sucess"))
	else:
		status_label=Gtk.Label(_("Status : Ready"))
		
	for v in finally_programs.values():
		hbox=Gtk.HBox(spacing=10)
		hbox.set_homogeneous(True)
		vbox.pack_start(hbox,True,True,0)
		label1=Gtk.Label(v[0])
		hbox.pack_start(label1,True,True,25)
		if v[2]==_("Installe"):
			button=Gtk.Button(label=_("Installed"))
			button.set_border_width(2)
			button.connect("clicked",installed,w)
			hbox.pack_start(button,True,True,0)
		else:
			button=Gtk.Button(label=_("Install"))
			button.set_border_width(2)
			button.connect("clicked",install,[v[1],w,vbox1,status_label,v[0],v[3]])
			hbox.pack_start(button,True,True,0)
	
	
	main_vbox.pack_start(vbox1,False,False,0)	
	vbox1.pack_start(status_label,True,True,0)
	refresh_button=Gtk.Button(stock=Gtk.STOCK_REFRESH)
	refresh_button.connect("clicked",reload_,w)
	about_button=Gtk.Button(stock=Gtk.STOCK_ABOUT)
	about_button.connect("clicked",about_,w)
	quit_button=Gtk.Button(stock=Gtk.STOCK_QUIT)
	quit_button.connect("clicked",Gtk.main_quit)
	vbox1.pack_start(refresh_button,True,True,0)
	vbox1.pack_start(about_button,True,True,0)
	vbox1.pack_start(quit_button,True,True,0)
	w.show_all()
	if not reset:
		Gtk.main()
if __name__ == "__main__":
	main_gui()
