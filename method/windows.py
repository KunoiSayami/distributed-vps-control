# -*- conding: utf-8 -*-
import wmi
import datetime
class windows_method:
	@staticmethod
	def query_start_time() -> str:
		# https://stackoverflow.com/a/36890977
		wmiob = wmi.WMI()
		sdata = wmiob.Win32_PerfFormattedData_PerfOS_System()
		uptime = sdata[-1].SystemUpTime
		utime = datetime.timedelta(seconds=int(uptime))
		return str(utime)