# Data Installation Guide

## ITU-R P.2145 Meteorological Data

### Overview

ITU-R P.2145 provides global meteorological statistics based on 30 years of ECMWF ERA5 reanalysis data. The dataset includes:

- Surface pressure (hPa)
- Surface temperature (K)
- Surface water vapour density (g/m³)
- Integrated water vapour content (kg/m²)
- Weibull distribution parameters
- Scale heights for altitude corrections

**Total size:** 2.3 GB (1.8 GB compressed)

### Installation Methods

#### Method 1: Download Script (Recommended)

```bash
python scripts/download_p2145_data.py
```

#### Method 2: Python API

```python
from itur.utils import download_p2145_data
download_p2145_data()
```

#### Method 3: Manual Download

1. Visit Zenodo: https://zenodo.org/record/18872526
2. Download `p2145_data.tar.gz`
3. Extract to your ITU-Rpy installation directory:
   ```bash
   tar -xzf p2145_data.tar.gz -C /path/to/itur/data/
   ```

### Verification

Verify the installation:

```python
from itur.utils.data_downloader import verify_p2145_data
if verify_p2145_data():
    print("✓ P.2145 data installed correctly")
else:
    print("✗ P.2145 data not found or incomplete")
```

### Troubleshooting

**Error: "ITU-R P.2145 DATA NOT FOUND"**

This error occurs when you try to use P.2145 functions without downloading the data. Follow the installation methods above.

**Download fails or is slow**

- Try downloading manually from Zenodo
- Use a download manager (wget, curl)
- Check your network connection and proxy settings

**Extraction fails**

- Verify the archive downloaded completely (should be ~1.8 GB)
- Try re-downloading the archive
- Check available disk space (need 2.3 GB free)

**ImportError: requests library not available**

Install the requests library:
```bash
pip install requests
```

Or download manually from Zenodo.

### Data Source

- **Repository:** Zenodo
- **DOI:** [10.5281/zenodo.18872526](https://doi.org/10.5281/zenodo.18872526)
- **License:** CC-BY-4.0
- **Citation:** Brown, E. (2026). ITU-R P.2145-0 Meteorological Digital Maps [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18872526

### Data Contents

After extraction, the following files should be present in `itur/data/2145/`:

**Annual Statistics (4 files):**
- `p_annual.npz` - Surface pressure
- `t_annual.npz` - Surface temperature
- `rho_annual.npz` - Surface water vapour density
- `v_annual.npz` - Integrated water vapour content

**Monthly Statistics (48 files):**
- `p_month01.npz` to `p_month12.npz` - Monthly surface pressure
- `t_month01.npz` to `t_month12.npz` - Monthly surface temperature
- `rho_month01.npz` to `rho_month12.npz` - Monthly water vapour density
- `v_month01.npz` to `v_month12.npz` - Monthly integrated water vapour

**Scale Heights (3 files):**
- `psch.npz` - Pressure scale height
- `tsch.npz` - Temperature scale height
- `vsch.npz` - Water vapour scale height

**Additional Data (2 files):**
- `weibull_annual.npz` - Weibull distribution parameters
- `z_ground.npz` - Ground elevation data

**Total: 57 files**

### Uninstallation

To remove P.2145 data:

```bash
rm -rf itur/data/2145/
```

Or manually delete the `itur/data/2145/` directory.

### Support

For issues with data download or installation:

1. Check this documentation
2. Verify your internet connection
3. Try manual download from Zenodo
4. Open an issue on GitHub: https://github.com/inigodelportillo/ITU-Rpy/issues
