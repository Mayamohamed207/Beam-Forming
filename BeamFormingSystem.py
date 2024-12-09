# BeamFormingSystem.py
import numpy as np
import matplotlib.pyplot as plt
from phased_array import initialize_simulation_grid, compute_wave_pattern, compute_beam_profile, compute_receiver_pattern
from mainStyle import darkColor, greenColor, purpleColor

class BeamForming:
    def __init__(self, fig, axs, initial_state):
        self.fig = fig

        # Handle axs for both list and single axes cases
        if isinstance(axs, list) or isinstance(axs, np.ndarray):
            self.map_ax = axs[0]
            self.profile_ax = axs[1]
        else:
            self.map_ax = axs
            self.profile_ax = axs

        self.state = {
            'mode': 'Emitter',        # Default mode
            'N': 8,                  # Default number of elements
            'f': 1000,              # Default frequency in Hz
            'distance': 0.1,         # Default element spacing in meters
            'dir': 0,                # Default direction angle
            'geometry': 'Linear',    # Default geometry
        }
        self.state.update(initial_state)  # Overwrite defaults with initial_state

        # Initialize simulation grid
        self.grid, self.wavelength = initialize_simulation_grid(
            self.state['N'], self.state['f'], self.state['distance']
        )

        # Call the update method to initialize plots
        self.update_wave_pattern()

    def update_wave_pattern(self):
        # Compute wave or receiver pattern based on mode
        if self.state['mode'] == 'Receiver':
            self.Z, self.positions = self.update_receiver_pattern()
            # Compute the beam profile for the received signal
            angles, beam_profile = self.compute_received_beam_profile()
        else:
            self.Z, self.positions = compute_wave_pattern(
                self.state['N'], self.state['f'], self.state['dir'], self.state['distance'],
                self.grid, geometry=self.state['geometry'], arc_radius=self.state.get('curvature', 1.0)
            )
            # Compute the beam profile for the transmitted wave
            angles, beam_profile = compute_beam_profile(
                self.state['N'], self.state['f'], self.state['distance'], self.state['dir'],
                geometry=self.state['geometry'], arc_radius=self.state.get('curvature', 1.0)
            )

        # Plot the simulation and beam profile
        self.plot_simulation()
        self.plot_beam_profile(angles, beam_profile)

    def update_receiver_pattern(self):
        receiver_count = self.state.get('receiver_count', 1)
        receiver_spacing = self.state.get('receiver_spacing', 0.5)
        receiver_positions = np.linspace(
        -receiver_spacing * (receiver_count - 1) / 2,
        receiver_spacing * (receiver_count - 1) / 2,
        receiver_count
        )
        receiver_positions = np.column_stack(
        (receiver_positions, np.zeros_like(receiver_positions))  # Place at Y = 0
        )

        Z, _ = compute_receiver_pattern(
            self.grid, receiver_positions, steering_angle=self.state['dir']
        )
        return Z, receiver_positions

    def compute_received_beam_profile(self):
        # Compute the beam profile for the received signal based on the receiver's pattern
        w = self.wavelength
        k = 2 * np.pi / w  # Wave number
        angles = np.linspace(-90, 90, 500)  # Array of angles in degrees
        dir_rad = np.radians(self.state['dir'])  # Convert steering angle to radians

        # Compute array factor for each angle (receiver's perspective)
        array_factor = np.zeros_like(angles, dtype=np.complex128)

        receiver_positions = self.positions
        for pos in receiver_positions:
            # Distance between receiver and observation point for each angle
            distance_to_point = np.hypot(pos[0] - self.state['distance'] * np.sin(dir_rad),
                                         pos[1] - self.state['distance'] * np.cos(dir_rad))

            # Phase shift calculation for receiver's perspective
            phase_shift = k * distance_to_point + k * (
                    pos[0] * np.sin(np.radians(angles)) - pos[1] * np.cos(np.radians(angles)))
            array_factor += np.exp(1j * phase_shift)

        array_factor = np.abs(array_factor)  # Get the magnitude
        array_factor /= np.max(array_factor)  # Normalize
        array_factor = np.clip(array_factor, 1e-10, 1)

        return angles, 20 * np.log10(array_factor)  # Convert to dB scale

    def plot_simulation(self):
        self.map_ax.clear()
        self.map_ax.set_facecolor(darkColor)
        self.fig.patch.set_facecolor(darkColor)
        self.map_ax.set_xticks(np.arange(np.min(self.grid[0]), np.max(self.grid[0]), 1))
        self.map_ax.set_xlim(np.min(self.grid[0]), np.max(self.grid[0]))
        self.map_ax.set_ylim(np.min(self.grid[1]), np.max(self.grid[1]))

        self.map_ax.contourf(self.grid[0], self.grid[1], self.Z, levels=50, cmap='viridis', extend='both')
        self.map_ax.plot(self.positions[:, 0], self.positions[:, 1], 'o', color=purpleColor, markersize=10)
        self.map_ax.set_xlabel("X Position (m)", color=greenColor)
        self.map_ax.set_ylabel("Y Position (m)", color=greenColor)
        self.map_ax.tick_params(axis='both', colors=greenColor)
        plt.draw()

    def plot_beam_profile(self, angles, beam_profile):
        self.profile_ax.clear()
        self.profile_ax.set_facecolor(darkColor)
        self.fig.patch.set_facecolor(darkColor)

        # Convert angles from degrees to radians
        angles_rad = np.radians(angles)

        # Polar plot setup
        self.profile_ax.plot(angles_rad, beam_profile, color=greenColor)

        # Set the angle limits from -90 to 90 degrees
        self.profile_ax.set_thetalim(-np.pi / 2, np.pi / 2)

        # Adjusting labels and styling
        self.profile_ax.set_theta_zero_location("N")  # Zero degrees at the top
        self.profile_ax.set_theta_direction(-1)  # Counterclockwise direction
        self.profile_ax.set_xticks(np.radians(np.arange(-90, 91, 30)))  # Angle ticks
        self.profile_ax.tick_params(axis='both', colors=greenColor)
        self.profile_ax.grid(True, color=greenColor)

        self.fig.subplots_adjust(left=0.12, right=0.9, top=1.0, bottom=0.04)
        self.profile_ax.set_aspect('auto')
        plt.draw()

    def update_state(self, **kwargs):
        self.state.update(kwargs)
        self.update_wave_pattern()
