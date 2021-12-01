import pandas as pd

"""
Basic parsing of keyboard log files

filepath: The path/name of the logfile
returns: Pandas DataFrame
"""
def parse_keyboard_log(filepath):
    return pd.read_csv(filepath, names=['time', 'key', 'action', 'class'])

"""
Basic parsing of mouse log files

filepath: The path/name of the logfile
returns: Pandas DataFrame
"""
def parse_mouse_log(filepath):
    return pd.read_csv(filepath, names=['time', 'x', 'y', 'button', 'action', 'class'])

"""
Parse a specified segment from a log file

parsedFile: The result of a parse_x_log() call
index: The index of the segment
seg_length: The length of the segment (default 60)
returns: Pandas DataFrame

*Note* Segment length determines index, i.e. "The 5th 15-second segment"
"""
def get_segment(parsedFile, index, seg_length=60):
    # Calculate first and last second of segment
    last_sec = (index + 1) * seg_length
    first_sec = last_sec - seg_length

    # Create a mask for the specified time range
    mask = (parsedFile.time >= first_sec) & (parsedFile.time < last_sec)

    # Return slice of dataframe within specified time frame
    return parsedFile[mask]


"""
Extract useful keyboard features from a logfile, such as average keypress 
duration and frequency

parsedFile: The result of a parse_keyboard_log() call
index: The index of the segment
seg_length: The length of the segment (default 60)
returns: Pandas DataFrame

*Note* Segment length determines index, i.e. "The 5th 15-second segment"
"""

 # The 49 default key bindings for team fortress 2
keyBindings = ["w","a","s","d",
                "Key.space",
                "Key.ctrl_l",
                "Key.comma",".",
                "q", "v", "b", "r",
                "1","2","3","4","5","6","7","8","9","0",
                "Key.tab"]

def extract_keyboard_features(parsedFile, index, seg_length=60):

    # Parse the file and get specified segment
    parsedFile = get_segment(parsedFile, index, seg_length)

    resultDict = {} # containing 'key':[last press time, last action, total duration, number of key strokes]

    #Calculate duration and freq for each key between startMin and endMin
    for _, row in parsedFile.iterrows():
        # Extract keyname (remove surrounding '' if needed)
        key = row['key']
        key = key.replace("'", "")

        if key in keyBindings:
            # Get the time of the action
            time = float(row['time'])
            action = row['action']

            if key in resultDict.keys():
                # If this key's last action was 'pressed'
                if resultDict[key][1] == "pressed":
                    if action == "released": # Ensure that this key's current action is 'released'
                        # Record that this key's last action was 'released'
                        resultDict[key][1] = action
                        # Add the duration of this key's press (duration = now - time of last press)
                        resultDict[key][2] += time - resultDict[key][0]
                        # Increment total number of keypresses for this key
                        resultDict[key][3] += 1

                else: # If last action was not 'pressed'
                    if action == "pressed": # Ensure that this action is 'pressed'
                        # Record time of this key press
                        resultDict[key][0] = time
                        # Record that this key's last action was 'pressed'
                        resultDict[key][1] = action

            else: # If the key hasn't been processed yet, add it to the dictionary
                if action == "pressed": # Only if the key's first action is 'pressed'
                    # Record when the key was pressed and nitialize duration and press count
                    resultDict[key] = [time, action, 0, 0]


    # Default value if log is empty
    classID = "Null"

    if len(parsedFile.index) > 0: # If the dataframe isnt empty
        # Infer class label from first line
        classID = parsedFile.iloc[0]["class"] 

    # Build Pandas DataFrame from results
    resultList = [] # Empty 2D array
    for key, values in resultDict.items():
        avg_duration = values[2] / max(values[3], 1) # Average duration = total duration / # key presses
        freq = values[3] / max(seg_length, 1) # Frequency = # key presses / segment length

        # Format the entry in the DataFrame
        sublist =[key, float(avg_duration), float(freq), classID]
        resultList.append(sublist)

    # Return a Pandas DataFrame built from results
    return pd.DataFrame(resultList, columns = ['key', 'avg_duration', 'freq', 'class'])

mouseBindings = ["left", "right"]

def extract_mouse_clicks(parsedFile, index, seg_length=60):

    # Parse the file and get specified segment
    parsedFile = get_segment(parsedFile, index, seg_length)
    # Remove all the mouse movement lines(makes the method 1000 times faster)
    parsedFile = parsedFile[parsedFile.button != "None"]

    resultDict = {} # containing 'key':[last press time, last action, total duration, number of key strokes]

    #Calculate duration and freq for each key between startMin and endMin
    for _, row in parsedFile.iterrows():
        # Extract keyname (remove surrounding '' if needed)
        key = row['button']

        if key in mouseBindings:
            # Get the time of the action
            time = float(row['time'])
            action = row['action']

            if key in resultDict.keys():
                # If this key's last action was 'pressed'
                if resultDict[key][1] == "pressed":
                    if action == "released": # Ensure that this key's current action is 'released'
                        # Record that this key's last action was 'released'
                        resultDict[key][1] = action
                        # Add the duration of this key's press (duration = now - time of last press)
                        resultDict[key][2] += time - resultDict[key][0]
                        # Increment total number of keypresses for this key
                        resultDict[key][3] += 1

                else: # If last action was not 'pressed'
                    if action == "pressed": # Ensure that this action is 'pressed'
                        # Record time of this key press
                        resultDict[key][0] = time
                        # Record that this key's last action was 'pressed'
                        resultDict[key][1] = action

            else: # If the key hasn't been processed yet, add it to the dictionary
                if action == "pressed": # Only if the key's first action is 'pressed'
                    # Record when the key was pressed and nitialize duration and press count
                    resultDict[key] = [time, action, 0, 0]


    # Default value if log is empty
    classID = "Null"

    if len(parsedFile.index) > 0: # If the dataframe isnt empty
        # Infer class label from first line
        classID = parsedFile.iloc[0]["class"] 

    # Build Pandas DataFrame from results
    resultList = [] # Empty 2D array
    for key, values in resultDict.items():
        avg_duration = values[2] / max(values[3], 1) # Average duration = total duration / # key presses
        freq = values[3] / max(seg_length, 1) # Frequency = # key presses / segment length

        # Format the entry in the DataFrame
        sublist =[key, float(avg_duration), float(freq), classID]
        resultList.append(sublist)

    # Return a Pandas DataFrame built from results
    return pd.DataFrame(resultList, columns = ['key', 'avg_duration', 'freq', 'class'])