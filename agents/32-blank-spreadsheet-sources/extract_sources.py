#!/usr/bin/env python3
"""Recover and verify the source files embedded in the Markdown archive."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re

PATTERN = re.compile(
    r'^<!-- source-file: (?P<path>[^\n]+) sha256:(?P<sha>[0-9a-f]{64}) -->\n'
    r'````python\n(?P<content>.*?)^````\n', re.MULTILINE | re.DOTALL)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown', type=Path, help='downloaded Markdown source archive')
    parser.add_argument('--output', type=Path, default=Path('blank-spreadsheet-sources'))
    parser.add_argument('--force', action='store_true', help='overwrite existing source files')
    args = parser.parse_args()
    document = args.markdown.read_text(encoding='utf-8')
    found = list(PATTERN.finditer(document))
    if len(found) != 392:
        raise SystemExit(f'Expected 392 source files, found {len(found)}. Is the Markdown complete?')
    output = args.output.resolve()
    seen = set()
    prepared = []
    for match in found:
        rel = PurePosixPath(match['path'])
        if rel.is_absolute() or '..' in rel.parts or not rel.parts or '\\' in match['path']:
            raise SystemExit(f'Unsafe path: {rel}')
        dest = (output / Path(*rel.parts)).resolve()
        if output not in dest.parents or dest in seen:
            raise SystemExit(f'Duplicate or unsafe destination: {dest}')
        seen.add(dest)
        data = match['content'].encode('utf-8')
        if hashlib.sha256(data).hexdigest() != match['sha']:
            raise SystemExit(f'Checksum mismatch: {rel}')
        if dest.exists() and not args.force:
            raise SystemExit(f'Refusing to overwrite {dest}; use --force if intended')
        prepared.append((dest, data))
    for dest, data in prepared:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    print(f'Extracted and verified {len(prepared)} source files to {output}')

if __name__ == '__main__':
    main()
