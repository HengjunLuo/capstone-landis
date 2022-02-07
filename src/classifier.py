from log_parser import parse_keyboard_log
from log_parser import parse_mouse_log
from keyboard_heatmap import KeyboardHeatmap
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor

class LANDIS_classifier: 
    # class name needs to be considered, this could be our generalized class for all classification methods
    def __init__(self, ct, target, seg_length):

        self.target = target
        self.classifier_type = ct
        self.mostRecentPredictions = []

        # List of parsed logfiles
        keyboard = []
        mouse = []

        # Read logfile paths from .routing
        log_paths = None
        with open("../.routing", 'r', encoding='utf-8') as f:
            log_paths = f.read().splitlines()   # Read lines without '\n's

        # Append each parsed log file to the appropriate list
        for log_path in log_paths: 
            if 'key.log' in log_path:
                keyboard.append(parse_keyboard_log(log_path))
            elif 'mouse.log' in log_path:
                mouse.append(parse_mouse_log(log_path))

        X_train = []  # List of segment heatmaps used for training
        y_train = []  # List of true or false labels based on current target

        # k = index of parsed kb file (0-indexed)
        for k, kb_parsed in enumerate(keyboard):
            # Get number of seg_length length segments from parsed log
            seg_count = int(kb_parsed.time.iloc[-1] / seg_length)
            # For each segment in the parsed log
            for i in range(seg_count):  # i = segment index
                # Create a heatmap for the segment
                heatmap = KeyboardHeatmap(kb_parsed, i, seg_length)
                # Convert labels to 'true' or 'false' (0 or 1) based on target
                heatmap = heatmap.to_binary_class_label(self.target)
                # If the heatmap isn't blank
                if heatmap.class_label() != 'Null':
                    # Append segment to training data
                    X_train.append(heatmap.heatmap_data().ravel().tolist())
                    y_train.append(heatmap.class_label())
        
        if ct == "RF":
            self.classifier = RandomForestClassifier(
                n_jobs=-1, 
                criterion='gini',
                max_features= 'sqrt',
                n_estimators = 100, 
                oob_score = True)
        #elif ct == "KNN":
        # implement KNN classifier here
        else :
            self.classifier = MLPClassifier(
                hidden_layer_sizes=(100,100), 
                activation='relu', 
                solver='adam', 
                max_iter=10000)
        
        self.classifier.fit(X_train, y_train)
    
    def predict(self, filepath):
        # Currently only uses keyboard file, will eventually have to use mouse
        # filepath as argument is a little convoluted, we are reading csv that is currently being written to
        # getting dataframe from input_logger would be better
        keyboard = parse_keyboard_log(filepath + "key.log")
        if keyboard.empty:
            return "---"
        file = open(filepath + "key.log","r+")
        file. truncate(0)
        heatmap = KeyboardHeatmap(keyboard, 0, keyboard.time.iloc[-1])
        heatmap = heatmap.to_binary_class_label(self.target)
        if heatmap.class_label() != 'Null':
            if len(self.mostRecentPredictions) < 2: 
                self.mostRecentPredictions.append(int(self.classifier.predict(heatmap.heatmap_data())[0]))
                #return self.mostRecentPredictions[-1]# return the most recent prediction
                return self.mostRecentPredictions
            elif len(self.mostRecentPredictions) == 2:
                # now we have 3 predictions, now vote!
                self.mostRecentPredictions.append(int(self.classifier.predict(heatmap.heatmap_data())[0]))
                '''if sum(self.mostRecentPredictions) > 1:
                    return 1
                else:
                    return 0'''
                return self.mostRecentPredictions
            elif len(self.mostRecentPredictions) == 3:
                
                # now we have 4 predictions, but we only use the most recent 3 predictions to vote
                self.mostRecentPredictions.append(int(self.classifier.predict(heatmap.heatmap_data())[0]))
                '''if sum(self.mostRecentPredictions[-3]) > 1:
                    return 1
                else:
                    return 0'''
                return self.mostRecentPredictions
            elif len(self.mostRecentPredictions) == 4:
                # now we have 5 predictions, vote!
                self.mostRecentPredictions.append(int(self.classifier.predict(heatmap.heatmap_data())[0]))
                '''if sum(self.mostRecentPredictions) > 2:
                    return 1
                else:
                    return 0'''
                return self.mostRecentPredictions
            elif len(self.mostRecentPredictions) == 5:
                # pop the oldest prediction and then add a new one to keep the prediction list size as 5
                self.mostRecentPredictions.pop(0)
                self.mostRecentPredictions.append(int(self.classifier.predict(heatmap.heatmap_data())[0]))
                '''if sum(self.mostRecentPredictions) > 2:
                    return 1
                else:
                    return 0'''
                return self.mostRecentPredictions
        else:
            return "---"
