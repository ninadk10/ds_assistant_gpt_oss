import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
import pandas as pd

# Load iris dataset
iris = load_iris()
X = iris.data
y = iris.target
feature_names = iris.feature_names
target_names = iris.target_names

# Create DataFrame for easy statistics
df = pd.DataFrame(X, columns=feature_names)
df['species'] = pd.Categorical.from_codes(y, target_names)

# Print basic statistics
print("Dataset shape:", df.shape)
print("\nFeature summary statistics:")
print(df.describe(include='all'))
print("\nTarget distribution:")
print(df['species'].value_counts())

# Scatter plot of petal length vs petal width colored by species
plt.figure(figsize=(8, 6))
colors = {'setosa': 'tab:blue', 'versicolor': 'tab:orange', 'virginica': 'tab:green'}
for species in target_names:
    subset = df[df['species'] == species]
    plt.scatter(subset['petal length (cm)'], subset['petal width (cm)'],
                label=species, alpha=0.7, edgecolors='k')
plt.xlabel('Petal Length (cm)')
plt.ylabel('Petal Width (cm)')
plt.title('Petal Length vs Petal Width by Species')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()