#!/usr/bin/env python3
"""
Jekyll/Markdown to Antora/AsciiDoc Migration Script

Converts 268 markdown files from injixo-help-center to helpcenter-docs format.
Handles front matter, links, images, icons, admonitions, and more.
"""

import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Configuration
SOURCE_DIR = Path("/Users/invision/Documents/Work/GitHub/injixo-help-center/_docs/_en")
TARGET_DIR = Path("/Users/invision/Documents/GitHub/helpcenter-docs/modules")
INCLUDES_SOURCE = Path("/Users/invision/Documents/Work/GitHub/injixo-help-center/_includes/reusables/en")
IMAGES_SOURCE = Path("/Users/invision/Documents/Work/GitHub/injixo-help-center/assets/img/en")

# Module mapping: Jekyll section -> Antora module
MODULE_MAPPING = {
    "account": "account",
    "features/account": "account",
    "administration": "administration",
    "features/administration": "administration",
    "best-practices": "best-practices",
    "features/forecast": "forecast",
    "features/general": "general",
    "getting-started": "getting-started",
    "features/injixo-me": "me",
    "features/me": "me",
    "features/monitoring": "monitoring",
    "features/scheduling": "scheduling",
    "features/time-off": "time-off",
    "features/time-management": "time-management",
    "features/people": "people",
    "features/intraday": "intraday",
    "features/reporting": "reporting",
    "features/acd-integration": "acd-integration",
    "support": "support",
    "gdpr": "gdpr",
    "glossary": "ROOT",
    "terminology": "ROOT",
}

# Icon mappings: Jekyll icon name -> AsciiDoc attribute
ICON_MAPPINGS = {
    "pencil": "icon-edit",
    "trash": "icon-delete",
    "ellipsis_v": "icon-context-menu",
    "filter_plus": "icon-filter-plus",
    "arrows-rotate": "icon-rotate",
    "full_screen_exit": "icon-full-screen-exit",
    "eye_slash": "icon-eye-slash",
    "svgviewer-output": "icon-svg-viewer",
    "item-add": "icon-wfm-add",
    "item-delete": "icon-wfm-delete",
    "item-edit": "icon-wfm-edit",
    "selection-filter-u": "icon-filter-u",
    "circle_exclamation": "icon-exclamation",
    "maximize": "icon-maximize",
    "chart-view": "icon-chart-view",
    "table-list": "icon-table-list",
    "duplicate": "icon-duplicate",
}

# Button mappings
BUTTON_MAPPINGS = {
    "Save": "btn-save",
    "Cancel": "btn-cancel",
    "Create": "btn-create",
    "Delete": "btn-delete",
    "Edit": "btn-edit",
    "Import": "btn-import",
    "Download": "btn-download-as-csv",
    "Close": "btn-close",
    "OK": "btn-ok",
}

class MigrationReport:
    def __init__(self):
        self.total_files = 0
        self.converted_files = 0
        self.errors = []
        self.warnings = defaultdict(list)
        self.unresolved_items = {
            "unknown_icons": set(),
            "unknown_buttons": set(),
            "missing_images": set(),
            "unresolved_xrefs": set(),
        }

    def add_error(self, filename: str, error: str):
        self.errors.append(f"{filename}: {error}")

    def add_warning(self, category: str, message: str):
        self.warnings[category].append(message)

    def print_summary(self):
        print("\n" + "="*80)
        print("MIGRATION REPORT")
        print("="*80)
        print(f"Total files: {self.total_files}")
        print(f"Converted: {self.converted_files}")
        print(f"Failed: {len(self.errors)}")

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\nWARNINGS:")
            for category, items in self.warnings.items():
                print(f"  {category}:")
                for item in items[:5]:  # Show first 5
                    print(f"    - {item}")
                if len(items) > 5:
                    print(f"    ... and {len(items) - 5} more")

        print("\nFLAGGED ITEMS FOR MANUAL REVIEW:")
        if self.unresolved_items["unknown_icons"]:
            print(f"  Unknown icons: {len(self.unresolved_items['unknown_icons'])}")
            for icon in sorted(list(self.unresolved_items["unknown_icons"])[:5]):
                print(f"    - {icon}")

        if self.unresolved_items["missing_images"]:
            print(f"  Missing images: {len(self.unresolved_items['missing_images'])}")
            for img in sorted(list(self.unresolved_items["missing_images"])[:5]):
                print(f"    - {img}")

        print("="*80 + "\n")


