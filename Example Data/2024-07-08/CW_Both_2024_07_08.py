# imports some software packages we'll use
import pandas as pd #Pandas lets us name the columns of our data more likea spread sheet.
import numpy as np #Numpy is used by pandas for calculatiions
import matplotlib as mpl #For ploting data
import matplotlib.pyplot as plt #For typing less when poloting data
import math #for other math we might do.
import seaborn as sns
from datetime import datetime, timedelta

yearDT = '2024'
monthDT = '07'
dayDT = '08'
hourDT = '10'
minDT = '16'
secDT = '33'

fileDateTime = yearDT + '-' + monthDT+ '-' + dayDT + '_' + hourDT + '-' + minDT + '-' + secDT

pFileName = fileDateTime + '_primary_data'
ptxtName = 'C:\Users\QuarkNet\Documents\GitHub\CosmicWatchSerialData\Example Data\2424-07-08\' + pFileName + '.txt'
pcsvName = pFileName + '.csv'

sFileName = fileDateTime + '_secondary_data'
stxtName = sFileName + '.txt'
scsvName = sFileName + '.csv'

def add_ms(row):
    row['Time'] = dt + timedelta(milliseconds = row['RunTime'])

# Read the .text file
dfPrimary = pd.read_csv(ptxtName, sep=' ', skiprows=6, names=['Event', 'RunTime', 'ADC','SiPM','DownTime','Temp'])
dfSecondary = pd.read_csv(stxtName, sep=' ', skiprows=6, names=['Event', 'RunTime', 'ADC','SiPM','DownTime','Temp'])

timeFmt = "yyyy-MM-dd' 'HH:mm:ss.SSS"

ts = datetime(int(yearDT),int(monthDT),int(dayDT),int(hourDT),int(minDT),int(secDT),0)
ts_ms = ts.timestamp()*1000

dfPrimary['Time_stamp_ms'] = ts_ms + dfPrimary.RunTime
dfSecondary['Time_stamp_ms'] = ts_ms + dfSecondary.RunTime

dfPrimary['Time_stamp'] = pd.to_datetime(dfPrimary['Time_stamp_ms'], unit='ms')
dfSecondary['Time_stamp'] = pd.to_datetime(dfSecondary['Time_stamp_ms'], unit='ms')

dfPrimary['Time_stamp2'] = dfPrimary['Time_stamp'].apply(lambda x: x.replace(microsecond=0))
dfSecondary['Time_stamp2'] = dfSecondary['Time_stamp'].apply(lambda x: x.replace(microsecond=0))

dfPrimary['Time_stamp3'] = dfPrimary['Time_stamp2'].apply(lambda x: x.replace(second=0))
dfSecondary['Time_stamp3'] = dfSecondary['Time_stamp2'].apply(lambda x: x.replace(second=0))

# Write the .csv file
dfPrimary.to_csv(pcsvName, index=False)
dfSecondary.to_csv(scsvName, index=False)

print(dfPrimary.shape)
print(dfSecondary.shape)
primaryFile = dateTime + '_primary_data.csv'
inline_rc = dict(mpl.rcParams) #Sets Parameters for plots.

timeFmt = "yyyy-MM-dd' 'HH:mm"

# Set A
dfPrimary = pd.read_csv('2024-07-08_10-16-33_primary_data.csv')
dfPrimary['Time_stamp_m'] = dfPrimary['Time_stamp']
lastRowA = dfPrimary.iloc[-1]
print("Primary:")
print(lastRowA)
print(" ")

# Set B
dfSecondary = pd.read_csv('2024-07-08_10-16-33_secondary_data.csv')
lastRowB = dfSecondary.iloc[-1]
print("Secondary:")
print(lastRowB)

dfPrimary['Time_stamp_m'] = dfPrimary['Time_stamp']
# new_datetime = original_datetime.replace(second=0, microsecond=0)

# This makes a histogram of that totally useless calculation above
plt.figure(figsize=(10,5))
plt.hist(dfPrimary.SiPM, bins=50, range=[0,175], log=False)
plt.hist(dfSecondary.SiPM, bins=50, range=[0,175], log=False)
plt.title("mV for Each Event")
plt.xlabel("SiPM [mV]")
plt.ylabel("Events");

#### Set A
dfPrimary['UpTime'] = (dfPrimary.RunTime - dfPrimary.DownTime)
dfPrimary['Time'] = pd.to_timedelta(dfPrimary.UpTime, unit='ms')
dfPrimary['Minute']= (dfPrimary.UpTime/(60000))
dfPrimary.Minute = (dfPrimary.Minute).astype(int)
dfPrimary['Hour']= (dfPrimary.Minute/(60))
dfPrimary['Days']= (dfPrimary.Hour/(24))
dfPrimary['avgRate'] = dfPrimary.Event/(dfPrimary.UpTime/1000)

