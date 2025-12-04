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
Tests for the clang_tidy_result_filter module
"""

import logging
import os
import tempfile
import typing as t
import unittest
from pathlib import Path

import pytest
import ruamel.yaml

import quality.private.clang_tidy.tools.clang_tidy_result_filter as unit
from quality.private.clang_tidy.tools import clang_tidy_runner, common

VALID_INPUT = """
app/fas/test/determinant_unit2_test.cpp:68:1: warning: variable 'gtest_DeterminantTestFixture_Determinant3DPositive_registered_' is non-const and globally accessible, consider making it const [cppcoreguidelines-avoid-non-const-global-variables]
TYPED_TEST(DeterminantTestFixture, Determinant3DPositive)
^
external/gtest/gtest-typed-test.h:206:15: note: expanded from macro 'TYPED_TEST'
  static bool gtest_##CaseName##_##TestName##_registered_                     \
              ^
note: expanded from here
app/fas/test/determinant_unit_test-foo.cpp:78:1: error: variable 'gtest_DeterminantTestFixture_Determinant3DNegative_registered_' is non-const and globally accessible, consider making it const [cppcoreguidelines-avoid-non-const-global-variables]
TYPED_TEST(DeterminantTestFixture, Determinant3DNegative)
^
external/gtest/gtest-typed-test.h:206:15: note: expanded from macro 'TYPED_TEST'
  static bool gtest_##CaseName##_##TestName##_registered_                     \
              ^
note: expanded from here
./app/fas/test/support/generic_point_eq_helper.h:17:22: warning: all parameters should be named in a function [readability-named-parameter]
inline void CheckEq(T, T)
                     ^
                      /*unused*/  /*unused*/
"""

MULTIPLE_NOTES = """
app/fas/test/span_container_adapter_unit_test.cpp:19:1: warning: class 'SpanContainerAdapter_Initialization_Test' defines a copy constructor and a copy assignment operator but does not define a destructor, a move constructor or a move assignment operator [cppcoreguidelines-special-member-functions]
TEST(SpanContainerAdapter, Initialization)
^
external/gtest/gtest.h:2338:42: note: expanded from macro 'TEST'
#define TEST(test_suite_name, test_name) GTEST_TEST(test_suite_name, test_name)
                                         ^
