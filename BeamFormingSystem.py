# # BeamFormingSystem.py
import numpy as np

import matplotlib.pyplot as plt
from phased_array import initialize_simulation_grid, compute_wave_pattern, compute_beam_profile
#
# class BeamForming:
#     def __init__(self, fig, ax, initial_state):
#         self.fig = fig
#         self.ax = ax
#         self.state = initial_state
#
#         # Initialize the grid
#         self.grid, self.wavelength = initialize_simulation_grid(
#             self.state['N'], self.state['f'], self.state['distance']
#         )
#         self.update_wave_pattern()
#
#     def update_wave_pattern(self):
#         self.Z, self.positions = compute_wave_pattern(
#             self.state['N'], self.state['f'], self.state['dir'], self.state['distance'], self.grid
#         )
#         self.plot_simulation()
#
#     def plot_simulation(self):
#         self.ax.clear()
#         self.ax.contourf(self.grid[0], self.grid[1], self.Z, levels=50, cmap='magma')
#         self.ax.plot(self.positions, [0] * len(self.positions), 'ro', markersize=10)
#         self.ax.set_xlabel("X Position (m)")
#         self.ax.set_ylabel("Y Position (m)")
#         self.ax.set_title(f"N={self.state['N']}, f={self.state['f']} Hz")
#         plt.draw()
#
#     def update_state(self, **kwargs):
#         self.state.update(kwargs)
#         self.update_wave_pattern()

class BeamForming:
    def __init__(self, fig, axs, initial_state):
        self.fig = fig

        # Ensure axs is a list/array, even if only one axis is provided
        if isinstance(axs, list) or isinstance(axs, np.ndarray):
            self.map_ax = axs[0]
            self.profile_ax = axs[1]
        else:
            self.map_ax = axs  # Single axis
            self.profile_ax = axs  # Or another axis if needed for profiling

        self.state = initial_state

        # Initialize the grid
        self.grid, self.wavelength = initialize_simulation_grid(
            self.state['N'], self.state['f'], self.state['distance']
        )
        self.update_wave_pattern()

    def update_wave_pattern(self):
        # Update Constructive/Destructive Map
        self.Z, self.positions = compute_wave_pattern(
            self.state['N'], self.state['f'], self.state['dir'], self.state['distance'], self.grid
        )
        self.plot_simulation()

        # Update Beam Profile
        angles, beam_profile = compute_beam_profile(
            self.state['N'], self.state['f'], self.state['distance'], self.state['dir']
        )
        self.plot_beam_profile(angles, beam_profile)

    def plot_simulation(self):
        self.map_ax.clear()
        self.map_ax.contourf(self.grid[0], self.grid[1], self.Z, levels=50, cmap='magma')
        self.map_ax.plot(self.positions, [0] * len(self.positions), 'ro', markersize=10)
        self.map_ax.set_xlabel("X Position (m)")
        self.map_ax.set_ylabel("Y Position (m)")
        self.map_ax.set_title(f"N={self.state['N']}, f={self.state['f']} Hz")
        plt.draw()

    def plot_beam_profile(self, angles, beam_profile):
        self.profile_ax.clear()
        self.profile_ax.plot(angles, beam_profile, color='blue')
        self.profile_ax.set_xlabel("Angle (degrees)")
        self.profile_ax.set_ylabel("Intensity (dB)")
        self.profile_ax.set_title("Beam Profile")
        self.profile_ax.grid(True)
        plt.draw()

    def update_state(self, **kwargs):
        self.state.update(kwargs)
        self.update_wave_pattern()
