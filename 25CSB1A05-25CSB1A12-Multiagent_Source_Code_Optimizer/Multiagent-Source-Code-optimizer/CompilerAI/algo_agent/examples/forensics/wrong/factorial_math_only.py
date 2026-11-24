# Known-wrong rewrite: math.factorial for everything
# Original returns 1 for n <= 1 (including negatives and floats like 0.5)
import math

def factorial(n):
    return math.factorial(n)
