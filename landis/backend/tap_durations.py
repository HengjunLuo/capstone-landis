import numpy as np
from statistics import NormalDist

from numpy_ringbuffer import RingBuffer
import pathlib

from backend.log_parser import parse_keyboard_log

# Size of sliding window for each key 
# (mean and stddev of the last {sample_size} key taps)
sample_size = 20

# Amount of data to record before overwriting old data
data_window_limit = 100

# Amount of profile training data to record before overwriting old data
profile_data_limit = 1000

# Read logfile paths from .routing
log_paths = None

"""
Data persistence functions
"""
# Load data from saved profile and return a tuple of dicts
def load_tap_profile (profile):
    mean_data = {}  # Dict to store mean data
    std_data  = {}  # Dict to store stddev data
    key_data  = []  # List to store all raw data associated with a key

    with open(f"profiles/{profile}.tap", 'r', encoding='utf-8') as f:
        lines = f.read().splitlines() # Read lines without '\n's
        # Group data 2 rows at a time (each key has 2 lines of data)
        for i in range(0, len(lines), 2): 
            key_data.append((lines[i], lines[i + 1]))
        # Iterate through each key's raw data
        for key_mean, key_std in key_data:
            # Separate values by commas
            key_mean = key_mean.split(',')
            key_std  = key_std.split(',')
            key = key_mean[0] # First value is always the key
            # Initialize ring buffers
            mean_data[key] = RingBuffer(profile_data_limit) 
            std_data[key]  = RingBuffer(profile_data_limit)
            # Append mean values to ring buffer
            for value in key_mean[2:]:
                mean_data[key].append(value)
            # Append stddev values to ring buffer
            for value in key_std[2:]:
                std_data[key].append(value)
    
    return (mean_data, std_data)

# Save data to file in profiles directory
def save_session_tap_data(profile, mean_data, std_data):
    # Expected that both dicts have similar keys
    keys = list(mean_data.keys()) # List keys that have data associated with them
    mean_profile, std_profile = mean_data, std_data # Default profile data

    # Add to the profile if it already exists
    if pathlib.Path(f"profiles/{profile}.tap").exists():
        mean_profile, std_profile = load_tap_profile(profile) # Load current profile
        # Iterate through keys and update the profile for each one
        for key in keys: 
            mean_np = np.array(mean_data[key]) # Convert arg to numpy array
            std_np  = np.array( std_data[key]) # Convert arg to numpy array
            # Append contents of each key ring buffer to loaded buffers
            for value in mean_np:
                # Check that key has data already
                if key not in mean_profile.keys():
                    # If no, create new ring buffer first
                    mean_profile[key] = RingBuffer(profile_data_limit)
                mean_profile[key].append(value) # Append new value to data
            # Same deal as above but with standard deviations
            for value in std_np:
                # Check that key has data already
                if key not in std_profile.keys():
                    # If no, create new ring buffer first
                    std_profile[key] = RingBuffer(profile_data_limit)
                std_profile[key].append(value) # Append new value to data

    # Save the combined data back to file
    with open(f"profiles/{profile}.tap", 'w', encoding='utf-8') as f:    
        for key in keys: # For each key
            mean_values = list(mean_profile[key])  # List mean values
            std_values  = list(std_profile[key])   # List stddev values
            # Write mean values (key,number of values, values...)
            f.write(str(key) + ',' + str(mean_profile[key].shape[0]) + ',')
            f.write(','.join(format(x, "0.4f") for x in mean_values))
            f.write('\n')
            # Write stddev values (key,number of values, values...)
            f.write(str(key) + ',' + str(std_profile[key].shape[0]) + ',')
            f.write(','.join(format(x, "0.4f") for x in std_values))
            f.write('\n')


