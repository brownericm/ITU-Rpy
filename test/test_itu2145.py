#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for ITU-R P.2145 implementation.

These tests are skipped in CI because P.2145 data (2.3 GB) is not available.
To run these tests locally, first download the data:

    python scripts/download_p2145_data.py
"""
import os
import sys
import unittest

# Skip all tests in this module if data not available
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'itur', 'data', '2145')
SKIP_TESTS = not os.path.exists(DATA_DIR) or len(list(os.listdir(DATA_DIR))) < 50

if SKIP_TESTS:
    print("Skipping P.2145 tests - data not available (2.3 GB download required)")
    print("To download: python scripts/download_p2145_data.py")


@unittest.skipIf(SKIP_TESTS, "P.2145 data not available (2.3 GB download required)")
class TestITU2145(unittest.TestCase):
    """Tests for ITU-R P.2145 implementation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        try:
            from itur import models
            cls.models = models
            cls.versions = [0]
            cls.lat = 41.39
            cls.lon = -71.05
        except ImportError:
            raise unittest.SkipTest("itur module not available")
    
    def test_version_management(self):
        """Test version switching."""
        for version in self.versions:
            self.models.itu2145.change_version(version)
            self.assertEqual(self.models.itu2145.get_version(), version)
    
    def test_invalid_version(self):
        """Test invalid version raises error."""
        with self.assertRaises(ValueError):
            self.models.itu2145.change_version(99)
    
    def test_surface_pressure_scalar(self):
        """Test surface pressure with scalar input."""
        p_mean = self.models.itu2145.surface_pressure_mean(self.lat, self.lon)
        self.assertIsInstance(p_mean, float)
        self.assertGreater(p_mean, 800)  # Reasonable range (hPa)
        self.assertLess(p_mean, 1100)
    
    def test_surface_temperature_scalar(self):
        """Test surface temperature with scalar input."""
        t_mean = self.models.itu2145.surface_temperature_mean(self.lat, self.lon)
        self.assertIsInstance(t_mean, float)
        self.assertGreater(t_mean, 200)  # Reasonable range (K)
        self.assertLess(t_mean, 320)
    
    def test_surface_water_vapour_density_scalar(self):
        """Test surface water vapour density with scalar input."""
        rho_mean = self.models.itu2145.surface_water_vapour_density_mean(
            self.lat, self.lon
        )
        self.assertIsInstance(rho_mean, float)
        self.assertGreater(rho_mean, 0)  # Reasonable range (g/m³)
        self.assertLess(rho_mean, 50)
    
    def test_integrated_water_vapour_content_scalar(self):
        """Test integrated water vapour content with scalar input."""
        v_mean = self.models.itu2145.integrated_water_vapour_content_mean(
            self.lat, self.lon
        )
        self.assertIsInstance(v_mean, float)
        self.assertGreater(v_mean, 0)  # Reasonable range (kg/m²)
        self.assertLess(v_mean, 100)
    
    def test_percentile_interpolation(self):
        """Test percentile interpolation."""
        # Test a percentile that's not exactly in the data
        t_1_5 = self.models.itu2145.surface_temperature(self.lat, self.lon, p=1.5)
        self.assertIsInstance(t_1_5, float)
        
        # Should be between 1% and 2% values
        t_1 = self.models.itu2145.surface_temperature(self.lat, self.lon, p=1)
        t_2 = self.models.itu2145.surface_temperature(self.lat, self.lon, p=2)
        self.assertGreaterEqual(t_1_5, min(t_1, t_2))
        self.assertLessEqual(t_1_5, max(t_1, t_2))
    
    def test_monthly_data(self):
        """Test monthly statistics."""
        # Test July (month 7)
        t_jul = self.models.itu2145.surface_temperature_mean(
            self.lat, self.lon, month=7
        )
        self.assertIsInstance(t_jul, float)
        
        # Should be different from annual
        t_annual = self.models.itu2145.surface_temperature_mean(
            self.lat, self.lon
        )
        # Just verify they're both reasonable temperatures
        self.assertGreater(t_jul, 200)
        self.assertLess(t_jul, 320)
    
    def test_weibull_parameters(self):
        """Test Weibull distribution parameters."""
        k_v = self.models.itu2145.weibull_shape(self.lat, self.lon)
        lambda_v = self.models.itu2145.weibull_scale(self.lat, self.lon)
        
        self.assertIsInstance(k_v, float)
        self.assertIsInstance(lambda_v, float)
        self.assertGreater(k_v, 0)
        self.assertGreater(lambda_v, 0)
    
    def test_scale_heights(self):
        """Test scale height calculations."""
        p_scale = self.models.itu2145.pressure_scale_height(self.lat, self.lon)
        t_scale = self.models.itu2145.temperature_scale_height(self.lat, self.lon)
        v_scale = self.models.itu2145.water_vapour_scale_height(self.lat, self.lon)
        
        self.assertIsInstance(p_scale, float)
        self.assertIsInstance(t_scale, float)
        self.assertIsInstance(v_scale, float)
        
        # Scale heights should be positive
        self.assertGreater(p_scale, 0)
        self.assertGreater(t_scale, 0)
        self.assertGreater(v_scale, 0)
    
    def test_ground_elevation(self):
        """Test ground elevation."""
        z_ground = self.models.itu2145.ground_elevation(self.lat, self.lon)
        
        self.assertIsInstance(z_ground, float)
        # Ground elevation should be reasonable (km)
        self.assertGreater(z_ground, -1)  # Allow below sea level
        self.assertLess(z_ground, 9)  # Below Mt Everest


if __name__ == '__main__':
    unittest.main()
