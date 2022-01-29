from log_parser import parse_keyboard_log
from log_parser import parse_mouse_log
from keyboard_heatmap import KeyboardHeatmap
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import VotingClassifier

routing_file = open('../.routing', 'r')
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

# Split into train and test sets
X_train = []
X_test = []
Y_train = []
Y_test = []
# 30 second segments fuggetaboutit
train_seg_length = 30
test_seg_length = 30
# The quintessential target class
target = "HENSOL"

for k in range(len(keyboard) - 1):
    for i in range(int(keyboard[k].time.iloc[-1] / train_seg_length)):
        # For each segment in each logfile
        # Create a heatmap for that segment
        heatmap = KeyboardHeatmap(keyboard[k], i, train_seg_length)
        heatmap = heatmap.to_binary_class_label(target)
        # If the heatmap isn't blank
        if heatmap.class_label() != 'Null':
            X_train.append(heatmap.heatmap_data().ravel().tolist())
            Y_train.append(heatmap.class_label())

for k in range(len(keyboard) - 1,len(keyboard)):
    for i in range(int(keyboard[k].time.iloc[-1] / test_seg_length)):
        # For each segment in each logfile
        # Create a heatmap for that segment
        heatmap = KeyboardHeatmap(keyboard[k], i, test_seg_length)
        heatmap = heatmap.to_binary_class_label(target)
        # If the heatmap isn't blank
        if heatmap.class_label() != 'Null':
            X_test.append(heatmap.heatmap_data().ravel().tolist())
            Y_test.append(heatmap.class_label())

# ensemble of models
estimator = []
estimator.append(('RF', RandomForestClassifier(
    n_jobs=-1, 
    criterion='gini',
    max_features= 'sqrt',
    n_estimators = 100, 
    oob_score = True)))
estimator.append(('MLP', MLPClassifier(
    hidden_layer_sizes=(100,100), 
    activation='relu', 
    solver='adam', 
    max_iter=10000)))
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

mlp = MLPClassifier(hidden_layer_sizes=(100,100), activation='relu', solver='adam', max_iter=10000)
mlp.fit(X_train, Y_train)
print( f"MLP Train score: {mlp.score(X_train, Y_train)} " + f"MLP Test score: {mlp.score(X_test, Y_test)}")

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, Y_train)
print( f"KNN Train score: {knn.score(X_train, Y_train)} " + f"KNN Test score: {knn.score(X_test, Y_test)}")