import numpy as np
import matplotlib.pyplot as plt

# Generate x values from 0 to 2π
x = np.linspace(0, 2 * np.pi, 1000)

# Compute sine and cosine values
sin_y = np.sin(x)
cos_y = np.cos(x)

# Create the plot
plt.figure(figsize=(8, 4))
plt.plot(x, sin_y, label='sin(x)')
plt.plot(x, cos_y, label='cos(x)')
plt.title('Sine and Cosine Waves')
plt.xlabel('x (radians)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

# Save the figure
plt.savefig('trig_plot.png', dpi=300)
plt.close()