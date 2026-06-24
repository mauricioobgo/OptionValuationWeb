"""Option pricing: binomial tree and Black-Scholes models."""
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class ValuationCalculus:
    spot: float
    strike: float
    rate: float
    volatility: float
    time_years: float
    nodes: int

    def _binomial_params(self) -> tuple[float, float, float, float]:
        """Return (u, d, prob_up, discount) for one time step."""
        dt = self.time_years / self.nodes
        u = np.exp(self.volatility * np.sqrt(dt))
        d = 1.0 / u
        growth = np.exp(self.rate * dt)
        prob_up = (growth - d) / (u - d)
        return u, d, prob_up, 1.0 / growth

    def _payoff(self, spots: np.ndarray, is_call: bool) -> np.ndarray:
        if is_call:
            return np.maximum(spots - self.strike, 0.0)
        return np.maximum(self.strike - spots, 0.0)

    def price_binomial(self, option_type: int) -> float:
        """Price via backward-induction binomial tree.

        option_type: 1=Call EU, 2=Put EU, 3=Call AM, 4=Put AM
        """
        u, d, prob_up, discount = self._binomial_params()
        prob_down = 1.0 - prob_up
        n = self.nodes
        is_call = option_type in (1, 3)
        is_american = option_type in (3, 4)

        j = np.arange(n + 1, dtype=float)
        terminal_spots = self.spot * u ** (n - j) * d ** j
        values = self._payoff(terminal_spots, is_call)

        for t in range(n - 1, -1, -1):
            cont = (prob_up * values[: t + 1] + prob_down * values[1 : t + 2]) * discount
            if is_american:
                j = np.arange(t + 1, dtype=float)
                node_spots = self.spot * u ** (t - j) * d ** j
                values[: t + 1] = np.maximum(cont, self._payoff(node_spots, is_call))
            else:
                values[: t + 1] = cont

        return float(values[0])

    def price_black_scholes(self, option_type: int) -> float:
        """Price via closed-form Black-Scholes.

        option_type: 5=Call BS, 6=Put BS
        """
        vol_sqrt_t = self.volatility * np.sqrt(self.time_years)
        d1 = (
            np.log(self.spot / self.strike)
            + (self.rate + 0.5 * self.volatility**2) * self.time_years
        ) / vol_sqrt_t
        d2 = d1 - vol_sqrt_t
        discount = np.exp(-self.rate * self.time_years)
        if option_type == 5:
            return float(self.spot * norm.cdf(d1) - self.strike * discount * norm.cdf(d2))
        return float(self.strike * discount * norm.cdf(-d2) - self.spot * norm.cdf(-d1))
