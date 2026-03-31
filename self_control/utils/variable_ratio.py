import math
import random


def _geometric_p(mean, min_value):
    """Compute the p parameter for a shifted geometric distribution."""
    return 1.0 / (mean - min_value + 1)


def generate_required_clicks_uniform(mean, min_value=1):
    """Generate required clicks using uniform distribution.
    Uniform distribution: [max(min_value, mean - mean//2), mean + mean//2]
    """
    half_range = mean // 2
    lower = max(min_value, mean - half_range)
    upper = mean + half_range
    return random.randint(lower, upper)


def generate_required_clicks(mean, min_value=1):
    """Generate required clicks for a VARIABLE RATIO/WARNING round.
    Shifted geometric distribution with minimum min_value and given mean.
    """
    p = _geometric_p(mean, min_value)
    return min_value + int(math.log(1 - random.random()) / math.log(1 - p))


def compute_warning_quartiles_uniform(mean, warning_hits):
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


def compute_warning_quartiles(mean, warning_hits):
    """Compute Q1, Q2, Q3 for the compound distribution of warning_signal_index.
    R ~ ShiftedGeometric(min_value=1, mean) and W|R ~ Uniform(1, R - warning_hits - 1).
    Returns the quartile cutoff points (Q1, Q2, Q3).
    """
    h = warning_hits
    min_value = 1
    p = _geometric_p(mean, min_value)
    a = max(min_value, h + 2)
    r_max = min_value + int(math.ceil(math.log(0.001) / math.log(1 - p)))

    def p_r(r):
        return p * (1 - p) ** (r - min_value)

    def pdf(w):
        total = 0
        for r in range(max(a, w + h + 1), r_max + 1):
            total += p_r(r) / (r - h - 1)
        return total

    max_w = r_max - h - 1
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
