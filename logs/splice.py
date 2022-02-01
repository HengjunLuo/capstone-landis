import sys
from pathlib import Path

# Default input and output filenames
keylogfile = "key.log"
mouselogfile = "mouse.log"
splicedfile = "key-click.log"

# Handle command line arguments
if len(sys.argv) == 3:
    # Copy filename arguments
    keylogfile = sys.argv[1]
    mouselogfile = sys.argv[2]
    kfile = Path(keylogfile)
    mfile = Path(mouselogfile)

    # Check validity of arguments
    valid = True
    if not kfile.is_file():
        print(f"\"{keylogfile}\" is not a valid keyboard log file")
        valid = False
    if not mfile.is_file():
        print(f"\"{mouselogfile}\" is not a valid mouse log file")
        valid = False
    
    # Exit if an invalid argument was given
    if not valid:
        exit(0)

# Open files
with open(keylogfile,   'r', encoding='utf-8') as keylog,   \
     open(mouselogfile, 'r', encoding='utf-8') as mouselog, \
     open(splicedfile,  'w', encoding='utf-8') as output:
    
    # Read lines into lists
    keylogs   = keylog.readlines()
    mouselogs = mouselog.readlines()
    
    # Initialize iterators
    it_key   = 0
    it_mouse = 0

    # Filter out click actions
    mouselogsstripped = []
    while it_mouse < len(mouselogs):
        line = mouselogs[it_mouse]
        tokens = line.split(',')
        if 'left' in tokens[3] or 'right' in tokens[3]:
            tokens[3] = "Mouse." + tokens[3]
            del tokens[1:3]
            mouselogsstripped.append(','.join(tokens))
        it_mouse += 1
    it_mouse = 0
    mouselogs = mouselogsstripped
    
    # Write lines to output file in order of timestamp
    while it_key < len(keylogs) and it_mouse < len(mouselogs):
        keylogtime = float(keylogs[it_key].split(',', 1)[0])
        mouselogtime = float(mouselogs[it_mouse].split(',', 1)[0])
        if keylogtime < mouselogtime:
            output.write(keylogs[it_key])
            it_key += 1
        else:
            output.write(mouselogs[it_mouse])
            it_mouse += 1

    # Write remaining lines to the file
    if it_key < len(keylogs):
        output.writelines(keylogs[it_key:])

    if it_mouse < len(mouselogs):
        output.writelines(mouselogs[it_mouse:])


