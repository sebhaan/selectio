"""
Factor importance model using mutual information.

Ref:
- https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.mutual_info_regression.html
- A. Kraskov, H. Stogbauer and P. Grassberger, "Estimating mutual
    information". Phys. Rev. E 69, 2004.
"""

from sklearn.feature_selection import mutual_info_regression
import numpy as np

def factor_importance(X_train, y_train, norm = True):
    """
    Factor importance using mutual information.

    Input:
        X: input data matrix with shape (npoints,nfeatures)
        y: target varable with shape (npoints)

    Return:
        mi: mutual information
    """

    mi = mutual_info_regression(X_train, y_train)
    if norm:
        mi /= np.max(mi)
    return mi