# -*- coding: utf-8 -*-
"""
Implementation of ITU-R P.2145-0: Digital maps related to the calculation of
gaseous attenuation and related effects.

This recommendation provides worldwide annual and monthly statistics of:
- Surface total (barometric) pressure (hPa)
- Surface temperature (K)
- Surface water vapour density (g/m³)
- Integrated water vapour content (kg/m² or mm)

Data source: 30 years of ECMWF ERA5 reanalysis data
"""
from __future__ import absolute_import, division, print_function

import os
import numpy as np

from itur import utils
from itur.models import itu1511

# Constants
dataset_dir = os.path.join(os.path.dirname(__file__), '..', 'data')


def _ensure_data_available():
    """
    Check if P.2145 data is available, raise helpful error if not.
    
    Raises
    ------
    RuntimeError
        If data files are not found, with instructions for downloading
    """
    from pathlib import Path
    data_dir = Path(dataset_dir) / '2145'
    
    # Check if data directory exists and has files
    if not data_dir.exists() or not any(data_dir.glob('*.npz')):
        raise RuntimeError(
            "\n"
            "=" * 70 + "\n"
            "ITU-R P.2145 DATA NOT FOUND\n"
            "=" * 70 + "\n"
            "\n"
            "The meteorological data files (2.3 GB) must be downloaded separately.\n"
            "\n"
            "TO DOWNLOAD:\n"
            "\n"
            "  Option 1: Run the download script\n"
            "    python scripts/download_p2145_data.py\n"
            "\n"
            "  Option 2: Use Python\n"
            "    from itur.utils import download_p2145_data\n"
            "    download_p2145_data()\n"
            "\n"
            "  Option 3: Manual download\n"
            "    1. Visit: https://zenodo.org/record/18872526\n"
            "    2. Download the archive\n"
            "    3. Extract to: " + str(data_dir) + "\n"
            "\n"
            "Data source: Zenodo (DOI: 10.5281/zenodo.18872526)\n"
            "Size: 1.8 GB compressed, 2.3 GB extracted\n"
            "=" * 70 + "\n"
        )


class __ITU2145__():
    """Wrapper class for ITU-R P.2145 recommendations.
    
    This class provides version management and dispatches to the
    appropriate version-specific implementation.
    """
    
    def __init__(self, version=0):
        if version == 0:
            self.instance = _ITU2145_0_()
        else:
            raise ValueError(f"Version {version} not implemented")
        
        self._version = version
    
    def get_version(self):
        return self._version
    
    def change_version(self, new_version):
        if new_version == 0:
            self.instance = _ITU2145_0_()
            self._version = new_version
        else:
            raise ValueError(f"Version {new_version} not implemented")


