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
        tap_verification = 0

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

        profile = str(session_data['class'].iloc[0])[:3]
        tap_verification = tap_durations.verify_session(session_data, profile)

        return (classifier_verificaiton, tap_verification)
        """
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
        """

