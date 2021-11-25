import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from log_parser import extract_keyboard_features


"""
KeyboardHeatmap class takes a segment from a parsed file generated from a 
keyboard_actions log file and provides methods to display it as a heatmap 
showing each keys frequency and duration during the specified segment
"""
class KeyboardHeatmap:

    """
    Construct the heatmap object by passing it a pandas dataframe
    The dataframe must be generated from a keyboard_actions log file
    index: The index of the segment
    seg_length: The length of the segment (default 60)
    """
    def __init__(self, dataframe, index, seg_length=60):
        # The 49 default key bindings for team fortress 2
        self.keyBindings = ["w","a","s","d","Key.space","Key.ctrl_l","'","/","Key.up","Key.down",
                    "v","y","u","z","x","c",",",".","m","n","Key.f2","Key.f3","l","g",
                    "h","i","f","b","-","r","q","1","2","3","4","5","6","7","8","9","0",
                    "t","Key.tab","Key.f5","Key.f6","Key.f7","`","j","k"]

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
        self.arrFreq = np.zeros_like(self.keyBindings, dtype=float)
        self.arrDura = np.zeros_like(self.keyBindings, dtype=float)

        # For each entry in the DataFrame, insert data into arrays
        for key in self.keyBindings:
            if key in self.keyboard_df.index:
                self.arrFreq[self.keyBindings.index(key)] = self.keyboard_df.freq[key]
                self.arrDura[self.keyBindings.index(key)] = self.keyboard_df.avg_duration[key]


    """
    Display the heatmap of specified segment
    """
    def show_heatmap(self):

        a1 = self.arrFreq.reshape((7, 7))
        a2 = self.arrDura.reshape((7, 7))
        a3 = np.append(a1, a2, axis=1)

        plt.figure(figsize=(8, 4))
        plt.imshow(a3, cmap='cividis')
        plt.tick_params(which='both', bottom=False, labelbottom=False, left=False, labelleft=False)
        plt.show()

    """
    Return the heatmap as a numpy array for feature input
    """
    def heatmap_data(self):
        a1 = self.arrFreq.reshape((7, 7))
        a2 = self.arrDura.reshape((7, 7))
        return np.append(a1, a2, axis=1)
    
    """
    Return the class that the heatmap data belongs to
    """
    def class_label(self):
        return self.class_label_

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