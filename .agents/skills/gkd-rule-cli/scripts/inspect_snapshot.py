#!/usr/bin/env python3
"""Read a GKD snapshot ZIP and print selector-relevant metadata without extracting it."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

PACKAGE_KEYS = ('packageName', 'package', 'appId', 'package_id')
ACTIVITY_KEYS = ('activityId', 'activityName', 'activity', 'activity_id')
VERSION_KEYS = ('versionName', 'appVersion', 'version', 'version_name')
NODE_KEYS = {
    'id', 'vid', 'text', 'desc', 'contentDescription', 'clickable', 'visibleToUser',
    'visible', 'parentId', 'childIds', 'children', 'bounds',
}


def scalar(value: Any) -> str | None:
    if value is None or isinstance(value, (dict, list)):
        return None
    return str(value)


def walk(value: Any) -> Iterator[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def first_value(documents: list[tuple[str, Any]], keys: tuple[str, ...]) -> str | None:
    for _, document in documents:
        for item in walk(document):
            for key in keys:
                result = scalar(item.get(key))
                if result:
                    return result
    return None


def screen_info(documents: list[tuple[str, Any]]) -> dict[str, Any] | None:
    for _, document in documents:
        for item in walk(document):
            for key in ('screen', 'screenInfo', 'display'):
                value = item.get(key)
                if isinstance(value, Mapping):
                    return {
                        name: value[name]
                        for name in ('width', 'height', 'rotation', 'density')
                        if name in value
                    }
    return None


def node_collections(documents: list[tuple[str, Any]]) -> list[tuple[str, list[Mapping[str, Any]]]]:
    found: list[tuple[str, list[Mapping[str, Any]]]] = []
    for name, document in documents:
        for item in walk(document):
            for key in ('nodes', 'nodeList', 'nodeInfoList', 'windows'):
                value = item.get(key)
                if isinstance(value, list) and value and all(isinstance(node, Mapping) for node in value):
                    nodes = list(value)
                    if any(NODE_KEYS.intersection(node) for node in nodes):
                        found.append((f'{name}:{key}', nodes))
    return found


def text_value(node: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = scalar(node.get(key))
        if value:
            return value
    return None


def node_identifier(node: Mapping[str, Any], fallback: int) -> str:
    return text_value(node, 'nodeId', 'id', 'index') or f'#{fallback}'


def format_node(node: Mapping[str, Any], index: int) -> dict[str, Any]:
    children = node.get('childIds', node.get('children', []))
    return {
        'node': node_identifier(node, index),
        'parent': text_value(node, 'parentId', 'parentNodeId', 'parent'),
        'children': children if isinstance(children, list) else None,
        'text': text_value(node, 'text'),
        'id': text_value(node, 'id', 'viewIdResourceName'),
        'vid': text_value(node, 'vid'),
        'desc': text_value(node, 'desc', 'contentDescription'),
        'clickable': node.get('clickable'),
        'visible': node.get('visibleToUser', node.get('visible')),
        'bounds': node.get('bounds'),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='path to a GKD snapshot ZIP')
    args = parser.parse_args()
    if not args.snapshot.is_file():
        parser.error(f'not a file: {args.snapshot}')

    documents: list[tuple[str, Any]] = []
    try:
        with zipfile.ZipFile(args.snapshot) as archive:
            for info in archive.infolist():
                if info.is_dir() or not info.filename.lower().endswith(('.json', '.json5')):
                    continue
                try:
                    documents.append((info.filename, json.loads(archive.read(info))))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
    except zipfile.BadZipFile:
        print('error: input is not a valid ZIP file', file=sys.stderr)
        return 2

    if not documents:
        print('error: no readable JSON documents found in ZIP', file=sys.stderr)
        return 2

    screens: list[dict[str, Any]] = []
    for source, nodes in node_collections(documents):
        screens.append({
            'source': source,
            'nodeCount': len(nodes),
            'nodes': [format_node(node, i) for i, node in enumerate(nodes)],
        })

    print(json.dumps({
        'package': first_value(documents, PACKAGE_KEYS),
        'activityId': first_value(documents, ACTIVITY_KEYS),
        'appVersion': first_value(documents, VERSION_KEYS),
        'screen': screen_info(documents),
        'jsonFiles': [name for name, _ in documents],
        'screens': screens,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())