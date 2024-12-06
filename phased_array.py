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
