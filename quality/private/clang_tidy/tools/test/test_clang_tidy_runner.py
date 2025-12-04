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
Tests for the clang_tidy_runner module.
"""

import json
import logging
import os
import subprocess
import typing as t
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

import pytest
import ruamel.yaml
from pytest_mock import MockerFixture

import quality.private.clang_tidy.tools.clang_tidy_runner as unit
from quality.private.clang_tidy.tools import common


def get_all_keys_from_yaml(yaml_config_string):
    """Returns all keys as a list from yaml."""
    all_keys = []
    for keys in ruamel.yaml.YAML(typ="safe", pure=True).load(yaml_config_string)["CheckOptions"]:
        all_keys.append((keys["key"]))
    return all_keys


all_suppressed = {
    "stderr": (
        "5 warnings generated.\n"
        "Suppressed 5 warnings (5 in non-user code).\n"
        "Use -header-filter=.* to display errors from all non-system headers.\n"
    ),
    "stdout": "",
}

one_finding = {
    "stderr": (
        "5 warnings generated.\n"
        "Suppressed 4 warnings (4 in non-user code).\n"
        "Use -header-filter=.* to display errors from all non-system headers.\n"
        "1 warning treated as error"
    ),
    "stdout": (
        "\x1b[1m/root/source.cpp:15:5: \x1b[0m\x1b[0;1;31merror: "
        "\x1b[0m\x1b[1mUnallowed call [some-check,-warnings-as-errors]\x1b[0m\n"
        'strcpy(s, "Hello world!");\n'
        "\x1b[0;1;32m^\n"
        "\x1b[0m\n"
    ),
}

one_warning = {
    "stderr": (
        "5 warnings generated.\n"
        "Suppressed 5 warnings (5 in non-user code).\n"
        "Use -header-filter=.* to display errors from all non-system headers."
    ),
    "stdout": (
        "/root/source.cpp:21:3: warning: "
        "variable 'var_float' of type 'float' can be declared 'const' [misc-const-correctness]\n"
    ),
}


def get_default_run_clang_tidy_args() -> dict:
    """Helper that provides default args for the function run_clang_tidy."""
    return {
        "src_file": "source.cpp",
        "clang_tidy_args": "",
        "compile_commands_file": "/tmp/compile_commands.json",
        "checks": None,
        "fixes": "/tmp/fixes.yaml",
        "tool_bin": "clang_tidy",
        "treat_clang_tidy_warnings_as_errors": True,
        "module_type": None,
        "config_files": [".clang-tidy-default"],
        "header_filter": None,
        "suppress_patterns": None,
        "system_headers": False,
        "verbose": True,
        "allow_enabling_analyzer_alpha_checkers": False,
    }


def get_default_build_command_args() -> dict:
    """Helper that provides default args for the function build_command."""
    return {
        "src_file": "bar/foo.cpp",
        "clang_tidy_args": "-I All",
        "compile_commands_file": "/tmp/compile_commands.json",
        "checks": None,
        "fixes": None,
        "tool_bin": "/usr/bin/clang-tidy",
        "config_file": "some_irrelevant_file_name.txt",
        "header_filter": None,
        "system_headers": False,
        "treat_clang_tidy_warnings_as_errors": True,
        "allow_enabling_analyzer_alpha_checkers": False,
    }


class ClangTidyRunnerTests(unittest.TestCase):
    """Test class for Clang Tidy Runner."""

    @patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stderr="", stdout=""),
    )
    def test_run_clang_tidy_no_output(self, subprocess_patch):
        """Test run clang tidy no output."""
        success = unit.run_clang_tidy(**get_default_run_clang_tidy_args())
        subprocess_patch.assert_called()
        self.assertTrue(success)

    @patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stderr=all_suppressed["stderr"],
            stdout=all_suppressed["stdout"],
        ),
    )
    def test_run_clang_tidy_all_suppressed(self, subprocess_patch):
        """Test run clang tidy all suppressed."""
        success = unit.run_clang_tidy(**get_default_run_clang_tidy_args())
        subprocess_patch.assert_called()
        self.assertTrue(success)

    @patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stderr=one_finding["stderr"],
            stdout=one_finding["stdout"],
        ),
    )
    def test_run_clang_tidy_one_finding_treated_as_error(self, subprocess_patch):
        """Test run clang tidy one finding treated as error."""
        success = unit.run_clang_tidy(**get_default_run_clang_tidy_args())
        subprocess_patch.assert_called()
        self.assertFalse(success)

    @patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stderr=all_suppressed["stderr"],
            stdout=one_finding["stdout"],
        ),
    )
    def test_run_clang_tidy_one_finding_not_treated_as_error(self, subprocess_patch):
        """Test run clang tidy one finding not treated as error."""
        success = unit.run_clang_tidy(**get_default_run_clang_tidy_args())
        subprocess_patch.assert_called()
        self.assertTrue(success)

    def test_get_result_count(self):
        """Test get result count."""
        self.assertEqual(unit.get_result_count(r"(.*)", "100"), 100)
        self.assertEqual(unit.get_result_count(r"Number (\d+)", "Number 42"), 42)

    def test_check_output_when_error(self):
        """Test check output when error."""
        arbitrary_output = (
            "583 warnings and 1 error generated.\n"
            "Error while processing /random/path/target.cpp\n"
            "Suppressed 583 warnings (582 in non-user code, 1 NOLINT).\n"
        )
        results = unit.check_output(arbitrary_output)
        self.assertEqual(results.errors, 1)
        self.assertEqual(results.warnings, 583)
        self.assertEqual(results.suppressions, 583)
        self.assertEqual(results.nolints, 1)

    def test_check_output_when_no_error(self):
        """Test check output when no error."""
        arbitrary_output = "4471 warnings generated.\nbSuppressed 4535 warnings (4464 in non-user code, 71 NOLINT).\n"
        results = unit.check_output(arbitrary_output)
        self.assertEqual(results.errors, 0)
        self.assertEqual(results.warnings, 4471)
        self.assertEqual(results.suppressions, 4535)
        self.assertEqual(results.nolints, 71)

    def test_build_command_when_all_possible_arguments_are_used(self):
        """Test build command when all possible arguments are used."""
        run_args = get_default_build_command_args()
        run_args["checks"] = "check-*"
        run_args["fixes"] = "file/fixes.txt"
        run_args["config_file"] = "Does not matter"
        run_args["header_filter"] = None
        run_args["treat_clang_tidy_warnings_as_errors"] = False
        run_args["allow_enabling_analyzer_alpha_checkers"] = True

        self.assertEqual(
            unit.build_command(**run_args),
            [
                "/usr/bin/clang-tidy",
                "--checks",
                "check-*",
                "--header-filter",
                ".*",
                "--export-fixes",
                "file/fixes.txt",
                "--allow-enabling-analyzer-alpha-checkers",
                "--extra-arg=-Xclang",
                "--extra-arg=-analyzer-config",
                "--extra-arg=-Xclang",
                "--extra-arg=aggressive-binary-operation-simplification=true",
                "--use-color",
                "bar/foo.cpp",
                "-p",
                "/tmp",
            ],
        )

        run_args["header_filter"] = "/path/to/some/header.h"
        run_args["system_headers"] = True

        self.assertEqual(
            unit.build_command(**run_args),
            [
                "/usr/bin/clang-tidy",
                "--checks",
                "check-*",
                "--header-filter",
                "/path/to/some/header.h",
                "--system-headers",
                "--export-fixes",
                "file/fixes.txt",
                "--allow-enabling-analyzer-alpha-checkers",
                "--extra-arg=-Xclang",
                "--extra-arg=-analyzer-config",
                "--extra-arg=-Xclang",
                "--extra-arg=aggressive-binary-operation-simplification=true",
                "--use-color",
                "bar/foo.cpp",
                "-p",
                "/tmp",
            ],
        )

        with open(run_args["compile_commands_file"], encoding="utf-8") as file_handle:
            com_db_content = json.load(file_handle)
            self.assertEqual(len(com_db_content), 1)
            self.assertEqual(com_db_content[0]["directory"], str(Path.cwd()))
            self.assertEqual(com_db_content[0]["file"], "bar/foo.cpp")
            self.assertEqual(com_db_content[0]["arguments"], ["-I All"])

    def test_has_no_problem(self):
        """Test has no problem."""
        # Total warnings = Warnings + Nolints
        # Suppressed warnings = Suppressed - Nolints
        # Counting = Total warnings - Suppressed warnings
        # TidyFindings(errors warnings suppressions nolints)  (e  w  s  n  c   r)
        self.assertEqual(unit.has_no_problem(common.TidyFindings(0, 0, 0, 0, 0), 0), True)  # All zero
        self.assertEqual(unit.has_no_problem(common.TidyFindings(0, 0, 0, 0, 0), 1), False)  # Return code != 0
        self.assertEqual(unit.has_no_problem(common.TidyFindings(1, 0, 0, 0, 0), 0), False)  # Error
        self.assertEqual(unit.has_no_problem(common.TidyFindings(1, 2, 3, 4, 2), 5), False)  # Error, others irrelevant
        self.assertEqual(unit.has_no_problem(common.TidyFindings(0, 1, 0, 0, 0), 0), False)  # Warning
        self.assertEqual(unit.has_no_problem(common.TidyFindings(0, 1, 1, 0, 0), 0), True)  # Warning == Suppression
        self.assertEqual(unit.has_no_problem(common.TidyFindings(0, 1, 2, 1, 0), 0), True)  # Warning == Suppresion - n
        self.assertEqual(unit.has_no_problem(common.TidyFindings(0, 5, 8, 3, 0), 1), True)  # Result code irrelevant

    def test_patch_protobuf_include(self):
        """Test patch protobuf include."""
        self.assertEqual(unit.patch_protobuf_include(""), "")
        self.assertEqual(unit.patch_protobuf_include("-I ."), "-I .")
        self.assertEqual(unit.patch_protobuf_include("-isystem foo"), "-isystem foo")
        self.assertEqual(
            unit.patch_protobuf_include("-I foo/_virtual_includes/bar_proto"),
            "-isystem foo/_virtual_includes/bar_proto",
        )
        self.assertEqual(
            unit.patch_protobuf_include("-I valid_path -I foo/_virtual_includes/bar_proto"),
            "-I valid_path -isystem foo/_virtual_includes/bar_proto",
        )
        self.assertEqual(
            unit.patch_protobuf_include("-I valid_path -I foo/_virtual_includes/bar_proto -isystem valid_path"),
            "-I valid_path -isystem foo/_virtual_includes/bar_proto -isystem valid_path",
        )

    def test_load_configuration_no_additional_key(self):
        """Test load configuration no additional key."""
        yaml_config_string, _ = unit.load_configuration(".clang-tidy-default", {})
        all_keys = get_all_keys_from_yaml(yaml_config_string)
        self.assertNotIn("ArbitraryKey", all_keys)

    def test_load_configuration_with_additional_key(self):
        """Test load configuration with additional key."""
        yaml_config_string, _ = unit.load_configuration(
            ".clang-tidy-default", {"key": "ArbitraryKey", "value": "ArbitraryValue"}
        )
        all_keys = get_all_keys_from_yaml(yaml_config_string)
        self.assertIn("ArbitraryKey", all_keys)


@pytest.mark.parametrize(
    "checks, stdout, stderr",
    [
        (None, "stdout_message", ""),
        ("check1,check2", "", "stderr_message"),
    ],
)
def test_write_results(
    tmp_path: Path,
    checks: t.Optional[str],
    stdout: str,
    stderr: str,
):
    """Test the function write_results."""
    tmp_file = tmp_path / "file.txt"

    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stderr=stderr,
        stdout=stdout,
    )

    unit.write_results(
        tmp_file,
        "file_path.cpp",
        "args",
        checks,
        "clang_tidy",
        result,
    )

    file_text = tmp_file.read_text()

    assert "File: 'file_path.cpp'" in file_text
    assert "Arguments: 'args'" in file_text
    assert f"Checks: '{checks}'" in file_text
    assert "Command: 'clang_tidy'" in file_text
    assert stderr in file_text
    if stdout:
        assert stdout in file_text
    else:
        assert "No clang-tidy finding(s)" in file_text


def test_run_clang_tidy_config_exception(mocker: MockerFixture):
    """Test run_clang_tidy when a config exception occurs."""
    mocker.patch(
        "quality.private.clang_tidy.tools.clang_tidy_configs.merge_configs",
        side_effect=common.ConfigException(message="exception_message"),
    )

    with pytest.raises(SystemExit) as context:
        unit.run_clang_tidy(**get_default_run_clang_tidy_args())

    assert context.value.code == 1


def test_run_clang_tidy_internal_error(mocker: MockerFixture, caplog: pytest.LogCaptureFixture):
    """Test run_clang_tidy when a clang_tidy internal error occurs."""
    stderr = "clang-tidy internal error"

    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stderr=stderr,
            stdout="",
        ),
    )

    assert not unit.run_clang_tidy(**get_default_run_clang_tidy_args())
    assert stderr in caplog.text


def test_run_clang_tidy_non_verbose_no_fixes(mocker: MockerFixture, caplog: pytest.LogCaptureFixture):
    """Test run_clang_tidy without the verbose flag and without creating an empty fixes file."""
    args = get_default_run_clang_tidy_args()
    args["fixes"] = None
    args["verbose"] = False

    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stderr="", stdout=""),
    )

    filter_results_mock = mocker.patch("quality.private.clang_tidy.tools.clang_tidy_runner.filter_results")

    with caplog.at_level(logging.DEBUG):
        unit.run_clang_tidy(**args)

    filter_results_mock.assert_not_called()
    assert "Running command:" not in caplog.text


def test_run_clang_tidy_one_warning_not_treated_as_error(mocker: MockerFixture):
    """Test run_clang_tidy with a warning that is not treated as error."""
    args = get_default_run_clang_tidy_args()
    args["treat_clang_tidy_warnings_as_errors"] = False

    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stderr=one_warning["stderr"],
            stdout=one_warning["stdout"],
        ),
    )

    success = unit.run_clang_tidy(**args)

    assert success


def test_present_output_with_no_stdout(caplog: pytest.LogCaptureFixture):
    """Test the function present_output when there is no stdout"""
    tidy_findings = common.TidyFindings(
        errors=0,
        warnings=0,
        suppressions=0,
        nolints=0,
        counting=0,
    )
    result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stderr="",
        stdout="",
    )
    with caplog.at_level(logging.INFO):
        unit.present_output(tidy_findings, result)

    assert "0 counting clang-tidy finding(s)" in caplog.text
    assert "---" not in caplog.text


@pytest.mark.parametrize(
    "stderr, stdout, expected_log_messages",
    [
        (
            one_warning["stderr"],
            one_warning["stdout"],
            ["Output from clang-tidy stderr:", "Output from clang-tidy stdout:"],
        ),
        (one_warning["stderr"], "", ["Output from clang-tidy stderr:"]),
        ("", "", []),
    ],
)
def test_present_stdoutputs(caplog: pytest.LogCaptureFixture, stderr: str, stdout: str, expected_log_messages: list):
    """Test the function present_stdoutputs."""

    with caplog.at_level(logging.INFO):
        unit.present_stdoutputs(
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stderr=stderr,
                stdout=stdout,
            )
        )

    assert all(expected_message in caplog.text for expected_message in expected_log_messages)
    assert stderr in caplog.text
    assert stdout in caplog.text


def test_present_summary_no_errors(caplog: pytest.LogCaptureFixture):
    """Test the function present_summary when clag-tidy detects no errors."""
    file_name = "source.cpp"
    tidy_findings = common.TidyFindings(
        errors=0,
        warnings=2,
        suppressions=2,
        nolints=1,
        counting=0,
    )

    with caplog.at_level(logging.INFO):
        unit.present_summary(file_name, tidy_findings, "findings.log")

    assert f"SUMMARY for '{file_name}'" in caplog.text
    assert "3 total clang-tidy finding(s)" in caplog.text
    assert "1 counting clang-tidy finding(s) in user code" in caplog.text
    assert "1 suppressed clang-tidy finding(s) in external code" in caplog.text
    assert "1 suppressed clang-tidy finding(s) via NOLINT" in caplog.text
    assert "For detailed logs see $(bazel info workspace)/findings.log" in caplog.text


def test_present_summary_with_errors(caplog: pytest.LogCaptureFixture):
    """Test the function present_summary when clang-tidy detects errors."""
    file_name = "source.cpp"
    tidy_findings = common.TidyFindings(
        errors=2,
        warnings=2,
        suppressions=2,
        nolints=1,
        counting=0,
    )

    with caplog.at_level(logging.ERROR):
        unit.present_summary(file_name, tidy_findings, "findings.log")

    assert "2 error(s) during clang-tidy execution" in caplog.text


@pytest.mark.parametrize(
    "merged_config, suppress_patterns, expected_stdout_arg,tidy_filtered_findings,expected_tidy_findings",
    [
        (
            {"Checks": "*"},
            ["TEST"],
            ["TEST"],
            common.TidyFindings(
                errors=0,
                warnings=2,
                suppressions=2,
                nolints=0,
                counting=0,
            ),
            common.TidyFindings(
                errors=0,
                warnings=2,
                suppressions=2,
                nolints=0,
                counting=0,
            ),
        ),
        (
            {"Checks": "*"},
            [],
            {"Checks": "*"},
            None,
            common.TidyFindings(
                errors=0,
                warnings=3,
                suppressions=2,
                nolints=0,
                counting=0,
            ),
        ),
    ],
)
def test_filter_results(  # pylint: disable=too-many-arguments
    mocker: MockerFixture,
    merged_config: dict,
    suppress_patterns: list,
    expected_stdout_arg: t.Union[dict, list],
    tidy_filtered_findings: t.Optional[common.TidyFindings],
    expected_tidy_findings: common.TidyFindings,
):
    """Test the function filter_results."""

    filter_stdout_mock = mocker.patch(
        "quality.private.clang_tidy.tools.clang_tidy_result_filter.filter_stdout",
        return_value=("filtered_stdout", tidy_filtered_findings),
    )

    fixes = "fixes.yaml"

    tidy_findings = unit.filter_results(
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="stdout",
            stderr="stderr",
        ),
        fixes,
        common.TidyFindings(
            errors=0,
            warnings=3,
            suppressions=2,
            nolints=0,
            counting=0,
        ),
        merged_config,
        suppress_patterns,
    )

    assert tidy_findings == expected_tidy_findings

    filter_stdout_mock.assert_called_with(
        "stdout",
        expected_stdout_arg,
        fixes,
        uses_color=True,
    )


@pytest.mark.parametrize(
    "expected_config_files, expected_behavior, expected_log_message",
    [
        ([], pytest.raises(SystemExit), "No file named config_name found"),
        (["/config_name"], nullcontext("/config_name"), ""),
        (
            ["/config_name", "/other_dir/config_name"],
            nullcontext("/config_name"),
            "Multiple files with name config_name found",
        ),
    ],
)
def test_find_clang_tidy_config(
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    expected_config_files: list,
    expected_behavior,
    expected_log_message: str,
):
    """Test the function find_clang_tidy_config."""

    mocker.patch("glob.glob", return_value=expected_config_files)

    with expected_behavior as e, caplog.at_level(logging.DEBUG):
        assert unit.find_clang_tidy_config("config_name") == e

    assert expected_log_message in caplog.text


@pytest.mark.parametrize(
    "yaml_config, custom_option_dict, expected_dict",
    [
        (
            {"Checks": "*"},
            None,
            {"Checks": "*"},
        ),
        (
            {"Checks": "*", "CheckOptions": [{"key": "IgnoredMacros", "value": "TEST"}]},
            {"key": "banned_functions", "value": "foo"},
            {
                "Checks": "*",
                "CheckOptions": [
                    {"key": "IgnoredMacros", "value": "TEST"},
                    {"key": "banned_functions", "value": "foo"},
                ],
            },
        ),
        (
            {"Checks": "*"},
            {"key": "banned_functions", "value": "foo"},
            {
                "Checks": "*",
                "CheckOptions": [
                    {"key": "banned_functions", "value": "foo"},
                ],
            },
        ),
    ],
)
def test_add_custom_config_values(
    yaml_config: dict,
    custom_option_dict: dict,
    expected_dict: dict,
):
    """Test the function add_custom_config_values."""
    unit.add_custom_config_values(yaml_config, custom_option_dict)

    assert yaml_config == expected_dict


@pytest.mark.parametrize(
    "extra_args, expected_success, expected_log",
    [
        ([], True, ""),
        ([], False, ""),
        (["--verbose"], True, ""),
        (["--silent"], True, ""),
        (["--treat_clang_tidy_warnings_as_errors"], True, ""),
        (["--treat_clang_tidy_warnings_as_errors"], False, "At least one clang-tidy finding was treated as error."),
    ],
)
def test_main(
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
    extra_args: list,
    expected_success: bool,
    expected_log: str,
):
    "Test the main function."

    mocked_args = [
        "--src_file",
        "/source.cpp",
        "--fixes",
        "/fixes/",
        "--tool_bin",
        "clang_tidy_bin",
        "--config_file",
        ".clang_tidy",
    ]

    mocker.patch("sys.argv", ["clang_tidy_runner"] + mocked_args + extra_args)

    run_clang_tidy_mock = mocker.patch(
        "quality.private.clang_tidy.tools.clang_tidy_runner.run_clang_tidy",
        return_value=expected_success,
    )

    assert not unit.main() == expected_success
    assert expected_log in caplog.text
    run_clang_tidy_mock.assert_called_once()


def test_windows_specifics(mocker: MockerFixture):
    """Test the Windows specifics behavior."""

    mocker.patch("quality.private.clang_tidy.tools.clang_tidy_runner.os_name", "nt")

    args = unit.build_command(**get_default_build_command_args())
    print(args)
    warnings_as_errors_index = args.index("--warnings-as-errors")
    assert args[warnings_as_errors_index + 1] == "'*'"

    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stderr="",
            stdout="",
        ),
    )
    unit.run_clang_tidy(**get_default_run_clang_tidy_args())

    assert os.environ["PROGRAMDATA"] == "C:\\ProgramData"
    assert os.environ["SYSTEMROOT"] == "C:\\WINDOWS"
    assert os.environ["WINDIR"] == "C:\\WINDOWS"
