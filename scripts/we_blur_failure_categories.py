"""Numeric-free failure aggregation for private original Blur instructions.

Never returns input words, names or exception text. This is diagnostic evidence,
not shader reconstruction or proof of complete operand coverage.
"""
from collections import Counter
from scripts.blur_cb_instruction import read

CATEGORIES = frozenset(('words', 'instruction', 'truncated operand',
 'truncated extension', 'unsupported extension', 'destination modifier',
 'relative operand', 'immediate shape', 'operand type', 'truncated payload',
 'CB destination', 'trailing words', 'bounded operand',
 'unsupported CB indexing', 'unsupported CB shape', 'source selection mode'))

def census(instructions):
    failures = Counter()
    accepted = 0
    reads = 0
    for words in instructions:
        try:
            result = read(words)
        except ValueError as error:
            reason = str(error)
            failures[reason if reason in CATEGORIES else 'unclassified'] += 1
        else:
            accepted += 1
            reads += len(result)
    return {'accepted_instructions': accepted, 'decoded_cb_reads': reads,
            'failure_categories': dict(sorted(failures.items())),
            'complete_coverage': not failures,
            'shader_reconstructed': False}
