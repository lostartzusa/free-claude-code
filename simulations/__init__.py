"""Discrete intensity-propagation simulation on arbitrary graphs.

Implements the recurrence::

    B_{t+1}(i) = (2/pi) [B_t(i) + alpha * sum_{j in N(i)} B_t(j)]

and analyses the effective information-propagation speed ("speed of light")
as a function of the propagation strength alpha and network topology.
"""
