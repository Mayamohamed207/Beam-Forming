import numpy as np
import logging
import matplotlib.pyplot as plt
from phased_array import initialize_simulation_grid, compute_wave_pattern, compute_beam_profile, \
    compute_receiver_pattern, current_speed
from mainStyle import darkColor, greenColor, purpleColor,redColor,blueGreenColor

logging.basicConfig(
    filename="Logging.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BeamForming:
    def __init__(self, fig, axs, initial_state):
        self.fig = fig

        if isinstance(axs, list) or isinstance(axs, np.ndarray):
            self.map_ax = axs[0]
            self.profile_ax = axs[1]
        else:
            self.map_ax = axs
            self.profile_ax = axs

        self.state = {
            'mode': 'Emitter','N': 2,'f': 500,'distance': 0.1,'direction': 0, 'geometry': 'Linear', 'scenario': 'Default Mode','sizeX': 5,'sizeY': 10}
        
        self.state.update(initial_state)  

        logging.info(f"Initial state: {self.state}")

        self.grid, self.wavelength = initialize_simulation_grid(
            self.state['N'], self.state['f'], self.state['distance'],sizeX=self.state['sizeX'],sizeY=self.state['sizeY']
        )
        self.colorbar = None
        self.update_wave_pattern()

    def update_wave_pattern(self):
        if self.state['mode'] == 'Receiver':
            self.state['f']  
            self.wavelength = current_speed / self.state['f']
            self.wave_pattern, self.positions = self.update_receiver_pattern()
            print(self.state['f'])

            angles, beam_profile =compute_beam_profile(self.state['N'], self.state['f'], self.state['distance'] ,self.state['direction'], self.positions,geometry=self.state['geometry'], arc_radius=self.state.get('curvature', 1.0), mode=self.state['mode'])
        else:
            self.wave_pattern, self.positions = compute_wave_pattern(
                self.state['N'], self.state['f'], self.state['direction'], self.state['distance'],
                self.grid, geometry=self.state['geometry'], arc_radius=self.state.get('curvature', 1.0)
            )
            print("trans wave")

            angles, beam_profile = compute_beam_profile(
                self.state['N'], self.state['f'], self.state['distance'], self.state['direction'],self.positions,
                geometry=self.state['geometry'], arc_radius=self.state.get('curvature', 1.0), mode=self.state['mode']
            )

        self.plot_simulation()
        self.plot_beam_profile(angles, beam_profile)
        logging.info("Wave pattern updated")

    def update_receiver_pattern(self):
        receiver_count = self.state.get('receiver_count', 1)
        receiver_spacing = self.state.get('receiver_spacing', 0.5)
        receiver_positions = np.linspace(
        -receiver_spacing * (receiver_count - 1) / 2,
        receiver_spacing * (receiver_count - 1) / 2,
        receiver_count
        )
        receiver_positions = np.column_stack(
        (receiver_positions, np.zeros_like(receiver_positions))
        )

        wave_pattern, _ = compute_receiver_pattern(
            self.grid, receiver_positions, frequency=self.state['f'],steering_angle=self.state['direction']
        )
        return wave_pattern, receiver_positions


    def plot_simulation(self):
        self.map_ax.clear()
        self.map_ax.set_facecolor(darkColor)
        self.fig.patch.set_facecolor(darkColor)
        self.map_ax.set_xticks(np.arange(np.min(self.grid[0]), np.max(self.grid[0]), 1))
        self.map_ax.set_xlim(np.min(self.grid[0]), np.max(self.grid[0]))
        self.map_ax.set_ylim(np.min(self.grid[1]), np.max(self.grid[1]))
        self.color_map = plt.cm.get_cmap("viridis")

        contour = self.map_ax.contourf(self.grid[0], self.grid[1], self.wave_pattern, levels=50, cmap='viridis', extend='both')

        if self.colorbar is None:       
            self.colorbar = self.fig.colorbar(contour, ax=self.map_ax, orientation='vertical', pad=0.05)
            self.colorbar.set_label("Wave Intensity", color=greenColor)
            self.colorbar.ax.tick_params(colors=greenColor)
        else:
            self.colorbar.update_normal(contour)

        self.map_ax.plot(self.positions[:, 0], self.positions[:, 1], 'o', color=redColor, markersize=10)
        self.map_ax.set_xlabel("X Position (m)", color=greenColor)
        self.map_ax.set_ylabel("Y Position (m)", color=greenColor)
        self.map_ax.tick_params(axis='both', colors=greenColor)
        plt.draw()

    def plot_beam_profile(self, angles, beam_profile):
        self.profile_ax.clear()
        self.profile_ax.set_facecolor(darkColor)
        self.fig.patch.set_facecolor(darkColor)

        angles_rad = np.radians(angles)
        self.profile_ax.plot(angles_rad, beam_profile, color=greenColor)

        # Threshold for -3 dB (70.7% of max intensity)
        threshold_dB = -3  # -3 dB relative to the peak
        max_dB = np.max(beam_profile)
        threshold = max_dB + threshold_dB  # Since dB is in log scale, add threshold

        # Find the angles where the beam profile crosses the threshold
        crossing_indices = np.where(beam_profile >= threshold)[0]
        if crossing_indices.size > 0:
            left_cross = angles_rad[crossing_indices[0]]
            right_cross = angles_rad[crossing_indices[-1]]

            # Plot lines at the -3 dB points
            self.profile_ax.axvline(left_cross, color=greenColor, linestyle='--', label="-3 dB Left")
            self.profile_ax.axvline(right_cross, color=greenColor, linestyle='--', label="-3 dB Right")

            # Annotate the points
            self.profile_ax.text(
                left_cross, max_dB - 5, f"{np.degrees(left_cross):.1f}°",
                color=greenColor, ha='center'
            )
            self.profile_ax.text(
                right_cross, max_dB - 5, f"{np.degrees(right_cross):.1f}°",
                color=greenColor, ha='center'
            )

        # Set the angle limits from -90 to 90 degrees
        self.profile_ax.set_thetalim(-np.pi / 2, np.pi / 2)
        self.profile_ax.set_theta_zero_location("N")
        self.profile_ax.set_theta_direction(-1)  # Counterclockwise direction
        self.profile_ax.set_xticks(np.radians(np.arange(-90, 91, 5)))
        self.profile_ax.tick_params(axis='both', colors=greenColor)
        self.profile_ax.grid(True, color=greenColor)

        self.fig.subplots_adjust(left=0.12, right=0.79, top=1.0, bottom=0.04)
        self.profile_ax.set_aspect('auto')
        plt.draw()

    def update_state(self, **kwargs):
        self.state.update(kwargs)
        print(f"Updated State: {self.state}")
        self.update_wave_pattern()
