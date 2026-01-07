# Mouse Tracking Data Explorer - GUI Application

This application provides an interactive graphical interface to analyze mouse tracking data from behavioral experiments.

## Files

- **data_explorer_analyses.py**: Contains the analysis functions for all four programs
- **data_explorer_GUI.py**: The graphical user interface application
- **data_explorer_games.py**: Original analysis script (reference)

## Requirements

All required packages are already installed in the virtual environment:
- numpy
- matplotlib
- pandas
- scipy
- tkinter (included with Python)

## Running the Application

To launch the GUI application, run:

```bash
python data_explorer_GUI.py
```

Or from the virtual environment:

```bash
.venv/Scripts/python.exe data_explorer_GUI.py
```

## Programs Available

### Program #1: Trajectory Plot
Plots the movement trajectories of selected mice over time.

**Parameters:**
- **Select Mice**: Choose which mice to include (Red, Blue, Yellow, Green)
- **Time Frame**: Specify start and end time in seconds (default: 0-300s = 5 minutes)
- **Behavior Markers**: Optional overlay on trajectories
  - **None**: Simple trajectory lines
  - **Zone-based styling**: Different line styles for different zones (you can select which zones to highlight)
  - **Rest markers**: Triangular markers where mice are resting (movement < 1cm over 5 seconds)
  - **Contact events**: Markers showing when pairs of mice are in close proximity (<10cm for >3 seconds)

### Program #2: Contact Heat Plot
Creates a heatmap showing total contact time between each pair of mice.

**Parameters:**
- **Select Mice**: Choose which mice to include (minimum 2 required)

**Output**: A color-coded matrix showing contact time in seconds for each pair

### Program #3: Speed Plot
Plots the instantaneous speed of each mouse over time.

**Parameters:**
- **Select Mice**: Choose which mice to include
- **Time Frame**: Specify start and end time in seconds (default: 0-300s = 5 minutes)

**Output**: Line plot showing speed (cm/sec) vs time for each selected mouse

### Program #4: Time by Zone Plot
Displays a stacked bar chart showing how much time each mouse spent in different zones.

**Parameters:**
- **Select Mice**: Choose which mice to include
- **Time Frame**: Specify start and end time in seconds (default: 0-300s = 5 minutes)

**Output**: Stacked bar chart with each zone color-coded

## GUI Layout

The application window is divided into two main sections:

### Left Panel - Controls
- **Program Selection**: Radio buttons to choose which analysis to run
- **Mouse Selection**: Checkboxes to select which mice to analyze
- **Time Frame**: Input fields for start and end times (visible for Programs 1, 3, 4)
- **Behavior Markers**: Options for trajectory visualization (visible only for Program 1)
  - When "Zone-based styling" is selected, a list of zones appears for selection
- **Run Analysis**: Button to execute the selected program
- **Clear Plot**: Button to clear the current visualization

### Right Panel - Results
Displays the generated plots and visualizations.

## Mouse Colors

The mice are identified by their colors:
- **Red Mouse** (Index 0)
- **Blue Mouse** (Index 1)
- **Yellow Mouse** (Index 2)
- **Green Mouse** (Index 3)

Trajectories are plotted in the corresponding colors.

## Zones

The experimental arena contains 11 zones:
1. Open
2. Feeder1
3. Feeder2
4. Water
5. SmallNest
6. Labyrinth
7. BigNest
8. Block
9. [Ramp1]
10. [Ramp2]
11. Water2

## Data File

The application expects the data file to be located at:
```
data/mouse_data_v7.mat
```

Make sure this file is present before running the application.

## Usage Tips

1. **Default Settings**: The application starts with all mice selected and a default time frame of 0-300 seconds (5 minutes)

2. **Time Frame Conversion**: Time is specified in seconds. The application automatically converts this to frames based on the video frame rate stored in the data file.

3. **Multiple Analyses**: You can run different analyses sequentially. Use the "Clear Plot" button to remove the current visualization before running a new one.

4. **Contact Analysis**: For meaningful contact analysis (Programs 1 with contact markers and Program 2), make sure to select at least 2 mice.

5. **Zone Selection**: When using zone-based trajectory styling, you can select specific zones to highlight, or select all zones to see the complete zone information.

## Analysis Details

### Frame Rate Calculation
- The application reads the frame rate from the video metadata
- Time-to-frame conversion: `frame_number = time_in_seconds * fps`

### Contact Detection
- **Proximity threshold**: 10 cm
- **Minimum duration**: 3 seconds
- Uses connected component labeling to identify continuous contact periods

### Rest Detection
- **Movement threshold**: < 1 cm over a rolling 5-second window
- Calculated using Euclidean distance in pixel space, converted to cm

### Speed Calculation
- Calculated as the Euclidean distance between consecutive frames
- Converted from pixels to cm using the pixel-to-cm conversion factor from the data
- Expressed in cm/sec

## Troubleshooting

**Error: "Data file not found"**
- Ensure the file `data/mouse_data_v7.mat` exists in the correct location

**Error: "No mice selected"**
- Select at least one mouse using the checkboxes

**Error: "Not enough mice"** (for contact analysis)
- Select at least 2 mice for contact-based analyses

**Error: "Invalid time range"**
- Ensure end time > start time >= 0

**Plots appear too small**
- You can resize the application window
- The plot panel will automatically adjust to fill the available space

## Code Structure

### data_explorer_analyses.py Functions

- `load_data()`: Loads and prepares the mouse tracking data
- `get_mouse_colormap()`: Extracts color mapping for mice
- `plot_trajectory()`: Program #1 implementation
- `plot_contact_heatmap()`: Program #2 implementation
- `plot_speed()`: Program #3 implementation
- `plot_time_by_zone()`: Program #4 implementation

### data_explorer_GUI.py Classes

- `MouseDataExplorerGUI`: Main GUI application class
  - `create_control_panel()`: Creates the parameter selection interface
  - `create_plot_panel()`: Creates the visualization area
  - `run_analysis()`: Executes the selected analysis program
  - `update_parameter_visibility()`: Shows/hides parameters based on program selection

## Extension Ideas

If you want to extend this application, consider:

1. Adding export functionality to save plots as images
2. Adding data export to save analysis results as CSV files
3. Implementing animation to show trajectories over time
4. Adding statistical summaries (mean speed, total distance, etc.)
5. Implementing custom zone definitions
6. Adding batch processing for multiple time windows
