import numpy as np
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# file_handler = logging.FileHandler('E:\DSP\Beam-Forming')
# file_handler.setFormatter(formatter)
# Default speeds
SPEED_OF_LIGHT = 3e8  # Speed of light in m/s (5G)
SPEED_OF_SOUND_AIR = 343  # Speed of sound in air (m/s, Ultrasound default)
SPEED_OF_SOUND_TISSUE = 1500  # Speed of sound in soft tissue (m/s, Ultrasound and Tumor Ablation)
five_g_reciever_frequency=5000000000

current_speed = SPEED_OF_SOUND_AIR  # Default speed of sound
reciever_frequency=five_g_reciever_frequency
max_size = 100  # Maximum grid size
dx = None  # Grid spacing
size=2

def set_speed(speed):
    global current_speed
    current_speed = speed
    logging.info(f"Speed updated to: {current_speed}")

def set_frequency(frequency):
    global reciever_frequency
    reciever_frequency = frequency
    logging.debug(f"Frequency updated to: {reciever_frequency}")


# def initialize_simulation_grid(N, frequency, distance, resolution=500, max_size=100):
#     """
#     Initializes the simulation grid based on resolution, frequency, and grid size.
#
#     Parameters:
#         N (int): Number of elements (e.g., antennas or sources).
#         frequency (float): Frequency of the wave (Hz).
#         distance (float): Distance between elements.
#         resolution (int): Number of points per grid axis for higher clarity.
#         max_size (float): Maximum grid size limit.
#
#     Returns:
#         tuple: (X, Y) mesh grid, wavelength of the wave.
#     """
#     # Calculate wavelength based on speed of wave
#     wavelength = current_speed / frequency
#
#     # Define grid size dynamically
#     grid_size = min(np.ceil(2 * (((N - 1) * distance) ** 2) / wavelength), max_size)
#
#     # Use resolution to control grid density
#     x = np.linspace(-grid_size, grid_size, resolution)
#     y = np.linspace(0, grid_size, resolution)
#
#     X, Y = np.meshgrid(x, y)
#
#     # Debug information
#     logging.debug(
#         f"Grid initialized with grid_size: {grid_size:.2f}, wavelength: {wavelength:.2e}, resolution: {resolution}")
#
#     return (X, Y), wavelength

def initialize_simulation_grid(N, frequency, distance, max_size=100):
    global dx
    wavelength = current_speed / frequency  # Wavelength
    dx = wavelength / 10  # Grid spacing

    size = min(np.ceil(2 * (((N - 1) * distance) ** 2) / wavelength * 4), max_size)
    X_grid = np.arange(-size, size, dx)
    Y_grid = np.arange(0, size, dx)
    logging.debug(f"Grid initialized with size: {size}, wavelength: {wavelength}, dx: {dx}")

    return np.meshgrid(X_grid, Y_grid), wavelength
def compute_wave_pattern(N, frequency, steering_angle, distance, grid, t=0, geometry="Linear", arc_radius=1.0):
    wavelength =  current_speed / frequency  # Wavelength
    print(current_speed)

    wave_number = 2 * np.pi / wavelength  # Wave number k = 2π / wavelength
    omega = 2 * np.pi * frequency  # Angular frequency
    steering_angle_rad = np.radians(steering_angle)  # Steering angle in radians
    
    logging.debug(f"wave pattern: N={N}, frequency={frequency}, steering_angle={steering_angle}")
    
    size = min(np.ceil(2 * (((N - 1) * distance) ** 2) / wavelength * 4), max_size)
    X_grid = np.arange(-size, size, dx)
    Y_grid = np.arange(0, size, dx)
    
    if geometry == "Curved":
        # Positions along a circular arc
        angles = np.linspace(-np.pi / 4, np.pi / 4, N)
        positions = arc_radius * np.stack((np.sin(angles), np.cos(angles)), axis=1) #Convert polar to cartesian coordinates
        phase_shifts = wave_number * arc_radius * np.sin(np.linspace(-np.pi / 4, np.pi / 4, N)) * np.sin(steering_angle_rad) #ϕ = k⋅R⋅sin(θs)⋅sin(θn)
    
    else:
        positions = np.linspace(-(N - 1) * distance / 2, (N - 1) * distance / 2, N)
        positions = np.column_stack((positions, np.zeros_like(positions)))  

        # Phase shift per emitter due to steering
        phase_shifts_per_distance = 2 * np.pi * distance * np.sin(steering_angle_rad) / wavelength # Δϕ = 2πdsin(θ)/λ , (Δx=d sin(θ): distance between adjacent emitters)
        phase_shifts = np.arange(-(N - 1) / 2, (N - 1) / 2 + 1) * phase_shifts_per_distance

    X_grid, Y_grid = grid
    emitter_distances = np.sqrt((X_grid[:, :, None] - positions[:, 0]) ** 2 + (Y_grid[:, :, None] - positions[:, 1]) ** 2)

    # wave equation = Acos(kx−ωt+ϕ)
    phase_shifts = wave_number * emitter_distances + omega * t + phase_shifts[None, None, :] # distances from each grid point to all emitter positions
    wave_pattern = np.sum(np.cos(phase_shifts), axis=2)
    
    logging.debug(f"Transmitter Wave pattern computed")
    
    return wave_pattern, positions


