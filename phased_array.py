# phased_array.py
import numpy as np

ultrasound_v_air = 343  # Speed of sound in air (m/s)
max_size = 100  # Maximum grid size
dx = None  # Grid spacing

def initialize_simulation_grid(N, f, d, max_size=100):
    global dx
    w = ultrasound_v_air / f  # Wavelength
    dx = w / 10  # Grid spacing
    size = min(np.ceil(2 * (((N - 1) * d) ** 2) / w * 4), max_size)
    x = np.arange(-size, size, dx)
    y = np.arange(0, size, dx)
    return np.meshgrid(x, y), w

def compute_wave_pattern(N, f, dir_angle, distance, grid, t=0, geometry="Linear", arc_radius=1.0):
    w = ultrasound_v_air / f  # Wavelength
    k = 2 * np.pi / w  # Wave number
    omega = 2 * np.pi * f  # Angular frequency
    dir_rad = np.radians(dir_angle)  # Steering angle in radians

    if geometry == "Curved":
        # Positions along a circular arc
        angles = np.linspace(-np.pi / 4, np.pi / 4, N)
        positions = arc_radius * np.stack((np.sin(angles), np.cos(angles)), axis=1)
        dphi = k * arc_radius * np.sin(np.linspace(-np.pi / 4, np.pi / 4, N)) * np.sin(dir_rad)
    else:
        # Linear positions: N emitters spaced along X-axis
        positions = np.linspace(-(N - 1) * distance / 2, (N - 1) * distance / 2, N)
        positions = np.column_stack((positions, np.zeros_like(positions)))  # Add Y=0 for Linear mode

        # Phase shift per emitter due to steering
        dphi_per_distance = 2 * np.pi * distance * np.sin(dir_rad) / w
        dphi = np.arange(-(N - 1) / 2, (N - 1) / 2 + 1) * dphi_per_distance

    # Precompute distances from emitters
    X, Y = grid
    Rs = np.sqrt((X[:, :, None] - positions[:, 0]) ** 2 + (Y[:, :, None] - positions[:, 1]) ** 2)

    # Apply phase shifts
    phase_shifts = k * Rs + omega * t + dphi[None, None, :]
    Z = np.sum(np.cos(phase_shifts), axis=2)
    return Z, positions



def compute_beam_profile(N, f, distance, dir_angle, geometry="Linear", arc_radius=1.0):
    w = ultrasound_v_air / f  # Wavelength
    k = 2 * np.pi / w  # Wave number
    angles = np.linspace(-90, 90, 500)  # Array of angles in degrees
    dir_rad = np.radians(dir_angle)  # Convert steering angle to radians

    # Compute array factor for each angle
    array_factor = np.zeros_like(angles, dtype=np.complex128)

    if geometry == "Curved":
        # Curved geometry: emitter positions on a circular arc
        emit_angles = np.linspace(-np.pi / 4, np.pi / 4, N)  # Spread emitters over a quarter-circle
        positions = arc_radius * np.array([np.sin(emit_angles), np.cos(emit_angles)]).T  # Emitter positions
        for pos in positions:
            r_angle = np.arctan2(pos[1], pos[0])  # Relative angle of the emitter
            phase_shift = k * distance * np.sin(np.radians(angles) - dir_rad) + r_angle
            array_factor += np.exp(1j * phase_shift)
    else:
        # Linear geometry: emitters spaced along X-axis
        for n in range(N):
            phase_shift = k * distance * np.sin(np.radians(angles - dir_angle)) * n
            array_factor += np.exp(1j * phase_shift)

    array_factor = np.abs(array_factor)  # Get the magnitude
    array_factor /= np.max(array_factor)  # Normalize
    return angles, 20 * np.log10(array_factor)  # Convert to dB scale
