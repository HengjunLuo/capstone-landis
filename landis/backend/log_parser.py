from cmath import inf
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
def get_segment(parsedFile, index = -1, seg_length=60):
    # Calculate first and last second of segment

    if index == -1: # default means we return all of the data unsegmented
        return parsedFile
    
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
                "Key.tab",
                "Mouse.left","Mouse.right"]


def extract_keyboard_features(parsedFile, index = -1, seg_length=60):

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
        sublist =[key, values[3], float(avg_duration), float(freq), classID]
        resultList.append(sublist)

    # Return a Pandas DataFrame built from results
    return pd.DataFrame(resultList, columns = ['key', 'count', 'avg_duration', 'freq', 'class'])


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

predefined_patterns = {'w':['s','q','1'], 's':['w'], 'd':['f'], 'f':['d'], 'q':['a','w'], 'a':['q','Key.tab'], '1':['w'],'Key.tab':['a']}
# w to s,q,1 belong to the middle finger, d to f belongs to the index inger, a to q belongs to the ring finger.
middleFingerPatterns = ['qw','wq','sw','ws','1w','w1']
indexFingerPatterns = ['df','fd']
ringFingerPatterns = ['aq','qa','aKey.tab','Key.taba']

def extract_predefined_patterns(parsedFile, index = -1, seg_length=60):

    # Parse the file and get specified segment
    parsedFile = get_segment(parsedFile, index, seg_length)

    # Temperory dictionaries used to stire the most recent press or release for keys in the predefined_patterns
    tempPressDict = {}
    tempReleaseDict = {}
    # The result dictionary used to store the average/highest/shortest duration for the key release-press pairs in the predefined_patterns
    # The result should have the following format:  'resultKey':[totalDuration, freq, longestDuration, shortestDuration, averageDuration]
    resultDict = {}
    #Find the key release-press pairs and calculate duration and freq for each pair, and re
    for _, row in parsedFile.iterrows():
        # Extract keyname (remove surrounding '' if needed)
        key = row['key']
        key = key.replace("'", "")

        if key in predefined_patterns:
            # Get the time and the action for this row
            time = float(row['time'])
            action = row['action']

            if action == 'pressed': # if it is the press of a release-press pair
                # Update the time in tempPressDict
                tempPressDict[key] = time
                # Check for the release-press pair
                for pairedKey in predefined_patterns[key]:# check release-press pair for all paired keys for this key
                    if pairedKey in tempReleaseDict:# if we have the data for the required key release 
                        # Validate a release-press pair by 2 metrics: 1. press time < release time. 2. (press time - release time) < 0.3 second
                        if tempReleaseDict[pairedKey] < time and time - tempReleaseDict[pairedKey] <= 0.3:
                            curr_duration = time - tempReleaseDict[pairedKey]# calculate duration for this release-press pair
                            resultKey = key + pairedKey # compute resultKey
                            
                            # Bias remover. Categorize flight time patterns into fingers
                            if resultKey in middleFingerPatterns:
                                resultKey = 'middle_finger'
                            elif resultKey in indexFingerPatterns:
                                resultKey = 'index_finger'
                            elif resultKey in ringFingerPatterns:
                                resultKey = 'ring_finger'

                            if resultKey in resultDict:# if it's not the first record for resultKey
                                # update total duration and freq
                                resultDict[resultKey][0] += curr_duration
                                resultDict[resultKey][1] += 1
                                if resultDict[resultKey][2] < curr_duration:# update longest duration
                                    resultDict[resultKey][2] = curr_duration
                                elif resultDict[resultKey][3] > curr_duration:# update shortest duration
                                    resultDict[resultKey][3] = curr_duration
                            else:# if it is the first record for resultKey
                                resultDict[resultKey] = [curr_duration,1,curr_duration,curr_duration,0]
            else: # if it is the release of a release-press pair
                tempReleaseDict[key] = time # Update the time in tempReleaseDict
    # Calculate the average duration for each pair in the result dictionary
    for pair in resultDict:
        resultDict[pair][4] = resultDict[pair][0]/resultDict[pair][1]
        resultDict[pair] = [resultDict[pair][2],resultDict[pair][3],resultDict[pair][4]]# drop the total duration and freq
    
    # Default value if log is empty
    classID = "Null"

    if len(parsedFile.index) > 0: # If the dataframe isnt empty
        # Infer class label from first line
        classID = parsedFile.iloc[0]["class"] 
    resultList = [] # Empty 2D array
    for key, values in resultDict.items():
        avg_duration = values[2]
        longestDuration = values[0]
        shortestDuration = values[1]

        # Format the entry in the DataFrame
        sublist =[key, float(avg_duration), float(longestDuration),float(shortestDuration), classID]
        resultList.append(sublist)

    # Return a Pandas DataFrame built from results
    return pd.DataFrame(resultList, columns = ['key', 'avg_duration', 'longestDuration', 'shortestDuration', 'class'])