"""
Extract data from a dataframe
"""
def get_session_data(dataframe):

    profile = str(dataframe['class'].iloc[0])[:3] # Use 3 letter profile name

    duration_dict = {} # Map each key to a ring buffer of size {sample_size}
    presstimes    = {} # Record the 'last pressed' time of each key
    mean          = {} # Records the mean of each key sample window
    stdev         = {} # Records the stdev of each key sample window
    
    for _, row in dataframe.iterrows():    # Analyze each piece of data one at a time
        key = str(row.key).replace('\'', '') # Get rid of ' characters

        if key not in duration_dict.keys():   # If key not added to dict yet
            duration_dict[key] = RingBuffer(sample_size) # Add it
        
        if row.action == 'pressed':     # If key was pressed
            presstimes[key] = row.time  # Record time of press
        
        # If key was released and it has been pressed before
        elif row.action == 'released' and key in presstimes.keys():
            duration = row.time - presstimes[key] # Calculate press duration

            if duration < 0.4: # Only append key taps (<0.4s)
                duration_dict[key].append(duration) # Append tap duration to ring buffer

                durations_np = np.array(duration_dict[key]) # Convert to numpy array
                if durations_np.size > 3:      # If more than 3 samples in the ring buffer
                    
                    if key not in mean.keys(): # If key not added to mean/stdev dicts yet
                        mean[key]   = RingBuffer(data_window_limit) # Add them
                        stdev[key]  = RingBuffer(data_window_limit)

                    # Record mean/stdev of sample in both dicts
                    mean[key].append(durations_np.mean())
                    stdev[key].append(durations_np.std())
    
    # Return a tuple of gathered information
    return (profile, mean, stdev)


# Helper function
def clamp(n, smallest, largest): 
    return max(smallest, min(n, largest))


"""
Verify the play session against a profile
"""
def verify_session(session_df, profile):
    # Load session data
    _, session_mean_data, session_std_data = get_session_data(session_df)

    # Load user's profile
    profile_mean_data, profile_std_data = load_tap_profile(profile)

    # Test only for keys that exist in both records
    shared_keys = set(session_mean_data.keys()).intersection(set(profile_mean_data.keys()))

    # Calculate mean and stdev of each key's mean and stdev (so meta)
    # Means in profile
    profile_mean_overall_mean, profile_mean_overall_std = {}, {}
    for key in list(profile_mean_data.keys()):
        profile_mean_overall_mean[key] = np.array(profile_mean_data[key]).mean()
        profile_mean_overall_std[key]  = np.array(profile_mean_data[key]).std()
    # Means in session
    session_mean_overall_mean, session_mean_overall_std = {}, {}
    for key in list(session_mean_data.keys()):
        session_mean_overall_mean[key] = np.array(session_mean_data[key]).mean()
        session_mean_overall_std[key]  = np.array(session_mean_data[key]).std()

    # Standard deviations in profile
    profile_std_overall_mean, profile_std_overall_std = {}, {}
    for key in list(profile_std_data.keys()):
        profile_std_overall_mean[key] = np.array(profile_std_data[key]).mean()
        profile_std_overall_std[key]  = np.array(profile_std_data[key]).std()
    # Standard deviations in session
    session_std_overall_mean, session_std_overall_std = {}, {}
    for key in list(session_mean_data.keys()):
        session_std_overall_mean[key] = np.array(session_std_data[key]).mean()
        session_std_overall_std[key]  = np.array(session_std_data[key]).std()

    scores = []
    for key in shared_keys:
        weight = min(np.array(session_mean_data[key]).size, np.array(profile_mean_data[key]).size)

        session_mean_dist = NormalDist(session_mean_overall_mean[key], session_mean_overall_std[key])
        session_std_dist  = NormalDist(session_std_overall_mean[key], session_std_overall_std[key])
        profile_mean_dist = NormalDist(profile_mean_overall_mean[key], profile_mean_overall_std[key])
        profile_std_dist  = NormalDist(profile_std_overall_mean[key], profile_std_overall_std[key])

        if (session_mean_dist.stdev == 0) or (session_std_dist.stdev == 0) or \
           (profile_mean_dist.stdev == 0) or (profile_std_dist.stdev == 0):
            continue

        means_overlap = session_mean_dist.overlap(profile_mean_dist)
        stdev_overlap = session_std_dist.overlap(profile_std_dist)

        # Lazy weighted average
        # Appends each score once for each sample used to create the distribution
        # So some scores get appended 100 times
        for _ in range(weight):
            scores.append(means_overlap)
            scores.append(stdev_overlap)

    weighted_avg_score = np.mean(scores)

    # W don't need to discuss whats going on here
    # But basically it's just adjusting the confidence score to fit in the [0, 1] range
    modified_score = weighted_avg_score * 1.75 - 0.5
    confidence = clamp(modified_score, 0, 1)
    return confidence


# Save the session to the appropriate profile
def save_session(session_df):
    save_session_tap_data(get_session_data(session_df))
