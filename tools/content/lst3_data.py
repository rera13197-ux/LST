"""Data layer for exercise 3.  Reads exercise-3/output/experiments.json.

Content modules take every number from here; nothing is typed by hand.
"""
from lst_data import prepare


def data():
    return prepare(3)
