#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals

import sys
import dbus
import dbus.service
import dbus.mainloop.glib
import os

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"
adapter_path = "/org/bluez/hci0"

sys.path.insert(0, '/usr/share/doc/bluez-test-scripts/examples')
import bluezutils

bus = None
device_obj = None

connected = False

CONFIRM_CODE = "Please confirm the code on your device"
CANCELLED = "Pairing Cancelled"
DISCOVERABLE = "I'm now discoverable"
NOT_DISCOVERABLE = "I'm now not discoverable"
CONNECTION_ERROR = "Connection failed, removing pairing information"

global last_connected_path
global last_connected_time
last_connected_path = ""
lcp_f = None
last_connected_time = 0.0
DISC_THRES = 2

def save_last_connected_path(path):
	last_connected_path = path
	lcp_f.seek(0, 0)
	lcp_f.write("%s\n" % path)

def audio_play(msg, param1):
    print("Audio Playback: %s : %s" % (msg, param1))

def set_discoverable():
	props = dbus.Interface(bus.get_object("org.bluez", adapter_path),
					"org.freedesktop.DBus.Properties")
	props.Set("org.bluez.Adapter1", "Powered", True)
	props.Set("org.bluez.Adapter1", "Pairable", True)
	props.Set("org.bluez.Adapter1", "Discoverable", True)
	audio_play(DISCOVERABLE, "")

def set_not_discoverable():
	props = dbus.Interface(bus.get_object("org.bluez", adapter_path),
					"org.freedesktop.DBus.Properties")
	props.Set("org.bluez.Adapter1", "Powered", True)
	props.Set("org.bluez.Adapter1", "Pairable", False)
	props.Set("org.bluez.Adapter1", "Discoverable", False)
	audio_play(NOT_DISCOVERABLE, "")

def set_trusted(path):
	props = dbus.Interface(bus.get_object("org.bluez", path),
					"org.freedesktop.DBus.Properties")
	props.Set("org.bluez.Device1", "Trusted", True)

class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
	exit_on_release = True

	def set_exit_on_release(self, exit_on_release):
		self.exit_on_release = exit_on_release

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Release(self):
		print("Release")
		if self.exit_on_release:
			mainloop.quit()

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		audio_play(CONFIRM_CODE, "%06d" % passkey)
		set_trusted(device)
		return

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Cancel(self):
		audio_play(CANCELLED, "")
		print("Cancel")

def properties_changed(interface, changed, invalidated, path):
	global last_connected_path
	global last_connected_time
	if interface != "org.bluez.Device1":
		return
	if changed == None:
		return
	if changed.has_key('Connected'):
		if changed['Connected'] == dbus.Boolean(1):
			save_last_connected_path(path)
			last_connected_time = os.times()[4]
			set_not_discoverable()
		elif changed['Connected'] == dbus.Boolean(0):
			time = os.times()[4]
			if((path == last_connected_path) and
				((time - last_connected_time) < DISC_THRES)):
				adapter = bluezutils.find_adapter()
				adapter.RemoveDevice(path)
				save_last_connected_path("")
				audio_play(CONNECTION_ERROR, "")
			set_discoverable()
	else:
		print ("PATH: %s PROPS: %s" % (path, changed))

if __name__ == '__main__':

# Create a file for saving last connected device
	persistent_file = "/tmp/last_bt_device"
	if (len(sys.argv) > 1):
		persistent_file = sys.argv[1]
	lcp_f = open(persistent_file, "w+")
	last_connected_path = lcp_f.readline()

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()
	mainloop = GObject.MainLoop()

# Create a pairing agent
	path = "/displayonly/agent"
	capability = "DisplayOnly"
	agent = Agent(bus, path)

#Register pairing agent to Agent Manager, as default
	obj = bus.get_object(BUS_NAME, "/org/bluez");
	manager = dbus.Interface(obj, "org.bluez.AgentManager1")
	manager.RegisterAgent(path, capability)
	manager.RequestDefaultAgent(path)

#Register to receive properties of the connection state
	bus.add_signal_receiver(properties_changed,
			dbus_interface = "org.freedesktop.DBus.Properties",
			signal_name = "PropertiesChanged",
			arg0 = "org.bluez.Device1",
			path_keyword = "path")

#Set our default adapter as discoverable
	set_discoverable()

#Finish setup - go to main loop
	mainloop.run()

