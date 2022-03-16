import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from log_parser import extract_keyboard_features
from log_parser import extract_mouse_clicks
from log_parser import extract_predefined_patterns


"""
KeyboardHeatmap class takes a segment from a parsed file generated from a 
keyboard_actions log file and provides methods to display it as a heatmap 
showing each keys frequency and duration during the specified segment
"""
class KeyboardHeatmap:
    # Class attribute
    # The 23 default key bindings for team fortress 2 + mouse buttons = 25 in total
    keyBindings = ["w","a","s","d",
                "Key.space",
                "Key.ctrl_l",
                "Key.comma",".",
                "q", "v", "b", "r",
                "1","2","3","4","5","6","7","8","9","0",
                "Key.tab",
                "Mouse.left","Mouse.right"]
    predefined_patterns = {'w':['s','q','1'], 's':['w'], 'd':['f'], 'f':['d'], 'q':['a','w'], 'a':['q','Key.tab'], '1':['w'],'Key.tab':['a']}
    flightTimePatterns = ["middle_finger", "index_finger","ring_finger"]
    # item in predefined_patterns:
    #    for subItem in predefined_patterns[item]:
    #        combineKey = item + subItem
    #        flightTimePatterns.append(combineKey)

    """
    Construct the heatmap object by passing it a pandas dataframe
    The dataframe must be generated from a keyboard_actions log file
    index: The index of the segment
    seg_length: The length of the segment (default 60)
    """
    def __init__(self, dataframe, index = -1, seg_length=60):
        
        # Extract frequency and duration data from segment
        self.keyboard_df = extract_keyboard_features(dataframe, index, seg_length)
        self.flightTime_df = extract_predefined_patterns(dataframe, index, seg_length)
        self.class_label_ = "Null"
        # Check that data is not empty
        if len(self.keyboard_df.index) > 0:
            # Infer class_label from first line of data
            self.class_label_ = self.keyboard_df['class'].iloc[0]
            self.class_label_ = self.class_label_[:3]#Only use player label

        # Set key column to index (unique values)
        self.keyboard_df.set_index('key', inplace=True)
        self.flightTime_df.set_index('key', inplace=True)

        # Create np arrays initialized with 0s the same shape as the keybindings list
        self.arrFreq = np.zeros_like(KeyboardHeatmap.keyBindings, dtype=float)
        self.arrDura = np.zeros_like(KeyboardHeatmap.keyBindings, dtype=float)
        self.flightAvgDura = np.zeros_like(KeyboardHeatmap.flightTimePatterns, dtype=float)
        self.flightShortestDura = np.zeros_like(KeyboardHeatmap.flightTimePatterns, dtype=float)
        self.flightLongestDura = np.zeros_like(KeyboardHeatmap.flightTimePatterns, dtype=float)

        # For each entry in the DataFrame, insert data into arrays
        for key in KeyboardHeatmap.keyBindings:
            if key in self.keyboard_df.index:
                self.arrFreq[KeyboardHeatmap.keyBindings.index(key)] = self.keyboard_df.freq[key]
                self.arrDura[KeyboardHeatmap.keyBindings.index(key)] = self.keyboard_df.avg_duration[key]

        for key in KeyboardHeatmap.flightTimePatterns:
            if key in self.flightTime_df.index:
                self.flightAvgDura[KeyboardHeatmap.flightTimePatterns.index(key)] = self.flightTime_df.avg_duration[key]
                self.flightShortestDura[KeyboardHeatmap.flightTimePatterns.index(key)] = self.flightTime_df.shortestDuration[key]
                self.flightLongestDura[KeyboardHeatmap.flightTimePatterns.index(key)] = self.flightTime_df.longestDuration[key]
                
    """
    Display the heatmap of specified segment
    """
    def show_heatmap(self):

        a1 = self.arrFreq.reshape((1, 51))
        a2 = self.arrDura.reshape((1, 51))
        a3 = np.append(a1, a2, axis=1)

        plt.figure(figsize=(8, 4))
        plt.imshow(a3, cmap='cividis')
        plt.tick_params(which='both', bottom=False, labelbottom=False, left=False, labelleft=False)
        plt.show()
    
    def heatmap_data(self):
        a1 = self.arrFreq.reshape((1, len(self.keyBindings)))
        a2 = self.arrDura.reshape((1, len(self.keyBindings)))
        a3 = self.flightAvgDura.reshape((1,len(self.flightTimePatterns)))
        a4 = self.flightShortestDura.reshape((1,len(self.flightTimePatterns)))
        a5 = self.flightLongestDura.reshape((1,len(self.flightTimePatterns)))

        result = np.append(a1, a2, axis=1)
        result = np.append(result, a3, axis=1)
        result = np.append(result, a4, axis=1)
        result = np.append(result, a5, axis=1)
        return result

    """
    Return the heatmap as a numpy array for feature input
    """
    @staticmethod
    def heatmap_data_gui(df, index = -1, seg_length=60):
        # Extract frequency and duration data from segment
        keyboard_df = extract_keyboard_features(df, index, seg_length)

        # Set key column to index (unique values)
        keyboard_df.set_index('key', inplace=True)

        # Create np arrays initialized with 0s the same shape as the keybindings list
        arrFreq = np.zeros_like(KeyboardHeatmap.keyBindings, dtype=float)
        arrDura = np.zeros_like(KeyboardHeatmap.keyBindings, dtype=float)

        for key in KeyboardHeatmap.keyBindings:
            if key in keyboard_df.index:
                arrFreq[KeyboardHeatmap.keyBindings.index(key)] = keyboard_df.freq[key]
                arrDura[KeyboardHeatmap.keyBindings.index(key)] = keyboard_df.avg_duration[key]

        return np.reshape(np.append(arrFreq, arrDura, axis=-1), [2,25])

    """
    Return the heatmap data as column names in ravel()ed heatmap order
    """
    @staticmethod
    def heatmap_data_names():
        frequency_names = np.array([key+'_frequency' for key in KeyboardHeatmap.keyBindings])
        duration_names = np.array([key+'_duration' for key in KeyboardHeatmap.keyBindings])
        flight_time_avg_names = np.array([key+'_avg_duration' for key in KeyboardHeatmap.flightTimePatterns])
        flight_time_shortest_names = np.array([key+'_shortest_duration' for key in KeyboardHeatmap.flightTimePatterns])
        flight_time_longest_names = np.array([key+'_longest_duration' for key in KeyboardHeatmap.flightTimePatterns])
        a1 = frequency_names.reshape((1, len(KeyboardHeatmap.keyBindings)))
        a2 = duration_names.reshape((1, len(KeyboardHeatmap.keyBindings)))
        a3 = flight_time_avg_names.reshape((1,len(KeyboardHeatmap.flightTimePatterns)))
        a4 = flight_time_shortest_names.reshape((1,len(KeyboardHeatmap.flightTimePatterns)))
        a5 = flight_time_longest_names.reshape((1,len(KeyboardHeatmap.flightTimePatterns)))
        result = np.append(a1, a2, axis=1)
        result = np.append(result, a3, axis=1)
        result = np.append(result, a4, axis=1)
         
        return np.append(result, a5, axis=1).ravel()
    
    """
    Return the class that the heatmap data belongs to
    """
    def class_label(self):
        return self.class_label_

    def to_binary_class_label(self,target="Null"):
        newHeatmap = self
        if self.class_label_ == target:
            newHeatmap.class_label_ = 1
        else:
            newHeatmap.class_label_ = 0
        return newHeatmap
    """
    Display the data as an infographic
    """
    def show_infographic(self):
        # Setting up the heatmaps
        fig, axes = plt.subplots(nrows=2)
        ax1,ax2 = axes
        plt.subplots_adjust(top=0.1, bottom=0)
        
        # Show heatmaps
        ax1.imshow([self.arrFreq], cmap='cividis')
        ax2.imshow([self.arrDura], cmap='cividis')

        # Set ticks and labels
        ax1.set_xticks(np.arange(len(KeyboardHeatmap.keyBindings)))
        ax1.set_xticklabels(KeyboardHeatmap.keyBindings)
        ax1.set_yticks(np.arange(len(['Frequency'])))
        ax1.set_yticklabels(['Frequency'])

        ax2.set_xticks(np.arange(len(KeyboardHeatmap.keyBindings)))
        ax2.set_xticklabels(KeyboardHeatmap.keyBindings)
        ax2.set_yticks(np.arange(len(['Average Duraion'])))
        ax2.set_yticklabels(['Average Duraion'])
        
        # Rotate the tick labels and set their alignment.
        plt.setp(ax1.get_xticklabels(), rotation=-30, ha="right")
        plt.setp(ax2.get_xticklabels(), rotation=-30, ha="right")

        for i in range(len(KeyboardHeatmap.keyBindings)):
            ax1.text(i, 0, f"{self.arrFreq[i]:.2f}", ha='center')
            ax2.text(i, 0, f"{self.arrDura[i]:.2f}", ha='center')
            
        ax1.set_title("Frequency")
        ax2.set_title("Average Duration")
        fig.set_size_inches(40,30)
        fig.suptitle("Frequency and average duartion pressed for keys", fontsize=16, ha='center', va='top', x=0.5, y= 0.12)
        fig.tight_layout

        # Show heatmaps for frequency and average duartion pressed for keys
        plt.show()