import matplotlib.pyplot as plt
import numpy as np

def draw_frame():
    fig, ax = plt.subplots()
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Frame outline (True-X shape)
    frame_points = np.array([[-40, 0], [-28, -28], [0, -40], [28, -28], [40, 0], [28, 28], [0, 40], [-28, 28], [-40, 0]])
    ax.plot(frame_points[:, 0], frame_points[:, 1], 'k-')
    
    # Motor mount holes
    motor_positions = [(-35, 0), (35, 0), (0, -35), (0, 35)]
    for x, y in motor_positions:
        ax.scatter([x, x+3, x-3], [y, y-3, y+3], color='black', s=10)
    
    # Flight controller mounting holes (20x20 and 25x25)
    fc_positions = [(-10, -10), (10, -10), (-10, 10), (10, 10), (-12.5, -12.5), (12.5, -12.5), (-12.5, 12.5), (12.5, 12.5)]
    for x, y in fc_positions:
        ax.scatter(x, y, color='black', s=10)
    
    plt.show()

draw_frame()
