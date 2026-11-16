"""Data layer for exercise 1.  Reads exercise-1/output/experiments.json.

Content modules take every number from here; nothing is typed by hand.
"""
from lst_data import prepare


def data():
    return prepare(1)
