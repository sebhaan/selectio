""" 
Association measurement through cross rank increments

Calculation of general correlation coefficient 
as described in Chatterjee, S. (2019, September 22):
A new coefficient of correlation. arxiv.org/abs/1909.10140
Returns correlation coefficient for testing independence

In comparison to Spearman, Pearson, and Kendalls, this new correlation coefficient
can measure associations that are not monotonic or non-linear, 
and is 0 if X and Y are independent, and is 1 if there is a function Y= f(X).
Note that this coefficient is intentionally not summetric, because we want to understand 
if Y is a function X, and not just if one of the variables is a function of the other.
"""

import numpy as np
import scipy.stats as stats

__name__ = 'XICOR'
__fullname__= 'Generalized Correlation Coefficient'


def factor_importance(X, y, norm = True):
    """
    Calculation of general correlation coefficient 

    This function also removes Nans and converts factor variables to integers automatically.

    Input:
        X: data feature array with shape (npoints, n_features)
        y: target variable as vector with size npoints
        norm: boolean, if True (default) normalize correlation coefficients to sum = 1

    Return:
        corr: correlation coefficients
    """
    n_features = X.shape[1] 
    corr = np.empty(n_features)
    pvals = np.empty(n_features)
    for i in range(n_features):
        xi_obj = Xicor(X[:,i], y)
        corr[i] = xi_obj.correlation
        pvals[i] = xi_obj.pval_asymptotic(ties=False, nperm=1000)
    # set correlation coefficient to zero for non-significant p_values (P > 0.01)
    corr[pvals>0.01] = 0
    if norm:
        if np.sum(corr) > 0:
            corr /= np.sum(corr)
        else:
            corr = np.zeros(len(corr))
    return corr


class Xicor:
    """
    Calculation of general correlation coefficient 
    as described in Chatterjee, S. (2019, September 22):
    A new coefficient of correlation. arxiv.org/abs/1909.10140
    Returns correlation coefficient for testing independence.

    In comparison to Spearman, Pearson, and Kendalls, this new correlation coefficient
    can measure associations that are not monotonic or non-linear, 
    and is 0 if X and Y are independent, and is 1 if there is a function Y= f(X).
    Note that this coefficient is  not symmetric, because we want to understand 
    if Y is a function X, and not just if one of the variables is a function of the other.

    Core compution follows implementation https://github.com/czbiohub/xicor, 
    and a stochastic data sampler is added for large samples to speed-up computation.

    x and y are the data vectors
    """

    def __init__(self, x, y):

        
        #if x.shape[0] > 2000:
        #	x = 

        self.x = x
        self.y = y

        self.stochastic_sample()

    def stochastic_sample(self, threshold = 1000):
        """
        Select random subsample of data if threshold is crossed
        """
        nsample = len(self.x)
        if nsample > threshold:
            idx = np.random.choice(np.arange(0,nsample), size = threshold, replace = False)
            self.x = self.x[idx]
            self.y = self.y[idx]

    @property
    def sample_size(self):
        return len(self.x)

    @property
    def x_ordered_rank(self):
        # PI is the rank vector for x, with ties broken at random
        # source (https://stackoverflow.com/a/47430384/1628971)
        # random shuffling of the data - reason to use random.choice is that
        # pd.sample(frac=1) uses the same randomizing algorithm
        len_x = len(self.x)
        randomized_indices = np.random.choice(np.arange(len_x), len_x, replace=False)
        randomized = [self.x[idx] for idx in randomized_indices]
        # same as pandas rank method 'first'
        rankdata = stats.rankdata(randomized, method="ordinal")
        # Reindexing based on pairs of indices before and after
        unrandomized = [
            rankdata[j] for i, j in sorted(zip(randomized_indices, range(len_x)))
        ]
        return unrandomized

    @property
    def y_rank_max(self):
        # f[i] is number of j s.t. y[j] <= y[i], divided by n.
        return stats.rankdata(self.y, method="max") / self.sample_size

    @property
    def g(self):
        # g[i] is number of j s.t. y[j] >= y[i], divided by n.
        return stats.rankdata([-i for i in self.y], method="max") / self.sample_size

    @property
    def x_ordered(self):
        # order of the x's, ties broken at random.
        return np.argsort(self.x_ordered_rank)

    @property
    def x_rank_max_ordered(self):
        # Rearrange f according to ord.
        return [self.y_rank_max[i] for i in self.x_ordered]
        
    @property
    def mean_absolute(self):
        return (
            np.mean(
                np.abs(
                    [
                        x - y
                        for x, y in zip(
                            self.x_rank_max_ordered[0 : (self.sample_size - 1)],
                            self.x_rank_max_ordered[1 : self.sample_size],
                        )
                    ]
                )
            )
            * (self.sample_size - 1)
            / (2 * self.sample_size)
        )

    @property
    def inverse_g_mean(self):
        return np.mean(self.g * (1 - self.g))

    @property
    def correlation(self):
        """xi correlation"""
        return 1 - self.mean_absolute / self.inverse_g_mean

    @classmethod
    def xi(cls, x, y):
        return cls(x, y)

    def pval_asymptotic(self, ties=False, nperm=1000):
        """
        Returns p values of the correlation
        Args:
            ties: boolean
                If ties is true, the algorithm assumes that the data has ties
                and employs the more elaborated theory for calculating
                the P-value. Otherwise, it uses the simpler theory. There is
                no harm in setting tiles True, even if there are no ties.
            nperm: int
                The number of permutations for the permutation test, if needed.
                default 1000
        Returns:
            p value
        """
        # If there are no ties, return xi and theoretical P-value:

        if ties:
            return 1 - stats.norm.cdf(
                np.sqrt(self.sample_size) * self.correlation / np.sqrt(2 / 5)
            )

        # If there are ties, and the theoretical method
        # is to be used for calculation P-values:
        # The following steps calculate the theoretical variance
        # in the presence of ties:
        sorted_ordered_x_rank = sorted(self.x_rank_max_ordered)

        ind = [i + 1 for i in range(self.sample_size)]
        ind2 = [2 * self.sample_size - 2 * ind[i - 1] + 1 for i in ind]

        a = (
            np.mean([i * j * j for i, j in zip(ind2, sorted_ordered_x_rank)])
            / self.sample_size
        )

        c = (
            np.mean([i * j for i, j in zip(ind2, sorted_ordered_x_rank)])
            / self.sample_size
        )

        cq = np.cumsum(sorted_ordered_x_rank)

        m = [
            (i + (self.sample_size - j) * k) / self.sample_size
            for i, j, k in zip(cq, ind, sorted_ordered_x_rank)
        ]

        b = np.mean([np.square(i) for i in m])
        v = (a - 2 * b + np.square(c)) / np.square(self.inverse_g_mean)

        return 1 - stats.norm.cdf(
            np.sqrt(self.sample_size) * self.correlation / np.sqrt(v)
        )