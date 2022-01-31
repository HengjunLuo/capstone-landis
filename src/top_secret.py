from log_parser import parse_keyboard_log
from log_parser import parse_mouse_log
from keyboard_heatmap import KeyboardHeatmap
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split

routing_file = open('.routing', 'r')
Lines = routing_file.readlines()

# List of parsed logfiles
keyboard = []
mouse = []

for line in Lines:
    line = line.strip()
    if 'key.log' in line:
        keyboard.append(parse_keyboard_log(line))
    elif 'mouse.log' in line:
        mouse.append(parse_mouse_log(line))

# 60 second segments fuggetaboutit
train_seg_length = 60
test_seg_length = 60
# The quintessential target class
target = "MARSOL"

# Empty lists for inserting data
X_actual = []
Y_actual = []

for k in range(len(keyboard)):
    for i in range(int(keyboard[k].time.iloc[-1] / train_seg_length)):
        # For each segment in each logfile
        # Create a heatmap for that segment
        heatmap = KeyboardHeatmap(keyboard[k], i, train_seg_length)
        heatmap = heatmap.to_binary_class_label(target)
        # If the heatmap isn't blank
        if heatmap.class_label() != 'Null':
            X_actual.append(heatmap.heatmap_data().ravel().tolist())
            Y_actual.append(heatmap.class_label())

X_train, X_test, Y_train, Y_test = train_test_split(X_actual, Y_actual, random_state=0)

# ensemble of models
estimator = []
estimator.append(('RF', RandomForestClassifier(
    n_jobs=-1, 
    criterion='gini',
    max_features= 'sqrt',
    n_estimators = 100, 
    oob_score = True)))
estimator.append(('KNN', KNeighborsClassifier(
    n_neighbors=5 # we dont talk about this number
    )))

print("target:" + target)

# Voting Classifier with soft voting
vot_soft = VotingClassifier(estimators = estimator, voting ='soft')
vot_soft.fit(X_train, Y_train)

print( f"Soft Train score: {vot_soft.score(X_train, Y_train)} " + f"Soft Test score: {vot_soft.score(X_test, Y_test)}")

# Voting Classifier with hard voting
vot_hard = VotingClassifier(estimators = estimator, voting ='hard')
vot_hard.fit(X_train, Y_train)

print( f"Hard Train score: {vot_hard.score(X_train, Y_train)} " + f"Hard Test score: {vot_hard.score(X_test, Y_test)}")

rfc = RandomForestClassifier(n_jobs=-1, criterion='gini', max_features= 'sqrt', n_estimators = 100, oob_score = True) 
rfc.fit(X_train, Y_train)
print( f"RFC Train score: {rfc.score(X_train, Y_train)} " + f"RFC Test score: {rfc.score(X_test, Y_test)}")

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, Y_train)
print( f"KNN Train score: {knn.score(X_train, Y_train)} " + f"KNN Test score: {knn.score(X_test, Y_test)}")