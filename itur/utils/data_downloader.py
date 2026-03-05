#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data download utility for ITU-R P.2145 meteorological data.

Downloads data from Zenodo and extracts to the appropriate directory.
"""
from __future__ import absolute_import, division, print_function

import os
import sys
import tarfile

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from pathlib import Path


# Zenodo configuration
ZENODO_DOI = "10.5281/zenodo.18872526"
ZENODO_URL = "https://zenodo.org/record/18872526/files/p2145_data.tar.gz"
EXPECTED_SIZE = 1800000000  # ~1.8 GB compressed


def download_p2145_data(verbose=True):
    """
    Download ITU-R P.2145 meteorological data from Zenodo.
    
    Downloads the compressed archive (1.8 GB) and extracts it to
    itur/data/2145/ directory.
    
    Parameters
    ----------
    verbose : bool
        Print progress messages (default: True)
    
    Raises
    ------
    RuntimeError
        If download fails or extraction fails
    ImportError
        If requests library is not available
    
    Examples
    --------
    >>> from itur.utils import download_p2145_data
    >>> download_p2145_data()
    Downloading P.2145 meteorological data...
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError(
            "The 'requests' library is required for downloading P.2145 data.\n"
            "Install it with: pip install requests\n"
            "Or download manually from: https://zenodo.org/record/18872526"
        )
    
    # Determine paths
    package_dir = Path(__file__).parent.parent
    data_dir = package_dir / 'data' / '2145'
    archive_path = package_dir / 'data' / 'p2145_data.tar.gz'
    
    # Check if already downloaded
    if data_dir.exists() and any(data_dir.iterdir()):
        if verbose:
            print("✓ P.2145 data already downloaded.")
            print(f"  Location: {data_dir}")
        return
    
    # Create data directory
    data_dir.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print("=" * 70)
        print("ITU-R P.2145 Meteorological Data Download")
        print("=" * 70)
        print(f"Source: Zenodo (DOI: {ZENODO_DOI})")
        print(f"Size:   ~1.8 GB compressed, 2.3 GB extracted")
        print(f"Target: {data_dir}")
        print()
    
    try:
        # Download archive
        if verbose:
            print("Downloading...")
        
        response = requests.get(ZENODO_URL, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', EXPECTED_SIZE))
        downloaded = 0
        
        with open(archive_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if verbose and downloaded % 100000000 == 0:  # Every 100 MB
                        progress = (downloaded / total_size) * 100
                        print(f"  Progress: {progress:.1f}% ({downloaded/1e9:.2f} GB)")
        
        if verbose:
            print("✓ Download complete")
        
        # Extract archive
        if verbose:
            print("Extracting...")
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(path=data_dir.parent)
        
        if verbose:
            print("✓ Extraction complete")
        
        # Clean up archive
        archive_path.unlink()
        
        # Verify extraction
        num_files = len(list(data_dir.glob('*.npz')))
        if verbose:
            print()
            print("=" * 70)
            print("✓ P.2145 data installation complete!")
            print(f"  Files installed: {num_files}")
            print(f"  Location: {data_dir}")
            print("=" * 70)
    
    except requests.RequestException as e:
        raise RuntimeError(
            f"Failed to download P.2145 data from Zenodo.\n"
            f"Error: {e}\n\n"
            f"Please try downloading manually from:\n"
            f"  https://zenodo.org/record/18872526\n"
            f"And extract to: {data_dir}"
        )
    
    except tarfile.TarError as e:
        raise RuntimeError(
            f"Failed to extract P.2145 data archive.\n"
            f"Error: {e}\n\n"
            f"The archive may be corrupted. Please try:\n"
            f"  1. Delete: {archive_path}\n"
            f"  2. Re-run: python scripts/download_p2145_data.py"
        )


def verify_p2145_data():
    """
    Verify that P.2145 data is available and valid.
    
    Returns
    -------
    bool
        True if data is available and valid, False otherwise
    """
    package_dir = Path(__file__).parent.parent
    data_dir = package_dir / 'data' / '2145'
    
    if not data_dir.exists():
        return False
    
    # Check for some key files (not exhaustive, just representative)
    key_files = [
        'p_annual.npz',
        't_annual.npz',
        'rho_annual.npz',
        'v_annual.npz',
        'psch.npz',
        'weibull_annual.npz',
        'z_ground.npz'
    ]
    
    for filename in key_files:
        if not (data_dir / filename).exists():
            return False
    
    # Check that we have a reasonable number of files (at least 50)
    npz_files = list(data_dir.glob('*.npz'))
    if len(npz_files) < 50:
        return False
    
    return True


if __name__ == '__main__':
    download_p2145_data()
