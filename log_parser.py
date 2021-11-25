import pandas as pd

"""
Function used to parse keyboard log files
filepath: The name of the logfile
returns: pandas DataFrame
"""
def parse_keyboard_log(filepath):
    return pd.read_csv(filepath, names=['time', 'key', 'action', 'class'])

"""
Function used to parse mouse log files
filepath: The name of the logfile
returns: pandas DataFrame
"""
def parse_mouse_log(filepath):
    return pd.read_csv(filepath, names=['time', 'x', 'y', 'button', 'action', 'class'])

"""
Function used for parsing a specified segment from a log file
parsedFile: The result of a parse_x_log() call
index: The index of the segment
seg_length: The length of the segment (default 60)
returns: pandas DataFrame
*Note* Segment length determines index, i.e. "The 5th 15-second segment"
"""
def get_segment(parsedFile, index, seg_length=60):
    # Calculate first and last second of segment
    last_sec = index * seg_length
    first_sec = last_sec - seg_length

    # Create a mask for the specified time range
    mask = (parsedFile.time >= first_sec) & (parsedFile.time < last_sec)

    # Return slice of dataframe within specified time frame
    return parsedFile[mask]
