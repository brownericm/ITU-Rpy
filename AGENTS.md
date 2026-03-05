# AGENTS.md - AI Assistant Guide for ITU-Rpy

## Project Overview

ITU-Rpy is a Python implementation of ITU-R P series recommendations for computing atmospheric attenuation in satellite and terrestrial radio communication links. It provides vectorized, fast computation of propagation losses for frequencies in the GHz range.

## Architecture

### Three-Tier Model Pattern
Each ITU recommendation follows this structure:
- `__ITU###__()`: Public wrapper class that dispatches to version-specific implementations
- `_ITU###_XX_()`: Version-specific implementation (e.g., `_ITU453_13_()` for version 13)
- Global singleton: `__model = __ITU###__()` instantiated at module level

### Version Management
```python
# Change ITU recommendation version
models.itu453.change_version(13)
version = models.itu453.get_version()
```

## Development Workflow

### Branch Naming
- Format: `P.{recommendation}-{version}` (e.g., `P.2145-1`)
- Example: `P.618-14` for ITU-R P.618 version 14 updates

### Commit Messages
Use conventional commit format:
- `feat:` - New features or ITU recommendation updates
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or updates
- `refactor:` - Code refactoring

### Pull Requests
- Create PR when feature is complete
- Include validation tests for any changes
- Ensure all tests pass before requesting review

### Merge Criteria
- All tests passing (pytest + coverage)
- No linting errors (flake8)
- Changes documented in commit messages
- PR includes validation against ITU examples where applicable

## Code Conventions

### Data Loading
- Data files located in `itur/data/{recommendation_number}/`
- Use `itur.utils.load_data()` for loading .npz, .npy, or .txt files
- Spatial data uses `itur.models.itu1144.bilinear_2D_interpolator()` for interpolation

### Array Handling
- `prepare_input_array()`: Converts inputs to 2D numpy arrays
- `prepare_output_array()`: Restores original input shape/type
- `prepare_quantity()`: Handles astropy unit conversions

### No Strict Conventions
Follow existing patterns in the codebase rather than enforcing new conventions. The project has minimal coding standards, so consistency with existing code is most important.

## Key Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
coverage run -m pytest

# View coverage report
coverage report -m

