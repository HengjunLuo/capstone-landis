from log_parser import parse_keyboard_log
from log_parser import parse_mouse_log
import tap_durations
import pickle

from keyboard_heatmap import KeyboardHeatmap

class LANDIS_classifier: 
    # class name needs to be considered, this could be our generalized class for all classification methods
    def __init__(self, target, ctype = 'None'):

        self.target = target
        self.classifier_type = ctype
        self.mostRecentPredictions = []
        self.classifier = None

        # Make me a try/catch in the future
        if self.classifier_type == 'None' or self.target == 'None':
            return
        
        with open('classifiers/' + target + '/' + ctype + '.pkl', 'rb') as f:
            self.classifier = pickle.load(f)  

    # Currently only uses keyboard file, will eventually have to use mouse
    def predict(self, session_data, seglength):
        # Verification outputs
        classifier_verificaiton = 0

        # Return if no data for prediction
        if session_data.empty:
            return (0, 0)

        if self.classifier:
            # Isolate inputs from last [seglength] seconds
            last_timestamp = session_data.time.iloc[-1]
            kb_session_seg = session_data[session_data.time > (last_timestamp - seglength)]

            heatmap = KeyboardHeatmap(kb_session_seg, 0, last_timestamp)
            heatmap = heatmap.to_binary_class_label(self.target)

            classifier_verificaiton = self.classifier.predict(heatmap.heatmap_data())[0]

        return (classifier_verificaiton)