data1MinP = dfPrimary.drop_duplicates(subset=['Time_stamp3'], keep='first')
data1MinP = data1MinP.loc[:,('Event','RunTime','DownTime','UpTime','Time','Time_stamp','Time_stamp2','Time_stamp3','Minute','Hour','Days','avgRate')]

data1MinP['DeltaCount'] = data1MinP.Event - data1MinP.Event.shift(1)
data1MinP['DeltaUpTime'] = data1MinP.UpTime - data1MinP.UpTime.shift(1)
data1MinP['Rate'] = data1MinP.DeltaCount / (data1MinP.DeltaUpTime /1000)

#### Set B
dfSecondary['UpTime'] = (dfSecondary.RunTime - dfSecondary.DownTime)
dfSecondary['Time'] = pd.to_timedelta(dfSecondary.UpTime, unit='ms')
dfSecondary['Minute']= (dfSecondary.UpTime/(60000))
dfSecondary.Minute = (dfSecondary.Minute).astype(int)
dfSecondary['Hour']= (dfSecondary.Minute/(60))
dfSecondary['Days']= (dfSecondary.Hour/(24))
dfSecondary ['avgRate'] = dfSecondary.Event/(dfSecondary.UpTime/1000)


data1MinS = dfSecondary.drop_duplicates(subset=['Time_stamp3'], keep='first')
data1MinS = data1MinS.loc[:,('Event','RunTime','DownTime','UpTime','Time','Time_stamp','Time_stamp2','Time_stamp3','Minute','Hour','Days','avgRate')]

data1MinS['DeltaCount'] = data1MinS.Event - data1MinS.Event.shift(1)
data1MinS['DeltaUpTime'] = data1MinS.UpTime - data1MinS.UpTime.shift(1)
data1MinS['Rate'] = data1MinS.DeltaCount / (data1MinS.DeltaUpTime /1000)

sigma = 1
data1MinP['RateSmooth'] = data1MinP['Rate'].rolling(50).mean()
data1MinS['RateSmooth'] = data1MinS['Rate'].rolling(50).mean()
"""
# Plot
plt.figure(figsize=(24,6))
plt.plot(data1MinP.Time_stamp3,data1MinP.Rate)
plt.plot(data1MinS.Time_stamp3,data1MinS.Rate)
plt.title("Rate Every 1 Minute")
plt.xlabel("")
plt.ylabel("");

"""

# Create a figure
fig = plt.figure(figsize=(12,12))

# Add the first subplot
ax1 = fig.add_subplot(411)  # 2 rows, 1 column, 1st subplot
ax1.plot(data1MinP.Days,data1MinP.Rate, 'r-')  # 'r-' is a red line
ax1.plot(data1MinP.Days,data1MinP.RateSmooth, 'b-')  # 'b-' is a blue line
ax1.set_title('Primary Rate Every 1 Minute')
ax1.set_xlabel('Time [Day]')
ax1.set_ylabel('Rate [Hz]')

# Add the first subplot
ax2 = fig.add_subplot(412)  # 2 rows, 1 column, 1st subplot
# ax2.plot(data1MinP.Minute,data1MinP.Rate, 'r-')  # 'r-' is a red line
ax2.plot(data1MinP.Days,data1MinP.RateSmooth, 'b-')  # 'b-' is a blue line
ax2.set_title('Primary Rate Every 1 Minute')
ax2.set_xlabel('Time [Day]')
ax2.set_ylabel('Rate [Hz]')

# Add the second subplot
ax3 = fig.add_subplot(413)  # 2 rows, 1 column, 2nd subplot
ax3.plot(data1MinS.Days,data1MinS.Rate, 'r-')  # 'r-' is a red line
ax3.plot(data1MinS.Days,data1MinS.RateSmooth, 'b-')  # 'b-' is a blue line
ax3.set_title('Secondary Rate Every 1 Minute')
ax3.set_xlabel('Time [Day]')
ax3.set_ylabel('Rate [Hz]')

# Add the second subplot
ax4 = fig.add_subplot(414)  # 2 rows, 1 column, 2nd subplot
# ax4.plot(data1MinS.Minute,data1MinS.Rate, 'r-')  # 'r-' is a red line
ax4.plot(data1MinS.Days,data1MinS.RateSmooth, 'b-')  # 'b-' is a blue line
ax4.set_title('Secondary Rate Every 1 Minute')
ax4.set_xlabel('Time [Day]')
ax4.set_ylabel('Rate [Hz]')

# Display the plots
plt.tight_layout()  # Adjusts the layout to prevent overlap
plt.show()