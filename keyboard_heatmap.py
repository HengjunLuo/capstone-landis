import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class KeyboardHeatmap:

    def __init__(self, dataframe):

        # The 49 default key bindings for team fortress 2
        self.keyBindings = ["w","a","s","d","Key.space","Key.ctrl_l","'","/","Key.up","Key.down",
                    "v","y","u","z","x","c",",",".","m","n","Key.f2","Key.f3","l","g",
                    "h","i","f","b","-","r","q","1","2","3","4","5","6","7","8","9","0",
                    "t","Key.tab","Key.f5","Key.f6","Key.f7","`","j","k"]

        # Extract frequency and duration data from segment
        self.keyboard_df = parseKeyboardLog(dataframe)

        # Set key column to index (unique values)
        self.keyboard_df.set_index('key', inplace=True)

        # Create np arrays initialized with 0s the same shape as the keybindings list
        self.arrFreq = np.zeros_like(self.keyBindings, dtype=float)
        self.arrDura = np.zeros_like(self.keyBindings, dtype=float)

        # For each entry in the DataFrame, insert data into arrays
        for key in self.keyBindings:
            if key in self.keyboard_df.index:
                self.arrFreq[self.keyBindings.index(key)] = self.keyboard_df.freq[key]
                self.arrDura[self.keyBindings.index(key)] = self.keyboard_df.avg_duration[key]


    def show_heatmap(self):
        # Setting up the heatmap
        fig, axes = plt.subplots( nrows=2)
        ax1,ax2 = axes
        plt.subplots_adjust(top=0.1, bottom=0)
        
        # Show heatmaps
        ax1.imshow([self.arrFreq], cmap='cividis')
        ax2.imshow([self.arrDura], cmap='cividis')

        # Set ticks and labels
        ax1.set_xticks(np.arange(len(self.keyBindings)))
        ax1.set_xticklabels(self.keyBindings)
        ax1.set_yticks(np.arange(len(['Frequency'])))
        ax1.set_yticklabels(['Frequency'])

        ax2.set_xticks(np.arange(len(self.keyBindings)))
        ax2.set_xticklabels(self.keyBindings)
        ax2.set_yticks(np.arange(len(['Average Duraion'])))
        ax2.set_yticklabels(['Average Duraion'])
        
        # Rotate the tick labels and set their alignment.
        plt.setp(ax1.get_xticklabels(), rotation=-30, ha="right")
        plt.setp(ax2.get_xticklabels(), rotation=-30, ha="right")

        for i in range(len(self.keyBindings)):
            ax1.text(i, 0, self.arrFreq[i], ha='center')
            ax2.text(i, 0, self.arrDura[i], ha='center')
            
        ax1.set_title("Frequency")
        ax2.set_title("Average Duration")
        fig.set_size_inches(40,30)
        fig.suptitle("Frequency and average duartion pressed for keys", fontsize=16, ha='center', va='top', x=0.5, y= 0.12)
        fig.tight_layout

        # Show heatmaps for frequency and average duartion pressed for keys
        plt.show()


def parseKeyboardLog(dataframe):
    # The 49 default key bindings for team fortress 2
    keyBindings = ["w","a","s","d","Key.space","Key.ctrl_l","'","/","Key.up","Key.down",
                "v","y","u","z","x","c",",",".","m","n","Key.f2","Key.f3","l","g",
                "h","i","f","b","-","r","q","1","2","3","4","5","6","7","8","9","0",
                "t","Key.tab","Key.f5","Key.f6","Key.f7","`","j","k"]

    resultDict = {} # containing 'key':[last press time, last action, total duration, number of key strokes]

    #Calculate duration and freq for each key between startMin and endMin
    for _, row in dataframe.iterrows():
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


    # Default values if log is empty
    classID = "NaN"
    seg_length = 0

    if len(dataframe.index) > 0: # If the dataframe isnt empty
        # Calculate segment duration
        seg_length = dataframe.time.max() - dataframe.time.min()
        # Infer class label from first line
        classID = dataframe.iloc[0]["class"] 

    # Build Pandas DataFrame from results
    resultList = [] # Empty 2D array
    for key, values in resultDict.items():
        avg_duration = values[2] / max(values[3], 1) # Average duration = total duration / # key presses
        freq = values[3] / max(seg_length, 1) # Frequency = # key presses / segment length

        # Format the entry in the DataFrame
        sublist =[key, str("{:.3f}".format(avg_duration)), str("{:.3f}".format(freq)), classID]
        resultList.append(sublist)

    # Return a Pandas DataFrame built from results
    return pd.DataFrame(resultList, columns = ['key', 'avg_duration', 'freq', 'class'])


"""
import log_parser

keyboard = log_parser.parse_keyboard_log("logs/joseph/keyboard.log")
keyboard_seg = log_parser.get_segment(keyboard, 1, seg_length=500)

parseKeyboardLog(keyboard_seg)
"""