import numpy as np
import matplotlib.pyplot as plt

"""
MouseHeatmap class takes a segment of a dataframe generated from a
mouse_actions log file and provides methods to display it as a heatmap
showing the relative amount of time the mouse cursor spent in each location 
on the screen
"""
class MouseHeatmap:

    """
    Construct the heatmap object by passing it a pandas dataframe
    The dataframe must be generated from a mouse_actions log file
    You can obtain a specified slice of time from the dataframe using get_segment()
    """
    def __init__(self, df_segment):
        # Copy DataFrame as instance attribute
        self.df = df_segment

        # Initialize values used for building heatmap image
        self.last_time, self.last_x, self.last_y = 0, 0, 0

        # Screen dimensions according to log min/max values
        screen_w_log = np.max(self.df.x) - np.min(self.df.x)
        screen_h_log = np.max(self.df.y) - np.min(self.df.y)

        # Use 1080p dimesnions if larger log file dimensions
        self.screen_w, self.screen_h = max(1920, screen_w_log), max(1080, screen_h_log)

        # Saturation value used in normalization
        self.saturation = 5

    
    """
    Utility method used to convert the instance's dataframe to a heatmap 
    of the specified resolution
    """
    def df_to_heatmap(self, res):
        # Initialize heatmap (with zeros)
        self.heatmap_values = np.zeros(res)
        self.heatmap_w, self.heatmap_h = res[0], res[1]

        # Reset last_time to signal the first line of data
        self.last_time = -1

        # Iterate through each row of dataframe segment
        for _, row in self.df.iterrows():
            line = row.values.tolist() # Convert row (pd.Series) to List
            self.line_to_heatmap(line) # Use list values to update heatmap image

        # Normalize heatmap values (divide by max value)
        self.heatmap_values /= max(np.max(self.heatmap_values), 1)

        # Compress the heatmap
        # Calculate max saturation = (mean / deviation) * (1 / saturation)
        threshold = self.heatmap_values.mean() / (max(self.heatmap_values.std(), 0.001) * self.saturation)
        # Anything above max_saturation is clamped to max_saturation
        self.heatmap_values[self.heatmap_values > threshold] = threshold

        # Transpose heatmap array to represent screenspace
        self.heatmap_values = self.heatmap_values.T


    """
    Utility method used to update the heatmap with a line of data
    - Add a line of data to the heatmap (in List form)
    - Uses the passed line to find duration that the mouse was in the last position
    - Adds previous line of data (from last function call) to heat map and prepares 
    the passed line for the next function call
    """
    def line_to_heatmap(self, line):
        
        # last_time is initialized to -1 to signal first line
        if self.last_time != -1:
            # Find duration of mouse in last position
            value = line[0] - self.last_time
            # Add last line of data to heatmap
            self.heatmap_values[self.last_x, self.last_y] += value

        # Prepare passed line of data for heatmap
        self.last_time = line[0]

        # Normalize and clamp data if needed
        x_raw, y_raw = line[1], line[2]
        x = int((x_raw / self.screen_w) * (self.heatmap_w - 1))
        y = int((y_raw / self.screen_h) * (self.heatmap_h - 1))
        if x < 0: x = 0
        if x > (self.heatmap_w - 1): x = self.heatmap_w - 1
        if y < 0: y = 0
        if y > (self.heatmap_h - 1): y = self.heatmap_h - 1
        self.last_x, self.last_y = x, y


    """
    Display the heatmap
    res: The resolution of the heatmap image
    """
    def show_heatmap(self, res=(100, 100)):
        # Convert DataFrame segment to np.ndarray in heatmap shape
        self.df_to_heatmap(res)

        # Show heatmap
        plt.figure(figsize=(7.5, 7.5))
        plt.imshow(self.heatmap_values, cmap='cividis')
        plt.tick_params(which='both', bottom=False, labelbottom=False, left=False, labelleft=False)
        plt.show()

    """
    Display the heatmap centered in the image
    Uses the mean and variance of the data to find the center and scale
    """
    def show_heatmap_centered(self, res=(100, 100)):
        print("show_heatmap_centered() method is undergoing renovations")
        """
        # Find center values by averaging the indices of the max 10 column/row sums
        x_center = int(np.mean(np.argsort(heatmap.sum(axis=0))[::-1][:10]))
        y_center = int(np.mean(np.argsort(heatmap.sum(axis=1))[::-1][:10]))

        # Find variance by index of first non-zero value - index of last non-zero value
        # Then divide in half
        x_variance = int(np.trim_zeros(np.trim_zeros(heatmap.sum(axis=0), 'f'), 'b').size / 2)
        y_variance = int(np.trim_zeros(np.trim_zeros(heatmap.sum(axis=1), 'f'), 'b').size / 2)

        # Choose largest variance value (so heatmap is 1:1 ratio)
        variance = max(x_variance, y_variance)

        # Zoom in a little
        variance = int(variance * 0.8)

        x_min = max(x_center - variance, 0)
        x_max = x_center + variance
        y_min = max(y_center - variance, 0)
        y_max = y_center + variance

        MouseHeatmap.show_heatmap(heatmap[y_min:y_max, x_min:x_max])
        """