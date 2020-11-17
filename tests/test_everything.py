import unittest
from goodolpypi import parse_date
import datetime as dt


class TestParseDate(unittest.TestCase):
    def test_simple_parse(self):
        self.assertEqual(
            parse_date("1923-04-23"), dt.date(year=1923, month=4, day=23)
        )

    def test_parse_yea(self):
        self.assertEqual(
            parse_date("1234"), dt.date(year=1234, month=1, day=1)
        )

    def test_parse_year_month(self):
        self.assertEqual(
            parse_date("1988-12"), dt.date(year=1988, month=12, day=1)
        )

    def test_string_too_long(self):
        with self.assertRaises(ValueError):
            parse_date("12-31-32-123")

    def test_bad_separator(self):
        with self.assertRaises(ValueError):
            parse_date("1233_01_23")

    def test_not_integers(self):
        with self.assertRaises(ValueError):
            parse_date("not-an-integer")

    def test_invalid_dates(self):
        with self.assertRaises(ValueError):
            parse_date("2020123-01-01")
        with self.assertRaises(ValueError):
            parse_date("2020-13")
        with self.assertRaises(ValueError):
            parse_date("2020-02-30")


class TestGetLatestVersion(unittest.TestCase):
    pass


class TestParseArgs(unittest.TestCase):
    pass
