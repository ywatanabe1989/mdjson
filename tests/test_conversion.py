#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-01 19:05:31 (ywatanabe)"
# File: /home/ywatanabe/proj/mdjson/tests/test_conversion.py

__file__ = "/home/ywatanabe/proj/mdjson/tests/test_conversion.py"

import unittest
import tempfile
import os
import json

from mdjson.convert import (
    _jsonify_markdown,
    _markdownify_json,
    _simplify_pandoc_json,
    _simplified_to_pandoc_json,
    _json_to_md,
    mdjson,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TestMarkdownJsonConversion(unittest.TestCase):
    def setUp(self):
        self.sample_md = """# Section 1
This is content 1

## Subsection 1.1
- Item 1
- Item 2

# Section 2
This is content 2
"""
        self.sample_json = {
            "pandoc-api-version": [1, 23, 1],
            "meta": {},
            "blocks": [
                {
                    "t": "Header",
                    "c": [
                        1,
                        ["section-1", [], []],
                        [
                            {"t": "Str", "c": "Section"},
                            {"t": "Space"},
                            {"t": "Str", "c": "1"},
                        ],
                    ],
                },
                {
                    "t": "Para",
                    "c": [
                        {"t": "Str", "c": "This"},
                        {"t": "Space"},
                        {"t": "Str", "c": "is"},
                        {"t": "Space"},
                        {"t": "Str", "c": "content"},
                        {"t": "Space"},
                        {"t": "Str", "c": "1"},
                    ],
                },
                {
                    "t": "Header",
                    "c": [
                        2,
                        ["subsection-1.1", [], []],
                        [
                            {"t": "Str", "c": "Subsection"},
                            {"t": "Space"},
                            {"t": "Str", "c": "1.1"},
                        ],
                    ],
                },
                {
                    "t": "BulletList",
                    "c": [
                        [
                            {
                                "t": "Plain",
                                "c": [
                                    {"t": "Str", "c": "Item"},
                                    {"t": "Space"},
                                    {"t": "Str", "c": "1"},
                                ],
                            }
                        ],
                        [
                            {
                                "t": "Plain",
                                "c": [
                                    {"t": "Str", "c": "Item"},
                                    {"t": "Space"},
                                    {"t": "Str", "c": "2"},
                                ],
                            }
                        ],
                    ],
                },
                {
                    "t": "Header",
                    "c": [
                        1,
                        ["section-2", [], []],
                        [
                            {"t": "Str", "c": "Section"},
                            {"t": "Space"},
                            {"t": "Str", "c": "2"},
                        ],
                    ],
                },
                {
                    "t": "Para",
                    "c": [
                        {"t": "Str", "c": "This"},
                        {"t": "Space"},
                        {"t": "Str", "c": "is"},
                        {"t": "Space"},
                        {"t": "Str", "c": "content"},
                        {"t": "Space"},
                        {"t": "Str", "c": "2"},
                    ],
                },
            ],
        }

    # def test_md_to_json(self):
    #     with tempfile.NamedTemporaryFile(
    #         mode="w", suffix=".md", delete=False
    #     ) as md_file, tempfile.NamedTemporaryFile(
    #         mode="w", suffix=".json", delete=False
    #     ) as json_file:
    #         md_file.write(self.sample_md)
    #         md_file.flush()

    #         _jsonify_markdown(md_file.name, json_file.name, 2)

    #         with open(json_file.name) as f:
    #             result = json.load(f)

    #         # self.assertEqual(result["blocks"][0]["t"], "Header")
    #         # self.assertEqual(result["blocks"][0]["c"][2][0]["c"], "Section")

    #         os.unlink(md_file.name)
    #         os.unlink(json_file.name)

    def test_md_to_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as md_file, tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as json_file:
            md_file.write(self.sample_md)
            md_file.flush()
            _jsonify_markdown(md_file.name, json_file.name, 2)
            with open(json_file.name) as f:
                result = json.load(f)

            self.assertEqual(result["blocks"][0]["t"], "Header")
            self.assertEqual(result["blocks"][0]["c"][2][0]["c"], "Section")
            os.unlink(md_file.name)
            os.unlink(json_file.name)


    def test_json_to_md(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as json_file, tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as md_file:
            json.dump(self.sample_json, json_file)
            json_file.flush()
            _markdownify_json(json_file.name, md_file.name)

            # Write pandoc JSON
            with open(os.path.join(OUTPUT_DIR, "test_output_pandoc.json"), "w") as f:
                json.dump(self.sample_json, f, indent=2)

            # Write simplified JSON
            simplified_json = _simplify_pandoc_json(self.sample_json)
            with open(os.path.join(OUTPUT_DIR, "test_output.json"), "w") as f:
                json.dump(simplified_json, f, indent=2)

            with open(md_file.name) as f:
                result = f.read()
                with open(os.path.join(OUTPUT_DIR, "test_output.md"), "w") as out_f:
                    out_f.write(result)

            self.assertIn("# Section 1", result)
            self.assertIn("## Subsection 1.1", result)

            os.unlink(json_file.name)
            os.unlink(md_file.name)

    def test_simplified_json_conversion(self):
        # First convert pandoc JSON to simplified JSON
        simplified = _simplify_pandoc_json(self.sample_json)

        # Then convert simplified JSON back to pandoc JSON
        pandoc_json = _simplified_to_pandoc_json(simplified)

        # Convert both JSONs to markdown for comparison
        original_md = _json_to_md(self.sample_json)
        converted_md = _json_to_md(pandoc_json)

        # Write files for inspection
        with open(os.path.join(OUTPUT_DIR, "test_simplified.json"), "w") as f:
            json.dump(simplified, f, indent=2)

        with open(os.path.join(OUTPUT_DIR, "test_converted_pandoc.json"), "w") as f:
            json.dump(pandoc_json, f, indent=2)

        with open(os.path.join(OUTPUT_DIR, "test_original_md.md"), "w") as f:
            f.write(original_md)

        with open(os.path.join(OUTPUT_DIR, "test_converted_md.md"), "w") as f:
            f.write(converted_md)

        # Compare the markdown outputs
        self.assertEqual(original_md.strip(), converted_md.strip())

    def test_mdjson(self):
        # Test MD to JSON
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as md_file, tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as json_file:
            md_file.write(self.sample_md)
            md_file.flush()
            mdjson(md_file.name, json_file.name)
            with open(json_file.name) as f:
                result = json.load(f)
            self.assertIn("sections", result)

            # Test JSON to MD
            output_md = tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False
            ).name
            mdjson(json_file.name, output_md)
            with open(output_md) as f:
                md_result = f.read()
            self.assertIn("Section 1", md_result)

            os.unlink(md_file.name)
            os.unlink(json_file.name)
            os.unlink(output_md)

if __name__ == "__main__":
    unittest.main()
