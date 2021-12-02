from log_parser import parse_keyboard_log
from log_parser import parse_mouse_log
from keyboard_heatmap import KeyboardHeatmap
from sklearn.ensemble import RandomForestClassifier

class LANDIS_classifier: 
    # class name needs to be considered, this could be our generalized class for all classification methods
    def __init__(self, target, seg_length):
        self.target = target
        routing_file = open('.routing', 'r')
        Lines = routing_file.readlines()

        # List of parsed logfiles
        keyboard = []
        mouse = []

        for line in Lines:
            line = line.strip()
            if 'keyboard_actions.log' in line:
                keyboard.append(parse_keyboard_log(line))
            elif 'mouse_actions.log' in line:
                mouse.append(parse_mouse_log(line))

        X_train = []
        Y_train = []

        for k in range(len(keyboard) - 1):
            for i in range(int(keyboard[k].time.iloc[-1] / seg_length)):
                # For each segment in each logfile
                # Create a heatmap for that segment
                heatmap = KeyboardHeatmap(keyboard[k], i, seg_length)
                heatmap = heatmap.to_binary_class_label(target)
                # If the heatmap isn't blank
                if heatmap.class_label() != 'Null':
                    X_train.append(heatmap.heatmap_data().ravel().tolist())
                    Y_train.append(heatmap.class_label())

        self.rfc = RandomForestClassifier(n_jobs=-1, criterion='gini', max_features= 'sqrt', n_estimators = 100, oob_score = True)
        self.rfc.fit(X_train, Y_train) 
    
    def predict(self, filepath):
        # Currently only uses keyboard file, will eventually have to use mouse
        # filepath as argument is a little convoluted, we are reading csv that is currently being written to
        # getting dataframe from input_logger would be better
        keyboard = parse_keyboard_log(filepath)
        heatmap = KeyboardHeatmap(keyboard, 0, keyboard.time.iloc[-1])
        heatmap = heatmap.to_binary_class_label(self.target)
        if heatmap.class_label() != 'Null':
            return self.rfc.predict(heatmap.heatmap_data())
        else:
            return "---"
