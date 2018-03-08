################################################################################
#
# Speedtest Python Plugin
#
# Author: Xorfor
#
################################################################################
"""
<plugin key="xfr_speedtest" name="Speedtest" author="Xorfor" version="1.3.0" wikilink="https://github.com/Xorfor/Domoticz-Speedtest-Plugin">
    <params>
        <param field="Mode1" label="Polling time (minutes)" width="100px" required="true" default="60"/>
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
import subprocess
import os


class BasePlugin:

    _HEARTBEATS2MIN = 6

    # Command
    _COMMAND = "speedtest-cli"
    _OPTIONS = "--simple"
    #
    # Device units
    _UNITS = {
        "PING":         1,
        "DOWNLOAD":     2,
        "UPLOAD":       3,
    }
    #
    # Search strings
    _PING = "Ping"
    _DOWNLOAD = "Download"
    _UPLOAD = "Upload"

    def __init__(self):
        self._runAgain = 0
        self._polling = 0

    def onStart(self):
        Domoticz.Debug("onStart called")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        # Check parameter for heartbeat. Default is 1. Check every 1 minute for the presence of the defined mac addresses
        self._polling = int(Parameters["Mode1"])
        if self._polling < 1:
            self._polling = 1
        #
        # Images
        # Check if images are in database
        if "xfr_speedtest" not in Images:
            Domoticz.Image("xfr_speedtest.zip").Create()
        image = Images["xfr_speedtest"].ID
        Domoticz.Debug("Image created. ID: "+str(image))
        # Create devices
        if (len(Devices) == 0):
            Domoticz.Device(Unit=self._UNITS["PING"], Name=self._PING, TypeName="Custom", Options={"Custom": "1;ms"}, Image=image, Used=1).Create()
            Domoticz.Device(Unit=self._UNITS["DOWNLOAD"], Name=self._DOWNLOAD, TypeName="Custom", Options={"Custom": "1;Mb/s"}, Image=image, Used=1).Create()
            Domoticz.Device(Unit=self._UNITS["UPLOAD"], Name=self._UPLOAD, TypeName="Custom", Options={"Custom": "1;Mb/s"}, Image=image, Used=1).Create()
        # Log config
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
        cmd = {}
        value = {}
        unit = {}
        #
        self._runAgain -= 1
        if self._runAgain <= 0:
            self._runAgain = self._polling * self._HEARTBEATS2MIN
            # Run command
            retList = subprocess.Popen([self._COMMAND, self._OPTIONS], stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip().splitlines()
            num = 0
            for ret in retList:
                cmd[num], value[num], unit[num] = ret.split(" ")
                num += 1
            #
            for num in range(len(cmd)):
                Domoticz.Debug(
                    "num: " + str(num) + " - cmd: " + cmd[num] + " - value: " + value[num] + " - units: " + unit[num])
                if cmd[num].find(self._PING) >= 0:
                    UpdateDevice(self._UNITS["PING"], int(float(value[num])), str(round(float(value[num]), 2)) + " " + unit[num])
                if cmd[num].find(self._DOWNLOAD) >= 0:
                    UpdateDevice(self._UNITS["DOWNLOAD"], int(float(value[num])), value[num] + " " + unit[num])
                if cmd[num].find(self._UPLOAD) >= 0:
                    UpdateDevice(self._UNITS["UPLOAD"], int(float(value[num])), value[num] + " " + unit[num])
        else:
            Domoticz.Debug("onHeartbeat called, run again in " + str(self._runAgain) + " heartbeats.")

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
        Domoticz.Debug("Unit...........: " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Idx............: " + str(Devices[x].ID))
        Domoticz.Debug("Name...........: " + Devices[x].Name)
        Domoticz.Debug("Type...........: " + str(Devices[x].Type) + " / " + str(Devices[x].SubType) )
        Domoticz.Debug("nValue.........: " + str(Devices[x].nValue))
        Domoticz.Debug("sValue.........: " + Devices[x].sValue)
        Domoticz.Debug("LastLevel......: " + str(Devices[x].LastLevel))
    for x in Settings:
        Domoticz.Debug("Setting........: " + str(x) + " - " + str(Settings[x]))

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "' - " + str(TimedOut))

def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details ("+str(len(httpDict))+"):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("....'"+x+" ("+str(len(httpDict[x]))+"):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")
