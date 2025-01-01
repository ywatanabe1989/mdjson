<!-- ---
!-- title: 2025-01-01 20:12:31
!-- author: ywata-note-win
!-- date: /home/ywatanabe/proj/mdjson/README.md
!-- --- -->

# mdjson

Convert between Markdown and simplified JSON format with pandoc integration.

## Installation
```bash
pip install mdjson
```
#### Dependencies: pandoc
```bash
sudo apt remove pandoc
wget https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-1-amd64.deb
sudo dpkg -i pandoc-3.1.11-1-amd64.deb
rm pandoc-3.1.11-1-amd64.deb
```

## Usage
### Command Line
```bash
mdjson /path/to/input.md  # or input.json
```
### Python
```python
from mdjson import mdjson
mdjson("input.md", "output.json")  # MD to JSON
mdjson("input.json", "output.md")  # JSON to MD
```

## Examples
### Reversible Conversion
- [Original MD](./tests/output/test_original_md.md)
- [JSON](./tests/output/test_output.json)
- [Converted MD](./tests/output/test_output.md)

### Non-reversible Conversion
In dependent on formats, conversions may be irreversible. In this case, warning will be raised: `Warning: Conversion was not perfectly reversible`

- [Original MD](./docs/github_example_orig.md)
- [JSON](./docs/github_example.json)
- [Converted MD](./docs/github_example.md)
- [Differences](./docs/github_example_conversion.diff) 
<!-- diff -u ./docs/github_example_orig.md ./docs/github_example.md > ./docs/github_example_conversion.diff -->

## Contact
Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)