external/gtest/gtest.h:2332:3: note: expanded from macro 'GTEST_TEST'
  GTEST_TEST_(test_suite_name, test_name, ::testing::Test, \
  ^
external/gtest/internal/gtest-internal.h:1355:9: note: expanded from macro 'GTEST_TEST_'
  class GTEST_TEST_CLASS_NAME_(test_suite_name, test_name)                    \
        ^
external/gtest/internal/gtest-internal.h:1347:3: note: expanded from macro 'GTEST_TEST_CLASS_NAME_'
  test_suite_name##_##test_name##_Test
  ^
note: expanded from here
"""

MULTIPLE_NOTES_FIXES_YAML = """
---
MainSourceFile:  '/tmp/span_container_adapter_unit_test.cpp'
Diagnostics:
  - DiagnosticName:  cppcoreguidelines-special-member-functions
    DiagnosticMessage:
      Message:         'class ''SpanContainerAdapter_Initialization_Test'' defines a copy constructor and a copy assignment operator but does not define a destructor, a move constructor or a move assignment operator'
      FilePath:        '/tmp/span_container_adapter_unit_test.cpp'
      FileOffset:      330
      Replacements:    []
    Notes:
      - Message:         'expanded from macro ''TEST'''
        FilePath:        'external/gtest/gtest.h'
        FileOffset:      89246
        Replacements:    []
      - Message:         'expanded from macro ''GTEST_TEST'''
        FilePath:        'external/gtest/gtest.h'
        FileOffset:      88939
        Replacements:    []
      - Message:         'expanded from macro ''GTEST_TEST_'''
        FilePath:        'external/gtest/internal/gtest-internal.h'
        FileOffset:      51987
        Replacements:    []
      - Message:         'expanded from macro ''GTEST_TEST_CLASS_NAME_'''
        FilePath:        'external/gtest/internal/gtest-internal.h'
        FileOffset:      51505
        Replacements:    []
      - Message:         expanded from here
        FilePath:        ''
        FileOffset:      0
        Replacements:    []
    Level:           Warning
    BuildDirectory:  'Omitted'
...
"""

EMPTY_INPUT = ""

SINGLE_COLORED_INPUT = (
    "\x1b[0m\n\x1b[1m./foo/bar.h:98:9: \x1b[0m\x1b[0;1;35mwarning: "
    "\x1b[0m\x1b[1mmember 'data' is public [cpp-public]\x1b[0m\n    "
    "DTO data;\n\x1b[0;1;32m        ^"
)

SINGLE_COLORED_INPUT_ERROR_MULTILINE = """
\x1b[0m\n\x1b[1m./color/multi.h:98:9: \x1b[0m\x1b[0;1;35merror: \x1b[0m\x1b[1mmember 'data' is private [cpp-private]\x1b[0m
    DTO data;\n\x1b[0;1;32m        ^
"""


SINGLE_INPUT = """
foo/bar.cpp:78:1: error: variable 'naming' [check]
void name
     ^
"""

SINGLE_INPUT_FIXES_YAML = """
---
MainSourceFile:  '/tmp/source.cpp'
Diagnostics:
  - DiagnosticName:  magic-number
    DiagnosticMessage:
      Message:         '5 is magic'
      FilePath:        '/tmp/source.cpp'
      FileOffset:      10
      Replacements:    []
    Notes:
      - Message:         'some interesting info'
        FilePath:        'amp/amp.h'
        FileOffset:      50
        Replacements:    []
    Level:           Warning
    BuildDirectory:  'Omitted'
...
"""

THREE_DIAGNOSTICS_INPUT_FIXES_YAML = """---
MainSourceFile:  '/tmp/temp.cpp'
Diagnostics:
  - DiagnosticName:  readability-inconsistent-declaration-parameter-name
    DiagnosticMessage:
      Message:         'function ''teamscale::BufferOverflow'' has a definition with different parameter names'
      FilePath:        '/tmp/temp.cpp'
      FileOffset:      266
      Replacements:    []
    Notes:
      - Message:         'differing parameters are named here: (''power''), in definition: (''index'')'
  - DiagnosticName:  cppcoreguidelines-special-member-functions
    DiagnosticMessage:
      Message:         'class ''SpanContainerAdapter_Initialization_Test'' defines a copy constructor and a copy assignment operator but does not define a destructor, a move constructor or a move assignment operator'
      FilePath:        '/tmp/temp.cpp'
      FileOffset:      330
      Replacements:    []
    Notes:
      - Message:         'expanded from macro ''TEST'''
        FilePath:        '/tmp/temp.cpp'
        FileOffset:      89246
        Replacements:    []
  - DiagnosticName:  cppcoreguidelines-avoid-c-arrays
    DiagnosticMessage:
      Message:         'do not declare C-style arrays, use std::array<> instead'
      FilePath:        '/tmp/temp.cpp'
      FileOffset:      242
      Replacements:    []
    Level:           Warning
    BuildDirectory:  'Omitted'
...
"""

SIMPLE_TEST_MACRO = """
test.cpp:10:20: warning: variable 'foo' is non-const [cppcoreguidelines-const]
  TEST_F(Fixture, Test)
         ^
         external/gtest.h:206:15: note: expanded from macro 'TEST_F'
"""


SIMPLE_TEST_MACRO_FIXES_YAML = """
---
MainSourceFile:  '/tmp/test.cpp'
Diagnostics:
  - DiagnosticName:  cppcoreguidelines-const
    DiagnosticMessage:
      Message:         'variable ''foo'' is non-const'
      FilePath:        '/tmp/test.cpp'
      FileOffset:      30
      Replacements:    []
    Notes:
      - Message:         'expanded from macro ''TEST_F'''
        FilePath:        'external/gtest.h'
        FileOffset:      100
        Replacements:    []
    Level:           Warning
    BuildDirectory:  'Omitted'
...
"""

HUGE_OUTPUT = """
app/project/cross_correlation_unit_test.cpp:23:1: warning: variable 'test_info_' provides global access to a non-const object; consider making the pointed-to data 'const' [cppcoreguidelines-avoid-non-const-global-variables]
TEST(CrossCorrelation, KernelLargerThanSignal)
^
external/gtest/gtest.h:2338:42: note: expanded from macro 'TEST'
#define TEST(test_suite_name, test_name) GTEST_TEST(test_suite_name, test_name)
                                         ^
external/gtest/gtest.h:2332:3: note: expanded from macro 'GTEST_TEST'
  GTEST_TEST_(test_suite_name, test_name, ::testing::Test, \
  ^
external/gtest/internal/gtest-internal.h:1362:39: note: expanded from macro 'GTEST_TEST_'
    static ::testing::TestInfo* const test_info_ GTEST_ATTRIBUTE_UNUSED_;     \
                                      ^
app/project/cross_correlation_unit_test.cpp:23:1: warning: initializing non-owner argument of type 'testing::internal::TestFactoryBase *' with a newly created 'gsl::owner<>' [cppcoreguidelines-owning-memory]
TEST(CrossCorrelation, KernelLargerThanSignal)
^
external/gtest/gtest.h:2338:42: note: expanded from macro 'TEST'
#define TEST(test_suite_name, test_name) GTEST_TEST(test_suite_name, test_name)
                                         ^
external/gtest/gtest.h:2332:3: note: expanded from macro 'GTEST_TEST'
  GTEST_TEST_(test_suite_name, test_name, ::testing::Test, \
  ^
external/gtest/internal/gtest-internal.h:1376:11: note: expanded from macro 'GTEST_TEST_'
          new ::testing::internal::TestFactoryImpl<GTEST_TEST_CLASS_NAME_(    \
          ^
app/project/cross_correlation_unit_test.cpp:23:1: warning: class 'CrossCorrelation_KernelLargerThanSignal_Test' defines a copy constructor and a copy assignment operator but does not define a destructor, a move constructor or a move assignment operator [cppcoreguidelines-special-member-functions]
TEST(CrossCorrelation, KernelLargerThanSignal)
^
external/gtest/gtest.h:2338:42: note: expanded from macro 'TEST'
#define TEST(test_suite_name, test_name) GTEST_TEST(test_suite_name, test_name)
                                         ^
external/gtest/gtest.h:2332:3: note: expanded from macro 'GTEST_TEST'
  GTEST_TEST_(test_suite_name, test_name, ::testing::Test, \
  ^
external/gtest/internal/gtest-internal.h:1355:9: note: expanded from macro 'GTEST_TEST_'
  class GTEST_TEST_CLASS_NAME_(test_suite_name, test_name)                    \
        ^
external/gtest/internal/gtest-internal.h:1347:3: note: expanded from macro 'GTEST_TEST_CLASS_NAME_'
  test_suite_name##_##test_name##_Test
  ^
note: expanded from here
app/project/cross_correlation_unit_test.cpp:34:1: warning: variable 'test_info_' provides global access to a non-const object; consider making the pointed-to data 'const' [cppcoreguidelines-avoid-non-const-global-variables]
TEST(CrossCorrelation, SignalEmpty)
^
external/gtest/gtest.h:2338:42: note: expanded from macro 'TEST'
#define TEST(test_suite_name, test_name) GTEST_TEST(test_suite_name, test_name)
                                         ^
external/gtest/gtest.h:2332:3: note: expanded from macro 'GTEST_TEST'
  GTEST_TEST_(test_suite_name, test_name, ::testing::Test, \
  ^
external/gtest/internal/gtest-internal.h:1362:39: note: expanded from macro 'GTEST_TEST_'
    static ::testing::TestInfo* const test_info_ GTEST_ATTRIBUTE_UNUSED_;     \
                                      ^
app/project/cross_correlation_unit_test.cpp:34:1: warning: initializing non-owner argument of type 'testing::internal::TestFactoryBase *' with a newly created 'gsl::owner<>' [cppcoreguidelines-owning-memory]
TEST(CrossCorrelation, SignalEmpty)
^
external/gtest/gtest.h:2338:42: note: expanded from macro 'TEST'
#define TEST(test_suite_name, test_name) GTEST_TEST(test_suite_name, test_name)
                                         ^
external/gtest/gtest.h:2332:3: note: expanded from macro 'GTEST_TEST'
  GTEST_TEST_(test_suite_name, test_name, ::testing::Test, \
  ^
external/gtest/internal/gtest-internal.h:1376:11: note: expanded from macro 'GTEST_TEST_'
          new ::testing::internal::TestFactoryImpl<GTEST_TEST_CLASS_NAME_(    \
          ^
app/project/cross_correlation_unit_test.cpp:34:1: warning: class 'CrossCorrelation_SignalEmpty_Test' defines a copy constructor and a copy assignment operator but does not define a destructor, a move constructor or a move assignment operator [cppcoreguidelines-special-member-functions]
TEST(CrossCorrelation, SignalEmpty)
^
external/gtest/gtest.h:2338:42: note: expanded from macro 'TEST'
#define TEST(test_suite_name, test_name) GTEST_TEST(test_suite_name, test_name)
                                         ^
external/gtest/gtest.h:2332:3: note: expanded from macro 'GTEST_TEST'
  GTEST_TEST_(test_suite_name, test_name, ::testing::Test, \
  ^
external/gtest/internal/gtest-internal.h:1355:9: note: expanded from macro 'GTEST_TEST_'
  class GTEST_TEST_CLASS_NAME_(test_suite_name, test_name)                    \
        ^
external/gtest/internal/gtest-internal.h:1347:3: note: expanded from macro 'GTEST_TEST_CLASS_NAME_'
  test_suite_name##_##test_name##_Test
  ^
note: expanded from here
"""


def get_example_diagnostics_and_findings() -> t.Tuple[t.List[t.Dict], t.List[str]]:
    """Helper that provides example diagnostics and respective findings."""
    diagnostics = [
        {
            "DiagnosticName": "misc-const-correctness",
            "DiagnosticMessage": {
                "Message": "variable 'var_float' of type 'float' can be declared 'const'",
                "FilePath": "this/is/not/a/file",
                "FileOffset": 417,
            },
            "Replacements": [],
            "Level": "Warning",
            "BuildDirectory": "",
        },
        {
            "DiagnosticName": "clang-diagnostic-unused-variable",
            "DiagnosticMessage": {
                "Message": "unused variable 'var_float",
                "FilePath": "standards/autosar/chapter_00/section_04/A0-4-2.cpp",
                "FileOffset": 423,
            },
            "Replacements": [],
            "Level": "Warning",
            "BuildDirectory": "",
        },
        {
            "DiagnosticName": "clang-diagnostic-unused-variable",
            "DiagnosticMessage": {
                "Message": "unused variable 'var_long_double",
                "FilePath": "standards/autosar/chapter_00/section_04/A0-4-2.cpp",
                "FileOffset": 514,
            },
            "Replacements": [],
            "Level": "Error",
            "BuildDirectory": "",
        },
    ]

    findings = [
        (
            "/standards/autosar/chapter_00/section_04/A0-4-2.cpp:21:3: error: variable 'var_float' of"
            " type 'float' can be declared 'const' [misc-const-correctness]\n  float var_float{0.1F};"
            "\n  ^\n        const "
        ),
        (
            "/standards/autosar/chapter_00/section_04/A0-4-2.cpp:21:9: error: unused variable "
            "'var_float' [clang-diagnostic-unused-variable]\n  float var_float{0.1F};\n        ^"
        ),
        (
            "/standards/autosar/chapter_00/section_04/A0-4-2.cpp:24:15: error: unused variable "
            "'var_long_double' [clang-diagnostic-unused-variable]"
        ),
    ]

    return diagnostics, findings


def create_temp_file_with_content(name, content):
    """Create a temp file with content."""
    with open(name, mode="w", encoding="utf-8") as file_handle:
        file_handle.write(content)


class ClangTidyResultFilterTests(unittest.TestCase):
    """Test class for result filter"""

    def setUp(self):
        """Unit test setup."""
        create_temp_file_with_content("/tmp/test.cpp", "")
        create_temp_file_with_content("/tmp/source.cpp", "")
        create_temp_file_with_content("/tmp/span_container_adapter_unit_test.cpp", "")
        create_temp_file_with_content("/tmp/temp.cpp", "")

        with open(clang_tidy_runner.find_clang_tidy_config(".clang-tidy-default"), encoding="utf-8") as file_handle:
            self.default_clang_tidy_config_dict = ruamel.yaml.YAML(typ="unsafe", pure=True).load(file_handle)

    def test_remove_symlinks(self):
        """Tests removal of symlinks from a fixes yaml content."""

        # First, setup two files "some_file" and a desired symlink to this file "symlink_to_some_file"
        some_file = Path("/tmp/some_file.txt")
        symlink_to_some_file = Path("/tmp/symlink_to_some_file.txt")

        # Remove any of the tmp files from previous runs
        some_file.unlink(missing_ok=True)
        symlink_to_some_file.unlink(missing_ok=True)

        # Check their realpaths
        self.assertEqual("some_file.txt", Path(os.path.realpath(some_file)).name)
        self.assertEqual("symlink_to_some_file.txt", Path(os.path.realpath(symlink_to_some_file)).name)

        # Create the actual symlink and test the pointed name
        symlink_to_some_file.symlink_to(some_file)
        self.assertEqual("some_file.txt", Path(os.path.realpath(symlink_to_some_file)).name)
        self.assertEqual("symlink_to_some_file.txt", symlink_to_some_file.name)

        # Add the symlink file to a dict and let the function change the content to the realpaths
        content = {"MainSourceFile": symlink_to_some_file}
        self.assertEqual(content["MainSourceFile"].name, "symlink_to_some_file.txt")
        unit.remove_symlinks(content)
        self.assertEqual(Path(content["MainSourceFile"]).name, "some_file.txt")

        # Test a more nested symlink replacement
        content = {"Diagnostics": [{"DiagnosticMessage": {"FilePath": symlink_to_some_file}}]}
        self.assertEqual(content["Diagnostics"][0]["DiagnosticMessage"]["FilePath"].name, "symlink_to_some_file.txt")
        unit.remove_symlinks(content)
        self.assertEqual(Path(content["Diagnostics"][0]["DiagnosticMessage"]["FilePath"]).name, "some_file.txt")

    def test_regex_warnings_scope_valid(self):
        """Test regex warnings scope valid."""
        warnings = unit.parse_warnings(VALID_INPUT, uses_color=False)
        self.assertEqual(len(warnings), 3)
        self.assertIn("determinant_unit2_test.cpp:68:1", warnings[0])
        self.assertIn("generic_point_eq_helper.h:17:22", warnings[2])

    def test_regex_warnings_scope_single(self):
        """Test regex warnings scope single."""
        warnings = unit.parse_warnings(SINGLE_INPUT, uses_color=False)
        self.assertEqual(len(warnings), 1)
        self.assertIn("bar.cpp:78:1", warnings[0])

    def test_regex_warnings_scope_empty(self):
        """Test regex warnings scope empty."""
        self.assertEqual(len(unit.parse_warnings(EMPTY_INPUT, uses_color=False)), 0)

    def test_regex_warnings_scope_huge(self):
        """Test regex warnings scope huge"""
        warnings = unit.parse_warnings(HUGE_OUTPUT, uses_color=False)
        self.assertEqual(len(warnings), 6)

    def test_regex_warnings_colored_warning(self):
        """Test regex warnings colored warnings."""
        warnings = unit.parse_warnings(SINGLE_COLORED_INPUT, uses_color=True)
        self.assertEqual(len(warnings), 1)
        self.assertIn("member 'data' is public", warnings[0])

    def test_regex_warnings_colored_error_multiline(self):
        """Test regex warnings colored error multiline."""
        errors = unit.parse_warnings(SINGLE_COLORED_INPUT_ERROR_MULTILINE, uses_color=True)
        self.assertEqual(len(errors), 1)
        self.assertIn("member 'data' is private", errors[0])

    def test_read_clang_tidy_config(self):
        """Test read clang tidy config."""
        config_file_location = clang_tidy_runner.find_clang_tidy_config(".clang-tidy-default")
        config = unit.read_config_file(config_file_location)
        allowed_macros = unit.get_ignored_macros(config)
        self.assertIn("TEST", allowed_macros)
        self.assertNotIn("TEST_P", allowed_macros)
        self.assertNotIn("TEST_F", allowed_macros)
        self.assertNotIn("TEST_FOO", allowed_macros)

    def test_read_fixes_file_test_macro(self):
        """Test read fixes file tet macro."""
        allowed_macros = ["TEST_F"]
        diagnostics = ruamel.yaml.YAML(typ="safe", pure=True).load(SIMPLE_TEST_MACRO_FIXES_YAML)["Diagnostics"]
        warnings = unit.parse_warnings(SIMPLE_TEST_MACRO, uses_color=False)
        filtered_warnings, filtered_errors = unit.filter_warnings(allowed_macros, diagnostics, warnings)
        self.assertEqual(len(filtered_warnings), 0)
        self.assertEqual(len(filtered_errors), 0)

    def test_read_fixes_file_random_macro(self):
        """Test read fixes file random macro."""
        allowed_macros = ["FOO"]
        diagnostics = ruamel.yaml.YAML(typ="safe", pure=True).load(SIMPLE_TEST_MACRO_FIXES_YAML)["Diagnostics"]
        warnings = unit.parse_warnings(SIMPLE_TEST_MACRO, uses_color=False)
        filtered_warnings, filtered_errors = unit.filter_warnings(allowed_macros, diagnostics, warnings)
        self.assertEqual(len(filtered_warnings), 1)
        self.assertEqual(len(filtered_errors), 0)
        self.assertIn(
            "variable 'foo' is non-const [cppcoreguidelines-const]",
            filtered_warnings[0].finding,
        )

    def test_filter_all_gone(self):
        """Test filter all gone."""
        with tempfile.NamedTemporaryFile(delete=False) as the_file:
            the_file.write(bytes(SIMPLE_TEST_MACRO_FIXES_YAML, encoding="utf-8"))
            the_file.flush()
            output, tidy_results = unit.filter_stdout(
                SIMPLE_TEST_MACRO,
                self.default_clang_tidy_config_dict,
                the_file.name,
                uses_color=False,
            )
            self.assertEqual(output, "")
            self.assertEqual(tidy_results.suppressions, 1)

    def test_filter_no_tests(self):
        """Test filter no tests."""
        with tempfile.NamedTemporaryFile(delete=False) as the_file:
            the_file.write(bytes(SINGLE_INPUT_FIXES_YAML, encoding="utf-8"))
            the_file.flush()
            output, tidy_results = unit.filter_stdout(
                SINGLE_INPUT,
                [],
                the_file.name,
                uses_color=False,
            )
            self.assertIn("78:1: error: variable 'naming' [check]", output)
            self.assertEqual(tidy_results.counting, 1)

    def test_filter_multiple_notes(self):
        """Test filter multiple notes."""
        with tempfile.NamedTemporaryFile(delete=False) as the_file:
            the_file.write(bytes(MULTIPLE_NOTES_FIXES_YAML, encoding="utf-8"))
            the_file.flush()
            output, tidy_results = unit.filter_stdout(
                MULTIPLE_NOTES,
                self.default_clang_tidy_config_dict,
                the_file.name,
                uses_color=False,
            )
            self.assertEqual(output, "")
            self.assertEqual(tidy_results.suppressions, 1)

    def test_written_fixes_file_when_filtered_warnings_is_empty(self):
        """Test written fixes file when filtered warnings is empty."""
        with tempfile.NamedTemporaryFile(delete=False) as fixes_file:
            fixes_file.write(bytes(SIMPLE_TEST_MACRO_FIXES_YAML, encoding="utf-8"))
            fixes_file.flush()
            unit.filter_stdout(
                SIMPLE_TEST_MACRO,
                self.default_clang_tidy_config_dict,
                fixes_file.name,
                uses_color=False,
            )
            with open(fixes_file.name, encoding="utf-8") as the_file:
                self.assertEqual(the_file.read(), common.NO_FIXES_REQUIRED)

    def test_written_fixes_file_when_filtered_warnings_is_non_empty(self):
        """Test written fixes file when filtered warnings is non empty."""
        self.maxDiff = None  # pylint: disable=invalid-name
        with tempfile.NamedTemporaryFile(delete=False) as fixes_file:
            fixes_file.write(bytes(THREE_DIAGNOSTICS_INPUT_FIXES_YAML, encoding="utf-8"))
            fixes_file.flush()
            unit.filter_stdout(
                SINGLE_INPUT * 3,
                self.default_clang_tidy_config_dict,
                fixes_file.name,
                uses_color=False,
            )
            expected_output = """---
MainSourceFile: '/tmp/temp.cpp'
Diagnostics:
- DiagnosticName: readability-inconsistent-declaration-parameter-name
  DiagnosticMessage:
    Message: 'function ''teamscale::BufferOverflow'' has a definition with different parameter names'
    FilePath: '/tmp/temp.cpp'
    FileOffset: 266
    Replacements: []
  Notes:
  - Message: 'differing parameters are named here: (''power''), in definition: (''index'')'
- DiagnosticName: cppcoreguidelines-avoid-c-arrays
  DiagnosticMessage:
    Message: 'do not declare C-style arrays, use std::array<> instead'
    FilePath: '/tmp/temp.cpp'
    FileOffset: 242
    Replacements: []
  Level: Warning
  BuildDirectory: 'Omitted'
...
"""
            with open(fixes_file.name, encoding="utf-8") as the_file:
                self.assertEqual(the_file.read(), expected_output)


def test_filter_findings(caplog: pytest.LogCaptureFixture):
    """Test the filter_findings function."""
    diagnostics, findings = get_example_diagnostics_and_findings()

    filter_patterns = [".*const.*"]

    expected_log_msg = "Filtered 1 warning(s) 1 error(s)"
    expected_warnings_count = 1
    expected_errors_count = 1

    with caplog.at_level(logging.DEBUG):
        warnings, errors = unit.filter_findings(filter_patterns, diagnostics, findings)

    assert expected_log_msg in caplog.text
    assert len(warnings) == expected_warnings_count
    assert len(errors) == expected_errors_count
    assert warnings[0][0] == diagnostics[1]
    assert errors[0][0] == diagnostics[2]


def test_filter_warnings(caplog: pytest.LogCaptureFixture):
    """Test the filter_warnings function."""
    diagnostics, findings = get_example_diagnostics_and_findings()
    expected_log_msg = "Filtered 1 warning(s) 1 error(s)"
    expected_warnings_count = 1
    expected_errors_count = 1

    with caplog.at_level(logging.DEBUG):
        warnings, errors = unit.filter_warnings([], diagnostics, findings)

    assert expected_log_msg in caplog.text
    assert len(warnings) == expected_warnings_count
    assert len(errors) == expected_errors_count
    assert warnings[0][0] == diagnostics[1]
    assert errors[0][0] == diagnostics[2]


@pytest.mark.parametrize(
    "config, expected_macros",
    [
        (
            {
                "Checks": "*,-llvm*,",
                "HeaderFilterRegex": ".*",
            },
            [],
        ),
        (
            {
                "Checks": "*,-llvm*,",
                "HeaderFilterRegex": ".*",
                "CheckOptions": [
                    {"key": "IgnoredMicros", "value": "assert.h"},
                    {"key": "IgnoredMacros", "value": "TEST,INSTANTIATE,BENCHMARK,MATCHER"},
                ],
            },
            ["TEST", "INSTANTIATE", "BENCHMARK", "MATCHER"],
        ),
    ],
)
def test_get_ignored_macros(
    caplog: pytest.LogCaptureFixture,
    config: dict,
    expected_macros: list,
):
    """Test the function get_ignored_macros."""
    expected_log = f"Ignored macros {expected_macros}"

    with caplog.at_level(logging.DEBUG):
        macros = unit.get_ignored_macros(config)

    assert macros == expected_macros
    assert expected_log in caplog.text
