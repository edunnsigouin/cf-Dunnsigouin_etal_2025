# cost_loss_enhanced.py
#
# A Python script illustrating a simple cost-loss decision example,
# now enhanced with:
#   1) A reliability diagram for each forecast (with the 1-to-1 line),
#   2) A function to compute the Brier Skill Score (BSS) relative to a climatological forecast,
#   3) An ROC curve for each forecast (TPR vs. FPR) and area-under-curve (AUC).
#
# We'll still compare:
#   - a 'good reliability' forecast
#   - a 'poor reliability' forecast
# vs. a binary ground truth of whether an event occurs.

import numpy as np
import matplotlib.pyplot as plt

###############################################################################
# 1. USER PARAMETERS
###############################################################################
N_DAYS = 1000         # Number of days to simulate
P_CLIM = 0.10       # Climatological probability that event occurs
COST   = 0.2        # Cost of mitigating action
LOSS   = 1.0        # Loss if event E occurs and we did not mitigate
NBINS  = 5          # Number of bins for the reliability diagram

###############################################################################
# 2. HELPER FUNCTIONS
###############################################################################
def generate_ground_truth(n_days, p_clim):
    """
    Create a binary time series representing whether an event E occurs (1) or not (0).
    Each day has probability p_clim of E=1, independently.
    """
    gt = (np.random.rand(n_days) < p_clim).astype(int)
    return gt

def generate_forecast_good_reliability(ground_truth):
    """
    Generate forecast probabilities that are fairly well calibrated:
      - If ground_truth=1, forecast ~0.6..0.9
      - If ground_truth=0, forecast ~0.0..0.3
    """
    n_days = len(ground_truth)
    forecast_probs = np.empty(n_days)
    for i in range(n_days):
        if ground_truth[i] == 1:
            forecast_probs[i] = 0.6 + 0.3*np.random.rand()
        else:
            forecast_probs[i] = 0.0 + 0.3*np.random.rand()
    return forecast_probs

def generate_forecast_poor_reliability(ground_truth):
    """
    Generate forecast probabilities that are poorly calibrated:
    - We ignore ground_truth and just pick random values near 0.4,
      so there's minimal correlation to the actual event.
    """
    n_days = len(ground_truth)
    forecast_probs = 0.4 + 0.2*(np.random.rand(n_days) - 0.5)*2.0
    forecast_probs = np.clip(forecast_probs, 0, 1)  # ensure in [0,1]
    return forecast_probs

def compute_decision_costs(ground_truth, forecast_probs, cost, loss):
    """
    For each day, decide whether to mitigate (cost) or not (risk loss)
    using the cost-loss rule: mitigate if p > (cost/loss).

    Returns:
        daily_cost: array of costs for each day
        avg_cost: mean cost over all days
    """
    n_days = len(ground_truth)
    R = cost / loss  # threshold probability
    daily_cost = np.zeros(n_days)

    for i in range(n_days):
        p = forecast_probs[i]
        if p > R:
            daily_cost[i] = cost  # mitigate
        else:
            daily_cost[i] = loss if ground_truth[i] == 1 else 0.0

    avg_cost = np.mean(daily_cost)
    return daily_cost, avg_cost

def compute_decision_costs_climatology(ground_truth, p_clim, cost, loss):
    """
    Using only the climatological probability, the user either:
      - always mitigate => daily cost = cost
      - never mitigate  => daily cost = p_clim * loss in expectation
    We'll pick whichever yields the lower expected cost, then
    compute actual daily costs for that strategy across the dataset.
    """
    if p_clim * loss < cost:
        # cheaper never to mitigate
        daily_cost = ground_truth * loss
        avg_cost = np.mean(daily_cost)
    else:
        # cheaper always to mitigate
        daily_cost = np.full_like(ground_truth, cost, dtype=float)
        avg_cost = cost
    return daily_cost, avg_cost

def brier_score(ground_truth, forecast_probs):
    """
    Brier Score = mean( (forecast_probs - ground_truth)^2 ).
    """
    return np.mean((forecast_probs - ground_truth)**2)

def brier_skill_score(ground_truth, forecast_probs, p_clim):
    """
    Brier Skill Score = 1 - (BS_forecast / BS_clim)
    where BS_clim is the Brier Score if we always forecast p_clim.
    """
    bs_f = brier_score(ground_truth, forecast_probs)
    bs_c = brier_score(ground_truth, np.full_like(ground_truth, p_clim, dtype=float))
    if bs_c == 0:
        return np.nan  # handle degenerate case
    return 1.0 - (bs_f / bs_c)

def reliability_diagram(forecast_probs, ground_truth, n_bins=NBINS):
    """
    Bin forecast_probs into n_bins. For each bin, compute:
     - avg_prob: mean forecast prob in that bin
     - obs_freq: fraction of events that occurred in that bin
     - bin_count: how many samples in that bin
    Returns (avg_prob, obs_freq, bin_count).
    """
    bins = np.linspace(0,1,n_bins+1)
    avg_prob = []
    obs_freq = []
    bin_count = []

    for i in range(n_bins):
        low_edge  = bins[i]
        high_edge = bins[i+1]
        in_bin = (forecast_probs >= low_edge) & (forecast_probs < high_edge)

        if np.any(in_bin):
            bin_fore = forecast_probs[in_bin]
            bin_gt   = ground_truth[in_bin]
            avg_prob.append(np.mean(bin_fore))
            obs_freq.append(np.mean(bin_gt))
            bin_count.append(np.sum(in_bin))
        else:
            avg_prob.append(np.nan)
            obs_freq.append(np.nan)
            bin_count.append(0)

    return np.array(avg_prob), np.array(obs_freq), np.array(bin_count)

