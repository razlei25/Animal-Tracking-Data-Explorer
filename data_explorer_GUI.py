"""
GUI for Mouse Tracking Data Analysis.
Provides a user interface to run various analysis programs on mouse tracking data.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import data_explorer_analyses as dea


class MouseDataExplorerGUI:
    """Main GUI application for mouse data analysis."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracking Data Explorer")
        self.root.geometry("1200x800")
        
        # Mouse names and indices
        self.mouse_names = ['Red', 'Blue', 'Yellow', 'Green']
        self.zone_names = [
            'Open', 'Feeder1', 'Feeder2', 'Water', 'SmallNest',
            'Labyrinth', 'BigNest', 'Block', '[Ramp1]', '[Ramp2]', 'Water2'
        ]
        
        # Create main layout
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with two panes
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - controls
        left_frame = ttk.Frame(main_pane, width=400)
        main_pane.add(left_frame, weight=1)
        
        # Right panel - plot display
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=3)
        
        # Create control panel
        self.create_control_panel(left_frame)
        
        # Create plot panel
        self.create_plot_panel(right_frame)
        
    def create_control_panel(self, parent):
        """Create the control panel with program selection and parameters."""
        # Make the parent scrollable
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Analysis Programs", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Program Selection
        program_frame = ttk.LabelFrame(scrollable_frame, text="Select Program", padding=10)
        program_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.program_var = tk.StringVar(value="trajectory")
        
        programs = [
            ("1. Trajectory Plot", "trajectory"),
            ("2. Contact Heat Plot", "contact_heat"),
            ("3. Speed Plot", "speed"),
            ("4. Time by Zone Plot", "time_zone")
        ]
        
        for text, value in programs:
            rb = ttk.Radiobutton(program_frame, text=text, variable=self.program_var, 
                                value=value, command=self.update_parameter_visibility)
            rb.pack(anchor=tk.W, pady=2)
        
        # Mouse Selection (common to all programs)
        self.create_mouse_selection(scrollable_frame)
        
        # Time Frame Selection (for programs 1, 3, 4)
        self.create_time_frame_selection(scrollable_frame)
        
        # Behavior Markers (for program 1 only)
        self.create_behavior_markers_selection(scrollable_frame)
        
        # Run Button
        run_button = ttk.Button(scrollable_frame, text="Run Analysis", 
                               command=self.run_analysis, style='Accent.TButton')
        run_button.pack(pady=20, padx=10, fill=tk.X)
        
        # Clear Button
        clear_button = ttk.Button(scrollable_frame, text="Clear Plot", 
                                 command=self.clear_plot)
        clear_button.pack(pady=5, padx=10, fill=tk.X)
        
    def create_mouse_selection(self, parent):
        """Create mouse selection checkboxes."""
        self.mouse_frame = ttk.LabelFrame(parent, text="Select Mice", padding=10)
        self.mouse_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mouse_vars = []
        colors = ['red', 'blue', 'yellow', 'green']
        
        for i, name in enumerate(self.mouse_names):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.mouse_frame, text=f"{name} Mouse", variable=var)
            cb.pack(anchor=tk.W, pady=2)
            self.mouse_vars.append(var)
        
    def create_time_frame_selection(self, parent):
        """Create time frame input fields."""
        self.time_frame = ttk.LabelFrame(parent, text="Time Frame (seconds)", padding=10)
        self.time_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Start time
        start_frame = ttk.Frame(self.time_frame)
        start_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_frame, text="Start:").pack(side=tk.LEFT)
        self.start_time_var = tk.StringVar(value="0")
        start_entry = ttk.Entry(start_frame, textvariable=self.start_time_var, width=15)
        start_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # End time
        end_frame = ttk.Frame(self.time_frame)
        end_frame.pack(fill=tk.X, pady=2)
        ttk.Label(end_frame, text="End:").pack(side=tk.LEFT)
        self.end_time_var = tk.StringVar(value="300")
        end_entry = ttk.Entry(end_frame, textvariable=self.end_time_var, width=15)
        end_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.time_label = ttk.Label(self.time_frame, text="(Default: 0-300s = 5 minutes)", 
                 font=('Arial', 8, 'italic'))
        self.time_label.pack(pady=2)
        
    def create_behavior_markers_selection(self, parent):
        """Create behavior markers selection (for trajectory plot only)."""
        self.behavior_frame = ttk.LabelFrame(parent, text="Behavior Markers (Trajectory Only)", 
                                            padding=10)
        self.behavior_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.behavior_var = tk.StringVar(value="none")
        
        # Radio buttons for behavior type
        behaviors = [
            ("None", "none"),
            ("Zone-based styling", "zone"),
            ("Rest markers", "rest"),
            ("Contact events", "contact")
        ]
        
        for text, value in behaviors:
            rb = ttk.Radiobutton(self.behavior_frame, text=text, 
                                variable=self.behavior_var, value=value,
                                command=self.update_zone_visibility)
            rb.pack(anchor=tk.W, pady=2)
        
        # Zone selection (only visible when zone is selected)
        self.zone_selection_frame = ttk.Frame(self.behavior_frame)
        self.zone_selection_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.zone_selection_frame, text="Select Zones to Highlight:", 
                 font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        # Create scrollable zone selection
        zone_canvas = tk.Canvas(self.zone_selection_frame, height=150)
        zone_scrollbar = ttk.Scrollbar(self.zone_selection_frame, orient="vertical", 
                                       command=zone_canvas.yview)
        self.zone_checkboxes_frame = ttk.Frame(zone_canvas)
        
        self.zone_checkboxes_frame.bind(
            "<Configure>",
            lambda e: zone_canvas.configure(scrollregion=zone_canvas.bbox("all"))
        )
        
        zone_canvas.create_window((0, 0), window=self.zone_checkboxes_frame, anchor="nw")
        zone_canvas.configure(yscrollcommand=zone_scrollbar.set)
        
        self.zone_vars = []
        for i, zone_name in enumerate(self.zone_names):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.zone_checkboxes_frame, text=zone_name, variable=var)
            cb.pack(anchor=tk.W, pady=1)
            self.zone_vars.append(var)
        
        zone_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        zone_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initially hide zone selection
        self.zone_selection_frame.pack_forget()
        
    def create_plot_panel(self, parent):
        """Create the plot display panel."""
        # Title
        title_label = ttk.Label(parent, text="Analysis Results", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Plot frame
        self.plot_frame = ttk.Frame(parent)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initial message
        self.info_label = ttk.Label(self.plot_frame, 
                                    text="Select a program and click 'Run Analysis' to display results",
                                    font=('Arial', 11))
        self.info_label.pack(expand=True)
        
        self.canvas = None
        
    def update_parameter_visibility(self):
        """Update which parameter sections are visible based on selected program."""
        program = self.program_var.get()
        
        # Time frame is used by programs 1, 2, 3, 4
        if program in ["trajectory", "contact_heat", "speed", "time_zone"]:
            self.time_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Update default timeframe based on program
            if program in ["trajectory", "speed"]:
                # 5 minutes for trajectory and speed
                if self.end_time_var.get() in ["300", "3600"]:
                    self.end_time_var.set("300")
                self.time_label.config(text="(Default: 0-300s = 5 minutes)")
            else:  # contact_heat, time_zone
                # 1 hour for contact heat and time by zone
                if self.end_time_var.get() in ["300", "3600"]:
                    self.end_time_var.set("3600")
                self.time_label.config(text="(Default: 0-3600s = 1 hour)")
        else:
            self.time_frame.pack_forget()
        
        # Behavior markers only for trajectory
        if program == "trajectory":
            self.behavior_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.behavior_frame.pack_forget()
            
    def update_zone_visibility(self):
        """Show/hide zone selection based on behavior marker choice."""
        if self.behavior_var.get() == "zone":
            self.zone_selection_frame.pack(fill=tk.X, pady=5)
        else:
            self.zone_selection_frame.pack_forget()
            
    def get_selected_mice(self):
        """Get list of selected mouse indices."""
        selected = []
        for i, var in enumerate(self.mouse_vars):
            if var.get():
                selected.append(i)
        return selected
    
    def get_selected_zones(self):
        """Get list of selected zone IDs (1-based)."""
        selected = []
        for i, var in enumerate(self.zone_vars):
            if var.get():
                selected.append(i + 1)  # Zone IDs are 1-based
        return selected
    
    def get_time_range(self):
        """Get time range from inputs."""
        try:
            start = float(self.start_time_var.get())
            end = float(self.end_time_var.get())
            
            if start < 0 or end <= start:
                raise ValueError("Invalid time range")
            
            return start, end
        except ValueError as e:
            messagebox.showerror("Invalid Input", 
                               "Please enter valid time values (end > start >= 0)")
            return None, None
    
    def clear_plot(self):
        """Clear the current plot."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        
        self.info_label = ttk.Label(self.plot_frame, 
                                   text="Select a program and click 'Run Analysis' to display results",
                                   font=('Arial', 11))
        self.info_label.pack(expand=True)
        
    def run_analysis(self):
        """Run the selected analysis program."""
        # Get selected mice
        selected_mice = self.get_selected_mice()
        if not selected_mice:
            messagebox.showwarning("No Mice Selected", 
                                 "Please select at least one mouse to analyze")
            return
        
        # Get program
        program = self.program_var.get()
        
        try:
            # Clear previous plot
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            if hasattr(self, 'info_label') and self.info_label:
                self.info_label.destroy()
            
            # Run appropriate analysis
            fig = None
            
            if program == "trajectory":
                # Get time range
                start, end = self.get_time_range()
                if start is None:
                    return
                
                # Get behavior markers
                behavior = self.behavior_var.get()
                if behavior == "none":
                    behavior = None
                
                # Get selected zones if needed
                selected_zones = None
                if behavior == "zone":
                    selected_zones = self.get_selected_zones()
                    if not selected_zones:
                        messagebox.showwarning("No Zones Selected", 
                                             "Please select at least one zone to highlight")
                        return
                
                fig = dea.plot_trajectory(selected_mice, start, end, behavior, selected_zones)
                
            elif program == "contact_heat":
                if len(selected_mice) < 2:
                    messagebox.showwarning("Not Enough Mice", 
                                         "Please select at least 2 mice for contact analysis")
                    return
                # Get time range
                start, end = self.get_time_range()
                if start is None:
                    return
                fig = dea.plot_contact_heatmap(selected_mice, start, end)
                
            elif program == "speed":
                # Get time range
                start, end = self.get_time_range()
                if start is None:
                    return
                fig = dea.plot_speed(selected_mice, start, end)
                
            elif program == "time_zone":
                # Get time range
                start, end = self.get_time_range()
                if start is None:
                    return
                fig = dea.plot_time_by_zone(selected_mice, start, end)
            
            # Display the plot
            if fig:
                self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Close the matplotlib figure to free memory
                # (the canvas keeps a reference)
                plt.close(fig)
                
        except FileNotFoundError as e:
            messagebox.showerror("Data File Not Found", 
                               f"Could not find data file:\n{str(e)}\n\n"
                               "Please ensure the data file is in the correct location.")
        except Exception as e:
            messagebox.showerror("Analysis Error", 
                               f"An error occurred during analysis:\n{str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')  # Use a modern theme
    
    # Create and run the application
    app = MouseDataExplorerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
