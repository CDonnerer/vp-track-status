#!/usr/bin/env bash
set -euo pipefail

# Update Victoria Park Track Status data
# This script is designed to run in GitHub Actions but can also be run locally

echo "=========================================="
echo "Victoria Park Track Status - Data Update"
echo "=========================================="
echo ""

# Fetch latest rainfall data (last 7 days)
echo "Step 1: Fetching latest rainfall data..."
vp-track-status fetch --mode latest --days 7

echo ""
echo "=========================================="
echo "Data update complete!"
echo "=========================================="
