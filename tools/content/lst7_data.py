"""Data layer for exercise 7.  Reads exercise-7/output/experiments.json.

Content modules take every number from here; nothing is typed by hand.
"""
from lst_data import prepare


def data():
    return prepare(7)
