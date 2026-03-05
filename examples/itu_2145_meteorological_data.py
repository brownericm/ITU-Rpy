# -*- coding: utf-8 -*-
"""
Example demonstrating the use of ITU-R P.2145 meteorological data.

This example shows how to access surface pressure, temperature, water vapour
density, and integrated water vapour content statistics from the ITU-R P.2145
recommendation.

The data is based on 30 years of ECMWF ERA5 reanalysis data and provides
annual and monthly statistics at 0.25° spatial resolution.
"""

import itur

# Location: Boston, MA
lat = 41.39
lon = -71.05

print("=" * 70)
print("ITU-R P.2145 Meteorological Data Example")
print("=" * 70)
print(f"\nLocation: Boston, MA ({lat}°N, {lon}°W)\n")

# Annual mean values
print("Annual Mean Values:")
print("-" * 70)

p_mean = itur.surface_pressure_mean(lat, lon)
t_mean = itur.surface_temperature_mean(lat, lon)
rho_mean = itur.surface_water_vapour_density_mean(lat, lon)
v_mean = itur.integrated_water_vapour_content_mean(lat, lon)

print(f"  Surface pressure:                 {p_mean:.1f} hPa")
print(f"  Surface temperature:              {t_mean:.1f} K ({t_mean - 273.15:.1f}°C)")
print(f"  Surface water vapour density:     {rho_mean:.2f} g/m³")
print(f"  Integrated water vapour content:  {v_mean:.1f} kg/m²")

# Monthly variations (July)
print("\n\nMonthly Statistics (July):")
print("-" * 70)

month = 7  # July
t_mean_july = itur.surface_temperature_mean(lat, lon, month=month)
t_std_july = itur.surface_temperature_std(lat, lon, month=month)
rho_mean_july = itur.surface_water_vapour_density_mean(lat, lon, month=month)

print(f"  Mean temperature:                 {t_mean_july:.1f} K ({t_mean_july - 273.15:.1f}°C)")
print(f"  Temperature std dev:              {t_std_july:.1f} K")
print(f"  Mean water vapour density:        {rho_mean_july:.2f} g/m³")

# Percentile values
print("\n\nPercentile Statistics (Annual):")
print("-" * 70)

# Temperature exceeded 1% of the time
t_1pct = itur.surface_temperature(lat, lon, p=1)
print(f"  Temperature exceeded 1% of time:  {t_1pct:.1f} K ({t_1pct - 273.15:.1f}°C)")

# Temperature exceeded 99% of the time
t_99pct = itur.surface_temperature(lat, lon, p=99)
print(f"  Temperature exceeded 99% of time: {t_99pct:.1f} K ({t_99pct - 273.15:.1f}°C)")

# Water vapour density exceeded 5% of the time
rho_5pct = itur.surface_water_vapour_density(lat, lon, p=5)
print(f"  Water vapour density (5%):        {rho_5pct:.2f} g/m³")

# Weibull distribution parameters (annual)
print("\n\nWeibull Distribution Parameters (Annual):")
print("-" * 70)

k_v = itur.models.itu2145.weibull_shape(lat, lon)
lambda_v = itur.models.itu2145.weibull_scale(lat, lon)

print(f"  Shape parameter (k_Vs):           {k_v:.3f}")
print(f"  Scale parameter (λ_Vs):           {lambda_v:.1f} kg/m²")

# Scale heights
print("\n\nScale Heights:")
print("-" * 70)

p_scale = itur.models.itu2145.pressure_scale_height(lat, lon)
t_scale = itur.models.itu2145.temperature_scale_height(lat, lon)
v_scale = itur.models.itu2145.water_vapour_scale_height(lat, lon)

print(f"  Pressure scale height:            {p_scale:.2f} km")
print(f"  Temperature scale height:         {t_scale:.2f} km")
print(f"  Water vapour scale height:        {v_scale:.2f} km")

# Ground elevation
print("\n\nTopography:")
print("-" * 70)

z_ground = itur.models.itu2145.ground_elevation(lat, lon)
print(f"  Ground elevation:                 {z_ground*1000:.0f} m")

print("\n" + "=" * 70)

# Example with multiple locations
print("\n\nMultiple Locations Example:")
print("-" * 70)

latitudes = [41.39, 51.5074, 35.6762]  # Boston, London, Tokyo
longitudes = [-71.05, -0.1278, 139.6503]
cities = ["Boston, MA", "London, UK", "Tokyo, Japan"]

print(f"\n{'City':<20} {'Pressure (hPa)':<18} {'Temp (K)':<12} {'WV (g/m³)':<12}")
print("-" * 70)

for lat, lon, city in zip(latitudes, longitudes, cities):
    p = itur.surface_pressure_mean(lat, lon)
    t = itur.surface_temperature_mean(lat, lon)
    rho = itur.surface_water_vapour_density_mean(lat, lon)
    print(f"{city:<20} {p:<18.1f} {t:<12.1f} {rho:<12.2f}")

print("=" * 70)