# Generate coverage HTML report
coverage html
```

### Linting
```bash
# Check for Python syntax errors
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Check with fewer strict rules (exit-zero treats all errors as warnings)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Build & Release
```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

## Dependencies

**Required:**
- numpy >= 1.14.0
- scipy >= 0.18.1
- astropy (unit handling)
- pyproj (geodetic calculations)
- pandas >= 0.24.2

**Optional:**
- matplotlib (plotting)
- cartopy (map visualization)

## ITU Recommendations Implemented

| Rec | Versions | Purpose | Doc |
|-----|----------|---------|-----|
| P.453 | 12-14 | Radio refractive index | [Link](https://www.itu.int/rec/R-REC-P.453) |
| P.530 | 16-17 | Terrestrial line-of-sight | [Link](https://www.itu.int/rec/R-REC-P.530) |
| P.618 | 12-13 | Earth-space propagation | [Link](https://www.itu.int/rec/R-REC-P.618) |
| P.676 | 9-13 | Gaseous attenuation | [Link](https://www.itu.int/rec/R-REC-P.676) |
| P.835 | 5-6 | Reference atmospheres | [Link](https://www.itu.int/rec/R-REC-P.835) |
| P.836 | 4-6 | Water vapour density | [Link](https://www.itu.int/rec/R-REC-P.836) |
| P.837 | 6-7 | Rainfall characteristics | [Link](https://www.itu.int/rec/R-REC-P.837) |
| P.838 | 0-3 | Rain specific attenuation | [Link](https://www.itu.int/rec/R-REC-P.838) |
| P.839 | 2-4 | Rain height model | [Link](https://www.itu.int/rec/R-REC-P.839) |
| P.840 | 4-9 | Cloud/fog attenuation | [Link](https://www.itu.int/rec/R-REC-P.840) |
| P.1144 | 10 | Interpolation methods | [Link](https://www.itu.int/rec/R-REC-P.1144) |
| P.1510 | 0-1 | Surface temperature | [Link](https://www.itu.int/rec/R-REC-P.1510) |
| P.1511 | 0-2 | Topography | [Link](https://www.itu.int/rec/R-REC-P.1511) |
| P.1623 | 0-1 | Fade dynamics | [Link](https://www.itu.int/rec/R-REC-P.1623) |
| P.1853 | 0-1 | Time series synthesis | [Link](https://www.itu.int/rec/R-REC-P.1853) |
| P.2145 | 0 | Meteorological digital maps | [Link](https://www.itu.int/rec/R-REC-P.2145) |

## File Structure

```
itur/
├── __init__.py              # Main API entry point
├── utils.py                 # Data loading, array prep, unit conversion
├── plotting.py              # Map visualization (Cartopy/Basemap)
├── models/
│   ├── itu###.py           # ITU recommendation implementations
│   └── itu1144.py          # Interpolation utilities
└── data/
    └── {###}/*.npz         # Binary data files by recommendation

test/
├── itur_test.py             # General function tests
├── ITU_validation_test.py   # Reference value validation
├── ITU_validation_report_test.py  # Modern validation with reports
└── test_data/               # ITU validation datasets
    ├── 453/
    ├── 618/
    ├── 676/
    ├── 836/
    ├── 837/
    ├── 838/
    ├── 839/
    ├── 840/
    ├── 1510/
    ├── 1511/
    └── 1623/

examples/
├── single_location.py       # Single point calculation example
├── multiple_location.py     # Multiple locations example
├── map_africa.py            # Map visualization example
└── itu_1510_mean_surface_temperature.py  # Temperature map example

docs/
├── index.rst                # Main documentation
└── apidoc/                  # Auto-generated API documentation
```

## Common Tasks

### Adding a New ITU Recommendation

1. Create `itur/models/itu{number}.py`
2. Implement `__ITU{number}__()` wrapper class with version management
3. Implement version-specific `_ITU{number}_XX_()` classes for each version
4. Add data files to `itur/data/{number}/` directory (.npz for binary, .txt for CSV)
5. Create validation tests in `test/test_data/{number}/` if ITU examples are available
6. Update `setup.py` to include new data files in `package_data`
7. Run tests to verify implementation

Example pattern from `itu453.py`:
```python
class __ITU453__():
    def __init__(self, version=13):
        if version == 13:
            self.instance = _ITU453_13_()
        elif version == 12:
            self.instance = _ITU453_12_()
        self._version = version

class _ITU453_13_():
    def __init__(self):
        self.__version__ = 13
        self.year = 2017
        self.month = 12
        self.link = 'https://www.itu.int/rec/R-REC-P.453-201712-I/en'

# Global singleton
__model = __ITU453__()

def function_name(...):
    return __model.instance.function_name(...)
```

### Updating to a New ITU Version

1. Add new `_ITU{number}_XX_()` class to existing model file
2. Update `__ITU{number}__()` to include new version in `if/elif` chain
3. If new data files are required, add them to `itur/data/{number}/`
4. Add validation tests for new version using ITU examples
5. Update version variable in new class
6. Run all tests to ensure compatibility

### Debugging Spatial Interpolation

1. **Check data file loading:**
   ```python
   from itur.utils import load_data, dataset_dir
   data = load_data('itur/data/453/v13_esalat.npz')
   print(data.shape)
   ```

2. **Verify lat/lon bounds:**
   - Latitude: -90 to 90 degrees
   - Longitude: -180 to 180 (or 0 to 360)

3. **Test interpolator:**
   ```python
   from itur.models.itu1144 import bilinear_2D_interpolator
   lats = load_data('itur/data/453/v13_esalat.npz')
   lons = load_data('itur/data/453/v13_esalon.npz')
   vals = load_data('itur/data/453/v13_esanwet.npz')
   interp = bilinear_2D_interpolator(lats, lons, vals)
   result = interp([[40.0, -70.0]])
   ```

4. **Common issues:**
   - Data file not found: Check path in `dataset_dir`
   - Out of bounds: Verify lat/lon within data extent
   - Slow performance: Interpolator caches results, but may need optimization for large arrays

### Working with Large Data Files

ITU-R P.2145 uses 2.3 GB of meteorological data that must be downloaded separately:

```bash
# Download data
python scripts/download_p2145_data.py
```

Data source: Zenodo (DOI: [10.5281/zenodo.18872526](https://doi.org/10.5281/zenodo.18872526))

The data is not included in the git repository to keep the repository size manageable. 

**Implementation Details:**
- Data files are stored in `itur/data/2145/` (not tracked by git)
- Functions automatically check for data availability
- Users receive clear error messages with download instructions if data is missing
- Download script: `scripts/download_p2145_data.py`
- Download utility: `itur.utils.data_downloader.download_p2145_data()`

**Adding New Large Datasets:**
If adding recommendations with large datasets (>100 MB), follow the P.2145 pattern:
1. Add data files to `itur/data/{number}/`
2. Add `itur/data/{number}/` to `.gitignore`
3. Upload data to Zenodo or similar repository
4. Create download utility in `itur/utils/data_downloader.py`
5. Create standalone download script in `scripts/`
6. Add data availability checks to model functions
7. Document in README.md and AGENTS.md

### Working with Astrophysical Units

Always use astropy units for physical quantities:

```python
import itur

# Correct
f = 22.5 * itur.u.GHz
D = 1 * itur.u.m
el = 60.0  # degrees (dimensionless, but dimensionless values work)

# Incorrect (will cause errors)
f = 22.5  # No unit specified
```

Use `to()` for conversions:

```python
from astropy import units as u
temp = 288.15  # Kelvin
temp_c = temp.to(u.Celsius, equivalencies=u.temperature())
```

## Validation Standards

### ITU Validation
ITU-Rpy is validated against the official [ITU Validation Examples (rev 5.1)](https://www.itu.int/en/ITU-R/study-groups/rsg3/ionotropospheric/CG-3M3J-13-ValEx-Rev5_1.xlsx).

### Test Requirements
- All ITU validation tests must pass
- Precision: 3-5 decimal places in assertions
- Test versions are tested in order (e.g., P.453 versions 12 → 13 → 14)
- Coverage tracking via codecov

### Running Validation
```bash
# Run all tests including ITU validation
pytest

# Run specific validation for a recommendation
pytest test/ITU_validation_test.py::TestFunctionsRecommendation453
```

## Important Notes

### Geographic Coordinates
- System: WGS-84 ellipsoid
- Latitude: degrees North, range -90 to 90
- Longitude: degrees East, range -180 to 180 (or 0 to 360)
- Use `pyproj` for geodetic calculations

### Units
- Always use astropy units for physical quantities
- Temperature equivalencies: Kelvin ↔ Celsius ↔ Fahrenheit
- Frequency: GHz, meters, etc.
- Pressure: hPa (hectopascals)

### Vectorization
Functions support scalar, list, and numpy array inputs:
```python
# Scalar
result = itur.gaseous_attenuation_slant_path(20*itur.u.GHz, 45, rho, P, T)

# List
results = itur.gaseous_attenuation_slant_path([20, 30]*itur.u.GHz, 45, rho, P, T)

# Array
results = itur.gaseous_attenuation_slant_path(np.array([20, 30, 40])*itur.u.GHz, 45, rho, P, T)
```

### Data Files
- Prefer .npz format for binary data (smaller, faster)
- CSV files should have numeric or bytes content
- Avoid committing large CSV files (>1MB)
- Data files are included in package via `setup.py` `package_data`

### Dependencies
- All required packages must be available at runtime
- Test environment should include pytest, coverage, flake8
- CI/CD tests on Python 3.9, 3.10, 3.11

## AI Subagents Reference

The following specialized AI subagents are available for ITU-Rpy development:

### 1. **Git Agent**
- Create and manage feature branches
- Write meaningful commit messages
- Generate CHANGELOG entries
- Create pull requests with proper formatting
- Handle merge conflicts and version bumps
- Create release notes from ITU updates

### 2. **ITU Recommendation Update Agent**
- Parse ITU recommendation PDFs/documents
- Compare changes between versions
- Update implementation code and data files
- Generate validation tests from ITU examples
- Update documentation

### 3. **RF Validation Agent**
- Run comprehensive validation suites
- Compare results with ITU reference values
- Identify precision issues or bugs
- Generate validation reports
- Cross-reference with scientific literature

### 4. **Spatial Data Agent**
- Convert data formats (CSV → NPZ)
- Update global datasets (rainfall, temperature, water vapor, etc.)
- Optimize data file sizes
- Validate spatial interpolation accuracy
- Generate new data files from ITU sources

### 5. **API Enhancement Agent**
- Add new convenience functions
- Improve error messages and warnings
- Add type hints (currently missing)
- Create new plotting utilities
- Write usage examples and tutorials

### 6. **Testing & Coverage Agent**
- Identify untested code paths
- Generate edge case tests
- Add property-based testing
- Improve test performance
- Add integration tests for complex scenarios

## Getting Help

### Documentation
- Main documentation: http://itu-rpy.readthedocs.io/
- Examples: `/examples/` directory
- Validation reports: http://itu-rpy.readthedocs.io/validation.html

### Examples

See `examples/single_location.py` for a complete example:
```python
import itur

# Link parameters
f = 22.5 * itur.u.GHz  # Frequency
el = 60                # Elevation angle (degrees)
D = 1 * itur.u.m       # Antenna diameter (m)
p = 0.1                # Percentage of time exceeded

# Compute total atmospheric attenuation
A = itur.atmospheric_attenuation_slant_path(
    lat=41.39, lon=-71.05,
    f=f, el=el, p=p, D=D
)

print(f"Total attenuation: {A:.2f} dB")
```

See `examples/map_africa.py` for map visualization:
```python
import itur
import matplotlib.pyplot as plt

# Create grid
lat, lon = itur.utils.regular_lat_lon_grid(
    resolution=5, bounds={'lat': [-35, 10], 'lon': [-20, 50]}
)

# Compute attenuation
f = 22.5 * itur.u.GHz
el = 30
p = 0.1
D = 1 * itur.u.m
Att = itur.atmospheric_attenuation_slant_path(lat, lon, f, el, p, D)

# Plot
itur.plotting.plot_in_map(Att.value, lat, lon,
                         cbar_text='Atmospheric attenuation [dB]')
plt.show()
```
