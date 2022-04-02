import pickle

from log_parser import parse_keyboard_log
from log_parser import parse_mouse_log
from keyboard_heatmap import KeyboardHeatmap

# This file sucks, dont use it

# List of parsed logfiles
keyboard = []
mouse = []

# Read logfile paths from .routing
with open(".routing", 'r', encoding='utf-8') as f:
    log_paths = f.read().splitlines()   # Read lines without '\n's
    for path in log_paths:
        if 'key.log' in path:
            keyboard.append(parse_keyboard_log(path))
        elif 'mouse.log' in path:
            mouse.append(parse_mouse_log(path))

seg_length = 60

# Empty lists for inserting data
X_actual = []
Y_actual = []

# For confusion matrix plotting
labels = []

target = "NON"

for k in range(len(keyboard)):
    l = None
    for i in range(int(keyboard[k].time.iloc[-1] / seg_length)):
        # For each segment in each logfile
        # Create a heatmap for that segment
        heatmap = KeyboardHeatmap(keyboard[k], i, seg_length)
        if target!='NON': heatmap = heatmap.to_binary_class_label(target)
        # If the heatmap isn't blank
        if heatmap.class_label() != 'Null':
            X_actual.append(heatmap.heatmap_data().ravel().tolist())
            Y_actual.append(heatmap.class_label())
        
        l = heatmap.class_label()
    labels.append(l)
labels = list( dict.fromkeys(labels)) # remove duplicate labels for non-binary classification

ctype = "RF"

with open('classifiers/' + target + '/' + ctype + '.pkl', 'rb') as f:
    classifier = pickle.load(f)  

print(f"RFC Test score: {classifier.score(X_actual, Y_actual)}")

# Plotting
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

print("RF Confusion Matrix:")
y_rf_predict = classifier.predict(X_actual)
ConfusionMatrixDisplay.from_predictions(Y_actual, y_rf_predict, cmap='cividis')
plt.show()

import numpy as np
import matplotlib.pyplot as plt

# We want to plot the feature importance of all features to see how our classifier is splitting data
importances = classifier.feature_importances_
#indices = np.argsort(importances)

# Expand figure vertically
plt.figure(figsize=(7,20))

# Barplot
plt.barh(range(len(importances)), importances)
# Add feature names as y-axis labels
# replace [indices[i] for i in indices] with feature labels
plt.yticks(range(len(importances)), KeyboardHeatmap.heatmap_data_names())
# Create plot title
plt.title("Feature Importance")
# Show plot
plt.show()