"""Data layer for exercise 4.  Reads exercise-4/output/experiments.json.

Content modules take every number from here; nothing is typed by hand.
"""
from lst_data import prepare


def data():
    return prepare(4)
