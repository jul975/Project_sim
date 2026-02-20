import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. Generate synthetic data
np.random.seed(42)
x = np.random.rand(50, 1) * 10
y = 2.5 * x + 5 + np.random.normal(0, 2, (50, 1)) # y = 2.5x + 5 + noise

# 2. Fit the model
model = LinearRegression().fit(x, y)
y_pred = model.predict(x)

# 3. Visualize
plt.figure(figsize=(10, 5))

# Plot 1: The Fit
plt.subplot(1, 2, 1)
plt.scatter(x, y, color='blue', alpha=0.5, label='Actual Data')
plt.plot(x, y_pred, color='red', label=f'Fit: y = {model.coef_[0][0]:.2f}x + {model.intercept_[0]:.2f}')
plt.title("Linear Regression Fit")
plt.legend()

# Plot 2: Residuals (Crucial for formalizing)
plt.subplot(1, 2, 2)
residuals = y - y_pred
plt.scatter(x, residuals, color='purple', alpha=0.5)
plt.axhline(0, color='black', linestyle='--')
plt.title("Residual Plot (Error $\epsilon$)")

plt.tight_layout()
plt.show()