"""
Test suite for Mouse Tracking Data Explorer.
Tests the analysis functions and GUI components.

To run tests:
    pytest test_data_explorer.py -v
    
Or with coverage:
    pytest test_data_explorer.py -v --cov=data_explorer_analyses --cov=data_explorer_GUI
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import data_explorer_analyses as dea


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def mock_data():
    """Create mock data for testing."""
    n_subjects = 4
    n_frames = 1000
    
    # Create mock tracking data
    tracking = Mock()
    tracking.x = np.random.rand(n_subjects, n_frames) * 500
    tracking.y = np.random.rand(n_subjects, n_frames) * 500
    tracking.zones = np.random.randint(1, 8, size=(n_subjects, n_frames))
    
    # Create mock video info
    video_info = Mock()
    video_info.FrameRate = 10.0
    video_info.NumberOfFrames = n_frames
    
    # Create mock arena
    arena = Mock()
    arena.PixelToCM = 3.0
    arena.Colormap = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], 
                               [1, 1, 0], [1, 0, 1], [0, 1, 1], [0.5, 0.5, 0.5]])
    
    # Create mock colors
    colors = Mock()
    colors.Mice = 'RBYG'
    colors.Colormap = np.array([[1, 0, 0], [0, 0, 1], [1, 1, 0], [0, 1, 0]])
    
    return {
        'tracking': tracking,
        'video_info': video_info,
        'arena': arena,
        'colors': colors,
        'n_subjects': n_subjects,
        'n_frames': n_frames
    }


@pytest.fixture
def mock_load_data(mock_data):
    """Mock the load_data function."""
    def _load_data():
        x = mock_data['tracking'].x
        y = mock_data['tracking'].y
        return (
            mock_data['tracking'],
            mock_data['video_info'],
            mock_data['arena'],
            mock_data['colors'],
            x,
            y,
            mock_data['n_subjects'],
            float(mock_data['video_info'].FrameRate)
        )
    return _load_data


# ==============================================================================
# Tests for Helper Functions
# ==============================================================================

class TestHelperFunctions:
    """Tests for utility helper functions."""
    
    def test_get_mouse_colormap_with_mice_string(self, mock_data):
        """Test colormap extraction using Mice string."""
        colors = mock_data['colors']
        n_subjects = mock_data['n_subjects']
        
        colormap = dea.get_mouse_colormap(colors, n_subjects)
        
        assert colormap.shape == (n_subjects, 3)
        assert np.all(colormap >= 0) and np.all(colormap <= 1)
        # Red should be [1, 0, 0]
        assert np.allclose(colormap[0], [1, 0, 0])
        # Blue should be [0, 0, 1]
        assert np.allclose(colormap[1], [0, 0, 1])
        # Yellow should be [1, 1, 0]
        assert np.allclose(colormap[2], [1, 1, 0])
        # Green should be [0, 1, 0]
        assert np.allclose(colormap[3], [0, 1, 0])
    
    def test_get_mouse_colormap_default(self):
        """Test colormap with minimal color object."""
        colors = Mock()
        colors.Mice = ''
        
        colormap = dea.get_mouse_colormap(colors, 4)
        
        assert colormap.shape == (4, 3)
        # Should use default RBYG colors
        assert np.allclose(colormap[0], [1, 0, 0])  # Red
        assert np.allclose(colormap[1], [0, 0, 1])  # Blue
        assert np.allclose(colormap[2], [1, 1, 0])  # Yellow
        assert np.allclose(colormap[3], [0, 1, 0])  # Green
    
    def test_get_mouse_names(self):
        """Test mouse name retrieval."""
        names = dea.get_mouse_names()
        
        assert len(names) == 4
        assert names == ['Red', 'Blue', 'Yellow', 'Green']
    
    @patch('data_explorer_analyses.Path')
    @patch('data_explorer_analyses.loadmat')
    def test_load_cheese_cube(self, mock_loadmat, mock_path):
        """Test data loading function."""
        mock_path_instance = Mock()
        mock_path.return_value = mock_path_instance
        
        test_data = {'test': 'data'}
        mock_loadmat.return_value = test_data
        
        result = dea.load_cheese_cube('test.mat')
        
        assert result == test_data
        mock_loadmat.assert_called_once()


# ==============================================================================
# Tests for Program #1: Trajectory Plot
# ==============================================================================

class TestTrajectoryPlot:
    """Tests for trajectory plotting function."""
    
    @patch('data_explorer_analyses.load_data')
    def test_basic_trajectory_plot(self, mock_load_func, mock_load_data):
        """Test basic trajectory plot without markers."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1, 2, 3]
        fig = dea.plot_trajectory(selected_mice, behavior_markers=None)
        
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_trajectory_plot_subset_mice(self, mock_load_func, mock_load_data):
        """Test trajectory plot with subset of mice."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 2]  # Only Red and Yellow
        fig = dea.plot_trajectory(selected_mice)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_trajectory_plot_custom_timeframe(self, mock_load_func, mock_load_data):
        """Test trajectory plot with custom time frame."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1]
        fig = dea.plot_trajectory(selected_mice, time_start=10, time_end=50)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_trajectory_plot_zone_markers(self, mock_load_func, mock_load_data):
        """Test trajectory plot with zone-based styling."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1]
        selected_zones = [1, 2, 3]
        fig = dea.plot_trajectory(selected_mice, behavior_markers='zone', 
                                 selected_zones=selected_zones)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_trajectory_plot_rest_markers(self, mock_load_func, mock_load_data):
        """Test trajectory plot with rest markers."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0]
        fig = dea.plot_trajectory(selected_mice, behavior_markers='rest')
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_trajectory_plot_contact_markers(self, mock_load_func, mock_load_data):
        """Test trajectory plot with contact event markers."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1]
        fig = dea.plot_trajectory(selected_mice, behavior_markers='contact')
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


# ==============================================================================
# Tests for Program #2: Contact Heat Plot
# ==============================================================================

class TestContactHeatPlot:
    """Tests for contact heatmap function."""
    
    @patch('data_explorer_analyses.load_data')
    def test_contact_heatmap_all_mice(self, mock_load_func, mock_load_data):
        """Test contact heatmap with all mice."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1, 2, 3]
        fig = dea.plot_contact_heatmap(selected_mice)
        
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_contact_heatmap_two_mice(self, mock_load_func, mock_load_data):
        """Test contact heatmap with two mice."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1]
        fig = dea.plot_contact_heatmap(selected_mice)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_contact_heatmap_custom_timeframe(self, mock_load_func, mock_load_data):
        """Test contact heatmap with custom time frame."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1, 2]
        fig = dea.plot_contact_heatmap(selected_mice, time_start=0, time_end=50)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