# Define pattern to be counted (currently set to rocket jump pattern)
pattern = ['q', 'q']

# Start of Pattern_recognition function
def pattern_recognition(parsedFile):

    # Put full logfile into variable parsed_File (assuming we are sticking with full logfile rather than live classification, can be changed based on application)
    parsedFile = parse_keyboard_log(parsedFile)

    # Initialize number of patterns counted as 0
    number_of_patterns = 0

    # Initialize list of keys pressed, times they were pressed at, and the overall time the pattern took
    list_of_keys_pressed = list()
    list_of_times = list()
    overall_times = list()

    # For loop to put logfile values into list_of_keys_pressed and list_of_times
    for _, row in parsedFile.iterrows():

        # Get key and action and remove ' if needed
        key = row['key']
        key = key.replace("'", "")
        action = row['action']
        time = row['time']
        
        # Only concerned with keys pressed for current known patterns
        if action == 'pressed':
            
            
            # Append the key pressed and the time it was pressed on this row to the lists
            list_of_keys_pressed.append(key)
            list_of_times.append(time)

    # Start of loop to figure out how many instances of the chosen pattern appear as well as to determine the average time and frequency of each instance of the pattern
    for x in range(len(list_of_keys_pressed)):
        storage = x+1
        # Determining if the xth index in the list_of_keys_pressed is equal to the first element of the pattern
        if list_of_keys_pressed[x] == pattern[0]:

            # storing the time that the first key in the pattern was pressed and storing the current index of list_of_keys_pressed + 1 (since we already checked the
            # 0th index of the pattern)
            initial_time = list_of_times[x]
            
            
            # Start of loop to iterate through each element of the specified pattern (within 1 second) to confirm that it has appeared in the logfile
            for key in range(1, len(pattern)):
                
                # Checking to see if the end of the pattern list has been reached AND if the value at the end of pattern equals the value in list_of_keys_pressed
                if (list_of_keys_pressed[storage] == pattern[key] and key == len(pattern)-1):
                   
                    # Increment the number of patterns seen by 1 and add the time it took to perform the pattern to the overall_times list
                    number_of_patterns += 1
                    overall_times.append(list_of_times[storage] - initial_time)
                    # Set the index to access the list_of_patterns to skip over the indices we have just analyzed
                    x += storage-1
                    
                # Checking to see if the next value in list_of_keys_pressed matches the pattern
                elif (list_of_keys_pressed[storage] == pattern[key]):
                    storage += 1

                # Checking to see if the time elapsed since the first key in the pattern has been pressed is lower than 1 second   
                elif (list_of_times[storage] - initial_time) < 1.0001:
                    # Increment storage to access the next value in list_of_keys_pressed, decrement key so when the for loop increments it the same value is retained
                    storage += 1
                    key -= 1
                
                # If none of the above conditions were met then the pattern has been broken, break and check the next index in the list_of_keys_pressed
                else:
                    break

            
    # Calculation of average time and frequency it takes to perform the pattern, also checking to make sure not to divide by 0
    if len(overall_times) != 0:
        avg_time = sum(overall_times) / len(overall_times)
        avg_freq = 1/avg_time
    else:
        avg_time = avg_freq = 0
    
   