def compute_receiver_pattern(grid, receiver_positions, steering_angle=0):
    X_grid, Y_grid = grid
    interference_pattern = np.zeros(X_grid.shape)
    steering_angle_rad = np.radians(steering_angle)  # Convert angle to radians

    for receiver in receiver_positions:

        distance_from_receiver = np.sqrt((X_grid - receiver[0]) ** 2 + (Y_grid - receiver[1]) ** 2) # Distance from receiver to each grid point
        interference_pattern += np.cos(2 * np.pi * distance_from_receiver / dx + 2 * np.pi * receiver[0] * np.sin(steering_angle_rad) / dx)  # Superposition of Waves : sum of cos( (2πR / λ) + (2πx₀ * sin(θ) / λ) )

    logging.debug(f"Receiver Wave pattern computed")
    return interference_pattern, receiver_positions


def compute_beam_profile(Elements_Number, frequency, distance, dir_angle,receiver_positions ,geometry="Linear", arc_radius=1.0, mode="Emitter"):
    Wavelength =  current_speed / frequency  # Wavelength
    k = 2 * np.pi / Wavelength  # Wave number
    angles = np.linspace(-90, 90, 500)  # Array of angles in degrees
    dir_rad = np.radians(dir_angle)  # Convert steering angle to radians

    # Compute array factor for each angle
    array_factor = np.zeros_like(angles, dtype=np.complex128)
    if mode == "Receiver":
        for pos in receiver_positions:
            # Distance between receiver and observation point for each angle
            distance_to_point = np.hypot(pos[0] - distance * np.sin(dir_rad),
                                         pos[1] - distance * np.cos(dir_rad))

            # Phase shift calculation for receiver's perspective
            phase_shift = k * distance_to_point + k * (
                    pos[0] * np.sin(np.radians(angles)) - pos[1] * np.cos(np.radians(angles)))
            array_factor += np.exp(1j * phase_shift)

    else:
        if geometry == "Curved":
            # Curved geometry: emitter positions on a circular arc
            emit_angles = np.linspace(-np.pi / 4, np.pi / 4, Elements_Number)  # Adjust based on arc_radius
            positions = arc_radius * np.array([np.cos(emit_angles), np.sin(emit_angles)]).T  # Emitter positions

            for pos in positions:
                # Distance between emitter and observation point for each angle
                distance_to_point = np.hypot(pos[0] - distance * np.sin(dir_rad), pos[1] - distance * np.cos(dir_rad))

                # Phase shift calculation
                phase_shift = k * distance_to_point + k * (
                            pos[0] * np.sin(np.radians(angles)) - pos[1] * np.cos(np.radians(angles)))
                array_factor += np.exp(1j * phase_shift)
        else:
            # Linear geometry: emitters spaced along X-axis
            for n in range(Elements_Number):
                phase_shift = k * distance * np.sin(np.radians(angles - dir_angle)) * n
                array_factor += np.exp(1j * phase_shift)

    array_factor = np.abs(array_factor)  # Get the magnitude
    array_factor /= np.max(array_factor)  # Normalize
    array_factor = np.clip(array_factor, 1e-10, 1)

    # logging.info(f"Array factor updated to : {array_factor}")

    logging.info(f"Beam profile is combuted")
    return angles, 20 * np.log10(array_factor)  # Convert to dB scale