# ==============================================================================
# Tests for Program #3: Speed Plot
# ==============================================================================

class TestSpeedPlot:
    """Tests for speed plotting function."""
    
    @patch('data_explorer_analyses.load_data')
    def test_speed_plot_all_mice(self, mock_load_func, mock_load_data):
        """Test speed plot with all mice."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1, 2, 3]
        fig = dea.plot_speed(selected_mice)
        
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_speed_plot_single_mouse(self, mock_load_func, mock_load_data):
        """Test speed plot with single mouse."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [2]
        fig = dea.plot_speed(selected_mice)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_speed_plot_custom_timeframe(self, mock_load_func, mock_load_data):
        """Test speed plot with custom time frame."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1]
        fig = dea.plot_speed(selected_mice, time_start=5, time_end=30)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


# ==============================================================================
# Tests for Program #4: Time by Zone Plot
# ==============================================================================

class TestTimeByZonePlot:
    """Tests for time by zone plotting function."""
    
    @patch('data_explorer_analyses.load_data')
    def test_time_by_zone_all_mice(self, mock_load_func, mock_load_data):
        """Test time by zone plot with all mice."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 1, 2, 3]
        fig = dea.plot_time_by_zone(selected_mice)
        
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_time_by_zone_subset_mice(self, mock_load_func, mock_load_data):
        """Test time by zone plot with subset of mice."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [0, 2]
        fig = dea.plot_time_by_zone(selected_mice)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @patch('data_explorer_analyses.load_data')
    def test_time_by_zone_custom_timeframe(self, mock_load_func, mock_load_data):
        """Test time by zone plot with custom time frame."""
        mock_load_func.return_value = mock_load_data()
        
        selected_mice = [1, 2, 3]
        fig = dea.plot_time_by_zone(selected_mice, time_start=10, time_end=100)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


# ==============================================================================
# Tests for GUI Components
# ==============================================================================

class TestGUI:
    """Tests for GUI functionality."""
    
    def test_gui_initialization(self):
        """Test GUI initializes without errors."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            gui = MouseDataExplorerGUI(root)
            
            assert gui.mouse_names == ['Red', 'Blue', 'Yellow', 'Green']
            assert len(gui.zone_names) == 11
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_get_selected_mice(self):
        """Test mouse selection retrieval."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            gui = MouseDataExplorerGUI(root)
            
            # Initially all should be selected
            selected = gui.get_selected_mice()
            assert selected == [0, 1, 2, 3]
            
            # Deselect some mice
            gui.mouse_vars[1].set(False)
            gui.mouse_vars[3].set(False)
            selected = gui.get_selected_mice()
            assert selected == [0, 2]
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_get_selected_zones(self):
        """Test zone selection retrieval."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            gui = MouseDataExplorerGUI(root)
            
            # Initially all should be selected
            selected = gui.get_selected_zones()
            assert len(selected) == 11
            assert selected[0] == 1  # Zone IDs are 1-based
            
            # Deselect some zones
            gui.zone_vars[0].set(False)
            gui.zone_vars[5].set(False)
            selected = gui.get_selected_zones()
            assert 1 not in selected
            assert 6 not in selected
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_time_range_validation_valid(self):
        """Test valid time range inputs."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            gui = MouseDataExplorerGUI(root)
            
            gui.start_time_var.set("0")
            gui.end_time_var.set("300")
            
            start, end = gui.get_time_range()
            assert start == 0.0
            assert end == 300.0
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_time_range_validation_invalid(self):
        """Test invalid time range inputs."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            gui = MouseDataExplorerGUI(root)
            
            # Invalid: end < start
            gui.start_time_var.set("500")
            gui.end_time_var.set("100")
            
            with patch('data_explorer_GUI.messagebox.showerror'):
                start, end = gui.get_time_range()
                assert start is None
                assert end is None
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_parameter_visibility_trajectory(self):
        """Test parameter visibility for trajectory program."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.update()  # Process pending events
            gui = MouseDataExplorerGUI(root)
            root.update()  # Process pending events
            
            gui.program_var.set("trajectory")
            gui.update_parameter_visibility()
            root.update()  # Process pending events
            
            # Time frame should be visible (check if packed)
            assert gui.time_frame.winfo_manager() == 'pack'
            # Behavior frame should be visible
            assert gui.behavior_frame.winfo_manager() == 'pack'
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_parameter_visibility_contact_heat(self):
        """Test parameter visibility for contact heat program."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.update()
            gui = MouseDataExplorerGUI(root)
            root.update()
            
            gui.program_var.set("contact_heat")
            gui.update_parameter_visibility()
            root.update()
            
            # Time frame should be visible (check if packed)
            assert gui.time_frame.winfo_manager() == 'pack'
            # Behavior frame should not be visible
            assert gui.behavior_frame.winfo_manager() == ''
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_zone_visibility_toggle(self):
        """Test zone selection visibility toggle."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.update()
            gui = MouseDataExplorerGUI(root)
            root.update()
            
            # Initially should not be visible
            gui.behavior_var.set("none")
            gui.update_zone_visibility()
            root.update()
            assert gui.zone_selection_frame.winfo_manager() == ''
            
            # Should be visible when zone is selected
            gui.behavior_var.set("zone")
            gui.update_zone_visibility()
            root.update()
            assert gui.zone_selection_frame.winfo_manager() == 'pack'
            
            # Should be hidden for other options
            gui.behavior_var.set("rest")
            gui.update_zone_visibility()
            root.update()
            assert gui.zone_selection_frame.winfo_manager() == ''
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")
    
    def test_timeframe_default_updates(self):
        """Test that timeframe defaults update based on program selection."""
        from data_explorer_GUI import MouseDataExplorerGUI
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            gui = MouseDataExplorerGUI(root)
            
            # Trajectory should use 300s default
            gui.program_var.set("trajectory")
            gui.update_parameter_visibility()
            assert gui.end_time_var.get() == "300"
            assert "5 minutes" in gui.time_label.cget("text")
            
            # Contact heat should use 3600s default
            gui.program_var.set("contact_heat")
            gui.update_parameter_visibility()
            assert gui.end_time_var.get() == "3600"
            assert "1 hour" in gui.time_label.cget("text")
            
            # Speed should use 300s default
            gui.program_var.set("speed")
            gui.update_parameter_visibility()
            assert gui.end_time_var.get() == "300"
            assert "5 minutes" in gui.time_label.cget("text")
            
            # Time zone should use 3600s default
            gui.program_var.set("time_zone")
            gui.update_parameter_visibility()
            assert gui.end_time_var.get() == "3600"
            assert "1 hour" in gui.time_label.cget("text")
            
            root.destroy()
        except tk.TclError as e:
            pytest.skip(f"Tkinter not properly configured: {e}")


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestIntegration:
    """Integration tests using real data if available."""
    
    def test_data_file_exists(self):
        """Test if the data file exists."""
        data_file = Path(r"data\mouse_data_v7.mat")
        
        if data_file.exists():
            assert data_file.is_file()
            assert data_file.suffix == '.mat'
        else:
            pytest.skip("Data file not found - skipping integration test")
    
    @pytest.mark.skipif(not Path(r"data\mouse_data_v7.mat").exists(), 
                       reason="Data file not available")
    def test_load_real_data(self):
        """Test loading real data file."""
        tracking, video_info, arena, colors, x, y, n_subjects, fps = dea.load_data()
        
        assert x.shape[0] == n_subjects
        assert y.shape[0] == n_subjects
        assert x.shape == y.shape
        assert fps > 0
        assert n_subjects > 0
    
    @pytest.mark.skipif(not Path(r"data\mouse_data_v7.mat").exists(), 
                       reason="Data file not available")
    def test_real_trajectory_plot(self):
        """Test trajectory plot with real data."""
        selected_mice = [0, 1]
        fig = dea.plot_trajectory(selected_mice, time_start=0, time_end=30)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    @pytest.mark.skipif(not Path(r"data\mouse_data_v7.mat").exists(), 
                       reason="Data file not available")
    def test_real_contact_heatmap(self):
        """Test contact heatmap with real data."""
        selected_mice = [0, 1, 2, 3]
        fig = dea.plot_contact_heatmap(selected_mice, time_start=0, time_end=60)
        
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


# ==============================================================================
# Run Tests
# ==============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
