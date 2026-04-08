"""Train a baseline conversion propensity model.

This is a starter scaffold script. Replace synthetic data loading with
feature-store data in later phases.
"""

from sklearn.linear_model import LogisticRegression


def build_model() -> LogisticRegression:
    return LogisticRegression(max_iter=500, class_weight="balanced")


if __name__ == "__main__":
    model = build_model()
    print(f"Initialized model: {model.__class__.__name__}")
