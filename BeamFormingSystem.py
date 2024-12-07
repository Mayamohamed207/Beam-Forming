# # BeamFormingSystem.py
import numpy as np

import matplotlib.pyplot as plt
from phased_array import initialize_simulation_grid, compute_wave_pattern, compute_beam_profile
from mainStyle  import darkColor, greenColor,purpleColor

class BeamForming:
    def __init__(self, fig, axs, initial_state):
        self.fig = fig

        if isinstance(axs, list) or isinstance(axs, np.ndarray):
            self.map_ax = axs[0]
            self.profile_ax = axs[1]
        else:
            self.map_ax = axs 
            self.profile_ax = axs  

        self.state = initial_state

        self.grid, self.wavelength = initialize_simulation_grid(
            self.state['N'], self.state['f'], self.state['distance']
        )
       
        self.update_wave_pattern()


    def update_wave_pattern(self):
        # Update Constructive/Destructive Map
        self.Z, self.positions = compute_wave_pattern(
            self.state['N'], self.state['f'], self.state['dir'], self.state['distance'],
            self.grid, geometry=self.state['geometry'], arc_radius=self.state.get('curvature', 1.0)
        )
        self.plot_simulation()

        # Update Beam Profile
        angles, beam_profile = compute_beam_profile(
            self.state['N'], self.state['f'], self.state['distance'], self.state['dir'],
            geometry=self.state['geometry'], arc_radius=self.state.get('curvature', 1.0)
        )
        self.plot_beam_profile(angles, beam_profile)


    def plot_simulation(self):
        self.map_ax.clear()
        self.map_ax.set_facecolor(darkColor)
        self.fig.patch.set_facecolor(darkColor)
        self.map_ax.set_xticks(np.arange(np.min(self.grid[0]), np.max(self.grid[0]), 1))
        self.map_ax.set_xlim(np.min(self.grid[0]), np.max(self.grid[0]))
        self.map_ax.set_ylim(np.min(self.grid[1]), np.max(self.grid[1]))

        self.map_ax.contourf(self.grid[0], self.grid[1], self.Z, levels=50, cmap='viridis',extend='both')
        self.map_ax.plot(self.positions[:, 0], self.positions[:, 1], 'o', color=purpleColor, markersize=10)
        self.map_ax.set_xlabel("X Position (m)",color=greenColor)
        self.map_ax.set_ylabel("Y Position (m)",color=greenColor)
        self.map_ax.tick_params(axis='both', colors=greenColor) 
        # self.fig.subplots_adjust(left=-1.5, right=0.95, top=0.1, bottom=0.05)
        # self.fig.tight_layout(pad=0.8) 
        # self.map_ax.set_title(f"N={self.state['N']}, f={self.state['f']} Hz",color=greenColor)
        plt.draw()

    def plot_beam_profile(self, angles, beam_profile):
        self.profile_ax.clear()
        self.profile_ax.set_facecolor(darkColor)
        self.fig.patch.set_facecolor(darkColor)
        self.profile_ax.plot(angles, beam_profile, color=greenColor)
        self.profile_ax.set_xlabel("Angle (degrees)",color=greenColor)
        self.profile_ax.set_ylabel("Intensity (dB)",color=greenColor)
        # self.profile_ax.set_title("Beam Profile",color=greenColor)
        self.profile_ax.tick_params(axis='both', colors=greenColor)  
        self.profile_ax.grid(True,color=greenColor)
        self.fig.patch.set_edgecolor(darkColor)
        self.fig.patch.set_linewidth(0)
        plt.draw()

    def update_state(self, **kwargs):
        self.state.update(kwargs)
        self.update_wave_pattern()
