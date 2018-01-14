# Speedtest
This plugin will check the speed of the Domoticz network.
## Prerequisite
This plugin uses `speedtest-cli` to check the speed in the Domoticz network. To install it, eg. on Raspberry Pi:
```bash
sudo apt-get install speedtest-cli -y
```
## Parameters
- **Interval in minutes**: Interval to check the network speed. Default **`60`** minutes.
## Remarks
- When running on Raspberry Pi, just note that the maximum speed is limited by its 100 Mbit/s LAN adapter.
- Frequent updates should be avoided.
- While running, network usage is fully utilized. This may have a negative effect on other devices on the network such as gaming consoles or streaming boxes.
