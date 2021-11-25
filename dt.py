# Import keyboard_heatmap module
import keyboard_heatmap
import log_parser
import numpy as np
import pandas as pd
import math

# 10 second time segments
segment_time = 10

# Getting the data from  parsed input keyboard log file
keyboard_data = log_parser.parse_keyboard_log("keyboard_actions_jon_spy_nov8.log")
nsegments = math.trunc(keyboard_data.iloc[-1]['time'] / segment_time)

keyboard_data = log_parser.parse_keyboard_log("keyboard_actions_jon_spy_nov8.log")

segment_list = []

for i in range(1,nsegments):
    keyboard_data_segment = log_parser.get_segment(keyboard_data, i, segment_time)
    segment_list.append(keyboard_heatmap.keyboardHeatmap.parseKeyboardLog(keyboard_data_segment))

print(segment_list)
