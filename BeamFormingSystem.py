# BeamFormingSystem.py
import matplotlib.pyplot as plt
from phased_array import initialize_simulation_grid, compute_wave_pattern

class BeamForming:
    def __init__(self, fig, ax, initial_state):
        self.fig = fig
        self.ax = ax
        self.state = initial_state

        # Initialize the grid
        self.grid, self.wavelength = initialize_simulation_grid(
            self.state['N'], self.state['f'], self.state['distance']
        )
        self.update_wave_pattern()

    def update_wave_pattern(self):
        self.Z, self.positions = compute_wave_pattern(
            self.state['N'], self.state['f'], self.state['dir'], self.state['distance'], self.grid
        )
        self.plot_simulation()

    def plot_simulation(self):
        self.ax.clear()
        self.ax.contourf(self.grid[0], self.grid[1], self.Z, levels=50, cmap='magma')
        self.ax.plot(self.positions, [0] * len(self.positions), 'ro', markersize=10)
        self.ax.set_xlabel("X Position (m)")
        self.ax.set_ylabel("Y Position (m)")
        self.ax.set_title(f"N={self.state['N']}, f={self.state['f']} Hz")
        plt.draw()

    def update_state(self, **kwargs):
        self.state.update(kwargs)
        self.update_wave_pattern()