class _ITU2145_0_():
    """Implementation of ITU-R P.2145-0 (08/2022)
    
    Digital maps related to the calculation of gaseous attenuation
    and related effects.
    """
    
    def __init__(self):
        self.__version__ = 0
        self.year = 2022
        self.month = 8
        self.link = 'https://www.itu.int/rec/R-REC-P.2145-0-202208-I/en'
        
        # Available percentiles (22 values from 0.01% to 99%)
        self.percentiles = [
            0.01, 0.02, 0.03, 0.05,
            0.10, 0.20, 0.30, 0.50,
            1.0, 2.0, 3.0, 5.0,
            10.0, 20.0, 30.0, 50.0,
            60.0, 70.0, 80.0, 90.0,
            95.0, 99.0
        ]
        
        # Interpolators (lazy-loaded)
        self._pressure = {}
        self._temperature = {}
        self._water_vapour = {}
        self._integrated_water_vapour = {}
        self._pressure_scale_height = None
        self._temperature_scale_height = None
        self._water_vapour_scale_height = None
        self._ground_elevation = None
        self._weibull = None
    
    def _get_data_filename(self, variable, month=None):
        """Get the data filename for a given variable and month.
        
        Parameters
        ----------
        variable : str
            One of 'p' (pressure), 't' (temperature), 'rho' (water vapour density),
            'v' (integrated water vapour content)
        month : int or None
            Month number (1-12) or None for annual
        
        Returns
        -------
        str
            Filename
        """
        if month is None:
            return f'{variable}_annual.npz'
        else:
            return f'{variable}_month{month:02d}.npz'
    
    def _load_percentile_data(self, variable, lat, lon, p, month=None, alt=None):
        """Load and interpolate data for a given percentile.
        
        Parameters
        ----------
        variable : str
            Variable identifier ('p', 't', 'rho', or 'v')
        lat, lon : array_like
            Geographic coordinates (degrees)
        p : float
            Exceedance probability (0.01 to 99%)
        month : int or None
            Month number (1-12) or None for annual
        alt : array_like or None
            Altitude above sea level (km). If None, uses P.1511
        
        Returns
        -------
        ndarray
            Interpolated values
        """
        # Check if data is available
        _ensure_data_available()
        
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load data file
        filename = self._get_data_filename(variable, month)
        filepath = os.path.join(dataset_dir, '2145', filename)
        
        # Check if we've already loaded this data
        cache_key = f'{variable}_{month}' if month else f'{variable}_annual'
        
        if variable == 'p':
            cache = self._pressure
        elif variable == 't':
            cache = self._temperature
        elif variable == 'rho':
            cache = self._water_vapour
        elif variable == 'v':
            cache = self._integrated_water_vapour
        else:
            raise ValueError(f"Unknown variable: {variable}")
        
        if cache_key not in cache:
            data = np.load(filepath)
            lat_1d = data['lat']
            lon_1d = data['lon']
            
            # Create meshgrid from 1D lat/lon arrays
            lon_grid, lat_grid = np.meshgrid(lon_1d, lat_1d)
            
            cache[cache_key] = {
                'lat': lat_grid,
                'lon': lon_grid,
                'data': data['data']
            }
        
        # Interpolate
        from itur.models.itu1144 import bilinear_2D_interpolator
        interp = bilinear_2D_interpolator(
            data_cache['lat'], 
            data_cache['lon'],
            data_cache['data']
        )
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)
        
        # Get data from cache
        data_cache = cache[cache_key]
        
        # Find bounding percentiles
        p_below = max([pct for pct in self.percentiles if pct <= p])
        p_above = min([pct for pct in self.percentiles if pct >= p])
        
        # If exact percentile match, use it directly
        if p_below == p_above:
            from itur.models.itu1144 import bilinear_2D_interpolator
            interp = bilinear_2D_interpolator(
                data_cache['lat'], 
                data_cache['lon'],
                data_cache['percentiles'][p_below]
            )
            values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        else:
            # Interpolate between percentiles
            from itur.models.itu1144 import bilinear_2D_interpolator
            
            interp_below = bilinear_2D_interpolator(
                data_cache['lat'],
                data_cache['lon'],
                data_cache['percentiles'][p_below]
            )
            interp_above = bilinear_2D_interpolator(
                data_cache['lat'],
                data_cache['lon'],
                data_cache['percentiles'][p_above]
            )
            
            val_below = interp_below(np.array([lat.ravel(), lon.ravel()]).T)
            val_above = interp_above(np.array([lat.ravel(), lon.ravel()]).T)
            
            # Linear interpolation in percentile space
            values = val_below + (val_above - val_below) * (p - p_below) / (p_above - p_below)
        
        # Apply altitude correction if needed
        if alt is not None:
            values = self._apply_altitude_correction(variable, lat, lon, values, alt, month)
        
        return utils.prepare_output_array(values, type_input)
    
    def _load_mean_data(self, variable, lat, lon, month=None, alt=None):
        """Load and interpolate mean data.
        
        Parameters
        ----------
        variable : str
            Variable identifier ('p', 't', 'rho', or 'v')
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual
        alt : array_like or None
            Altitude above sea level (km). If None, uses P.1511
        
        Returns
        -------
        ndarray
            Interpolated mean values
        """
        # Check if data is available
        _ensure_data_available()
        
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load data file
        filename = self._get_data_filename(variable, month)
        filepath = os.path.join(dataset_dir, '2145', filename)
        
        # Check cache
        cache_key = f'{variable}_{month}' if month else f'{variable}_annual'
        
        if variable == 'p':
            cache = self._pressure
        elif variable == 't':
            cache = self._temperature
        elif variable == 'rho':
            cache = self._water_vapour
        elif variable == 'v':
            cache = self._integrated_water_vapour
        else:
            raise ValueError(f"Unknown variable: {variable}")
        
        if cache_key not in cache:
            # Load and cache data
            data = np.load(filepath)
            cache[cache_key] = {
                'lat': data['lat'],
                'lon': data['lon'],
                'mean': data['mean'],
                'std': data['std'],
                'percentiles': {}
            }
        
        # Interpolate mean values
        from itur.models.itu1144 import bilinear_2D_interpolator
        data_cache = cache[cache_key]
        
        interp = bilinear_2D_interpolator(
            data_cache['lat'],
            data_cache['lon'],
            data_cache['mean']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        # Apply altitude correction if needed
        if alt is not None:
            values = self._apply_altitude_correction(variable, lat, lon, values, alt, month)
        
        return utils.prepare_output_array(values, type_input)
    
    def _load_std_data(self, variable, lat, lon, month=None):
        """Load and interpolate standard deviation data.
        
        Parameters
        ----------
        variable : str
            Variable identifier ('p', 't', 'rho', or 'v')
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual
        
        Returns
        -------
        ndarray
            Interpolated standard deviation values
        """
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load data file
        filename = self._get_data_filename(variable, month)
        filepath = os.path.join(dataset_dir, '2145', filename)
        
        # Check cache
        cache_key = f'{variable}_{month}' if month else f'{variable}_annual'
        
        if variable == 'p':
            cache = self._pressure
        elif variable == 't':
            cache = self._temperature
        elif variable == 'rho':
            cache = self._water_vapour
        elif variable == 'v':
            cache = self._integrated_water_vapour
        else:
            raise ValueError(f"Unknown variable: {variable}")
        
        if cache_key not in cache:
            # Load and cache data
            data = np.load(filepath)
            cache[cache_key] = {
                'lat': data['lat'],
                'lon': data['lon'],
                'mean': data['mean'],
                'std': data['std'],
                'percentiles': {}
            }
        
        # Interpolate std values
        from itur.models.itu1144 import bilinear_2D_interpolator
        data_cache = cache[cache_key]
        
        interp = bilinear_2D_interpolator(
            data_cache['lat'],
            data_cache['lon'],
            data_cache['std']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)
    
    def _apply_altitude_correction(self, variable, lat, lon, values, alt, month=None):
        """Apply altitude correction using scale heights.
        
        Parameters
        ----------
        variable : str
            Variable identifier
        lat, lon : array_like
            Geographic coordinates
        values : array_like
            Values to correct
        alt : array_like
            Target altitude (km)
        month : int or None
            Month for scale height selection
        
        Returns
        -------
        ndarray
            Altitude-corrected values
        """
        # Get ground elevation from P.2145 data
        z_ground = self.ground_elevation(lat, lon)
        
        # Get appropriate scale height
        if variable == 'p':
            scale_height = self.pressure_scale_height(lat, lon, month)
        elif variable == 't':
            scale_height = self.temperature_scale_height(lat, lon, month)
        elif variable in ['rho', 'v']:
            scale_height = self.water_vapour_scale_height(lat, lon, month)
        else:
            return values  # No correction for unknown variables
        
        # Apply altitude correction: X_i = X_i' * exp(-(alt - alt_i) / scale_height)
        correction = np.exp(-(alt - z_ground) / scale_height)
        
        return values * correction
    
    # ==================== SURFACE PRESSURE ====================
    
    def surface_pressure(self, lat, lon, p=None, month=None, alt=None):
        """Calculate surface total (barometric) pressure.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        p : float or None
            Exceedance probability (%) [0.01 to 99]. If None, returns mean
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Surface pressure (hPa)
        """
        if p is None:
            return self.surface_pressure_mean(lat, lon, month, alt)
        else:
            return self._load_percentile_data('p', lat, lon, p, month, alt)
    
    def surface_pressure_mean(self, lat, lon, month=None, alt=None):
        """Calculate mean surface pressure.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Mean surface pressure (hPa)
        """
        return self._load_mean_data('p', lat, lon, month, alt)
    
    def surface_pressure_std(self, lat, lon, month=None):
        """Calculate standard deviation of surface pressure.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        
        Returns
        -------
        ndarray
            Standard deviation of surface pressure (hPa)
        """
        return self._load_std_data('p', lat, lon, month)
    
    # ==================== SURFACE TEMPERATURE ====================
    
    def surface_temperature(self, lat, lon, p=None, month=None, alt=None):
        """Calculate surface temperature.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        p : float or None
            Exceedance probability (%) [0.01 to 99]. If None, returns mean
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Surface temperature (K)
        """
        if p is None:
            return self.surface_temperature_mean(lat, lon, month, alt)
        else:
            return self._load_percentile_data('t', lat, lon, p, month, alt)
    
    def surface_temperature_mean(self, lat, lon, month=None, alt=None):
        """Calculate mean surface temperature.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Mean surface temperature (K)
        """
        return self._load_mean_data('t', lat, lon, month, alt)
    
    def surface_temperature_std(self, lat, lon, month=None):
        """Calculate standard deviation of surface temperature.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        
        Returns
        -------
        ndarray
            Standard deviation of surface temperature (K)
        """
        return self._load_std_data('t', lat, lon, month)
    
    # ==================== SURFACE WATER VAPOUR DENSITY ====================
    
    def surface_water_vapour_density(self, lat, lon, p=None, month=None, alt=None):
        """Calculate surface water vapour density.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        p : float or None
            Exceedance probability (%) [0.01 to 99]. If None, returns mean
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Surface water vapour density (g/m³)
        """
        if p is None:
            return self.surface_water_vapour_density_mean(lat, lon, month, alt)
        else:
            return self._load_percentile_data('rho', lat, lon, p, month, alt)
    
    def surface_water_vapour_density_mean(self, lat, lon, month=None, alt=None):
        """Calculate mean surface water vapour density.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Mean surface water vapour density (g/m³)
        """
        return self._load_mean_data('rho', lat, lon, month, alt)
    
    def surface_water_vapour_density_std(self, lat, lon, month=None):
        """Calculate standard deviation of surface water vapour density.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        
        Returns
        -------
        ndarray
            Standard deviation of surface water vapour density (g/m³)
        """
        return self._load_std_data('rho', lat, lon, month)
    
    # ==================== INTEGRATED WATER VAPOUR CONTENT ====================
    
    def integrated_water_vapour_content(self, lat, lon, p=None, month=None, alt=None):
        """Calculate integrated water vapour content.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        p : float or None
            Exceedance probability (%) [0.01 to 99]. If None, returns mean
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Integrated water vapour content (kg/m² or mm)
        """
        if p is None:
            return self.integrated_water_vapour_content_mean(lat, lon, month, alt)
        else:
            return self._load_percentile_data('v', lat, lon, p, month, alt)
    
    def integrated_water_vapour_content_mean(self, lat, lon, month=None, alt=None):
        """Calculate mean integrated water vapour content.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Mean integrated water vapour content (kg/m² or mm)
        """
        return self._load_mean_data('v', lat, lon, month, alt)
    
    def integrated_water_vapour_content_std(self, lat, lon, month=None):
        """Calculate standard deviation of integrated water vapour content.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        
        Returns
        -------
        ndarray
            Standard deviation of integrated water vapour content (kg/m² or mm)
        """
        return self._load_std_data('v', lat, lon, month)
    
    # ==================== WEIBULL PARAMETERS ====================
    
    def weibull_shape(self, lat, lon, alt=None):
        """Calculate Weibull shape parameter for integrated water vapour content.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Weibull shape parameter k_Vs
        """
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load Weibull data
        if self._weibull is None:
            filepath = os.path.join(dataset_dir, '2145', 'weibull_annual.npz')
            data = np.load(filepath)
            self._weibull = {
                'lat': data['lat'],
                'lon': data['lon'],
                'lambda_v': data['lambda_v'],
                'k_v': data['k_v']
            }
        
        # Interpolate
        from itur.models.itu1144 import bilinear_2D_interpolator
        interp = bilinear_2D_interpolator(
            self._weibull['lat'],
            self._weibull['lon'],
            self._weibull['k_v']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)
    
    def weibull_scale(self, lat, lon, alt=None):
        """Calculate Weibull scale parameter for integrated water vapour content.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        alt : array_like or None
            Altitude above sea level (km). If None, no altitude correction
        
        Returns
        -------
        ndarray
            Weibull scale parameter lambda_Vs (kg/m² or mm)
        """
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load Weibull data
        if self._weibull is None:
            filepath = os.path.join(dataset_dir, '2145', 'weibull_annual.npz')
            data = np.load(filepath)
            self._weibull = {
                'lat': data['lat'],
                'lon': data['lon'],
                'lambda_v': data['lambda_v'],
                'k_v': data['k_v']
            }
        
        # Interpolate
        from itur.models.itu1144 import bilinear_2D_interpolator
        interp = bilinear_2D_interpolator(
            self._weibull['lat'],
            self._weibull['lon'],
            self._weibull['lambda_v']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)
    
    # ==================== SCALE HEIGHTS ====================
    
    def pressure_scale_height(self, lat, lon, month=None):
        """Calculate pressure scale height.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        
        Returns
        -------
        ndarray
            Pressure scale height (km)
        """
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load scale height data
        if self._pressure_scale_height is None:
            filepath = os.path.join(dataset_dir, '2145', 'psch.npz')
            data = np.load(filepath)
            self._pressure_scale_height = {
                'lat': data['lat'],
                'lon': data['lon'],
                'data': data['data']
            }
        
        # Interpolate
        from itur.models.itu1144 import bilinear_2D_interpolator
        interp = bilinear_2D_interpolator(
            self._pressure_scale_height['lat'],
            self._pressure_scale_height['lon'],
            self._pressure_scale_height['data']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)
    
    def temperature_scale_height(self, lat, lon, month=None):
        """Calculate temperature scale height.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        
        Returns
        -------
        ndarray
            Temperature scale height (km)
        """
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load scale height data
        if self._temperature_scale_height is None:
            filepath = os.path.join(dataset_dir, '2145', 'tsch.npz')
            data = np.load(filepath)
            self._temperature_scale_height = {
                'lat': data['lat'],
                'lon': data['lon'],
                'data': data['data']
            }
        
        # Interpolate
        from itur.models.itu1144 import bilinear_2D_interpolator
        interp = bilinear_2D_interpolator(
            self._temperature_scale_height['lat'],
            self._temperature_scale_height['lon'],
            self._temperature_scale_height['data']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)
    
    def water_vapour_scale_height(self, lat, lon, month=None):
        """Calculate water vapour scale height.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        month : int or None
            Month number (1-12) or None for annual statistics
        
        Returns
        -------
        ndarray
            Water vapour scale height (km)
        """
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load scale height data
        if self._water_vapour_scale_height is None:
            filepath = os.path.join(dataset_dir, '2145', 'vsch.npz')
            data = np.load(filepath)
            self._water_vapour_scale_height = {
                'lat': data['lat'],
                'lon': data['lon'],
                'data': data['data']
            }
        
        # Interpolate
        from itur.models.itu1144 import bilinear_2D_interpolator
        interp = bilinear_2D_interpolator(
            self._water_vapour_scale_height['lat'],
            self._water_vapour_scale_height['lon'],
            self._water_vapour_scale_height['data']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)
    
    # ==================== GROUND ELEVATION ====================
    
    def ground_elevation(self, lat, lon):
        """Calculate ground elevation above mean sea level.
        
        Parameters
        ----------
        lat, lon : array_like
            Geographic coordinates (degrees)
        
        Returns
        -------
        ndarray
            Ground elevation (km)
        """
        # Prepare inputs
        lat = utils.prepare_input_array(lat)
        lon = utils.prepare_input_array(lon)
        type_input = utils.get_input_type(lat)
        
        # Load ground elevation data
        if self._ground_elevation is None:
            filepath = os.path.join(dataset_dir, '2145', 'z_ground.npz')
            data = np.load(filepath)
            self._ground_elevation = {
                'lat': data['lat'],
                'lon': data['lon'],
                'data': data['data']
            }
        
        # Interpolate
        from itur.models.itu1144 import bilinear_2D_interpolator
        interp = bilinear_2D_interpolator(
            self._ground_elevation['lat'],
            self._ground_elevation['lon'],
            self._ground_elevation['data']
        )
        
        values = interp(np.array([lat.ravel(), lon.ravel()]).T)
        
        return utils.prepare_output_array(values, type_input)


# Create global singleton instance
__model = __ITU2145__()


# ==================== PUBLIC API FUNCTIONS ====================

def get_version():
    """Get the current version of ITU-R P.2145 being used.
    
    Returns
    -------
    int
        Version number
    """
    return __model.get_version()


def change_version(new_version):
    """Change the version of ITU-R P.2145 being used.
    
    Parameters
    ----------
    new_version : int
        Version number to use
    """
    __model.change_version(new_version)


# Surface Pressure
def surface_pressure(lat, lon, p=None, month=None, alt=None):
    """Calculate surface total (barometric) pressure.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    p : float or None
        Exceedance probability (%) [0.01 to 99]. If None, returns mean
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Surface pressure (hPa)
    """
    return __model.instance.surface_pressure(lat, lon, p, month, alt)


def surface_pressure_mean(lat, lon, month=None, alt=None):
    """Calculate mean surface pressure.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Mean surface pressure (hPa)
    """
    return __model.instance.surface_pressure_mean(lat, lon, month, alt)


def surface_pressure_std(lat, lon, month=None):
    """Calculate standard deviation of surface pressure.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    
    Returns
    -------
    ndarray
        Standard deviation of surface pressure (hPa)
    """
    return __model.instance.surface_pressure_std(lat, lon, month)


# Surface Temperature
def surface_temperature(lat, lon, p=None, month=None, alt=None):
    """Calculate surface temperature.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    p : float or None
        Exceedance probability (%) [0.01 to 99]. If None, returns mean
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Surface temperature (K)
    """
    return __model.instance.surface_temperature(lat, lon, p, month, alt)


def surface_temperature_mean(lat, lon, month=None, alt=None):
    """Calculate mean surface temperature.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Mean surface temperature (K)
    """
    return __model.instance.surface_temperature_mean(lat, lon, month, alt)


def surface_temperature_std(lat, lon, month=None):
    """Calculate standard deviation of surface temperature.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    
    Returns
    -------
    ndarray
        Standard deviation of surface temperature (K)
    """
    return __model.instance.surface_temperature_std(lat, lon, month)


# Surface Water Vapour Density
def surface_water_vapour_density(lat, lon, p=None, month=None, alt=None):
    """Calculate surface water vapour density.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    p : float or None
        Exceedance probability (%) [0.01 to 99]. If None, returns mean
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Surface water vapour density (g/m³)
    """
    return __model.instance.surface_water_vapour_density(lat, lon, p, month, alt)


def surface_water_vapour_density_mean(lat, lon, month=None, alt=None):
    """Calculate mean surface water vapour density.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Mean surface water vapour density (g/m³)
    """
    return __model.instance.surface_water_vapour_density_mean(lat, lon, month, alt)


def surface_water_vapour_density_std(lat, lon, month=None):
    """Calculate standard deviation of surface water vapour density.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    
    Returns
    -------
    ndarray
        Standard deviation of surface water vapour density (g/m³)
    """
    return __model.instance.surface_water_vapour_density_std(lat, lon, month)


# Integrated Water Vapour Content
def integrated_water_vapour_content(lat, lon, p=None, month=None, alt=None):
    """Calculate integrated water vapour content.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    p : float or None
        Exceedance probability (%) [0.01 to 99]. If None, returns mean
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Integrated water vapour content (kg/m² or mm)
    """
    return __model.instance.integrated_water_vapour_content(lat, lon, p, month, alt)


def integrated_water_vapour_content_mean(lat, lon, month=None, alt=None):
    """Calculate mean integrated water vapour content.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Mean integrated water vapour content (kg/m² or mm)
    """
    return __model.instance.integrated_water_vapour_content_mean(lat, lon, month, alt)


def integrated_water_vapour_content_std(lat, lon, month=None):
    """Calculate standard deviation of integrated water vapour content.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    
    Returns
    -------
    ndarray
        Standard deviation of integrated water vapour content (kg/m² or mm)
    """
    return __model.instance.integrated_water_vapour_content_std(lat, lon, month)


# Weibull Parameters
def weibull_shape(lat, lon, alt=None):
    """Calculate Weibull shape parameter for integrated water vapour content.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Weibull shape parameter k_Vs
    """
    return __model.instance.weibull_shape(lat, lon, alt)


def weibull_scale(lat, lon, alt=None):
    """Calculate Weibull scale parameter for integrated water vapour content.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    alt : array_like or None
        Altitude above sea level (km). If None, no altitude correction
    
    Returns
    -------
    ndarray
        Weibull scale parameter lambda_Vs (kg/m² or mm)
    """
    return __model.instance.weibull_scale(lat, lon, alt)


# Scale Heights
def pressure_scale_height(lat, lon, month=None):
    """Calculate pressure scale height.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    
    Returns
    -------
    ndarray
        Pressure scale height (km)
    """
    return __model.instance.pressure_scale_height(lat, lon, month)


def temperature_scale_height(lat, lon, month=None):
    """Calculate temperature scale height.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    
    Returns
    -------
    ndarray
        Temperature scale height (km)
    """
    return __model.instance.temperature_scale_height(lat, lon, month)


def water_vapour_scale_height(lat, lon, month=None):
    """Calculate water vapour scale height.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    month : int or None
        Month number (1-12) or None for annual statistics
    
    Returns
    -------
    ndarray
        Water vapour scale height (km)
    """
    return __model.instance.water_vapour_scale_height(lat, lon, month)


# Ground Elevation
def ground_elevation(lat, lon):
    """Calculate ground elevation above mean sea level.
    
    Parameters
    ----------
    lat, lon : array_like
        Geographic coordinates (degrees)
    
    Returns
    -------
    ndarray
        Ground elevation (km)
    """
    return __model.instance.ground_elevation(lat, lon)
