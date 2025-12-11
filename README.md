# Mouse Tracking Data Visualizer
**A no-code, user-friendly program for exploring animal tracking data.**

## :mag: Overview
This program is a no-code, user-friendly tool for exploring animal tracking data from social box experiments. It allows quick calculations and visualizations of pre-processed mouse movement datasets, making analysis accessible to both coders and non-coders. Designed for behavioral neuroscience research, it helps users examine group dynamics and activity in a semi-naturalistic environment. Example data and visualizations are provided for convenience. The tool streamlines initial data exploration, enabling users to focus on scientific insights.


## :dizzy: Motivation
Animal movement tracking is a foundational to behavioral neuroscience research. At [Forkosh Lab](https://www.forkoshlab.com/), we use the social box - a seminatural setup for automatic and prolonged monitoring of mouse group dynamics (see "The Social Box Setup" below).

This is an original setup that was developed by a group of researchers (up-to-date setup as described at [Forkosh et al., 2019](https://www.nature.com/articles/s41593-019-0516-y)) and has been used in our lab as the standard framework for running our experiments.

The datasets resulting from these filmed experiments (after initial processing of video, including application of tags to the frames, etc.) are rich but may be difficult to analyze for someone who's unfamiliar with their structure or with coding. Additionally, even researchers who are familiar with it may occasionally need to run a few quick checks to get an idea of the results before and while diving in to their analyses. Therefore it can be handy to have a tool that allows users to run quick calculations and visualizations of their data, without having to dirty their hands with long scripts of code.

An important to clarification - most of the research in our lab in based on these types of experiments and so while this program is tailor-made for our data, its use is wide within our group. This program is sure to make data exploration easier for students in our lab.


## :key: Key Features
Data exploration features include:
* Trajectory plotting
* Activity level comparison
* Behaviour identification
* Movement distance calculation


Accompanying attributes:


* Graphing and visualization options
* Selection of:


        * Animal identity
        * Time frame
        * Location


## :file_folder: Project Structure
```
Animal-Tracking-Data-Explorer/
├── data_explorer_calculator.py
├── data_explorer_GUI.py
├── main.py
├── pyproject.toml
├── README.md
├── data/
│   └── THREE_CHAMBER-exp.exp0014.day01.cam04.mp4.obj.mat
├── images/
│   └── social_box_setup.png
```


## :mouse2: The Social Box Setup
In our experiments, we used groups of four mice, that were marked with dyes of four different colors for identification purposes. The mice were housed in an enriched semi-naturalistic environment where they could move and interact freely over multiple days. Each arena contained a closed nest, two feeders, two water bottles, two ramps, an open shelter, and an S-shaped separation wall in the center.
<p align="center">
<img src="https://github.com/razlei25/Animal-Tracking-Data-Explorer/blob/main/images/social_box_setup.png" width="33%" />
</p>


## :paperclip: Data
The program takes files of tracking data that have been pre-processed using a graphical wizard and our internal algorithm. In short, videos go through scaling, labeling & marking (a semi-manual process) and finally, frame segmentation and path tracking are employed.
For convenience, I've attached example data from our social box experiments (```data\THREE_CHAMBER-exp.exp0014.day01.cam04.mp4.obj```). Additional data files are publicly available at our [GitHub](https://github.com/OrenForkosh/6170_Animal_Cognition/tree/main/tracks).




