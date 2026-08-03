#!/usr/bin/env python3
"""Safely extract a GKD snapshot ZIP into a local directory."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PureWindowsPath


def unsafe_member(name: str, info: zipfile.ZipInfo) -> bool:
    normalized = name.replace('\\', '/')
    parts = normalized.split('/')
    mode = info.external_attr >> 16
    return (
        not name
        or name.startswith(('/', '\\'))
        or PureWindowsPath(name).is_absolute()
        or PureWindowsPath(name).drive != ''
        or '..' in parts
        or stat.S_IFMT(mode) == stat.S_IFLNK
    )


def extract(archive_path: Path, output_dir: Path) -> None:
    try:
        archive = zipfile.ZipFile(archive_path)
    except zipfile.BadZipFile as error:
        raise ValueError('input is not a valid ZIP file') from error

    with archive:
        if output_dir.exists():
            raise FileExistsError(f'output directory already exists: {output_dir}')
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        members = archive.infolist()
        for info in members:
            if unsafe_member(info.filename, info):
                raise ValueError(f'unsafe ZIP entry: {info.filename!r}')

        with tempfile.TemporaryDirectory(
            dir=output_dir.parent,
            prefix=f'.{output_dir.name}.extract-',
        ) as temporary:
            temporary_dir = Path(temporary)
            for info in members:
                relative_path = Path(info.filename.replace('\\', '/'))
                destination = temporary_dir / relative_path
                if info.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, destination.open('wb') as target:
                    shutil.copyfileobj(source, target)

            if output_dir.exists():
                raise FileExistsError(f'output directory already exists: {output_dir}')
            os.rename(temporary_dir, output_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='path to a GKD snapshot ZIP')
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='directory to create (default: .agents/tmp/snapshots/<zip-stem>)',
    )
    args = parser.parse_args()
    archive_path = args.snapshot.resolve()
    if not archive_path.is_file():
        parser.error(f'not a file: {args.snapshot}')

    output_dir = args.output_dir or Path('.agents/tmp/snapshots') / archive_path.stem
    output_dir = output_dir.resolve()
    try:
        extract(archive_path, output_dir)
    except (FileExistsError, OSError, ValueError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2

    print(output_dir)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