def roc_curve_points(ground_truth, forecast_probs):
    """
    Compute points on the ROC curve by sweeping threshold from 0..1.
    Returns arrays of (fpr, tpr).
    """
    thresholds = np.linspace(0,1,101)
    tpr = []
    fpr = []

    for thr in thresholds:
        pred = (forecast_probs >= thr).astype(int)
        TP = np.sum((pred==1)&(ground_truth==1))
        FP = np.sum((pred==1)&(ground_truth==0))
        TN = np.sum((pred==0)&(ground_truth==0))
        FN = np.sum((pred==0)&(ground_truth==1))

        if (TP+FN)>0:
            tpr_val = TP/(TP+FN)
        else:
            tpr_val = 0
        if (FP+TN)>0:
            fpr_val = FP/(FP+TN)
        else:
            fpr_val = 0
        tpr.append(tpr_val)
        fpr.append(fpr_val)

    return np.array(fpr), np.array(tpr)

def auc_score(fpr, tpr):
    """
    Approximate area under the ROC curve via trapezoidal rule.
    """
    sort_idx = np.argsort(fpr)
    fpr_s = fpr[sort_idx]
    tpr_s = tpr[sort_idx]
    return np.trapz(tpr_s, x=fpr_s)

###############################################################################
# 3. MAIN SCRIPT
###############################################################################
def main():
    np.random.seed(42)  # for reproducibility

    # 1. Generate ground truth
    ground_truth = generate_ground_truth(N_DAYS, P_CLIM)

    # 2. Generate two forecasts
    fcst_good = generate_forecast_good_reliability(ground_truth)
    fcst_poor = generate_forecast_poor_reliability(ground_truth)

    # 3. Compute Brier Skill Scores for each forecast
    bss_good = brier_skill_score(ground_truth, fcst_good, P_CLIM)
    bss_poor = brier_skill_score(ground_truth, fcst_poor, P_CLIM)

    # 4. Compute ROC curves + area under curve
    fpr_good, tpr_good = roc_curve_points(ground_truth, fcst_good)
    auc_good = auc_score(fpr_good, tpr_good)
    fpr_poor, tpr_poor = roc_curve_points(ground_truth, fcst_poor)
    auc_poor = auc_score(fpr_poor, tpr_poor)

    # 5. Print skill metrics
    print('--- Forecast Skill Metrics ---')
    print(f'Good Reliability Forecast => BSS: {bss_good:.3f}, AUC: {auc_good:.3f}')
    print(f'Poor Reliability Forecast => BSS: {bss_poor:.3f}, AUC: {auc_poor:.3f}')

    # 6. Timeseries comparison
    days = np.arange(N_DAYS)
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    # Panel 1: good forecast vs. ground truth
    axes[0].plot(days, ground_truth, 'o-', label='Ground Truth (1=Event)')
    axes[0].plot(days, fcst_good, 'x--', label='Good Forecast Prob.')
    axes[0].set_title('Good Reliability Forecast vs. Ground Truth')
    axes[0].set_ylabel('Event / Probability')
    axes[0].legend()

    # Panel 2: poor forecast vs. ground truth
    axes[1].plot(days, ground_truth, 'o-', label='Ground Truth (1=Event)')
    axes[1].plot(days, fcst_poor, 'x--', label='Poor Forecast Prob.')
    axes[1].set_title('Poor Reliability Forecast vs. Ground Truth')
    axes[1].set_xlabel('Day Index')
    axes[1].set_ylabel('Event / Probability')
    axes[1].legend()

    plt.tight_layout()
    plt.show()

    # 7. Reliability diagrams
    fig2, axes2 = plt.subplots(1, 2, figsize=(10,4), sharey=True)

    # (a) Good forecast reliability
    avg_prob_good, obs_freq_good, _ = reliability_diagram(fcst_good, ground_truth, n_bins=NBINS)
    axes2[0].plot([0,1],[0,1],'k--', label='1-to-1')
    axes2[0].plot(avg_prob_good, obs_freq_good, 'o-', label='Good Forecast')
    axes2[0].set_title('Reliability Diagram: Good Forecast')
    axes2[0].set_xlabel('Mean Predicted Probability')
    axes2[0].set_ylabel('Observed Frequency')
    axes2[0].set_xlim([0,1])
    axes2[0].set_ylim([0,1])
    axes2[0].legend()

    # (b) Poor forecast reliability
    avg_prob_poor, obs_freq_poor, _ = reliability_diagram(fcst_poor, ground_truth, n_bins=NBINS)
    axes2[1].plot([0,1],[0,1],'k--', label='1-to-1')
    axes2[1].plot(avg_prob_poor, obs_freq_poor, 'o-', label='Poor Forecast')
    axes2[1].set_title('Reliability Diagram: Poor Forecast')
    axes2[1].set_xlabel('Mean Predicted Probability')
    axes2[1].set_xlim([0,1])
    axes2[1].set_ylim([0,1])
    axes2[1].legend()

    plt.tight_layout()
    plt.show()

    # 8. ROC curves
    fig3, ax3 = plt.subplots(figsize=(5,4))
    ax3.plot([0,1],[0,1],'k--', label='No-skill')
    ax3.plot(fpr_good, tpr_good, 'r-', label=f'Good Forecast (AUC={auc_good:.2f})')
    ax3.plot(fpr_poor, tpr_poor, 'b-', label=f'Poor Forecast (AUC={auc_poor:.2f})')
    ax3.set_xlabel('False Positive Rate')
    ax3.set_ylabel('True Positive Rate')
    ax3.set_title('ROC Curves')
    ax3.set_xlim([0,1])
    ax3.set_ylim([0,1])
    ax3.legend()
    plt.tight_layout()
    plt.show()

# If run as a script, invoke main()
if __name__ == '__main__':
    main()
