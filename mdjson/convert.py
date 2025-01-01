#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-01 19:33:54 (ywatanabe)"
# File: /home/ywatanabe/proj/mdjson/mdjson/convert.py

__file__ = "/home/ywatanabe/proj/mdjson/mdjson/convert.py"

import subprocess
import json
import tempfile
from typing import Optional
import os


def _md_to_json(markdown_file: str) -> dict:
    """Convert markdown to JSON using pandoc"""
    cmd = ["pandoc", "-f", "markdown", "-t", "json", markdown_file]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if result.stderr:
        raise RuntimeError(f"Pandoc error: {result.stderr}")

    # Modify JSON to use correct API version
    json_data = json.loads(result.stdout)
    json_data["pandoc-api-version"] = [1, 23, 1]
    return json_data


def _json_to_md(json_data: dict) -> str:
    """Convert JSON to markdown using pandoc"""
    json_data["pandoc-api-version"] = [1, 23, 1]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", encoding="utf-8"
    ) as temp:
        json.dump(json_data, temp)
        temp.flush()

        cmd = [
            "pandoc",
            "-f",
            "json",
            "-t",
            "markdown",
            "--wrap=none",
            temp.name,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error output: {e.stderr}")
            with open(temp.name, "r") as f:
                print(f"JSON content: {f.read()[:200]}...")
            raise RuntimeError(f"Pandoc error: {e.stderr}")


def _jsonify_markdown(
    markdown_file: str, outfile: Optional[str], indent: int
) -> int:
    """Main function for markdown to JSON conversion"""
    result = _md_to_json(markdown_file)
    with open(outfile, "w") as f:
        json.dump(result, f, indent=indent)
    return 0


def _markdownify_json(json_file: str, outfile: str) -> int:
    """Main function for JSON to markdown conversion"""
    with open(json_file) as f:
        json_data = json.load(f)
    markdown = _json_to_md(json_data)
    with open(outfile, "w") as f:
        f.write(markdown)
    return 0


# def _simplify_pandoc_json(pandoc_json):
#     def join_text_elements(elements):
#         return " ".join(
#             elem.get("c", "")
#             for elem in elements
#             if isinstance(elem, dict) and elem.get("t") in ["Str", "Space"]
#         )

#     simplified = {"sections": []}
#     current_section = None

#     for block in pandoc_json.get("blocks", []):
#         if block["t"] == "Header":
#             level = block["c"][0]
#             title = join_text_elements(block["c"][2])

#             if level == 1:
#                 current_section = {
#                     "title": title,
#                     "content": [],
#                     "subsections": [],
#                 }
#                 simplified["sections"].append(current_section)
#             elif level == 2:
#                 subsection = {"title": title, "content": []}
#                 current_section["subsections"].append(subsection)
#                 current_section = subsection

#         elif block["t"] == "Para":
#             content = join_text_elements(block["c"])
#             if current_section:
#                 current_section["content"].append(content)

#         elif block["t"] == "BulletList":
#             items = []
#             for item in block["c"]:
#                 item_text = join_text_elements(item[0]["c"])
#                 items.append(item_text)
#             if current_section:
#                 current_section["content"].append(items)

#     return simplified

def _simplify_pandoc_json(pandoc_json):
    def join_text_elements(elements):
        return " ".join(
            elem.get("c", "")
            for elem in elements
            if isinstance(elem, dict) and elem.get("t") in ["Str", "Space"]
        )

    simplified = {"sections": []}
    root_section = None
    current_section = None

    for block in pandoc_json.get("blocks", []):
        if block["t"] == "Header":
            level = block["c"][0]
            title = join_text_elements(block["c"][2])
            if level == 1:
                root_section = {
                    "title": title,
                    "content": [],
                    "subsections": []
                }
                simplified["sections"].append(root_section)
                current_section = root_section
            elif level == 2 and root_section is not None:
                subsection = {"title": title, "content": []}
                root_section["subsections"].append(subsection)
                current_section = subsection
        elif block["t"] == "Para" and current_section:
            content = join_text_elements(block["c"])
            current_section["content"].append(content)
        elif block["t"] == "BulletList" and current_section:
            items = []
            for item in block["c"]:
                item_text = join_text_elements(item[0]["c"])
                items.append(item_text)
            current_section["content"].append(items)

    return simplified


def _simplified_to_pandoc_json(simplified_json):
    def create_text_elements(text):
        words = text.split()
        elements = []
        for word in words:
            elements.append({"t": "Str", "c": word})
            elements.append({"t": "Space"})
        return elements[:-1]

    pandoc_json = {
        # "pandoc-api-version": [1, 24],
        "meta": {},
        "blocks": [],
    }

    for section in simplified_json["sections"]:
        pandoc_json["blocks"].append(
            {
                "t": "Header",
                "c": [
                    1,
                    ["", [], []],  # Changed: removed identifier
                    create_text_elements(section["title"]),
                ],
            }
        )

        for content in section["content"]:
            if isinstance(content, str):
                pandoc_json["blocks"].append(
                    {"t": "Para", "c": create_text_elements(content)}
                )
            elif isinstance(content, list):
                bullet_items = []
                for item in content:
                    bullet_items.append(
                        [{"t": "Plain", "c": create_text_elements(item)}]
                    )
                pandoc_json["blocks"].append(
                    {"t": "BulletList", "c": bullet_items}
                )

        for subsection in section.get("subsections", []):
            pandoc_json["blocks"].append(
                {
                    "t": "Header",
                    "c": [
                        2,
                        ["", [], []],  # Changed: removed identifier
                        create_text_elements(subsection["title"]),
                    ],
                }
            )

            for content in subsection["content"]:
                if isinstance(content, str):
                    pandoc_json["blocks"].append(
                        {"t": "Para", "c": create_text_elements(content)}
                    )
                elif isinstance(content, list):
                    bullet_items = []
                    for item in content:
                        bullet_items.append(
                            [{"t": "Plain", "c": create_text_elements(item)}]
                        )
                    pandoc_json["blocks"].append(
                        {"t": "BulletList", "c": bullet_items}
                    )

    return pandoc_json



def mdjson(
    input_file: str, output_file: Optional[str] = None, indent: int = 2, check_reversible: bool = True
) -> int:
    """
    Convert between markdown and simplified JSON based on file extensions
    If output_file is not specified, creates output with changed extension

    Args:
        input_file: Path to input file (.md or .json)
        output_file: Optional path to output file
        indent: JSON indentation level
        check_reversible: If True, checks if conversion is reversible
    """
    input_file = os.path.expanduser(input_file)
    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = (
            f"{base}.json" if input_file.endswith(".md") else f"{base}.md"
        )
    else:
        output_file = os.path.expanduser(output_file)

    if input_file.endswith(".md"):
        # Convert markdown to simplified JSON
        pandoc_json = _md_to_json(input_file)
        simplified_json = _simplify_pandoc_json(pandoc_json)
        with open(output_file, "w") as f:
            json.dump(simplified_json, f, indent=indent)

        if check_reversible:
            # Test reverse conversion
            test_pandoc_json = _simplified_to_pandoc_json(simplified_json)
            test_md = _json_to_md(test_pandoc_json)
            original_md = open(input_file).read()
            if test_md.strip() != original_md.strip():
                print("Warning: Conversion was not be perfectly reversible")

    elif input_file.endswith(".json"):
        # Convert simplified JSON to markdown
        with open(input_file) as f:
            simplified_json = json.load(f)
        pandoc_json = _simplified_to_pandoc_json(simplified_json)
        markdown = _json_to_md(pandoc_json)
        with open(output_file, "w") as f:
            f.write(markdown)

        if check_reversible:
            # Test reverse conversion
            test_pandoc_json = _md_to_json(output_file)
            test_simplified = _simplify_pandoc_json(test_pandoc_json)
            original_json = json.load(open(input_file))
            if test_simplified != original_json:
                print("Warning: Conversion may not be perfectly reversible")

    else:
        raise ValueError("Input file must have .md or .json extension")

    return 0

# def mdjson(
#     input_file: str, output_file: Optional[str] = None, indent: int = 2
# ) -> int:
#     """
#     Convert between markdown and simplified JSON based on file extensions
#     If output_file is not specified, creates output with changed extension
#     """
#     input_file = os.path.expanduser(input_file)

#     if output_file is None:
#         base = os.path.splitext(input_file)[0]
#         output_file = (
#             f"{base}.json" if input_file.endswith(".md") else f"{base}.md"
#         )
#     else:
#         output_file = os.path.expanduser(output_file)

#     if input_file.endswith(".md"):
#         # Convert markdown to simplified JSON
#         pandoc_json = _md_to_json(input_file)
#         simplified_json = _simplify_pandoc_json(pandoc_json)
#         with open(output_file, "w") as f:
#             json.dump(simplified_json, f, indent=indent)
#     elif input_file.endswith(".json"):
#         # Convert simplified JSON to markdown
#         with open(input_file) as f:
#             simplified_json = json.load(f)
#         pandoc_json = _simplified_to_pandoc_json(simplified_json)
#         markdown = _json_to_md(pandoc_json)
#         with open(output_file, "w") as f:
#             f.write(markdown)
#     else:
#         raise ValueError("Input file must have .md or .json extension")
#     return 0
