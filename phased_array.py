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

def compute_wave_pattern(N, f, dir_angle, distance, grid, t=0):
    w = ultrasound_v_air / f  # Wavelength
    k = 2 * np.pi / w  # Wave number
    omega = 2 * np.pi * f  # Angular frequency
    dir_rad = np.radians(dir_angle)  # Direction in radians
    dphi = 2 * np.pi * distance * np.sin(dir_rad) / w  # Phase difference
    positions = np.linspace(-(N - 1) * distance / 2, (N - 1) * distance / 2, N)

    # Precompute distances from each emitter
    X, Y = grid
    Rs = np.sqrt((X[:, :, None] - positions) ** 2 + Y[:, :, None] ** 2)
    Z = np.sum(np.cos(k * Rs + omega * t + dphi * np.arange(N)), axis=2)
    return Z, positions



def compute_beam_profile(N, f, distance, dir_angle):
    w = ultrasound_v_air / f  # Wavelength
    k = 2 * np.pi / w  # Wave number
    angles = np.linspace(-90, 90, 500)  # Array of angles in degrees
    dir_rad = np.radians(dir_angle)  # Convert steering angle to radians

    # Compute array factor for each angle
    array_factor = np.zeros_like(angles, dtype=np.complex128)
    for n in range(N):
        # Calculate phase shift for each emitter based on the steering direction
        phase_shift = k * distance * np.sin(np.radians(angles - dir_angle)) * n  # Adjust for steering direction
        array_factor += np.exp(1j * phase_shift)

    array_factor = np.abs(array_factor)  # Get the magnitude
    array_factor /= np.max(array_factor)  # Normalize
    return angles, 20 * np.log10(array_factor)  # Convert to dB scale
