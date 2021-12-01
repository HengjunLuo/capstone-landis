import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from log_parser import extract_keyboard_features
from log_parser import extract_mouse_clicks

"""
KeyboardHeatmap class takes a segment from a parsed file generated from a 
keyboard_actions log file and provides methods to display it as a heatmap 
showing each keys frequency and duration during the specified segment
"""
class KeyboardHeatmap:

    # Class attribute
    # The 49 default key bindings for team fortress 2
     # The 49 default key bindings for team fortress 2
    keyBindings = ["w","a","s","d",
                "Key.space",
                "Key.ctrl_l",
                "Key.comma",".",
                "q", "v", "b", "r",
                "1","2","3","4","5","6","7","8","9","0",
                "Key.tab"]

    """
    Construct the heatmap object by passing it a pandas dataframe
    The dataframe must be generated from a keyboard_actions log file
    index: The index of the segment
    seg_length: The length of the segment (default 60)
    """
    def __init__(self, dataframe, index, seg_length=60):
        
        # Extract frequency and duration data from segment
        self.keyboard_df = extract_keyboard_features(dataframe, index, seg_length)
        self.class_label_ = "Null"
        # Check that data is not empty
        if len(self.keyboard_df.index) > 0:
            # Infer class_label from first line of data
            self.class_label_ = self.keyboard_df['class'].iloc[0]

        # Set key column to index (unique values)
        self.keyboard_df.set_index('key', inplace=True)

        # Create np arrays initialized with 0s the same shape as the keybindings list
        self.arrFreq = np.zeros_like(KeyboardHeatmap.keyBindings, dtype=float)
        self.arrDura = np.zeros_like(KeyboardHeatmap.keyBindings, dtype=float)

        # For each entry in the DataFrame, insert data into arrays
        for key in KeyboardHeatmap.keyBindings:
            if key in self.keyboard_df.index:
                self.arrFreq[KeyboardHeatmap.keyBindings.index(key)] = self.keyboard_df.freq[key]
                self.arrDura[KeyboardHeatmap.keyBindings.index(key)] = self.keyboard_df.avg_duration[key]


    """
    Display the heatmap of specified segment
    """
    def show_heatmap(self):

        a1 = self.arrFreq.reshape((1, 23))
        a2 = self.arrDura.reshape((1, 23))
        a3 = np.append(a1, a2, axis=1)

        plt.figure(figsize=(8, 4))
        plt.imshow(a3, cmap='cividis')
        plt.tick_params(which='both', bottom=False, labelbottom=False, left=False, labelleft=False)
        plt.show()

    """
    Return the heatmap as a numpy array for feature input
    """
    def heatmap_data(self):
        a1 = self.arrFreq.reshape((1, 23))
        a2 = self.arrDura.reshape((1, 23))
        return np.append(a1, a2, axis=1)

    """
    Return the heatmap data as column names in ravel()ed heatmap order
    """
    @staticmethod
    def heatmap_data_names():
        frequency_names = np.array([key+'_frequency' for key in KeyboardHeatmap.keyBindings])
        duration_names = np.array([key+'_duration' for key in KeyboardHeatmap.keyBindings])
        a1 = frequency_names.reshape((1, 23))
        a2 = duration_names.reshape((1, 23))
        return np.append(a1, a2, axis=1).ravel()
    
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
        fig, axes = plt.subplots( nrows=2)
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
            ax1.text(i, 0, self.arrFreq[i], ha='center')
            ax2.text(i, 0, self.arrDura[i], ha='center')
            
        ax1.set_title("Frequency")
        ax2.set_title("Average Duration")
        fig.set_size_inches(40,30)
        fig.suptitle("Frequency and average duartion pressed for keys", fontsize=16, ha='center', va='top', x=0.5, y= 0.12)
        fig.tight_layout

        # Show heatmaps for frequency and average duartion pressed for keys
        plt.show()