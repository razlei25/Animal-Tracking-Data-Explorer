"""
Python translation of MATLAB mouse tracking analysis script.   
Analyzes behavioral data from a three-chamber experiment with multiple mice.  

Required packages:
- numpy
- matplotlib
- pandas
- scipy
- opencv-python
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from scipy.io import loadmat
from scipy.ndimage import label
import warnings

# ==============================================================================
# Helper Functions
# ==============================================================================

def load_cheese_cube(mat_file_path):
    """
    Load CheeseCube data from . mat file.
    
    Parameters: 
    -----------
    mat_file_path :   str or Path
        Path to the .mat file containing experiment data
    
    Returns: 
    --------
    dict :   Dictionary containing all loaded data
    """
    data = loadmat(mat_file_path, struct_as_record=False, squeeze_me=True)
    return data

def get_mouse_colormap(colors_obj, n_subjects):
    """
    Extract mouse colormap from colors object, handling various formats.
    
    Parameters:
    -----------
    colors_obj :   various
        Colors object/struct from the data
    n_subjects : int
        Number of subjects/mice
    
    Returns:  
    --------
    numpy.ndarray :   n_subjects x 3 RGB colormap (values 0-1)
    """
    letter_map = {
        'R': [1, 0, 0], 'G': [0, 1, 0], 'B': [0, 0, 1], 'Y': [1, 1, 0],
        'C': [0, 1, 1], 'M':  [1, 0, 1], 'K': [0, 0, 0], 'W': [1, 1, 1]
    }
    
    # Default color order: Red, Blue, Yellow, Green
    default_colors = np.array([
        [1, 0, 0],    # Red
        [0, 0, 1],    # Blue
        [1, 1, 0],    # Yellow
        [0, 1, 0]     # Green
    ])
    
    numeric_map = None
    mice_str = ''
    
    # Try to extract colormap and mice string
    try:
        if hasattr(colors_obj, 'Colormap'):
            numeric_map = np.array(colors_obj. Colormap, dtype=float)
        elif hasattr(colors_obj, 'colormap'):
            numeric_map = np.array(colors_obj. colormap, dtype=float)
            
        if hasattr(colors_obj, 'Mice'):
            mice_str = str(colors_obj.Mice)
        elif hasattr(colors_obj, 'mice'):
            mice_str = str(colors_obj.mice)
    except:
        pass
    
    # Normalize if needed
    if numeric_map is not None and numeric_map.max() > 1:
        numeric_map = numeric_map / 255.0
    
    # Build colormap
    cmap = np.zeros((n_subjects, 3))
    
    # First try to use the Mice string to map letters to colors
    for s in range(n_subjects):
        if s < len(mice_str):
            ch = mice_str[s]. upper()
            if ch in letter_map:  
                cmap[s] = letter_map[ch]
                continue
        
        # Then try numeric colormap
        if numeric_map is not None and s < len(numeric_map):
            cmap[s] = numeric_map[s]
        # Finally, use default RBYG colors
        elif s < len(default_colors):
            cmap[s] = default_colors[s]
        else:
            # Fallback for more than 4 mice
            cmap[s] = plt.cm.viridis(s / n_subjects)[:3]
    
    return cmap

# ==============================================================================
# Setup and Data Loading
# ==============================================================================

# Use the v7 converted file
data_file = Path(r"data\mouse_data_v7.mat")

print(f"Loading data from: {data_file}")

# Check if file exists
if not data_file.exists():
    raise FileNotFoundError(f"Data file not found:   {data_file}")

cube_day1 = load_cheese_cube(data_file)

# ==============================================================================
# Explore the Data
# ==============================================================================

print("\n" + "="*80)
print("DATA EXPLORATION")
print("="*80)

print(f"\nLoaded object type: {type(cube_day1)}")
print(f"Available keys: {list(cube_day1.keys())}")

# Show summary of main data structures
for key in cube_day1.keys():
    if not key.startswith('__'):
        val = cube_day1[key]
        print(f"  {key:12s} :   type={type(val).__name__:20s}  shape={getattr(val, 'shape', 'N/A')}")

# Extract main components (capital letters to match loaded data)
tracking = cube_day1.get('Tracking', None)
video_info = cube_day1.get('Video', None)
background_struct = cube_day1.get('Background', None)
arena = cube_day1.get('ROI', None)
colors = cube_day1.get('Colors', None)

# Debug: Print structure
if tracking is not None:
    print("\nTracking attributes:")
    if hasattr(tracking, '_fieldnames'):
        print(f"  Fields: {tracking._fieldnames}")
    print(f"  Type: {type(tracking)}")
    
if video_info is not None:  
    print("\nVideo attributes:")
    if hasattr(video_info, '_fieldnames'):
        print(f"  Fields:  {video_info._fieldnames}")

# Video info
if video_info is not None: 
    print("\nVideo Information:")
    if hasattr(video_info, 'FrameRate'):
        fps = float(video_info.FrameRate)
        print(f"  Frame rate: {fps} fps")
    if hasattr(video_info, 'NumberOfFrames'):
        total_frames = int(video_info.NumberOfFrames)
        print(f"  Total frames:  {total_frames}")

# Background - extract the image array
background = None
if background_struct is not None:
    print("\nBackground:")
    if hasattr(background_struct, 'Image'):
        background = background_struct.Image
    elif hasattr(background_struct, 'image'):
        background = background_struct.image
    elif isinstance(background_struct, np.ndarray):
        background = background_struct
        
    if background is not None and isinstance(background, np.ndarray):
        print(f"  Shape: {background.shape}")
        print(f"  Min/Max: {background.min()} / {background.max()}")
        
        # Display background
        plt.figure(figsize=(10, 8))
        plt.imshow(background, cmap='gray')
        plt.title('Background Image')
        plt.colorbar()
        plt.tight_layout()

# Tracking data
if tracking is not None:
    print("\nTracking Data:")
    if hasattr(tracking, 'x') and hasattr(tracking, 'y'):
        x = np.array(tracking.x, dtype=float)
        y = np.array(tracking.y, dtype=float)
        print(f"  x shape: {x.shape}")
        print(f"  y shape: {y.shape}")
        
        n_subjects = x.shape[0]
        n_frames = x.shape[1]
        print(f"  Number of subjects: {n_subjects}")
        print(f"  Number of frames: {n_frames}")
        
        # Sample trajectory plot
        if background is not None and isinstance(background, np.ndarray):
            plt.figure(figsize=(12, 10))
            plt.imshow(background, cmap='gray', alpha=0.5)
            
            # Plot first subject's trajectory (first 1000 valid points)
            subj = 0
            valid_mask = np.ones(n_frames, dtype=bool)
            if hasattr(tracking, 'valid'):
                valid_data = np.array(tracking.valid, dtype=bool)
                if valid_data.ndim == 2:
                    valid_mask = valid_data[subj, :]
                else:
                    valid_mask = valid_data
            
            valid_idx = np.where(valid_mask)[0][:1000]
            plt.plot(x[subj, valid_idx], y[subj, valid_idx], 'r-', linewidth=1, alpha=0.7)
            plt.plot(x[subj, valid_idx[0]], y[subj, valid_idx[0]], 'go', markersize=8, label='Start')
            plt.plot(x[subj, valid_idx[-1]], y[subj, valid_idx[-1]], 'rx', markersize=8, label='End')
            plt.title(f'Sample Trajectory - Subject {subj+1}')
            plt.legend()
            plt.tight_layout()

plt.show()

# ==============================================================================
# Game 1: Plot trajectories for first 15 minutes
# ==============================================================================

print("\n" + "="*80)
print("GAME 1: Trajectories (First 15 Minutes)")
print("="*80)

# Extract tracking data
x = np.array(tracking.x, dtype=float)
y = np.array(tracking.y, dtype=float)
fps = float(video_info.FrameRate)  # Capital F and R

# Calculate frames for 15 minutes
frames_15 = min(int(15 * 60 * fps), x.shape[1])
print(f"15 minutes = {frames_15} frames at {fps} fps")

n_subjects = x.shape[0]

# Get mouse colormap
mouse_cmap = get_mouse_colormap(colors, n_subjects)
# Debug: Print extracted color information
print(f"\nMouse color mapping:")
if hasattr(colors, 'Mice'):
    print(f"  Mice string: {colors.Mice}")
elif hasattr(colors, 'mice'):
    print(f"  Mice string: {colors.mice}")
print(f"  Extracted colormap:\n{mouse_cmap}")

# Plot trajectories
plt.figure(figsize=(14, 12))
for s in range(n_subjects):
    xs = x[s, :frames_15]
    ys = y[s, :frames_15]
    plt.plot(xs, ys, '-', color=mouse_cmap[s], linewidth=1.5, label=f'Mouse {s+1}')

plt.axis('equal')
plt.xlabel('X (pixels)')
plt.ylabel('Y (pixels)')
plt.title(f'Mouse Trajectories - First 15 Minutes ({fps:.3f} fps, {frames_15} frames)')
plt.legend(loc='best')
plt.gca().invert_yaxis()  # Match MATLAB's default image coordinate system
plt.grid(True, alpha=0.3)
plt.tight_layout()

# ==============================================================================
# Game 2: Highlight Time Spent in Different Zones
# ==============================================================================

print("\n" + "="*80)
print("GAME 2: Zone-Based Trajectory Styling")
print("="*80)

zones = np.array(tracking.zones, dtype=float)

# Real zone names
real_zone_names = [
    'Open', 'Feeder1', 'Feeder2', 'Water', 'SmallNest',
    'Labyrinth', 'BigNest', 'Block', '[Ramp1]', '[Ramp2]', 'Water2'
]

# Get unique zones
if zones.ndim == 1:
    zone_vals = np.unique(zones[: frames_15])
else:
    zone_vals = np.unique(zones[:, :frames_15])

zone_vals = zone_vals[zone_vals > 0]  # Remove invalid zones
n_zones = len(zone_vals)

# Zone labels
zone_labels = []
for zid in zone_vals:
    zid_int = int(zid)
    if zid_int <= len(real_zone_names):
        zone_labels.append(real_zone_names[zid_int - 1])
    else:
        zone_labels.append(f'Zone {zid_int}')

# Line styles for zones
line_styles = ['-', '--', ':', '-.']
zone_style_map = {}
for i, zid in enumerate(zone_vals):
    zone_style_map[zid] = line_styles[i % len(line_styles)]

# Plot
plt.figure(figsize=(14, 12))

for s in range(n_subjects):
    xs = x[s, :frames_15]
    ys = y[s, :frames_15]
    
    if zones.ndim == 1:
        zs = zones[:frames_15]
    else:
        zs = zones[s, :frames_15]
    
    zs[zs == 0] = np.nan  # Mark invalid zones
    
    # Find zone transitions
    zone_changes = np.concatenate(([0], np.where(np.diff(zs) != 0)[0] + 1, [frames_15]))
    
    for k in range(len(zone_changes) - 1):
        idx1 = zone_changes[k]
        idx2 = zone_changes[k + 1]
        
        zone_id = zs[idx1]
        if np.isnan(zone_id):
            continue
        
        style = zone_style_map.get(zone_id, '-')
        plt.plot(xs[idx1:idx2], ys[idx1:idx2], 
                style, color=mouse_cmap[s], linewidth=1.5)

plt.axis('equal')
plt.xlabel('X (pixels)')
plt.ylabel('Y (pixels)')
plt.title('Zone-Styled Trajectories (First 15 Minutes)')
plt.gca().invert_yaxis()
plt.grid(True, alpha=0.3)

# Create custom legend
from matplotlib.lines import Line2D
legend_elements = []

# Zone styles
for i, zid in enumerate(zone_vals):
    legend_elements.append(Line2D([0], [0], color='black', 
                                  linestyle=zone_style_map[zid],
                                  linewidth=1.5, label=zone_labels[i]))

# Mouse colors
for s in range(n_subjects):
    legend_elements.append(Line2D([0], [0], color=mouse_cmap[s], 
                                  linewidth=2, label=f'Mouse {s+1}'))

plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()

# ==============================================================================
# Game 3: Histogram of Time Spent in Each Zone
# ==============================================================================

print("\n" + "="*80)
print("GAME 3: Time Spent per Zone")
print("="*80)

# Get arena colormap for zones
zone_cmap = None
if hasattr(arena, 'Colormap'):
    zone_cmap = np.array(arena.Colormap, dtype=float)
elif hasattr(arena, 'colormap'):
    zone_cmap = np.array(arena.colormap, dtype=float)

if zone_cmap is not None and zone_cmap.max() > 1:
    zone_cmap = zone_cmap / 255.0
else:
    zone_cmap = plt.cm.tab10(np.linspace(0, 1, n_zones))

# Calculate time spent in each zone
zone_times = np.zeros((n_subjects, n_zones))

for s in range(n_subjects):
    if zones.ndim == 1:
        zs = zones[:frames_15]
    else:
        zs = zones[s, : frames_15]
    
    for k, zone_id in enumerate(zone_vals):
        zone_times[s, k] = np.sum(zs == zone_id) / fps

# Stacked bar chart
fig, ax = plt.subplots(figsize=(12, 8))
bottom = np.zeros(n_subjects)

for k in range(n_zones):
    color = zone_cmap[k % len(zone_cmap)]
    ax.bar(range(n_subjects), zone_times[:, k], bottom=bottom,
           color=color, label=zone_labels[k])
    bottom += zone_times[:, k]

ax.set_xlabel('Mouse #')
ax.set_ylabel('Time Spent (seconds)')
ax.set_title(f'Time Spent in Each Zone by Mouse (First 15 min, {fps:.2f} fps)')
ax.set_xticks(range(n_subjects))
ax.set_xticklabels([f'Mouse {s+1}' for s in range(n_subjects)])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()

# Print table
print("\nTime spent in each zone by mouse (seconds):")
df_zones = pd.DataFrame(zone_times, 
                       columns=zone_labels,
                       index=[f'Mouse {s+1}' for s in range(n_subjects)])
print(df_zones)

# ==============================================================================
# Game 4. 1: Calculate Distance Traveled
# ==============================================================================

print("\n" + "="*80)
print("GAME 4.1: Distance Traveled")
print("="*80)

# Get pixel to cm conversion from ROI
pixel_to_cm = None
if hasattr(arena, 'PixelToCM'):
    pixel_to_cm = float(arena.PixelToCM)
elif hasattr(arena, 'pixelToCM'):
    pixel_to_cm = float(arena.pixelToCM)
else:
    # Fallback - estimate from typical arena size
    print("Warning: pixelToCM not found, using default value of 3.0")
    pixel_to_cm = 3.0

total_distance_m = np.zeros(n_subjects)

for s in range(n_subjects):
    xs = x[s, :frames_15]
    ys = y[s, :frames_15]
    
    dx = np.diff(xs)
    dy = np.diff(ys)
    d_pix = np.sqrt(dx**2 + dy**2)
    
    d_cm = d_pix / pixel_to_cm
    d_m = d_cm / 100
    
    total_distance_m[s] = np.nansum(d_m)

print("\nTotal distance traveled by each mouse (meters):")
for s in range(n_subjects):
    print(f"Mouse {s+1}: {total_distance_m[s]:.3f} meters")

# ==============================================================================
# Game 4.2: Social Proximity Analysis
# ==============================================================================

print("\n" + "="*80)
print("GAME 4.2: Social Proximity Analysis")
print("="*80)

threshold_cm = 5.0

# Generate all pairs
from itertools import combinations
pairs = list(combinations(range(n_subjects), 2))
n_pairs = len(pairs)

near_frame_counts = np.zeros(n_pairs)
near_seconds = np.zeros(n_pairs)

for p, (i, j) in enumerate(pairs):
    xi = x[i, :frames_15]
    yi = y[i, :frames_15]
    xj = x[j, : frames_15]
    yj = y[j, :frames_15]
    
    dist_pix = np.sqrt((xi - xj)**2 + (yi - yj)**2)
    dist_cm = dist_pix / pixel_to_cm
    
    close_frames = dist_cm < threshold_cm
    near_frame_counts[p] = np.nansum(close_frames)
    near_seconds[p] = near_frame_counts[p] / fps

# Create results table
pair_names = [f'Mouse {i+1} & Mouse {j+1}' for i, j in pairs]
df_proximity = pd.DataFrame({
    'FramesClose': near_frame_counts.astype(int),
    'SecondsClose': near_seconds
}, index=pair_names)

print("\nNumber of frames and seconds each pair spent within 5 cm proximity:")
print(df_proximity)

# ==============================================================================
# Game 5: Identify Resting Periods
# ==============================================================================

print("\n" + "="*80)
print("GAME 5: Resting Periods")
print("="*80)

window_seconds = 5
window_frames = int(np.round(window_seconds * fps))
rest_threshold_cm = 1.0

plt.figure(figsize=(14, 12))

for s in range(n_subjects):
    xs = x[s, :frames_15]
    ys = y[s, :frames_15]
    
    # Plot main trajectory
    plt.plot(xs, ys, '-', color=mouse_cmap[s], linewidth=2, label=f'Mouse {s+1}')
    
    # Calculate rolling movement
    movement_cm = np.full(frames_15, np.nan)
    for idx in range(window_frames, frames_15):
        window_x = xs[idx - window_frames: idx]
        window_y = ys[idx - window_frames:idx]
        dx = np.diff(window_x)
        dy = np.diff(window_y)
        d_pix = np.sqrt(dx**2 + dy**2)
        movement_cm[idx] = np.sum(d_pix) / pixel_to_cm
    
    # Find resting periods
    is_resting = movement_cm < rest_threshold_cm
    rest_idx = np.where(is_resting)[0]
    
    # Plot resting markers
    plt.plot(xs[rest_idx], ys[rest_idx], '^', 
            color=mouse_cmap[s], markersize=9, 
            markerfacecolor=mouse_cmap[s],
            label=f'Mouse {s+1} rest')

plt.axis('equal')
plt.xlabel('X (pixels)')
plt.ylabel('Y (pixels)')
plt.title(f'Trajectories with Resting Periods (triangle markers, first 15 min, {fps:.2f} fps)')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.gca().invert_yaxis()
plt.grid(True, alpha=0.3)
plt.tight_layout()

# ==============================================================================
# Game 6: Identify Contacts
# ==============================================================================

print("\n" + "="*80)
print("GAME 6: Contact Analysis")
print("="*80)

contact_thresh_cm = 10.0
min_contact_frames = int(np.round(3 * fps))

# Distinct marker colors and types
marker_list = ['o', 's', 'D', '^', '+', '*', 'x', '>', '<', 'v', 'p', 'h']
distinct_contact_colors = np.array([
    [0, 0, 0],      # black
    [1, 0, 1],      # magenta
    [0, 1, 1],      # cyan
    [1, 0.5, 0],    # orange
    [0.5, 0, 0.5],  # purple
    [0.5, 0.25, 0], # brown
    [0.5, 0.5, 0.5],# gray
    [0.3, 0.3, 1],  # blueish
])

# Contact detection
pairwise_contact_counts = np.zeros((n_subjects, n_subjects))
contact_event_details = [[[] for _ in range(n_subjects)] for _ in range(n_subjects)]

for idx, (i, j) in enumerate(pairs):
    xi = x[i, :frames_15]
    yi = y[i, : frames_15]
    xj = x[j, :frames_15]
    yj = y[j, :frames_15]
    
    dist_pix = np.sqrt((xi - xj)**2 + (yi - yj)**2)
    dist_cm = dist_pix / pixel_to_cm
    is_contact = dist_cm < contact_thresh_cm
    
    # Label connected components
    labeled, num_features = label(is_contact)
    contact_frames_list = []
    
    for seg in range(1, num_features + 1):
        fr_idx = np.where(labeled == seg)[0]
        if len(fr_idx) >= min_contact_frames:
            contact_frames_list.extend(fr_idx.tolist())
    
    pairwise_contact_counts[i, j] += len(contact_frames_list)
    pairwise_contact_counts[j, i] += len(contact_frames_list)
    contact_event_details[i][j] = contact_frames_list
    contact_event_details[j][i] = contact_frames_list

# Plot trajectories with contact markers
plt.figure(figsize=(14, 12))

# Plot trajectories
for s in range(n_subjects):
    xs = x[s, :frames_15]
    ys = y[s, :frames_15]
    plt.plot(xs, ys, '-', color=mouse_cmap[s], linewidth=2, label=f'Mouse {s+1}')

# Plot contact events
legend_elements = []
for idx, (i, j) in enumerate(pairs):
    contact_frames = contact_event_details[i][j]
    if not contact_frames:
        continue
    
    xs_i = x[i, contact_frames]
    ys_i = y[i, contact_frames]
    
    marker_type = marker_list[idx % len(marker_list)]
    contact_color = distinct_contact_colors[idx % len(distinct_contact_colors)]
    
    plt.plot(xs_i, ys_i, marker_type, 
            color=contact_color, markersize=9, linewidth=1.5,
            markerfacecolor=contact_color,
            label=f'Contact:  Mouse {i+1} & {j+1}')

plt.xlabel('X (pixels)')
plt.ylabel('Y (pixels)')
plt.title(f'Trajectories and Contact Events (<10cm >3s, first 15 min, {fps:.2f} fps)')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.axis('equal')
plt.gca().invert_yaxis()
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Contact time matrix
time_matrix = pairwise_contact_counts / fps

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(time_matrix, cmap='hot')
plt.colorbar(im, ax=ax)
ax.set_title('Total Contact Time for Each Pair (seconds)')
ax.set_xlabel('Mouse')
ax.set_ylabel('Mouse')
ax.set_xticks(range(n_subjects))
ax.set_yticks(range(n_subjects))
ax.set_xticklabels([f'Mouse {s+1}' for s in range(n_subjects)])
ax.set_yticklabels([f'Mouse {s+1}' for s in range(n_subjects)])

# Add text annotations
for row in range(n_subjects):
    for col in range(n_subjects):
        text = ax.text(col, row, f'{time_matrix[row, col]:.1f}',
                      ha="center", va="center", color="w", fontweight='bold')

plt.tight_layout()

# ==============================================================================
# Game 7: Compare Activity Levels
# ==============================================================================

print("\n" + "="*80)
print("GAME 7: Activity Levels (Speed vs Time)")
print("="*80)

dt = 1 / fps  # Time step between frames

plt.figure(figsize=(14, 8))

speed_mat = np.zeros((n_subjects, frames_15 - 1))

for s in range(n_subjects):
    xs = x[s, :frames_15]
    ys = y[s, : frames_15]
    
    dx = np.diff(xs)
    dy = np.diff(ys)
    d_pix = np.sqrt(dx**2 + dy**2)
    d_cm = d_pix / pixel_to_cm
    speed_cm_s = d_cm / dt
    
    speed_mat[s] = speed_cm_s
    
    time_vec = np.arange(1, frames_15) / fps
    plt.plot(time_vec, speed_cm_s, '-', color=mouse_cmap[s], 
            linewidth=1.5, label=f'Mouse {s+1}')

plt.xlabel('Time (seconds)')
plt.ylabel('Speed (cm/sec)')
plt.title('Mouse Speed Over Time (First 15 Min)')
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Print mean speeds
print("\nMean speed for each mouse (cm/sec, first 15 min):")
for s in range(n_subjects):
    mean_speed = np.nanmean(speed_mat[s])
    print(f"Mouse {s+1}: {mean_speed:.2f} cm/sec")

# Show all plots
plt.show()

print("\n" + "="*80)
print("Analysis complete!")
print("="*80)