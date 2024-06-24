import numpy as np


def softmax(x):
    """
    Compute the softmax of vector x.

    Parameters:
    x (numpy.ndarray): Input array.

    Returns:
    numpy.ndarray: Softmax of the input array.
    """
    # Subtract the maximum value from the input array for numerical stability
    exp_shifted = np.exp(x - np.max(x))

    # Calculate the softmax
    softmax_values = exp_shifted / np.sum(exp_shifted)

    return softmax_values


# Example usage:
x = np.array([0.0320586, 0.08714432 , 0.23688282])
print(softmax(x))

# [0.09003057 0.24472847 0.66524096]
# [0.0320586  0.08714432 0.23688282 0.64391426]
#