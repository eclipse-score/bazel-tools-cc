# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

"""
Tests for the clang_tidy_configs module.
"""

import unittest

import pytest

import quality.private.clang_tidy.tools.clang_tidy_configs as unit
from quality.private.clang_tidy.tools import common


class ClangTidyConfigsTests(unittest.TestCase):
    """Test class for clang_tidy_configs module."""

    def test_merge_configs_checks_single(self):
        """Merge a single config == do not merge."""
        self.assertEqual(unit.merge_configs([{}]), {})
        self.assertEqual(unit.merge_configs([{"Checks": ""}])["Checks"], "")
        self.assertEqual(unit.merge_configs([{"Checks": "check1"}])["Checks"], "check1")
        self.assertEqual(unit.merge_configs([{"Checks": "check1,check2"}])["Checks"], "check1,check2")
        self.assertEqual(
            unit.merge_configs([{"Checks": "check2,check1"}])["Checks"],
            "check2,check1",
        )
        self.assertEqual(
            unit.merge_configs([{"Checks": "-check2,check1"}])["Checks"],
            "-check2,check1",
        )

    def test_merge_configs_checks_multiple(self):
        """Merge multiple configs when different checks."""
        self.assertEqual(
            unit.merge_configs([{"Checks": "check1"}, {"Checks": "check1"}])["Checks"],
            "check1",
        )
        self.assertEqual(
            unit.merge_configs([{"Checks": "check1"}, {"Checks": "check2"}])["Checks"],
            "check1,check2",
        )
        self.assertEqual(
            unit.merge_configs([{"Checks": "-check3,check1"}, {"Checks": "check2"}])["Checks"],
            "-check3,check1,check2",
        )

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "check1"}, {"Checks": "-check1"}])
        self.assertEqual(raised_exit.exception.message, "CheckConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "check1, check2"}, {"Checks": "   -check2,check1"}])
        self.assertEqual(raised_exit.exception.message, "CheckConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "check1, -check2"}, {"Checks": "check1"}])
        self.assertEqual(raised_exit.exception.message, "CheckOrderConflict")

    def test_merge_configs_checks_single_wildcard(self):
        """Merge a single config with wildcards == do not merge."""
        self.assertEqual(
            unit.merge_configs([{"Checks": "cat-*,cat-*,other-cat-*,cat-check,other-cat-check"}])["Checks"],
            "cat-*,cat-*,other-cat-*,cat-check,other-cat-check",
        )
        self.assertEqual(
            unit.merge_configs([{"Checks": "-cat-*,-cat-check"}])["Checks"],
            "-cat-*,-cat-check",
        )

    def test_merge_configs_checks_multiple_wildcard(self):
        """Merge multiple configs with wildcards."""
        self.assertEqual(
            unit.merge_configs([{"Checks": "cat-*"}, {"Checks": "cat-check"}])["Checks"],
            "cat-*",
        )

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "cat-*"}, {"Checks": "-cat-check"}])
        self.assertEqual(raised_exit.exception.message, "CheckWildcardConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "-cat-my-check,cat-*"}, {"Checks": "-cat-check"}])
        self.assertEqual(raised_exit.exception.message, "CheckWildcardConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "-cat-other-cat-*,cat-*,"}, {"Checks": "*"}])
        self.assertEqual(raised_exit.exception.message, "CheckWildcardConflict")

        self.assertEqual(
            unit.merge_configs([{"Checks": "-cat-*"}, {"Checks": "-cat-*, -cat-foo"}])["Checks"],
            "-cat-*",
        )

    def test_merge_configs_checks_multiple_wildcard_special_case(self):
        """Merge multiple configs with wildcards if there is one special "-*" case."""
        self.assertEqual(
            unit.merge_configs([{"Checks": "-*"}, {"Checks": "check"}])["Checks"],
            "-*,check",
        )

        self.assertEqual(
            unit.merge_configs(
                [
                    {"Checks": "-*, foo-check,  all-*"},
                    {"Checks": "-foo-bar-*, check,    all-check"},
                ]
            )["Checks"],
            "-*,all-*,check,foo-check",
        )

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "-*,-check"}, {"Checks": "check"}])
        self.assertEqual(raised_exit.exception.message, "CheckConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "-*,-foo-*,check"}, {"Checks": "check, foo-bar"}])
        self.assertEqual(raised_exit.exception.message, "CheckWildcardConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "-*,-foo-*,check,"}, {"Checks": "check,foo-*"}])
        self.assertEqual(raised_exit.exception.message, "CheckConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "-*,-foo-*,check,"}, {"Checks": "check,foo-check"}])
        self.assertEqual(raised_exit.exception.message, "CheckWildcardConflict")

        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs([{"Checks": "-*,-foo-*,check,"}, {"Checks": "check,foo-check-*"}])
        self.assertEqual(raised_exit.exception.message, "CheckWildcardConflict")

    def test_merge_configs_check_options_single(self):
        """Merge a single config with options == do not merge."""
        self.assertEqual(
            unit.merge_configs([{"CheckOptions": [{"key": "my_key", "value": True}]}])["CheckOptions"],
            [{"key": "my_key", "value": True}],
        )
        self.assertEqual(
            unit.merge_configs([{"CheckOptions": [{"key": "my_key", "value": "string"}]}])["CheckOptions"],
            [{"key": "my_key", "value": "string"}],
        )

    def test_merge_configs_check_options_multiple(self):
        """Merge multiple configs with check options, only merge when all are the same."""
        self.assertEqual(
            unit.merge_configs(
                [
                    {"CheckOptions": [{"key": "banned_functions", "value": "foo;"}]},
                    {"CheckOptions": [{"key": "banned_functions", "value": ";bar"}]},
                ]
            )["CheckOptions"],
            [{"key": "banned_functions", "value": "bar;foo;"}],
        )
        self.assertEqual(
            unit.merge_configs(
                [
                    {"CheckOptions": [{"key": "banned_functions", "value": ";bar"}]},
                    {"CheckOptions": [{"key": "banned_functions", "value": ";bar"}]},
                ]
            )["CheckOptions"],
            [{"key": "banned_functions", "value": "bar;"}],
        )
        self.assertEqual(
            unit.merge_configs(
                [
                    {"CheckOptions": [{"key": "banned_functions", "value": "foo,bar,"}]},
                    {"CheckOptions": [{"key": "banned_functions", "value": "baz,blu,"}]},
                ]
            )["CheckOptions"],
            [{"key": "banned_functions", "value": "bar,baz,blu,foo,"}],
        )

    def test_merge_configs_one_list_one_no_list(self):
        """Merge multiple configs with check options where one is a list and one not."""
        with self.assertRaises(common.ConfigException) as raised_exit:
            unit.merge_configs(
                [
                    {"CheckOptions": [{"key": "banned_functions", "value": "a"}]},
                    {"CheckOptions": [{"key": "banned_functions", "value": "b,c"}]},
                ]
            )
        self.assertEqual(raised_exit.exception.message, "TypesMismatch")

    def test_merge_string_list(self):
        """Test string list merger."""
        merged = unit.merge_strings({"foo"}, ",")
        self.assertEqual(merged, "foo,")


def test_merge_configs_with_other_keys(caplog: pytest.LogCaptureFixture):
    """Test merge_configs with keys that do not start with Checks/CheckOptions."""
    uniqueness_error_msg = (
        "Conflict: For key `HeaderFileExtensions` all values must be exactly the same among all configs."
    )

    with pytest.raises(common.ConfigException) as context:
        unit.merge_configs(
            [
                {"HeaderFileExtensions": (".h", ".hpp")},
                {"HeaderFileExtensions": (".h")},
            ]
        )

    assert context.value.message == "Uniqueness"
    assert uniqueness_error_msg in caplog.text

    merged_config = unit.merge_configs(
        [
            {"HeaderFileExtensions": (".h", ".hpp")},
            {"HeaderFileExtensions": (".h", ".hpp")},
        ]
    )

    assert merged_config["HeaderFileExtensions"] == (".h", ".hpp")
