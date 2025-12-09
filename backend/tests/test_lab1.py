"""
Unit tests for Lab 1: GCD and LCG
"""

import pytest
import numpy as np
from lab1_utils.gcd import gcd
from lab1_utils.lcg import lcg


class TestGCD:
    """Test cases for GCD function"""

    def test_gcd_basic(self):
        """Test basic GCD calculations"""
        assert gcd(48, 18) == 6
        assert gcd(100, 50) == 50
        assert gcd(17, 13) == 1
        assert gcd(270, 192) == 6

    def test_gcd_with_zero(self):
        """Test GCD with zero"""
        assert gcd(5, 0) == 5
        assert gcd(0, 7) == 7
        assert gcd(0, 0) == 0

    def test_gcd_with_one(self):
        """Test GCD with one"""
        assert gcd(1, 1) == 1
        assert gcd(1, 100) == 1
        assert gcd(50, 1) == 1

    def test_gcd_same_numbers(self):
        """Test GCD of same numbers"""
        assert gcd(42, 42) == 42
        assert gcd(7, 7) == 7
        assert gcd(100, 100) == 100

    def test_gcd_prime_numbers(self):
        """Test GCD of prime numbers"""
        assert gcd(7, 11) == 1
        assert gcd(13, 17) == 1
        assert gcd(23, 29) == 1

    def test_gcd_large_numbers(self):
        """Test GCD with large numbers"""
        assert gcd(123456, 789012) == 12
        assert gcd(1000000, 500000) == 500000
        assert gcd(999999, 111111) == 111111

    def test_gcd_commutative(self):
        """Test that GCD is commutative (a,b) = (b,a)"""
        assert gcd(48, 18) == gcd(18, 48)
        assert gcd(100, 75) == gcd(75, 100)
        assert gcd(17, 19) == gcd(19, 17)


class TestLCG:
    """Test cases for Linear Congruential Generator"""

    def test_lcg_basic(self):
        """Test basic LCG generation"""
        numbers = lcg(seed=1, a=1103515245, c=12345, m=2**31, n=5)
        assert len(numbers) == 5
        assert all(isinstance(n, int) for n in numbers)
        assert all(0 <= n < 2**31 for n in numbers)

    def test_lcg_deterministic(self):
        """Test that LCG is deterministic (same seed produces same results)"""
        params = {"seed": 42, "a": 1103515245, "c": 12345, "m": 2**31, "n": 10}
        numbers1 = lcg(**params)
        numbers2 = lcg(**params)
        assert numbers1 == numbers2

    def test_lcg_different_seeds(self):
        """Test that different seeds produce different sequences"""
        numbers1 = lcg(seed=1, a=1103515245, c=12345, m=2**31, n=10)
        numbers2 = lcg(seed=2, a=1103515245, c=12345, m=2**31, n=10)
        assert numbers1 != numbers2

    def test_lcg_output_range(self):
        """Test that LCG output is within valid range"""
        m = 2**20 - 1
        numbers = lcg(seed=1, a=343, c=89, m=m, n=100)
        assert all(0 <= n < m for n in numbers)

    def test_lcg_length(self):
        """Test that LCG generates correct number of values"""
        for n in [1, 5, 10, 50, 100]:
            numbers = lcg(seed=1, a=343, c=89, m=2**20, n=n)
            assert len(numbers) == n

    def test_lcg_default_params(self):
        """Test LCG with commonly used parameters"""
        numbers = lcg(seed=1, a=1103515245, c=12345, m=2**31, n=20)
        assert len(numbers) == 20
        # Verify numbers are distinct (no immediate repetition)
        assert len(set(numbers)) > 1

    def test_lcg_small_modulus(self):
        """Test LCG with small modulus"""
        m = 100
        numbers = lcg(seed=1, a=21, c=17, m=m, n=50)
        assert all(0 <= n < m for n in numbers)

    def test_lcg_zero_increment(self):
        """Test LCG with zero increment (multiplicative congruential generator)"""
        numbers = lcg(seed=1, a=7, c=0, m=100, n=10)
        assert len(numbers) == 10
        assert all(isinstance(n, int) for n in numbers)

    def test_lcg_returns_list(self):
        """Test that LCG returns a list, not numpy array"""
        numbers = lcg(seed=1, a=343, c=89, m=2**20, n=5)
        assert isinstance(numbers, list)
        assert not isinstance(numbers, np.ndarray)