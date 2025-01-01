#!/bin/bash
# Time-stamp: "2025-01-01 17:56:50 (ywatanabe)"
# File: ./mngs_repo/docs/update_package.sh

rm -rf build dist/* src/mdjson.egg-info
python3 setup.py sdist bdist_wheel
twine upload -r pypi dist/*

# EOF
