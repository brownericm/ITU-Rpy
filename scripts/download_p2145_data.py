#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Standalone download script for ITU-R P.2145 meteorological data.

Usage:
    python scripts/download_p2145_data.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from itur.utils.data_downloader import download_p2145_data

if __name__ == '__main__':
    try:
        download_p2145_data()
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
