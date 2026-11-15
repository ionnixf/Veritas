import pytest


@pytest.fixture(autouse=True)
def forbid_training(monkeypatch):
    """Application tests must use the frozen model without fitting."""
    import xgboost
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.tree import DecisionTreeClassifier

    def forbidden(*args, **kwargs):
        raise AssertionError("Training/fitted preprocessing is forbidden in preparation checks")

    for klass in [
        xgboost.XGBClassifier,
        DummyClassifier,
        IsolationForest,
        LogisticRegression,
        DecisionTreeClassifier,
        Pipeline,
        SimpleImputer,
        StandardScaler,
        OneHotEncoder,
    ]:
        monkeypatch.setattr(klass, "fit", forbidden)
    monkeypatch.setattr(xgboost, "train", forbidden)
    monkeypatch.setattr(xgboost.Booster, "update", forbidden)
    monkeypatch.setattr(xgboost.Booster, "boost", forbidden)
