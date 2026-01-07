# Mouse Tracking Data Visualizer
**A no-code, user-friendly program for exploring animal tracking data.**

## :mag: Overview
This program is a no-code, user-friendly tool for exploring animal tracking data from social box experiments. It allows quick visualizations of pre-processed mouse movement datasets, making analysis accessible to both coders and non-coders. Designed for behavioral neuroscience research, it helps users examine group dynamics and activity in a semi-naturalistic environment. Example data and visualizations are provided for convenience. The tool streamlines initial data exploration, enabling users to focus on scientific insights.


## :dizzy: Motivation
Animal movement tracking is foundational to behavioral neuroscience research. At [Forkosh Lab](https://www.forkoshlab.com/), we use the social box - a seminatural setup for automatic and prolonged monitoring of mouse group dynamics (see "The Social Box Setup" below).

This is an original setup that was developed by a group of researchers (up-to-date setup as described at [Forkosh et al., 2019](https://www.nature.com/articles/s41593-019-0516-y)) and is used in our lab as the standard framework for running our experiments.

The datasets resulting from these filmed experiments (after initial processing of video, including application of tags to the frames, etc.) are rich but may be difficult to analyze for someone who's unfamiliar with their structure or with coding. Additionally, even researchers who are familiar with it may occasionally need to run a few quick checks to get an idea of the results before and while diving in to their analyses. Therefore it can be handy to have a tool that allows users to run quick calculations and visualizations of their data, without having to dirty their hands with long scripts of code.

An important clarification - most of the research in our lab in based on these types of experiments and so while this program is tailor-made for our data, its use is wide within our group. This program is sure to make data exploration easier for students in our lab.


## :key: Key Features
The plots visualize mouse movement, interaction, activity and behaviour.


4 data exploration visualization types:
* Movement trajectory
    * Zone (indication of time spent in different locations)
    * Rest (indication lack of movement)
    * Contact events (indecation of interaction between mice)
* Contact heat map
* Speed plot
* Zone time spending distribution


Accompanying attributes:
* Selection of:
    * Animal identity
    * Time frame
* Graphing options
* Plot download



## :file_folder: Project Structure
```
Animal-Tracking-Data-Explorer/
├── data_explorer_analyses.py    # Core analysis functions
├── data_explorer_GUI.py          # Interactive GUI application
├── test_data_explorer.py         # Comprehensive test suite
├── pyproject.toml                # Project configuration and dependencies
├── README.md                     # Project overview
├── README_proposal.md                     # Original project proposal
├── .python-version               # Python version pinning for uv
├── data/
│   └── mouse_data_v7.mat         # Example tracking data
├── images/
│   └── social_box_setup.png      # Social box setup diagram
└── outputs/                      # Generated plots (git-ignored)
```

### Code Structure

#### data_explorer_analyses.py Functions

- `load_data()`: Loads and prepares the mouse tracking data
- `get_mouse_colormap()`: Extracts color mapping for mice
- `plot_trajectory()`: Program #1 implementation
- `plot_contact_heatmap()`: Program #2 implementation
- `plot_speed()`: Program #3 implementation
- `plot_time_by_zone()`: Program #4 implementation

#### data_explorer_GUI.py Classes

- `MouseDataExplorerGUI`: Main GUI application class
  - `create_control_panel()`: Creates the parameter selection interface
  - `create_plot_panel()`: Creates the visualization area
  - `run_analysis()`: Executes the selected analysis program
  - `update_parameter_visibility()`: Shows/hides parameters based on program selection



## :mouse2: The Social Box Setup
In our experiments, we used groups of four mice, that were marked with dyes of four different colors for identification purposes. The mice were housed in an enriched semi-naturalistic environment where they could move and interact freely over multiple days. Each arena contained a closed nest, two feeders, two water bottles, two ramps, an open shelter, and an S-shaped separation wall in the center.
<p align="center">
<img src="https://github.com/razlei25/Animal-Tracking-Data-Explorer/blob/main/images/social_box_setup.png" width="33%" />
</p>


## :paperclip: Data
The program takes files of tracking data that have been pre-processed using a graphical wizard and our internal algorithm. In short, videos go through scaling, labeling & marking (a semi-manual process) and finally, frame segmentation and path tracking are employed.
For convenience, I've attached example data from our social box experiments (```data\mouse_data_v7.mat```). Additional data files are publicly available at our [GitHub](https://github.com/OrenForkosh/6170_Animal_Cognition/tree/main/tracks).



## :wrench: Operation
### Requirements
See `pyproject.toml` for dependencies.

Required packages (already in virtual environment):
- numpy >= 1.20
- matplotlib >= 3.5
- scipy >= 1.10 (requires 64-bit Python on Windows)
- tkinter (included with Python)

### Installations

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

1. **Install uv** (if not already installed):
   ```bash
   # On Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone or download** this repository

3. **Navigate to the project directory**:
   ```bash
   cd Animal-Tracking-Data-Explorer
   ```

### Running the Application

The easiest way to run the application is with uv (automatically handles dependencies):

```bash
uv run data_explorer_GUI.py
```

Alternatively, using the command-line script:
```bash
uv run mouse-tracker-gui
```

Or run the standalone demo examples:
```bash
uv run data_explorer_games.py
```

### Running Tests

To run the test suite with development dependencies:

```bash
uv run --extra dev pytest
```

For verbose output:
```bash
uv run --extra dev pytest -v
```

### Troubleshooting

**Error: "Failed to build scipy"**
- Ensure you're using 64-bit Python (not 32-bit)
- uv automatically installs 64-bit Python 3.8.20
- Run: `uv python pin 3.8.20` to ensure correct Python version

**Error: "Data file not found"**
- Ensure the file `data/mouse_data_v7.mat` exists in the correct location

**Error: "No mice selected"**
- Select at least one mouse using the checkboxes

**Error: "Not enough mice"** (for contact analysis)
- Select at least 2 mice for contact-based analyses

**Error: "Invalid time range"**
- Ensure end time > start time >= 0
- Ensure both start and end times are within the video duration (0 to 43200.35 seconds / 720.01 minutes for the example data)
- The error message will display the valid time range for your specific data file

**Plots appear too small**
- You can resize the application window
- The plot panel will automatically adjust to fill the available space