class MarkdownToAsciiDocConverter:
    def __init__(self, filepath: Path, report: MigrationReport):
        self.filepath = filepath
        self.report = report
        self.article_slug = filepath.stem  # filename without extension
        self.front_matter = {}
        self.content = ""
        self.target_module = None
        self.target_path = None

    def read_file(self) -> bool:
        """Read markdown file and extract front matter and content."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split front matter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter_str = parts[1].strip()
                    self.content = parts[2].strip()

                    # Parse YAML front matter
                    self.front_matter = yaml.safe_load(front_matter_str) or {}
                else:
                    self.content = content
            else:
                self.content = content

            return True
        except Exception as e:
            self.report.add_error(str(self.filepath), str(e))
            return False

    def determine_module(self) -> str:
        """Determine target module based on file path."""
        rel_path = self.filepath.relative_to(SOURCE_DIR)
        parts = rel_path.parts[:-1]  # Exclude filename

        # Try exact match, then prefix match
        for i in range(len(parts), 0, -1):
            prefix = "/".join(parts[:i])
            if prefix in MODULE_MAPPING:
                self.target_module = MODULE_MAPPING[prefix]
                return self.target_module

            # Try parent sections
            if parts[0] in MODULE_MAPPING:
                self.target_module = MODULE_MAPPING[parts[0]]
                return self.target_module

        # Default to ROOT
        self.target_module = "ROOT"
        return self.target_module

    def get_target_path(self) -> Path:
        """Get target path for converted file."""
        rel_path = self.filepath.relative_to(SOURCE_DIR)
        parts = rel_path.parts

        # Determine module
        self.determine_module()

        # Build target path
        # e.g., features/forecast/staff-requirements/task-save.md -> forecast/pages/staff-requirements/task-save.adoc
        remaining_parts = parts[1:] if parts[0] == "features" else parts[1:] if parts[0] in MODULE_MAPPING else parts

        # Skip the section part and build pages path
        if len(parts) > 1 and parts[0] in ("features", "best-practices", "support", "getting-started", "gdpr"):
            # e.g., features/forecast/staff-requirements/file.md -> pages/staff-requirements/file.adoc
            page_parts = parts[2:] if len(parts) > 1 else parts[1:]
        else:
            page_parts = parts[1:] if len(parts) > 0 else []

        # Reconstruct path
        filename = self.filepath.stem + ".adoc"
        if page_parts:
            target_path = TARGET_DIR / self.target_module / "pages" / Path(*page_parts[:-1]) / filename
        else:
            target_path = TARGET_DIR / self.target_module / "pages" / filename

        self.target_path = target_path
        return target_path

    def convert_front_matter(self) -> str:
        """Convert YAML front matter to AsciiDoc attributes."""
        lines = []

        # Title (converted to AsciiDoc heading)
        title = self.front_matter.get('title', 'Untitled')
        lines.append(f"= {title}")

        # Include libs
        lines.append("include::help-center:ROOT:partial$libs/libs.adoc[]")

        # Author (placeholder)
        lines.append(":author: ")
        lines.append(":email: ")

        # Product label
        if 'product_label' in self.front_matter:
            labels = self.front_matter['product_label']
            if isinstance(labels, list):
                labels = ", ".join(labels)
            lines.append(f":product-label: {labels}")

        # Topic type (inferred from filename)
        topic_type = self.infer_topic_type()
        if topic_type:
            lines.append(f":{topic_type}:")

        # Description
        if 'description' in self.front_matter:
            lines.append(f":description: {self.front_matter['description']}")

        # Related articles
        if 'related_articles' in self.front_matter:
            articles = self.front_matter['related_articles']
            if isinstance(articles, list):
                article_files = []
                for article in articles:
                    if isinstance(article, dict) and 'filepath' in article:
                        filename = Path(article['filepath']).stem + ".adoc"
                        article_files.append(filename)
                if article_files:
                    lines.append(f":related-articles: {', '.join(article_files)}")

        # Redirects (page aliases)
        if 'redirect_from' in self.front_matter:
            redirects = self.front_matter['redirect_from']
            if isinstance(redirects, list) and redirects:
                # Take first redirect
                first_alias = redirects[0].strip('/')
                if first_alias:
                    lines.append(f":page-aliases: {first_alias}")

        return "\n".join(lines)

    def infer_topic_type(self) -> Optional[str]:
        """Infer topic type from filename prefix."""
        filename = self.filepath.name
        if filename.startswith("task-"):
            return "topic-type-task"
        elif filename.startswith("concept-"):
            return "topic-type-concept"
        elif filename.startswith("ref-"):
            return "topic-type-reference"
        else:
            return "topic-type-concept"  # default

    def convert_links(self, text: str) -> str:
        """Convert Jekyll link_new tags to AsciiDoc xrefs."""

        # Pattern 1: {% link_new text | path.md | #anchor %}
        pattern1 = r'{%\s*link_new\s+([^|]+)\s*\|\s*([^|]+)\s*\|\s*#([^%}]+)\s*%}'
        def replace_link_with_anchor(match):
            text = match.group(1).strip()
            path = match.group(2).strip()
            anchor = match.group(3).strip()

            module = self.get_module_from_path(path)
            page = Path(path).stem + ".adoc"

            return f"xref:{module}:{page}#{anchor}[{text}]"

        text = re.sub(pattern1, replace_link_with_anchor, text)

        # Pattern 2: {% link_new text | path.md %} (normal pipe)
        pattern2 = r'{%\s*link_new\s+([^|;]+)\s*\|\s*([^%}]+)\s*%}'
        def replace_link(match):
            text = match.group(1).strip()
            path = match.group(2).strip()

            module = self.get_module_from_path(path)
            page = Path(path).stem + ".adoc"

            return f"xref:{module}:{page}[{text}]"

        text = re.sub(pattern2, replace_link, text)

        # Pattern 3: {% link_new text ; path.md %} (semicolon variant in tables)
        pattern3 = r'{%\s*link_new\s+([^;]+)\s*;\s*([^%}]+)\s*%}'
        def replace_link_semicolon(match):
            text = match.group(1).strip()
            path = match.group(2).strip()

            module = self.get_module_from_path(path)
            page = Path(path).stem + ".adoc"

            return f"xref:{module}:{page}[{text}]"

        text = re.sub(pattern3, replace_link_semicolon, text)

        # Convert markdown anchor links to xrefs
        pattern_anchor = r'\[([^\]]+)\]\(#([^)]+)\)'
        text = re.sub(pattern_anchor, r'xref:#\2[\1]', text)

        return text

    def get_module_from_path(self, path: str) -> str:
        """Get module name from article path."""
        parts = path.split('/')

        for i in range(len(parts), 0, -1):
            prefix = "/".join(parts[:i])
            if prefix in MODULE_MAPPING:
                return MODULE_MAPPING[prefix]

        return "ROOT"

    def convert_images(self, text: str) -> str:
        """Convert Jekyll image tags to AsciiDoc."""

        # Pattern: {{ N | image: 'alt text' }}
        pattern1 = r"\{\{\s*(\d+)\s*\|\s*image:\s*['\"]([^'\"]+)['\"]\s*\}\}"
        def replace_image(match):
            num = match.group(1)
            alt = match.group(2)
            self.report.unresolved_items["missing_images"].add(f"{self.article_slug}/image-{num}.png")
            return f"image::{self.article_slug}/image-{num}.png[{alt}]"

        text = re.sub(pattern1, replace_image, text)

        # Pattern: {{ N | image: 'alt text', 'width' }}
        pattern2 = r"\{\{\s*(\d+)\s*\|\s*image:\s*['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\s*\}\}"
        def replace_image_with_width(match):
            num = match.group(1)
            alt = match.group(2)
            width = match.group(3)
            self.report.unresolved_items["missing_images"].add(f"{self.article_slug}/image-{num}.png")
            return f"image::{self.article_slug}/image-{num}.png[{alt}, width={width}]"

        text = re.sub(pattern2, replace_image_with_width, text)

        return text

    def convert_icons(self, text: str) -> str:
        """Convert Jekyll icon tags to AsciiDoc."""

        # Pattern: {% icon name %} or {% icon name | icon-only %}
        pattern = r'{%\s*icon\s+([^\s%|]+)(?:\s*\|\s*icon-only)?\s*%}'

        def replace_icon(match):
            icon_name = match.group(1)

            if icon_name in ICON_MAPPINGS:
                return "{" + ICON_MAPPINGS[icon_name] + "}"
            else:
                self.report.unresolved_items["unknown_icons"].add(icon_name)
                return f"{{icon-{icon_name.lower().replace('_', '-')}}}"

        text = re.sub(pattern, replace_icon, text)

        return text

    def convert_iald_styling(self, text: str) -> str:
        """Convert Kramdown IAL (Inline Attribute Lists) to AsciiDoc."""

        # Pattern: _Text_{:.class}
        # For breadcrumbs, try to use button/label attributes

        # Breadcrumbs with specific patterns
        breadcrumb_pattern = r'_([^_]{1,}?)_{:\\.breadcrumbs}'
        text = re.sub(breadcrumb_pattern, r'{bc-\1}', text)  # Placeholder for later attribute lookup

        # Doc buttons
        button_pattern = r'_([^_]{1,}?)_{:\\.doc-button}'
        def replace_button(match):
            btn_text = match.group(1)
            # Try to find in button mappings
            for btn_name, btn_attr in BUTTON_MAPPINGS.items():
                if btn_name.lower() in btn_text.lower():
                    return "{" + btn_attr + "}"
            # Default to bold
            return f"*{btn_text}*"

        text = re.sub(button_pattern, replace_button, text)

        # Labels
        label_pattern = r'_([^_]{1,}?)_{:\\.label}'
        text = re.sub(label_pattern, r'*\1*', text)

        # ID labels
        id_pattern = r'_([^_]{1,}?)_{:\\.id-label}'
        text = re.sub(id_pattern, r'*\1*', text)

        # Doc button icons (special image handling)
        icon_pattern = r'_!\[([^\]]+)\]\(/assets/img/common/item-([^.]+)\.gif\)_{:\\.doc-button-icon}'
        text = re.sub(icon_pattern, r'{icon-wfm-\2}', text)

        # Generic CSS classes (fallback)
        generic_pattern = r'_([^_]{1,}?)_{:\\.([a-z-]+)}'
        text = re.sub(generic_pattern, r'[.\2]#\1#', text)

        return text

    def convert_admonitions(self, text: str) -> str:
        """Convert blockquote admonitions to AsciiDoc."""

        # Find all blockquote blocks
        lines = text.split('\n')
        result = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is a blockquote admonition
            if line.startswith('> '):
                admonition_type = "NOTE"
                content_lines = []

                # Parse the admonition type from first line
                first_line = line[2:].strip()
                if first_line.startswith('Note'):
                    admonition_type = "NOTE"
                    if first_line != "Note":
                        content_lines.append(first_line[4:].strip())
                elif first_line.startswith('Warning'):
                    admonition_type = "WARNING"
                    if first_line != "Warning":
                        content_lines.append(first_line[7:].strip())
                elif first_line.startswith('Tip'):
                    admonition_type = "TIP"
                    if first_line != "Tip":
                        content_lines.append(first_line[3:].strip())
                elif first_line.startswith('Important'):
                    admonition_type = "IMPORTANT"
                    if first_line != "Important":
                        content_lines.append(first_line[9:].strip())
                else:
                    content_lines.append(first_line)

                # Collect remaining lines
                i += 1
                while i < len(lines) and (lines[i].startswith('> ') or lines[i].strip() == ''):
                    if lines[i].startswith('> '):
                        content = lines[i][2:].strip()
                        if content:
                            content_lines.append(content)
                    i += 1

                # Build AsciiDoc admonition
                result.append(f"[{admonition_type}]")
                result.append("====")
                result.extend(content_lines)
                result.append("====")
                continue

            result.append(line)
            i += 1

        return '\n'.join(result)

    def convert_headings(self, text: str) -> str:
        """Convert markdown headings with named anchors to AsciiDoc."""

        # Pattern: ## Heading <a name="anchor"></a>
        pattern = r'^(#{1,6})\s+(.+?)\s*<a\s+name=["\']([^"\']+)["\']\s*></a>\s*$'

        def replace_heading(match):
            hashes = match.group(1)
            title = match.group(2).strip()
            anchor = match.group(3)

            # Convert # to = for AsciiDoc
            asciidoc_level = '=' * len(hashes)
            return f"[#{anchor}]\n{asciidoc_level} {title}"

        text = re.sub(pattern, replace_heading, text, flags=re.MULTILINE)

        # Convert remaining markdown headings (without anchors)
        pattern2 = r'^(#{1,6})\s+(.+)$'

        def replace_heading2(match):
            hashes = match.group(1)
            title = match.group(2).strip()
            asciidoc_level = '=' * len(hashes)
            return f"{asciidoc_level} {title}"

        text = re.sub(pattern2, replace_heading2, text, flags=re.MULTILINE)

        return text

    def convert_includes(self, text: str) -> str:
        """Convert Jekyll includes to Antora includes."""

        # Pattern: {% include reusables/{{ page.lang }}/path.md %}
        pattern = r'{%\s*include\s+reusables/\{\{.*?\}\}/(.+?)\s*%}'

        def replace_include(match):
            include_path = match.group(1)
            # Convert .md to .adoc
            adoc_path = Path(include_path).stem + ".adoc"
            return f"include::help-center:ROOT:partial$reusables/{adoc_path}[]"

        text = re.sub(pattern, replace_include, text)

        # Pattern: {% include accordion.html %} - skip for now (special handling)
        text = re.sub(r'{%\s*include\s+accordion\.html\s*%}', '', text)

        # Pattern: {% include terminology.html %} - skip for now
        text = re.sub(r'{%\s*include\s+terminology\.html\s*%}', '', text)

        return text

    def convert_tables(self, text: str) -> str:
        """Convert markdown tables to AsciiDoc format."""

        lines = text.split('\n')
        result = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is a markdown table (starts with |)
            if line.strip().startswith('|'):
                table_lines = [line]
                i += 1

                # Collect all table lines
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1

                # Convert to AsciiDoc table
                asciidoc_table = self.markdown_table_to_asciidoc(table_lines)
                result.append(asciidoc_table)
                continue

            result.append(line)
            i += 1

        return '\n'.join(result)

    def markdown_table_to_asciidoc(self, table_lines: List[str]) -> str:
        """Convert a markdown table to AsciiDoc format."""

        if len(table_lines) < 2:
            return '\n'.join(table_lines)

        # Parse table
        header_line = table_lines[0]
        separator_line = table_lines[1]

        # Extract columns
        headers = [col.strip() for col in header_line.split('|')[1:-1]]
        num_cols = len(headers)

        # Build AsciiDoc table header
        asciidoc_lines = [f"[%header, cols=\"{'1a,' * num_cols}\".rstrip(',')]"]
        asciidoc_lines.append("|===")

        # Add headers
        for header in headers:
            asciidoc_lines.append(f"|{header}")

        # Add rows
        for table_line in table_lines[2:]:
            if table_line.strip().startswith('|'):
                row_cols = [col.strip() for col in table_line.split('|')[1:-1]]
                for col_content in row_cols:
                    # Convert <br> to +
                    col_content = col_content.replace('<br>', ' +')
                    asciidoc_lines.append(f"|{col_content}")

        asciidoc_lines.append("|===")

        return '\n'.join(asciidoc_lines)

    def convert_code_blocks(self, text: str) -> str:
        """Convert fenced code blocks to AsciiDoc."""

        # Pattern: ```language\n...\n```
        pattern = r'```(\w*)\n(.*?)\n```'

        def replace_code(match):
            language = match.group(1)
            code = match.group(2)

            if language:
                return f"[source,{language}]\n----\n{code}\n----"
            else:
                return f"----\n{code}\n----"

        text = re.sub(pattern, replace_code, text, flags=re.DOTALL)

        return text

    def convert(self) -> bool:
        """Convert markdown file to AsciiDoc."""

        if not self.read_file():
            return False

        # Get target path
        target_path = self.get_target_path()

        # Convert front matter
        header = self.convert_front_matter()

        # Convert content
        content = self.content
        content = self.convert_links(content)
        content = self.convert_images(content)
        content = self.convert_icons(content)
        content = self.convert_iald_styling(content)
        content = self.convert_admonitions(content)
        content = self.convert_headings(content)
        content = self.convert_includes(content)
        content = self.convert_tables(content)
        content = self.convert_code_blocks(content)

        # Combine
        asciidoc_content = f"{header}\n\n{content}"

        # Create directories if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(asciidoc_content)

            return True
        except Exception as e:
            self.report.add_error(str(self.filepath), f"Failed to write: {e}")
            return False


def migrate_includes():
    """Convert Jekyll includes to Antora partials."""

    partials_dir = TARGET_DIR / "ROOT" / "partials" / "reusables"
    partials_dir.mkdir(parents=True, exist_ok=True)

    count = 0

    for include_file in INCLUDES_SOURCE.rglob("*.md"):
        try:
            with open(include_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Get relative path from INCLUDES_SOURCE
            rel_path = include_file.relative_to(INCLUDES_SOURCE)

            # Create subdirectories
            target_partial = partials_dir / rel_path.with_suffix('.adoc')
            target_partial.parent.mkdir(parents=True, exist_ok=True)

            # Convert markdown to asciidoc (simple conversion for includes)
            # Most includes are just notes, so minimal conversion needed
            asciidoc_content = content  # Placeholder - could enhance this

            with open(target_partial, 'w', encoding='utf-8') as f:
                f.write(asciidoc_content)

            count += 1

        except Exception as e:
            print(f"Error converting include {include_file}: {e}")

    print(f"Converted {count} include files to partials")


def main():
    report = MigrationReport()

    print("Starting Jekyll/Markdown to Antora/AsciiDoc migration...")
    print(f"Source: {SOURCE_DIR}")
    print(f"Target: {TARGET_DIR}")

    # Find all markdown files
    md_files = list(SOURCE_DIR.rglob("*.md"))
    report.total_files = len(md_files)

    print(f"\nFound {report.total_files} markdown files")

    # Convert each file
    for i, md_file in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Processing {i}/{report.total_files}...")

        converter = MarkdownToAsciiDocConverter(md_file, report)
        if converter.convert():
            report.converted_files += 1

    # Convert includes
    print("\nConverting includes...")
    migrate_includes()

    # Print summary
    report.print_summary()


if __name__ == "__main__":
    main()
