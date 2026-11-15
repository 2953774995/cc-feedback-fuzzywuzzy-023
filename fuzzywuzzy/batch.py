#!/usr/bin/env python
# encoding: utf-8
"""Batch nearest-neighbor matching reports.

Provides :func:`nearest`, which matches each query in ``queries`` against
``candidates`` and splits the results into best matches that meet a score
threshold and misses that need manual review.

    >>> from fuzzywuzzy.batch import nearest
    >>> res = nearest(["New Yrok"], ["New York", "Los Angeles"], threshold=80)
    >>> res.matches[0].choice
    'New York'
    >>> res.misses
    []

Scoring is delegated to :func:`fuzzywuzzy.process.extractOne`, so the
existing ``processor`` / ``scorer`` defaults (``utils.full_process`` and
``fuzz.WRatio``) apply unchanged.
"""
from collections import namedtuple

from . import process


Match = namedtuple('Match', ['query', 'choice', 'score'])

NearestResult = namedtuple('NearestResult', ['matches', 'misses'])


def nearest(queries, candidates, threshold=80):
    """Match every query against the candidate list, keeping the best one.

    Each query is matched independently: the single highest-scoring
    candidate is kept. If that best score is at least ``threshold``, the
    result is appended to ``matches``; otherwise the query itself is
    appended to ``misses`` for manual review.

    Args:
        queries: An iterable of strings to match.
        candidates: An iterable of candidate strings to match against.
        threshold: Minimum score (0-100) for a match to be accepted.
            Defaults to 80.

    Returns:
        A :class:`NearestResult` namedtuple with:

        - ``matches``: list of :class:`Match` namedtuples, each with
          ``query``, ``choice`` and ``score``, in query order.
        - ``misses``: list of queries whose best score was below
          ``threshold``, in query order.

        For example::

            NearestResult(
                matches=[Match(query='New Yrok', choice='New York', score=88)],
                misses=[],
            )
    """
    matches = []
    misses = []

    for query in queries:
        best = process.extractOne(query, candidates)
        if best is None or best[1] < threshold:
            misses.append(query)
        else:
            matches.append(Match(query, best[0], best[1]))

    return NearestResult(matches=matches, misses=misses)
