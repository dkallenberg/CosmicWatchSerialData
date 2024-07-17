# data_read_in.py

import pandas as pd
import re
from datetime import datetime

def read_and_filter_txt():
    with open('primary_data.txt', 'r') as file:
        lines = file.readlines()
    
    # Extract the timestamp from the first line
    timestamp_pattern = r"^Connection established at (\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$"
    timestamp_match = re.match(timestamp_pattern, lines[0])
    timestamp_str = timestamp_match.group(1) if timestamp_match else None
    
    # Convert the timestamp string to a datetime object
    ts = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S') if timestamp_str else None
    ts_ms = ts.timestamp()*1000

    pFileName = 'primary_data.txt'
    sFileName = 'secondary_data.txt'

    # Primary
    dataA = pd.read_csv(pFileName, sep=' ', skiprows=7, names=['Event', 'RunTime', 'ADC','SiPM','DownTime','Temp'])
    dataA['Time_stamp_ms'] = ts_ms + dataA.RunTime
    dataA['Time_stamp'] = pd.to_datetime(dataA['Time_stamp_ms'], unit='ms')
    dataA['Time_stamp2'] = dataA['Time_stamp'].apply(lambda x: x.replace(microsecond=0))
    dataA['Time_stamp3'] = dataA['Time_stamp2'].apply(lambda x: x.replace(second=0))
    
    # Secondary
    dataB = pd.read_csv(sFileName, sep=' ', skiprows=7, names=['Event', 'RunTime', 'ADC','SiPM','DownTime','Temp'])
    dataB['Time_stamp_ms'] = ts_ms + dataB.RunTime
    dataB['Time_stamp'] = pd.to_datetime(dataB['Time_stamp_ms'], unit='ms')
    dataB['Time_stamp2'] = dataB['Time_stamp'].apply(lambda x: x.replace(microsecond=0))
    dataB['Time_stamp3'] = dataB['Time_stamp2'].apply(lambda x: x.replace(second=0))

    

        
    return dataA, dataB, ts
