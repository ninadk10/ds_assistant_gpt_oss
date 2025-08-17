import random
import matplotlib.pyplot as plt

# Simulate rolling two dice 20 times
rolls = [random.randint(1, 6) + random.randint(1, 6) for _ in range(20)]

# Display the results
print("Roll results:", rolls)

# Create histogram of the sums
plt.figure(figsize=(8, 4))
plt.hist(rolls, bins=range(2, 14), align='left', rwidth=0.8, edgecolor='black')
plt.title('Histogram of Two-Dice Sums (20 Rolls)')
plt.xlabel('Sum of Dice')
plt.ylabel('Frequency')
plt.xticks(range(2, 13))
plt.grid(axis='y', alpha=0.75)
plt.show()