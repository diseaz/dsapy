#!/usr/bin/python3
# -*- mode: python; coding: utf-8 -*-

import collections


def bfs(start, exits):
    visited = set()
    q = collections.deque(start)
    while q:
        node = q.popleft()
        yield node
        visited.add(node)
        for e in exits(node):
            if e in visited:
                continue
            q.append(e)


def dfs(start, exits):
    visited = set()
    q = list(reversed(start))
    while q:
        node = q.pop()
        yield node
        visited.add(node)
        for e in exits(node):
            if e in visited:
                continue
            q.append(e)


if __name__ == '__main__':
    # Run the doctest tests.
    import sys
    import doctest
    doctest.testmod(sys.modules['__main__'])
