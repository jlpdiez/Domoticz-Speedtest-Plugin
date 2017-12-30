################################################################################
#
# Speedtest Python Plugin
#
# Author: Xorfor
#
################################################################################
"""
<plugin key="xfr_speedtest" name="Speedtest" author="Xorfor" version="1.2.0" wikilink="https://github.com/Xorfor/Domoticz/tree/master/plugins/speedtest">
    <params>
        <param field="Mode1" label="Polling time (minutes)" width="100px" required="true" default="15"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import os

_HEARTBEATS = 6  # minutes

_COMMAND = "speedtest-cli"
_OPTIONS = "--simple"
_PING = "Ping"
_DOWNLOAD = "Download"
_UPLOAD = "Upload"

_PING_UNIT = 1
_DOWNLOAD_UNIT = 2
_UPLOAD_UNIT = 3


class BasePlugin:

    def __init__(self):
        self.__config_ok = False
        self.__runAgain = 0
        self.__polling = 0

    def onStart(self):
        Domoticz.Debug("onStart called")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        # Check parameter for heartbeat. Default is 1. Check every 1 minute for the presence of the defined mac addresses
        self.__polling = int(Parameters["Mode1"])
        if self.__polling < 1:
            self.__polling = 1
        #
        # Check for the existence of the command
        ret = os.popen("dpkg -l | grep " + _COMMAND).read()
        pos = ret.find(_COMMAND)
        if pos >= 0:
            self.__config_ok = True
        else:
            self.__config_ok = False
            Domoticz.Error(_COMMAND + " not found")
            return
        #
        if (len(Devices) == 0):
            Domoticz.Device(Unit=_PING_UNIT, Name=_PING, TypeName="Custom", Options={"Custom": "1;ms"}, Used=1).Create()
            Domoticz.Device(Unit=_DOWNLOAD_UNIT, Name=_DOWNLOAD, TypeName="Custom", Options={"Custom": "1;Mb/s"},
                            Used=1).Create()
            Domoticz.Device(Unit=_UPLOAD_UNIT, Name=_UPLOAD, TypeName="Custom", Options={"Custom": "1;Mb/s"},
                            Used=1).Create()

        DumpConfigToLog()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug(
            "onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        if not self.__config_ok:
            return

        cmd = {}
        value = {}
        units = {}
        #
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            # Run command
            retList = os.popen(_COMMAND + " " + _OPTIONS).read().splitlines()
            num = 0
            for ret in retList:
                cmd[num], value[num], units[num] = ret.split(" ")
                num += 1
            #
            for num in range(len(cmd)):
                Domoticz.Debug(
                    "num: " + str(num) + " - cmd: " + cmd[num] + " - value: " + value[num] + " - units: " + units[num])
                if cmd[num].find(_PING) >= 0:
                    UpdateDevice(_PING_UNIT, int(float(value[num])), value[num] + " " + units[num])
                if cmd[num].find(_DOWNLOAD) >= 0:
                    UpdateDevice(_DOWNLOAD_UNIT, int(float(value[num])), value[num] + " " + units[num])
                if cmd[num].find(_UPLOAD) >= 0:
                    UpdateDevice(_UPLOAD_UNIT, int(float(value[num])), value[num] + " " + units[num])
            self.__runAgain = self.__polling * _HEARTBEATS
        else:
            Domoticz.Debug("onHeartbeat called, run again in " + str(self.__runAgain) + " heartbeats.")


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

################################################################################
# Generic helper functions
################################################################################
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
