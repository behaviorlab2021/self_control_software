import random


def generate_required_clicks(mean, min_value=1):
    """Generate required clicks for a VARIABLE RATIO/WARNING round.
    Uniform distribution: [max(min_value, mean - mean//2), mean + mean//2]
    """
    half_range = mean // 2
    lower = max(min_value, mean - half_range)
    upper = mean + half_range
    return random.randint(lower, upper)


def compute_warning_quartiles(mean, warning_hits):
    """Compute Q1, Q2, Q3 for the compound distribution of warning_signal_index.
    R ~ Uniform(lower, upper) and W|R ~ Uniform(1, R - warning_hits - 1).
    Returns the quartile cutoff points (Q1, Q2, Q3).
    """
    h = warning_hits
    half = mean // 2
    a = max(h + 2, mean - half)
    b = mean + half
    n_r = b - a + 1

    def pdf(w):
        total = 0
        for r in range(max(a, w + h + 1), b + 1):
            total += 1.0 / (r - h - 1)
        return total / n_r

    max_w = b - h - 1
    cumulative = 0
    q1 = q2 = q3 = None
    for w in range(1, max_w + 1):
        cumulative += pdf(w)
        if cumulative >= 0.25 and q1 is None:
            q1 = w
        if cumulative >= 0.50 and q2 is None:
            q2 = w
        if cumulative >= 0.75 and q3 is None:
            q3 = w
            break

    return q1, q2, q3
