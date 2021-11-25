import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class keyboardHeatmap:
    maxFreq = 0.0
    maxDura = 0.0
    def __init__(self, dataframe):
        self.keyboard_df = keyboardHeatmap.parseKeyboardLog(dataframe)
        # The 49 default key bindings for team fortress 2
        self.keyBindings = ["w","a","s","d","Key.space","Key.ctrl_l","'","/","Key.up","Key.down",
                    "v","y","u","z","x","c",",",".","m","n","Key.f2","Key.f3","l","g",
                    "h","i","f","b","-","r","q","1","2","3","4","5","6","7","8","9","0",
                    "t","Key.tab","Key.f5","Key.f6","Key.f7","`","j","k"]
        keyFreqDict ={}
        keyDuraDict = {}

        for key in self.keyBindings:
            keyFreqDict[key] = 0
            keyDuraDict[key] = 0
        theKeyboardDict = self.keyboard_df.to_dict('records')
        for item in theKeyboardDict:
            keyFreqDict[item['key']] = item['freq']
            keyDuraDict[item['key']] = item['avg_duration']
        self.keyFreqList = []
        self.keyDuraList = []
        for item in self.keyBindings:
            if item in keyFreqDict:
                self.keyFreqList.append(float(keyFreqDict[item]))
            else:
                self.keyFreqList.append(0)
            if item in keyDuraDict:
                self.keyDuraList.append(float(keyDuraDict[item]))
            else:
                self.keyDuraList.append(0)
        self.arrFreq = np.array([self.keyFreqList])
        self.arrDura = np.array([self.keyDuraList])

    @staticmethod
    def show_heatmap(heatmap):
        # Setting up the heatmap
        fig, axes = plt.subplots( nrows=2)
        ax1,ax2 = axes
        im1 = ax1.imshow(heatmap.arrFreq, cmap='cividis', vmax=keyboardHeatmap.maxFreq)
        im2 = ax2.imshow(heatmap.arrDura, cmap='cividis', vmax=keyboardHeatmap.maxDura)

        
        plt.subplots_adjust(top=0.1, bottom=0)


        ax1.set_xticks(np.arange(len(heatmap.keyBindings)))
        ax1.set_yticks(np.arange(len(['Frequency'])))
        ax2.set_xticks(np.arange(len(heatmap.keyBindings)))
        ax2.set_yticks(np.arange(len(['Average Duraion'])))

        ax1.set_xticklabels(heatmap.keyBindings)
        ax1.set_yticklabels(['Frequency'])
        ax2.set_xticklabels(heatmap.keyBindings)
        ax2.set_yticklabels(['Average Duraion'])
        # Rotate the tick labels and set their alignment.
        plt.setp(ax1.get_xticklabels(), rotation=20, ha="right")
        plt.setp(ax2.get_xticklabels(), rotation=20, ha="right")
        for i in range(len(heatmap.keyBindings)):
            text = ax1.text(i,0, heatmap.keyFreqList[i], ha='center')
            text = ax2.text(i,0, heatmap.keyDuraList[i], ha='center')
        ax1.set_title("Frequency")
        ax2.set_title("Average Duration")
        fig.set_size_inches(40,30)
        fig.suptitle("Frequency and average duartion pressed for keys", fontsize=16, ha='center', va='top', x=0.5, y= 0.12)
        fig.tight_layout

        # Show heatmaps for frequency and average duartion pressed for keys
        plt.show()


    @staticmethod
    def parseKeyboardLog(dataframe):
        # The 49 default key bindings for team fortress 2
        keyBindings = ["w","a","s","d","Key.space","Key.ctrl_l","'","/","Key.up","Key.down",
                    "v","y","u","z","x","c",",",".","m","n","Key.f2","Key.f3","l","g",
                    "h","i","f","b","-","r","q","1","2","3","4","5","6","7","8","9","0",
                    "t","Key.tab","Key.f5","Key.f6","Key.f7","`","j","k"]
        resultDict = {} # containing 'key':[last press time, last action, total duration, freq]

        #Calculate duration and freq for each key between startMin and endMin
        for index, row in dataframe.iterrows():
            key = row['key'][1]
            if key in keyBindings:
                time = float(row['time'])
                action = row['action']
                if key in resultDict:
                    if resultDict[key][1] == "pressed":
                        if action == "released":
                            newDura = time - resultDict[key][0]
                            resultDict[key][2] += newDura
                            resultDict[key][1] = action
                            resultDict[key][3] += 1
                    else:
                            if action == "pressed":
                                resultDict[key][0] = time
                                resultDict[key][1] = action
                else:
                    if action == "pressed":
                        resultDict[key] = [time,action,0,0]
        

        #Calculating the actual segment duration in seconds by subtracting the time of first key press from the time of last key release
        firstPress = dataframe.query('action.eq("pressed")').index.min()
        startTime = float(dataframe.iloc[firstPress]['time'])
        lastRelease = dataframe.query('action.eq("released")').index.max()
        endTime = float(dataframe.iloc[lastRelease]['time'])
        segDuration = endTime - startTime

        #Write result to output file

        resultList = []
        for key in resultDict:
            totalDura = resultDict[key][2]
            freq = 60 * resultDict[key][3]/segDuration
            avgDura = totalDura/resultDict[key][3]
            sublist =[key, str("{:.3f}".format(avgDura)), str("{:.3f}".format(freq)), "NaN"]
            resultList.append(sublist)

        return pd.DataFrame(resultList, columns = ['key', 'avg_duration', 'freq', 'class'])