""" Download a day of data and look at the PPSD for that day of data
"""
from obspy.core import *
import obspy.clients.fdsn as fdsn
import obspy.clients.iris as iris
from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx
import sys
import os
import logging

logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)

# Should use command line arguments to enter these
stations=[
'ASBU',
'CIHL',
'CPCO',
'CLCV',
'CLMS',
'CLBH',
'CRST',
'CLWZ',
'HUSB',
'HIYU',
'JRO',
'KWBU',
'NORM',
'PRLK',
'SWNB',
'TMBU',
'SWF2',
'SHRK',
'WIFE',
'TCBU',
'STD',
'VALT',
'SVIC',
'STAR',
'SUG',
'SEP',
'OSBR',
'PANH',
'PALM',
'TIMB',
'SR41'
]
network='CC'
if len(sys.argv)>1:
  day=UTCDateTime(sys.argv[1])
else:
  day=UTCDateTime('2016-150T00:00:00.0')
secperday=24*60*60.
datadir="data/"
respdir="resp/"
qcfigs="qcfigs/"
def respfilename(seedid):
  return "%sRESP.%s" % (respdir,ch)
  
def path_verify(path):
  head,tail=os.path.split(path)
  try:
    os.makedirs(head)
  except:
    pass
  return path

client=fdsn.Client("IRIS")

for station in stations:
	filename="%s%d/%03d/%s.%s.seed" % (datadir,day.year,day.julday,network,station)
	path_verify(filename)
	if os.path.exists(filename):
		st=read(filename)
	else:
		try:
			st=client.get_waveforms(network,station,"*","*",day,day+secperday)
			#Save data to selected location here
			st.write(filename,format='MSEED',reclen=512)
		except:
			print("Unable to download data for %s %s" %(station,str(day)))
	# Get all of our channel ids
	ids=[]
	for tr in st:
	 ids.append(tr.id)
	ids=set(ids)
	# Make sure our resp files are up to date
	irisclient=iris.Client()
	for ch in ids:
		n,s,loc,chan=ch.split('.')
		try:
			resp=irisclient.resp(network,station,location=loc,channel=chan,starttime=UTCDateTime('2004-001T00:00:00.0'),endtime=day+secperday,filename=respfilename(ch))
			resp=irisclient.evalresp(network,station,loc,chan,filename="%s%s.png" % (qcfigs,ch),output='plot')
		except:
			print("No response data for channel %s" % (ch))
	data={}
	for ch in ids:
		print(respfilename(ch))
		stch=st.select(id=ch) # Just take the data for a single channel
		try:
			ppsd=PPSD(stch[0].stats,metadata=str(respfilename(ch)))
			ppsd.add(stch)
			figname="%s%d/%03d/%s.png" % (qcfigs,day.year,day.julday,ch)
			path_verify(figname)
			ppsd.plot(figname,cmap=pqlx)
			data[ch]=ppsd.get_percentile(percentile=50)
		except:
			print("Error with PPSD for %s check for response" % (ch))
	
	print(data)
    
