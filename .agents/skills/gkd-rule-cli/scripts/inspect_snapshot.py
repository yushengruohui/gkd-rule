#!/usr/bin/env python3
"""Read an extracted GKD snapshot directory and print selector-relevant data."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

PACKAGE_KEYS = ('packageName', 'package', 'appId', 'package_id')
ACTIVITY_KEYS = ('activityId', 'activityName', 'activity', 'activity_id')
VERSION_KEYS = ('versionName', 'appVersion', 'version', 'version_name')
NODE_KEYS = {
    'id', 'nodeId', 'pid', 'parentId', 'vid', 'text', 'desc', 'clickable',
    'visibleToUser', 'visible', 'attr',
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
        if not isinstance(document, Mapping):
            continue
        width = document.get('screenWidth')
        height = document.get('screenHeight')
        if width is not None or height is not None:
            return {
                'width': width,
                'height': height,
                **({'isLandscape': document['isLandscape']} if 'isLandscape' in document else {}),
            }
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


def merged_node(node: Mapping[str, Any]) -> dict[str, Any]:
    """Merge selector attributes while preserving structural node fields."""
    merged = dict(node)
    attributes = node.get('attr')
    if isinstance(attributes, Mapping):
        merged.update(attributes)
    return merged


def text_value(node: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = scalar(node.get(key))
        if value:
            return value
    return None


def node_identifier(raw_node: Mapping[str, Any], fallback: int) -> str:
    return text_value(raw_node, 'nodeId', 'id', 'index') or f'#{fallback}'


def parent_identifier(raw_node: Mapping[str, Any]) -> str | None:
    return text_value(raw_node, 'pid', 'parentId', 'parentNodeId', 'parent')


def is_true(value: Any) -> bool:
    return value is True or value == 1 or (isinstance(value, str) and value.lower() == 'true')


def bounds(node: Mapping[str, Any]) -> Any:
    if node.get('bounds') is not None:
        return node['bounds']
    names = ('left', 'top', 'right', 'bottom')
    if any(name in node for name in names):
        return [node.get(name) for name in names]
    return None


def format_node(raw_node: Mapping[str, Any], index: int) -> dict[str, Any]:
    node = merged_node(raw_node)
    visible = node.get('visibleToUser', node.get('visible'))
    return {
        'node': node_identifier(raw_node, index),
        'parent': parent_identifier(raw_node),
        'name': text_value(node, 'name', 'className', 'class'),
        'text': text_value(node, 'text'),
        'id': text_value(node, 'id', 'viewIdResourceName'),
        'vid': text_value(node, 'vid'),
        'desc': text_value(node, 'desc', 'contentDescription'),
        'clickable': node.get('clickable'),
        'visible': visible,
        'bounds': bounds(node),
    }


def clickable_ancestors(nodes: list[Mapping[str, Any]], index: int) -> list[dict[str, Any]]:
    identifiers = {node_identifier(node, position): position for position, node in enumerate(nodes)}
    ancestors: list[dict[str, Any]] = []
    parent = parent_identifier(nodes[index])
    visited: set[int] = set()
    while parent is not None and parent in identifiers:
        parent_index = identifiers[parent]
        if parent_index in visited:
            break
        visited.add(parent_index)
        parent_node = merged_node(nodes[parent_index])
        if is_true(parent_node.get('clickable')):
            ancestors.append(format_node(nodes[parent_index], parent_index))
        parent = parent_identifier(nodes[parent_index])
    return ancestors


def matches_search(node: Mapping[str, Any], text: str) -> bool:
    query = text.casefold()
    merged = merged_node(node)
    return any(
        query in value.casefold()
        for value in (
            text_value(merged, 'id', 'viewIdResourceName'),
            text_value(merged, 'vid'),
            text_value(merged, 'text'),
            text_value(merged, 'desc', 'contentDescription'),
        )
        if value is not None
    )


def read_documents(snapshot_dir: Path) -> list[tuple[str, Any]]:
    documents: list[tuple[str, Any]] = []
    for path in sorted(snapshot_dir.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.json', '.json5'):
            continue
        try:
            documents.append((path.relative_to(snapshot_dir).as_posix(), json.loads(path.read_text('utf-8'))))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
    return documents


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot_dir', type=Path, help='path to an extracted GKD snapshot directory')
    parser.add_argument('--search', help='search id, vid, text, and desc')
    parser.add_argument('--all-nodes', action='store_true', help='include every node instead of visible clickable candidates')
    args = parser.parse_args()
    snapshot_dir = args.snapshot_dir.resolve()
    if not snapshot_dir.is_dir():
        parser.error(f'not a directory: {args.snapshot_dir}')

    documents = read_documents(snapshot_dir)
    if not documents:
        print('error: no readable JSON documents found in snapshot directory', file=sys.stderr)
        return 2

    screens: list[dict[str, Any]] = []
    for source, raw_nodes in node_collections(documents):
        formatted = [format_node(node, index) for index, node in enumerate(raw_nodes)]
        if args.all_nodes:
            output_nodes = formatted
        else:
            output_nodes = [
                node for node in formatted
                if is_true(node['visible']) and is_true(node['clickable'])
            ]
        screen: dict[str, Any] = {
            'source': source,
            'nodeCount': len(raw_nodes),
            'nodes': output_nodes,
        }
        if args.search:
            screen['searchResults'] = [
                {
                    'node': formatted[index],
                    'clickableAncestors': clickable_ancestors(raw_nodes, index),
                }
                for index, node in enumerate(raw_nodes)
                if matches_search(node, args.search)
            ]
        screens.append(screen)

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
