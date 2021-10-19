class KeyLog:
    def __init__(self):
        # initializer function
        # think of self as 'this' in c++ 
        self.time    = []
        self.action  = []
        self.key     = []
        self.numLogs = 0
    def addLog(self, time, action, key):
        # add a single log to our table
        # arrays are not initialized, so we use append function
        self.time  .append(time)
        self.action.append(action)
        self.key   .append(key)
        ++self.numLogs
    def getNumLogs():
        # return number of logs the table stores
        return numLogs
    # add various class functions, like retrieve number of 'a' inputs, or time between two logs

# open the logfile that we have generated with input_logger.py
with open('keyboard_actions.log') as KeyLogFile: 
    lines = KeyLogFile.readlines() # list containing lines of file
    myKeyLog = KeyLog()
    for line in lines: # nonsensical python magic, line was never initialized but it works in a for loop, dont understand it
        line = line.strip() # remove leading/trailing white spaces
        if line:
            # format for a log is 2021-10-18 17:22:06,829: pressed 't'
            # separating by spaces gives us substrings for date, time, action, key
            # date and time should be condensed into a single variable, need to find a smart way to do this
            subStrings = line.split(' ');
            # remove spaces from substrings
            subStrings = [name.strip() for name in subStrings]
            # separate substrings into their own variables
            # currently time and key are stored as strings, but we will probably want to parse them in a different way
            time   = subStrings[0] + ' ' + subStrings[1]
            # storing the string 'pressed' or 'unpressed' is useless, better to use a boolean
            action = True if subStrings[2] == 'pressed' else False
            key    = subStrings[3]
            myKeyLog.addLog(time, action, key)
    #print some logs to prove it worked
    print(myKeyLog.time[0], myKeyLog.action[0], myKeyLog.key[0])
    print(myKeyLog.time[1], myKeyLog.action[1], myKeyLog.key[1])
    print(myKeyLog.time[2], myKeyLog.action[2], myKeyLog.key[2])