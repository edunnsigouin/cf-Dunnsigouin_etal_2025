import numpy as np
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

# Predicted probabilities and observed outcomes
predicted_probs = np.array([...])  # Replace with your predicted probabilities
observed_outcomes = np.array([...])  # Replace with binary outcomes (1 if >2 claims, else 0)

# Compute calibration curve
fraction_of_positives, mean_predicted_prob = calibration_curve(
    observed_outcomes, predicted_probs, n_bins=10, strategy='uniform'
)

# Plot reliability diagram
plt.figure(figsize=(8, 8))
plt.plot(mean_predicted_prob, fraction_of_positives, marker='o', label='Model')
plt.plot([0, 1], [0, 1], 'k--', label='Perfect reliability')
plt.axhline(y=0.02, color='red', linestyle='--', label='Climatological frequency (2%)')
plt.xlabel('Mean predicted probability')
plt.ylabel('Observed frequency')
plt.title('Reliability Diagram for >2 Claims Prediction')
plt.legend()
plt.grid()
plt.show()
