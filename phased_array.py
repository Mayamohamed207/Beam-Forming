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



def compute_beam_profile(N, f, distance, dir_angle, receiver_positions,geometry="Linear", arc_radius=1.0, mode="Emitter"):
    w = ultrasound_v_air / f  # Wavelength
    k = 2 * np.pi / w  # Wave number
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
            emit_angles = np.linspace(-np.pi / 4, np.pi / 4, N)  # Adjust based on arc_radius
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
            for n in range(N):
                phase_shift = k * distance * np.sin(np.radians(angles - dir_angle)) * n
                array_factor += np.exp(1j * phase_shift)

    array_factor = np.abs(array_factor)  # Get the magnitude
    array_factor /= np.max(array_factor)  # Normalize
    array_factor = np.clip(array_factor, 1e-10, 1)
    # print(array_factor)
    return angles, 20 * np.log10(array_factor)  # Convert to dB scale


# def compute_received_beam_profile( f,dir_angle,distance, receiver_positions):
#     # Compute the beam profile for the received signal based on the receiver's pattern
#     w = ultrasound_v_air / f  # Wavelength
#     k = 2 * np.pi / w  # Wave number
#     angles = np.linspace(-90, 90, 500)  # Array of angles in degrees
#     dir_rad = np.radians(dir_angle)  # Convert steering angle to radians
#
#     # Compute array factor for each angle (receiver's perspective)
#     array_factor = np.zeros_like(angles, dtype=np.complex128)
#
#     for pos in receiver_positions:
#         # Distance between receiver and observation point for each angle
#         distance_to_point = np.hypot(pos[0] - distance * np.sin(dir_rad),
#                                      pos[1] - distance * np.cos(dir_rad))
#
#         # Phase shift calculation for receiver's perspective
#         phase_shift = k * distance_to_point + k * (
#                 pos[0] * np.sin(np.radians(angles)) - pos[1] * np.cos(np.radians(angles)))
#         array_factor += np.exp(1j * phase_shift)
#
#     array_factor = np.abs(array_factor)  # Get the magnitude
#     array_factor /= np.max(array_factor)  # Normalize
#     array_factor = np.clip(array_factor, 1e-10, 1)
#
#     return angles, 20 * np.log10(array_factor)  # Convert to dB scale


def compute_receiver_pattern(grid, receiver_positions, steering_angle=0):
    X, Y = grid
    Z = np.zeros(X.shape)
    dir_rad = np.radians(steering_angle)  # Convert angle to radians

    for rx in receiver_positions:
        # Add phase adjustment for steering
        Rs = np.sqrt((X - rx[0]) ** 2 + (Y - rx[1]) ** 2)
        Z += np.cos(2 * np.pi * Rs / dx + 2 * np.pi * rx[0] * np.sin(dir_rad) / dx)

    return Z, receiver_positions
