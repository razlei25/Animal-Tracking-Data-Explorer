"""
Analysis functions for mouse tracking data.
Based on code from data_explorer_games.py

These functions provide various analysis capabilities for visualizing
and analyzing multi-mouse behavioral tracking data.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from scipy.io import loadmat
from scipy.ndimage import label


# ==============================================================================
# Helper Functions (shared across all programs)
# ==============================================================================

def load_cheese_cube(mat_file_path):
    """
    Load CheeseCube data from .mat file.
    
    Parameters:
    -----------
    mat_file_path : str or Path
        Path to the .mat file containing experiment data
    
    Returns:
    --------
    dict : Dictionary containing all loaded data
    """
    data = loadmat(mat_file_path, struct_as_record=False, squeeze_me=True)
    return data


def get_mouse_colormap(colors_obj, n_subjects):
    """
    Extract mouse colormap from colors object, handling various formats.
    
    Parameters:
    -----------
    colors_obj : various
        Colors object/struct from the data
    n_subjects : int
        Number of subjects/mice
    
    Returns:
    --------
    numpy.ndarray : n_subjects x 3 RGB colormap (values 0-1)
    """
    letter_map = {
        'R': [1, 0, 0], 'G': [0, 1, 0], 'B': [0, 0, 1], 'Y': [1, 1, 0],
        'C': [0, 1, 1], 'M': [1, 0, 1], 'K': [0, 0, 0], 'W': [1, 1, 1]
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
            numeric_map = np.array(colors_obj.Colormap, dtype=float)
        elif hasattr(colors_obj, 'colormap'):
            numeric_map = np.array(colors_obj.colormap, dtype=float)
            
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
            ch = mice_str[s].upper()
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


def load_data():
    """
    Load and prepare mouse tracking data.
    
    Returns:
    --------
    tuple : (tracking, video_info, arena, colors, x, y, n_subjects, fps)
    """
    data_file = Path(r"data\mouse_data_v7.mat")
    
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    cube_day1 = load_cheese_cube(data_file)
    
    # Extract main components
    tracking = cube_day1.get('Tracking', None)
    video_info = cube_day1.get('Video', None)
    arena = cube_day1.get('ROI', None)
    colors = cube_day1.get('Colors', None)
    
    # Extract tracking data
    x = np.array(tracking.x, dtype=float)
    y = np.array(tracking.y, dtype=float)
    n_subjects = x.shape[0]
    fps = float(video_info.FrameRate)
    
    return tracking, video_info, arena, colors, x, y, n_subjects, fps


def get_mouse_names():
    """Return the standard mouse names based on their colors."""
    return ['Red', 'Blue', 'Yellow', 'Green']


# ==============================================================================
# Program #1: Trajectory Plot
# ==============================================================================

def plot_trajectory(selected_mice, time_start=0, time_end=300, 
                   behavior_markers=None, selected_zones=None):
    """
    Plot mouse trajectories with optional behavior markers.
    
    Parameters:
    -----------
    selected_mice : list of int
        Indices of mice to plot (0=Red, 1=Blue, 2=Yellow, 3=Green)
    time_start : float
        Start time in seconds (default: 0)
    time_end : float
        End time in seconds (default: 300 = 5 minutes)
    behavior_markers : str or None
        Type of markers to add: 'zone', 'rest', 'contact', or None
    selected_zones : list of int or None
        Zone IDs to highlight (only used if behavior_markers='zone')
    
    Returns:
    --------
    matplotlib.figure.Figure : The created figure
    """
    # Load data
    tracking, video_info, arena, colors, x, y, n_subjects, fps = load_data()
    
    # Calculate frame range
    frame_start = int(time_start * fps)
    frame_end = min(int(time_end * fps), x.shape[1])
    
    # Get mouse colormap
    mouse_cmap = get_mouse_colormap(colors, n_subjects)
    mouse_names = get_mouse_names()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 12))
    
    if behavior_markers == 'zone':
        # Zone-based styling
        zones = np.array(tracking.zones, dtype=float)
        
        # Real zone names
        real_zone_names = [
            'Open', 'Feeder1', 'Feeder2', 'Water', 'SmallNest',
            'Labyrinth', 'BigNest', 'Block', '[Ramp1]', '[Ramp2]', 'Water2'
        ]
        
        # Line styles for zones
        line_styles = ['-', '--', ':', '-.']
        zone_style_map = {}
        
        if selected_zones is None:
            # Get all unique zones
            if zones.ndim == 1:
                zone_vals = np.unique(zones[frame_start:frame_end])
            else:
                zone_vals = np.unique(zones[:, frame_start:frame_end])
            zone_vals = zone_vals[zone_vals > 0]
        else:
            zone_vals = np.array(selected_zones)
        
        for i, zid in enumerate(zone_vals):
            zone_style_map[zid] = line_styles[i % len(line_styles)]
        
        # Plot each mouse
        for s in selected_mice:
            xs = x[s, frame_start:frame_end]
            ys = y[s, frame_start:frame_end]
            
            if zones.ndim == 1:
                zs = zones[frame_start:frame_end]
            else:
                zs = zones[s, frame_start:frame_end]
            
            zs[zs == 0] = np.nan
            
            # Find zone transitions
            zone_changes = np.concatenate(([0], np.where(np.diff(zs) != 0)[0] + 1, [len(zs)]))
            
            for k in range(len(zone_changes) - 1):
                idx1 = zone_changes[k]
                idx2 = zone_changes[k + 1]
                
                zone_id = zs[idx1]
                if np.isnan(zone_id):
                    continue
                
                style = zone_style_map.get(zone_id, '-')
                ax.plot(xs[idx1:idx2], ys[idx1:idx2], 
                       style, color=mouse_cmap[s], linewidth=1.5)
        
        # Create legend
        from matplotlib.lines import Line2D
        legend_elements = []
        
        # Zone styles
        zone_labels = []
        for zid in zone_vals:
            zid_int = int(zid)
            if zid_int <= len(real_zone_names):
                zone_labels.append(real_zone_names[zid_int - 1])
            else:
                zone_labels.append(f'Zone {zid_int}')
        
        for i, zid in enumerate(zone_vals):
            legend_elements.append(Line2D([0], [0], color='black', 
                                         linestyle=zone_style_map[zid],
                                         linewidth=1.5, label=zone_labels[i]))
        
        # Mouse colors
        for s in selected_mice:
            legend_elements.append(Line2D([0], [0], color=mouse_cmap[s], 
                                         linewidth=2, label=f'{mouse_names[s]} Mouse'))
        
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_title(f'Zone-Styled Trajectories ({time_start:.1f}s - {time_end:.1f}s)')
    
    elif behavior_markers == 'rest':
        # Plot trajectories with rest markers
        window_seconds = 5
        window_frames = int(np.round(window_seconds * fps))
        rest_threshold_cm = 1.0
        
        # Get pixel to cm conversion
        pixel_to_cm = 3.0  # default
        if hasattr(arena, 'PixelToCM'):
            pixel_to_cm = float(arena.PixelToCM)
        elif hasattr(arena, 'pixelToCM'):
            pixel_to_cm = float(arena.pixelToCM)
        
        for s in selected_mice:
            xs = x[s, frame_start:frame_end]
            ys = y[s, frame_start:frame_end]
            
            # Plot main trajectory
            ax.plot(xs, ys, '-', color=mouse_cmap[s], linewidth=2, 
                   label=f'{mouse_names[s]} Mouse')
            
            # Calculate rolling movement
            movement_cm = np.full(len(xs), np.nan)
            for idx in range(window_frames, len(xs)):
                window_x = xs[idx - window_frames:idx]
                window_y = ys[idx - window_frames:idx]
                dx = np.diff(window_x)
                dy = np.diff(window_y)
                d_pix = np.sqrt(dx**2 + dy**2)
                movement_cm[idx] = np.sum(d_pix) / pixel_to_cm
            
            # Find resting periods
            is_resting = movement_cm < rest_threshold_cm
            rest_idx = np.where(is_resting)[0]
            
            # Plot resting markers
            ax.plot(xs[rest_idx], ys[rest_idx], '^', 
                   color=mouse_cmap[s], markersize=9, 
                   markerfacecolor=mouse_cmap[s])
        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_title(f'Trajectories with Rest Markers ({time_start:.1f}s - {time_end:.1f}s)')
    
    elif behavior_markers == 'contact':
        # Plot trajectories with contact event markers
        contact_thresh_cm = 10.0
        min_contact_frames = int(np.round(3 * fps))
        
        # Get pixel to cm conversion
        pixel_to_cm = 3.0  # default
        if hasattr(arena, 'PixelToCM'):
            pixel_to_cm = float(arena.PixelToCM)
        elif hasattr(arena, 'pixelToCM'):
            pixel_to_cm = float(arena.pixelToCM)
        
        # Distinct marker colors and types
        marker_list = ['o', 's', 'D', '^', '+', '*', 'x', '>', '<', 'v', 'p', 'h']
        distinct_contact_colors = np.array([
            [0, 0, 0],      # black
            [1, 0, 1],      # magenta
            [0, 1, 1],      # cyan
            [1, 0.5, 0],    # orange
            [0.5, 0, 0.5],  # purple
            [0.5, 0.25, 0], # brown
        ])
        
        # Plot trajectories
        for s in selected_mice:
            xs = x[s, frame_start:frame_end]
            ys = y[s, frame_start:frame_end]
            ax.plot(xs, ys, '-', color=mouse_cmap[s], linewidth=2, 
                   label=f'{mouse_names[s]} Mouse')
        
        # Detect and plot contact events
        from itertools import combinations
        pairs = list(combinations(selected_mice, 2))
        
        for idx, (i, j) in enumerate(pairs):
            xi = x[i, frame_start:frame_end]
            yi = y[i, frame_start:frame_end]
            xj = x[j, frame_start:frame_end]
            yj = y[j, frame_start:frame_end]
            
            dist_pix = np.sqrt((xi - xj)**2 + (yi - yj)**2)
            dist_cm = dist_pix / pixel_to_cm
            is_contact = dist_cm < contact_thresh_cm
            
            # Label connected components
            labeled, num_features = label(is_contact)
            contact_frames = []
            
            for seg in range(1, num_features + 1):
                fr_idx = np.where(labeled == seg)[0]
                if len(fr_idx) >= min_contact_frames:
                    contact_frames.extend(fr_idx.tolist())
            
            if contact_frames:
                xs_i = xi[contact_frames]
                ys_i = yi[contact_frames]
                
                marker_type = marker_list[idx % len(marker_list)]
                contact_color = distinct_contact_colors[idx % len(distinct_contact_colors)]
                
                ax.plot(xs_i, ys_i, marker_type, 
                       color=contact_color, markersize=9, linewidth=1.5,
                       markerfacecolor=contact_color,
                       label=f'Contact: {mouse_names[i]} & {mouse_names[j]}')
        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_title(f'Trajectories with Contact Events ({time_start:.1f}s - {time_end:.1f}s)')
    
    else:
        # Simple trajectory plot
        for s in selected_mice:
            xs = x[s, frame_start:frame_end]
            ys = y[s, frame_start:frame_end]
            ax.plot(xs, ys, '-', color=mouse_cmap[s], linewidth=1.5, 
                   label=f'{mouse_names[s]} Mouse')
        
        ax.legend(loc='best')
        ax.set_title(f'Mouse Trajectories ({time_start:.1f}s - {time_end:.1f}s)')
    
    ax.axis('equal')
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig


# ==============================================================================
# Program #2: Contact Heat Plot
# ==============================================================================

def plot_contact_heatmap(selected_mice, time_start=0, time_end=None):
    """
    Create a heatmap showing contact time between pairs of mice.
    
    Parameters:
    -----------
    selected_mice : list of int
        Indices of mice to include (0=Red, 1=Blue, 2=Yellow, 3=Green)
    time_start : float
        Start time in seconds (default: 0)
    time_end : float or None
        End time in seconds (default: None = entire recording)
    
    Returns:
    --------
    matplotlib.figure.Figure : The created figure
    """
    # Load data
    tracking, video_info, arena, colors, x, y, n_subjects, fps = load_data()
    
    # Calculate frame range
    frame_start = int(time_start * fps)
    if time_end is None:
        frame_end = x.shape[1]
    else:
        frame_end = min(int(time_end * fps), x.shape[1])
    
    # Parameters
    contact_thresh_cm = 10.0
    min_contact_frames = int(np.round(3 * fps))
    
    # Get pixel to cm conversion
    pixel_to_cm = 3.0  # default
    if hasattr(arena, 'PixelToCM'):
        pixel_to_cm = float(arena.PixelToCM)
    elif hasattr(arena, 'pixelToCM'):
        pixel_to_cm = float(arena.pixelToCM)
    
    # Initialize contact matrix for selected mice
    n_selected = len(selected_mice)
    pairwise_contact_counts = np.zeros((n_selected, n_selected))
    
    # Generate all pairs from selected mice
    from itertools import combinations
    pairs = list(combinations(range(n_selected), 2))
    
    # Detect contacts
    for (i_idx, j_idx) in pairs:
        i = selected_mice[i_idx]
        j = selected_mice[j_idx]
        
        xi = x[i, frame_start:frame_end]
        yi = y[i, frame_start:frame_end]
        xj = x[j, frame_start:frame_end]
        yj = y[j, frame_start:frame_end]
        
        dist_pix = np.sqrt((xi - xj)**2 + (yi - yj)**2)
        dist_cm = dist_pix / pixel_to_cm
        is_contact = dist_cm < contact_thresh_cm
        
        # Label connected components
        labeled, num_features = label(is_contact)
        contact_frame_count = 0
        
        for seg in range(1, num_features + 1):
            fr_idx = np.where(labeled == seg)[0]
            if len(fr_idx) >= min_contact_frames:
                contact_frame_count += len(fr_idx)
        
        pairwise_contact_counts[i_idx, j_idx] = contact_frame_count
        pairwise_contact_counts[j_idx, i_idx] = contact_frame_count
    
    # Convert to time
    time_matrix = pairwise_contact_counts / fps
    
    # Create heatmap
    mouse_names = get_mouse_names()
    selected_names = [mouse_names[i] for i in selected_mice]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(time_matrix, cmap='hot')
    plt.colorbar(im, ax=ax, label='Contact Time (seconds)')
    
    if time_end is None:
        time_end_display = frame_end / fps
    else:
        time_end_display = time_end
    ax.set_title(f'Total Contact Time for Each Pair ({time_start:.1f}s - {time_end_display:.1f}s)')
    ax.set_xlabel('Mouse')
    ax.set_ylabel('Mouse')
    ax.set_xticks(range(n_selected))
    ax.set_yticks(range(n_selected))
    ax.set_xticklabels(selected_names)
    ax.set_yticklabels(selected_names)
    
    # Add text annotations
    for row in range(n_selected):
        for col in range(n_selected):
            text = ax.text(col, row, f'{time_matrix[row, col]:.1f}',
                          ha="center", va="center", color="w", fontweight='bold')
    
    plt.tight_layout()
    return fig


# ==============================================================================
# Program #3: Speed Plot
# ==============================================================================

def plot_speed(selected_mice, time_start=0, time_end=300):
    """
    Plot mouse speed over time.
    
    Parameters:
    -----------
    selected_mice : list of int
        Indices of mice to plot (0=Red, 1=Blue, 2=Yellow, 3=Green)
    time_start : float
        Start time in seconds (default: 0)
    time_end : float
        End time in seconds (default: 300 = 5 minutes)
    
    Returns:
    --------
    matplotlib.figure.Figure : The created figure
    """
    # Load data
    tracking, video_info, arena, colors, x, y, n_subjects, fps = load_data()
    
    # Calculate frame range
    frame_start = int(time_start * fps)
    frame_end = min(int(time_end * fps), x.shape[1])
    
    # Get pixel to cm conversion
    pixel_to_cm = 3.0  # default
    if hasattr(arena, 'PixelToCM'):
        pixel_to_cm = float(arena.PixelToCM)
    elif hasattr(arena, 'pixelToCM'):
        pixel_to_cm = float(arena.pixelToCM)
    
    # Get mouse colormap
    mouse_cmap = get_mouse_colormap(colors, n_subjects)
    mouse_names = get_mouse_names()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    dt = 1 / fps  # Time step between frames
    
    for s in selected_mice:
        xs = x[s, frame_start:frame_end]
        ys = y[s, frame_start:frame_end]
        
        dx = np.diff(xs)
        dy = np.diff(ys)
        d_pix = np.sqrt(dx**2 + dy**2)
        d_cm = d_pix / pixel_to_cm
        speed_cm_s = d_cm / dt
        
        time_vec = time_start + np.arange(1, len(xs)) / fps
        ax.plot(time_vec, speed_cm_s, '-', color=mouse_cmap[s], 
               linewidth=1.5, label=f'{mouse_names[s]} Mouse')
    
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Speed (cm/sec)')
    ax.set_title(f'Mouse Speed Over Time ({time_start:.1f}s - {time_end:.1f}s)')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return fig


# ==============================================================================
# Program #4: Time by Zone Plot
# ==============================================================================

def plot_time_by_zone(selected_mice, time_start=0, time_end=3600):
    """
    Plot time spent in each zone as a bar chart.
    
    Parameters:
    -----------
    selected_mice : list of int
        Indices of mice to plot (0=Red, 1=Blue, 2=Yellow, 3=Green)
    time_start : float
        Start time in seconds (default: 0)
    time_end : float
        End time in seconds (default: 3600 = 1 hour)
    
    Returns:
    --------
    matplotlib.figure.Figure : The created figure
    """
    # Load data
    tracking, video_info, arena, colors, x, y, n_subjects, fps = load_data()
    
    # Calculate frame range
    frame_start = int(time_start * fps)
    frame_end = min(int(time_end * fps), x.shape[1])
    
    # Get zones
    zones = np.array(tracking.zones, dtype=float)
    
    # Real zone names
    real_zone_names = [
        'Open', 'Feeder1', 'Feeder2', 'Water', 'SmallNest',
        'Labyrinth', 'BigNest', 'Block', '[Ramp1]', '[Ramp2]', 'Water2'
    ]
    
    # Get unique zones
    if zones.ndim == 1:
        zone_vals = np.unique(zones[frame_start:frame_end])
    else:
        zone_vals = np.unique(zones[:, frame_start:frame_end])
    
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
    
    # Calculate time spent in each zone for selected mice
    mouse_names = get_mouse_names()
    selected_names = [mouse_names[i] for i in selected_mice]
    n_selected = len(selected_mice)
    
    zone_times = np.zeros((n_selected, n_zones))
    
    for idx, s in enumerate(selected_mice):
        if zones.ndim == 1:
            zs = zones[frame_start:frame_end]
        else:
            zs = zones[s, frame_start:frame_end]
        
        for k, zone_id in enumerate(zone_vals):
            zone_times[idx, k] = np.sum(zs == zone_id) / fps
    
    # Stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    bottom = np.zeros(n_selected)
    
    for k in range(n_zones):
        color = zone_cmap[k % len(zone_cmap)]
        ax.bar(range(n_selected), zone_times[:, k], bottom=bottom,
               color=color, label=zone_labels[k])
        bottom += zone_times[:, k]
    
    ax.set_xlabel('Mouse')
    ax.set_ylabel('Time Spent (seconds)')
    ax.set_title(f'Time Spent in Each Zone by Mouse ({time_start:.1f}s - {time_end:.1f}s)')
    ax.set_xticks(range(n_selected))
    ax.set_xticklabels(selected_names)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    return fig


if __name__ == '__main__':
    # Test the functions
    print("Testing analysis functions...")
    
    # Test with all mice
    all_mice = [0, 1, 2, 3]
    
    print("Testing trajectory plot...")
    plot_trajectory(all_mice)
    
    print("Testing contact heatmap...")
    plot_contact_heatmap(all_mice)
    
    print("Testing speed plot...")
    plot_speed(all_mice)
    
    print("Testing time by zone plot...")
    plot_time_by_zone(all_mice)
    
    plt.show()
    print("All tests complete!")
