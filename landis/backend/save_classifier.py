import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from imblearn.under_sampling import RandomUnderSampler

from log_parser import parse_keyboard_log
from log_parser import parse_mouse_log
from keyboard_heatmap import KeyboardHeatmap

# Set to false to test non-binary classification
test_binary = False

# Set to false for regular sampling
undersampling = True

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

# Ahh yes... the quintessential target class non nonbinary... it'll make sense later
target = "NON"

while(1):
    # Empty lists for inserting data
    X_actual = []
    Y_actual = []

    # For confusion matrix plotting
    labels = []

    for k in range(len(keyboard)):
        l = None
        for i in range(int(keyboard[k].time.iloc[-1] / seg_length)):
            # For each segment in each logfile
            # Create a heatmap for that segment
            heatmap = KeyboardHeatmap(keyboard[k], i, seg_length)
            if test_binary: heatmap = heatmap.to_binary_class_label(target)
            # If the heatmap isn't blank
            if heatmap.class_label() != 'Null':
                X_actual.append(heatmap.heatmap_data().ravel().tolist())
                Y_actual.append(heatmap.class_label())

            l = heatmap.class_label()
        labels.append(l)
    labels = list( dict.fromkeys(labels)) # remove duplicate labels for non-binary classification

    if undersampling:
        # define undersample strategy
        undersample = RandomUnderSampler(sampling_strategy='majority')
        # fit and apply the transform
        X_actual, Y_actual = undersample.fit_resample(X_actual, Y_actual)

    rfc = RandomForestClassifier(n_jobs=-1, criterion='gini', max_features= 'sqrt', n_estimators = 100, oob_score = True) 
    knn = KNeighborsClassifier(n_neighbors=5)
    ann = MLPClassifier(hidden_layer_sizes=(100,100), activation='relu',solver='adam', max_iter=10000)
    nb = GaussianNB()

    # We dont need to test, so use all data available
    rfc.fit(X_actual, Y_actual)
    knn.fit(X_actual, Y_actual)
    ann.fit(X_actual, Y_actual)
    nb.fit(X_actual, Y_actual)

    with open('classifiers/' + target + '/RF.pkl', 'wb') as f:
        pickle.dump(rfc, f)    
    with open('classifiers/' + target + '/KNN.pkl', 'wb') as f:
        pickle.dump(knn, f) 
    with open('classifiers/' + target + '/ANN.pkl', 'wb') as f:
        pickle.dump(ann, f) 
    with open('classifiers/' + target + '/NB.pkl', 'wb') as f:
        pickle.dump(nb, f) 

    if target == 'NON':
        test_binary = True
        target = 'HEN'
    elif target == 'HEN':
        target = 'JON'
    elif target == 'JON':
        target = 'JOS'
    elif target == 'JOS':
        target = 'MAR'
    elif target == 'MAR':
        target = 'MIT'
    elif target == 'MIT':
        target = 'ZIR'
    elif target == 'ZIR':
        break