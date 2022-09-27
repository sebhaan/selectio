"""
Factor importance using randomized decision trees (a.k.a. extra-trees)
on various sub-samples of the dataset
"""

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor


def factor_importance(X_train, y_train, norm = False):
    """
    Factor importance using randomized decision trees (a.k.a. extra-trees)
    on various sub-samples of the dataset

    Input:
        X: input data matrix with shape (npoints,nfeatures)
        y: target varable with shape (npoints)
        norm: normalize results to maximum feature importance is unity

    Return:
        result: feature importances
    """
    model = ExtraTreesRegressor(n_estimators=500, random_state = 42)
    model.fit(X_train, y_train)
    result = model.feature_importances_
    result[result < 0.001] = 0
    if norm:
        result /= result.max()
    return result