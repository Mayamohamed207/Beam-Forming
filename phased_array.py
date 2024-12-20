import numpy as np
import logging
# logging.basicConfig(
#     filename="Logging.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

SPEED_OF_LIGHT = 3e8  # Speed of light in m/s (5G)
SPEED_OF_SOUND_AIR = 343  # Speed of sound in air (m/s, Ultrasound default)
SPEED_OF_SOUND_TISSUE = 1500  # Speed of sound in soft tissue (m/s, Ultrasound and Tumor Ablation)
five_g_reciever_frequency=5000000000
RESOLUTION_FACTOR=100

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

def initialize_simulation_grid(N, frequency, distance,sizeX=5,sizeY=100, max_size=100,max_points=1000,geometry="linear"):
    global dx
    wavelength =  current_speed / frequency  # Wavelength
    dx = wavelength / 10  # Grid spacing
    max_dx = max(sizeX, sizeY) / max_points  # Upper bound for dx
    dx = max(dx, max_dx)  # Ensure dx is not too small
    logging.info(f"Calculated wavelength: {wavelength:.6f}, dx: {dx:.6f}")

    adjusted_sizeX = max(min(sizeX, max_size), 2 * dx)  # Ensure minimum grid size
    adjusted_sizeY = max(min(sizeY, max_size), 2 * dx)
    if geometry == "Curved":
         Y_grid = np.arange(-adjusted_sizeY, adjusted_sizeY, dx)
    else:
        Y_grid = np.arange(0, adjusted_sizeY, dx)
        
    X_grid = np.arange(-adjusted_sizeX, adjusted_sizeX, dx)
    

    if X_grid.size == 0 or Y_grid.size == 0:
        logging.error("Grid size is invalid. Check dx and input parameters.")
        raise ValueError("Invalid grid size: dx is too large or frequency too small.")
    logging.info(f"Grid initialized with size: {size}, wavelength: {wavelength}, dx: {dx}")

    return np.meshgrid(X_grid, Y_grid), wavelength

def compute_wave_pattern(N, frequency, steering_angle, distance, grid, t=0, geometry="Linear", arc_radius=1.0):
    wavelength =  current_speed / frequency  # Wavelength
    print(current_speed)

    wave_number = 2 * np.pi / wavelength  # Wave number k = 2π / wavelength
    omega = 2 * np.pi * frequency  # Angular frequency
    steering_angle_rad = np.radians(steering_angle)  # Steering angle in radians
    
    logging.info(f"wave pattern: N={N}, frequency={frequency}, steering_angle={steering_angle}")
    
    
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

def compute_receiver_pattern(grid, receiver_positions, frequency,steering_angle=0, current_speed=343, t=0):
    X_grid, Y_grid = grid
    interference_pattern = np.zeros(X_grid.shape)
    
    transmitter_position = np.array([20, 20])
    
    wavelength = current_speed / frequency 
    wave_number = 2 * np.pi / wavelength  # k = 2π / wavelength
    omega = 2 * np.pi * frequency  # Angular frequency (ω = 2π * frequency)    
    emitter_distances = np.sqrt((X_grid - transmitter_position[0]) ** 2 + (Y_grid - transmitter_position[1]) ** 2)
    
    # wave equation: A * cos(kx - ωt + φ))
    phase_shifts = wave_number * emitter_distances - omega * t
    wave_pattern = np.cos(phase_shifts)  # Using cosine to represent the wave propagation
    interference_pattern += wave_pattern

    return interference_pattern, wave_pattern




def compute_beam_profile(Elements_Number, frequency, distance, dir_angle, receiver_positions, geometry="Linear",
                         arc_radius=1.0, mode="Emitter"):
    # Calculate wavelength: λ = c / f
    Wavelength = current_speed / frequency  # Wavelength

    # Calculate wave number: k = 2π / λ
    k = 2 * np.pi / Wavelength  # Wave number

    # Generate an array of observation angles from -90° to 90°
    angles = np.linspace(-90, 90, 500)  # Array of angles in degrees

    # Convert the steering angle from degrees to radians
    dir_rad = np.radians(dir_angle)  # Convert steering angle to radians

    # Initialize array factor as a complex number array
    array_factor = np.zeros_like(angles, dtype=np.complex128)

    if mode == "Receiver":
        # Calculate array factor for receiver mode
        for pos in receiver_positions:
            # Distance between receiver and observation point: r = √((x - d·sin(θ))² + (y - d·cos(θ))²)
            distance_to_point = np.hypot(pos[0] - distance * np.sin(dir_rad),
                                         pos[1] - distance * np.cos(dir_rad))

            # Phase shift calculation: φ = kr + k(x·sin(θ) - y·cos(θ))
            phase_shift = k * distance_to_point + k * (
                    pos[0] * np.sin(np.radians(angles)) - pos[1] * np.cos(np.radians(angles)))

            # Accumulate contributions to the array factor
            array_factor += np.exp(1j * phase_shift)

    else:
        if geometry == "Curved":
            # Curved geometry: emitter positions on a circular arc
            # Generate emitter angles evenly spaced along the arc
            emit_angles = np.linspace(-np.pi / 4, np.pi / 4, Elements_Number)  # Adjust based on arc_radius

            # Emitter positions: [x, y] = R[cos(θ), sin(θ)]
            positions = arc_radius * np.array([np.cos(emit_angles), np.sin(emit_angles)]).T

            for pos in positions:
                # Distance between emitter and observation point: r = √((x - d·sin(θ))² + (y - d·cos(θ))²)
                distance_to_point = np.hypot(pos[0] - distance * np.sin(dir_rad),
                                             pos[1] - distance * np.cos(dir_rad))

                # Phase shift calculation: φ = kr + k(x·sin(θ) - y·cos(θ))
                phase_shift = k * distance_to_point + k * (
                        pos[0] * np.sin(np.radians(angles)) - pos[1] * np.cos(np.radians(angles)))

                # Accumulate contributions to the array factor
                array_factor += np.exp(1j * phase_shift)
        else:
            # Linear geometry: emitters spaced along X-axis
            for n in range(Elements_Number):
                # Phase shift for linear array: φ = kd·sin(θ)·n
                phase_shift = k * distance * np.sin(np.radians(angles - dir_angle)) * n

                # Accumulate contributions to the array factor
                array_factor += np.exp(1j * phase_shift)

    # Magnitude of the array factor |AF(θ)|
    array_factor = np.abs(array_factor)

    # Normalize array factor by its maximum value
    array_factor /= np.max(array_factor)

    # Clip values to avoid logarithm issues
    array_factor = np.clip(array_factor, 1e-10, 1)

    # logging.info(f"Array factor updated to : {array_factor}")
    logging.info(f"Beam profile is computed")

    # Return the beam profile in dB scale: AF(θ) = 20·log10(|AF(θ)|)
    return angles, 20 * np.log10(array_factor)  # Convert to dB scale




