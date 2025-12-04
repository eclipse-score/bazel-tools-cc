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

"""Tests for the clang_format runner."""

import pathlib
import subprocess
import typing

import pytest
from pytest_mock import MockerFixture

from quality.private.clang_format.tool import clang_format_runner


def test_clang_format_output_parser_with_no_issues() -> None:
    """Tests clang_format_output_parser function."""

    expected_findings = clang_format_runner.Findings()

    subprocess_output = clang_format_runner.SubprocessInfo(
        stdout="",
        stderr="",
        return_code=0,
    )

    findings = clang_format_runner.clang_format_output_parser(subprocess_output)
    assert expected_findings == findings


@pytest.fixture(name="aspect_args")
def fixture_aspect_argument(tmp_path: pathlib.Path) -> clang_format_runner.AspectArguments:
    """Fixture to return the clang format AspectArguments class."""

    test = tmp_path / "test.c"
    test.write_text("")
    compiler_path = tmp_path / "clang-format"
    compiler_path.touch()

    return clang_format_runner.AspectArguments(
        target_files=set([test]),
        tool_output_text=pathlib.Path("output.text"),
        tool_output_json=pathlib.Path("output.json"),
        refactor=False,
        compiler_executable=compiler_path,
        config_file=pathlib.Path(".config_clang_format"),
    )


@pytest.mark.parametrize(
    "aspect_args, expected_command",
    [
        (
            {
                "target_files": {pathlib.Path("file.cpp")},
                "tool_output_text": pathlib.Path("out.txt"),
                "tool_output_json": pathlib.Path("out.json"),
                "refactor": False,
                "config_file": None,
            },
            ["/clang-format", "--dry-run"],
        ),
        (
            {
                "target_files": {pathlib.Path("file.cpp")},
                "tool_output_text": pathlib.Path("out.txt"),
                "tool_output_json": pathlib.Path("out.json"),
                "refactor": True,
                "config_file": pathlib.Path(".config_clang_format"),
            },
            ["/clang-format", "-i", "-style=file:.config_clang_format"],
        ),
    ],
)
def test_get_clang_format_command(tmp_path, aspect_args: dict, expected_command: typing.List[str]) -> None:
    """Tests get_clang_format_command function return commands."""

    test_clang_format = pathlib.Path("/clang-format")
    compiler_path = tmp_path / "clang-format"
    compiler_path.touch()
    aspect_args["compiler_executable"] = compiler_path

    clang_format_command = clang_format_runner.get_clang_format_command(
        aspect_arguments=clang_format_runner.AspectArguments(**aspect_args), clang_format=test_clang_format
    )

    assert (command in clang_format_command for command in expected_command)


@pytest.mark.parametrize(
    "subprocess_output, finding",
    [
        (  # Normal case with valid output.
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="file.cpp:11:12: error: code should be clang-formatted [-Wclang-format-violations]\n",
                return_code=0,
            ),
            clang_format_runner.Finding(
                path=pathlib.Path("file.cpp"),
                message="code should be clang-formatted",
                severity=clang_format_runner.Severity.ERROR,
                tool="clang-format",
                rule_id="-Wclang-format-violations",
                line=11,
                column=12,
            ),
        ),
        (  # Normal case with colon in path.
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="/file.cpp:5:14: error: code should be clang-formatted [-Wclang-format-violations]\n",
                return_code=0,
            ),
            clang_format_runner.Finding(
                path=pathlib.Path("/file.cpp"),
                message="code should be clang-formatted",
                severity=clang_format_runner.Severity.ERROR,
                tool="clang-format",
                rule_id="-Wclang-format-violations",
                line=5,
                column=14,
            ),
        ),
        (  # Normal case with colon in path and no column.
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="/folder:file.cpp:1:2: error: code should be clang-formatted [-Wclang-format-violations]\n",
                return_code=0,
            ),
            clang_format_runner.Finding(
                path=pathlib.Path("/folder:file.cpp"),
                message="code should be clang-formatted",
                severity=clang_format_runner.Severity.ERROR,
                tool="clang-format",
                rule_id="-Wclang-format-violations",
                line=1,
                column=2,
            ),
        ),
    ],
)
def test_clang_format_output_parser_with_issues(
    subprocess_output: clang_format_runner.SubprocessInfo, finding: clang_format_runner.Finding
) -> None:
    """Tests clang_format_output_parser function with results of files with issues."""

    expected_findings = clang_format_runner.Findings([finding])

    findings = clang_format_runner.clang_format_output_parser(subprocess_output)

    assert expected_findings == findings


@pytest.mark.parametrize(
    "subprocess_output, expected_log",
    [
        (  # Case dash instead of colon between line and column.
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="file.cpp:11-12: error: code should be clang-formatted [-Wclang-format-violations]\n",
                return_code=0,
            ),
            "file.cpp:11-12: error: code should be clang-formatted [-Wclang-format-violations]",
        ),
        (  # Case missing rule id.
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="file.cpp:11:12: error: code should be clang-formatted\n",
                return_code=0,
            ),
            "file.cpp:11:12: error: code should be clang-formatted",
        ),
        (  # Case missing line (should not match regex, should log warning)
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="test-file/file.cpp: error: code should be clang-formatted [-Wclang-format-violations]\n",
                return_code=0,
            ),
            "test-file/file.cpp: error: code should be clang-formatted [-Wclang-format-violations]",
        ),
    ],
)
def test_clang_format_output_parser_without_regex_match(
    subprocess_output: clang_format_runner.SubprocessInfo, expected_log: str
) -> None:
    """Tests clang_format_output_parser function when no lines match the regex."""

    with pytest.raises(ValueError) as error:
        clang_format_runner.clang_format_output_parser(subprocess_output)
    assert expected_log in str(error.value)


@pytest.mark.parametrize(
    "subprocess_output",
    [
        (  # Case missing error message.
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="file.cpp:13:1: error: [-Wclang-format-violations]\n",
                return_code=0,
            )
        ),
        (  # Case empty line (should not match regex, should not log anything)
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="\n",
                return_code=0,
            )
        ),
        (  # Case completely malformed line (should not match regex, should log warning)
            clang_format_runner.SubprocessInfo(
                stdout="",
                stderr="not_a_valid_clang_format_output_line\n",
                return_code=0,
            )
        ),
    ],
)
def test_clang_format_output_parser_without_string_match(subprocess_output: clang_format_runner.SubprocessInfo) -> None:
    """Tests clang_format_output_parser function when no lines match the regex."""

    findings = clang_format_runner.clang_format_output_parser(subprocess_output)

    assert findings == clang_format_runner.Findings()


@pytest.mark.parametrize(
    "issue_string, expected_match",
    [
        # Standard case
        (
            "file.cpp:11:12: warning: code should be clang-formatted [-Wclang-format-violations]\n",
            True,
        ),
        # Standard case without column
        (
            "file.cpp:11: warning: code should be clang-formatted [-Wclang-format-violations]\n",
            False,
        ),
        # Case with extra colons in message path
        (
            "/folder:my_file.cpp:22:5: warning: code should: be clang-formatted [-Wclang-format-violations]\n",
            True,
        ),
        # Case with colon in path
        (
            "/file.cpp:11:2: warning: code should be clang-formatted [-Wclang-format-violations]\n",
            True,
        ),
        # Case with colon in path, no column
        (
            "/folder:my_file.cpp:22: warning: code should be clang-formatted [-Wclang-format-violations]\n",
            False,
        ),
        # Case with extra spaces before rule id
        (
            "file.cpp:11:12: warning: code should be clang-formatted  [-Wclang-format-violations]\n",
            True,
        ),
        # Case with severity 'note' and no rule id
        (
            "file.cpp:3:1: note: code should be clang-formatted  [-Wclang-format-violations]\n",
            True,
        ),
        # Case with only path and line, no column, no rule id
        (
            "file.cpp:7: error: Something happened\n",
            False,
        ),
        # Case with only path, line, column, no rule id
        (
            "file.cpp:7:2: error: Something happened\n",
            False,
        ),
    ],
)
def test_match_issue_line(issue_string: str, expected_match: bool) -> None:
    """Tests match_issue_line function with issue strings."""
    match = clang_format_runner.match_issue_line(issue_string)
    if expected_match:
        assert match is not None
        assert match.string == issue_string
    else:
        assert match is None


def test_linter_subprocess_error_str():
    """Test LinterSubprocessError string representation."""

    commands = ["clang-format", "--dry-run", "file.c"]
    return_code = 1
    stdout = ""
    stderr = "Some error occurred"

    error = clang_format_runner.LinterSubprocessError(
        commands=commands,
        return_code=return_code,
        stdout=stdout,
        stderr=stderr,
    )

    assert str(error).startswith("The command")
    assert "clang-format" in str(error)
    assert "Some error occurred" in str(error)
    assert error.return_code == return_code


def test_execute_subprocess_success(mocker: MockerFixture):
    """Test execute_subprocess returns correct SubprocessInfo on success."""

    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr="exception stderr",
        ),
    )
    commands = [
        "path/to/tool_entry_point",
        "--diff",
        "--config",
        "path/to/pyproject.toml",
        "path/to/test.py",
    ]
    expected_stderr = "exception stderr"
    expected_return_code = 0

    result = clang_format_runner.execute_subprocess(commands=commands)

    assert result.stdout == ""
    assert result.stderr == expected_stderr
    assert result.return_code == expected_return_code


def test_parse_args(monkeypatch, tmp_path):
    """Test parse_args parses command line arguments correctly."""

    test_file = tmp_path / "test.c"
    compiler_executable = tmp_path / "clang-format"
    compiler_executable.touch()

    args = [
        "clang-format",
        "--target-files",
        str(test_file),
        "--compiler-executable",
        str(compiler_executable),
        "--tool-output-text",
        str(tmp_path / "output.text"),
        "--tool-output-json",
        str(tmp_path / "output.json"),
        "--refactor",
        "True",
    ]
    monkeypatch.setattr("sys.argv", args)

    result = clang_format_runner.parse_args()

    assert str(test_file) in result.target_files
    assert result.compiler_executable == tmp_path / "clang-format"
    assert result.tool_output_text == tmp_path / "output.text"
    assert result.tool_output_json == tmp_path / "output.json"
    assert result.refactor is True


def test_main_with_finding(mocker: MockerFixture, tmp_path: pathlib.Path):
    """Test main error raises when findings are present."""

    test_file = tmp_path / "test.c"
    test_file_text = tmp_path / "test.text"
    test_file_json = tmp_path / "test.json"
    test_clang_format = tmp_path / "clang-format"
    test_clang_format.touch()

    mocker.patch(
        "quality.private.clang_format.tool.clang_format_runner.parse_args",
        return_value=clang_format_runner.AspectArguments(
            target_files={test_file},
            tool_output_text=test_file_text,
            tool_output_json=test_file_json,
            refactor=False,
            compiler_executable=test_clang_format,
            config_file=pathlib.Path(".config_clang_format"),
        ),
    )
    mocker.patch(
        "quality.private.clang_format.tool.clang_format_runner.execute_subprocess",
        return_value=clang_format_runner.SubprocessInfo(
            stdout="",
            stderr="test.c:1:1: warning: code should be clang-formatted [-Wclang-format-violations]\n",
            return_code=0,
        ),
    )

    with pytest.raises(clang_format_runner.LinterFindingAsError) as linter_error:
        clang_format_runner.main()
    assert "clang-format" in str(linter_error.value)
    assert "test.c" in str(linter_error.value)


def test_main_without_findings(mocker: MockerFixture, tmp_path: pathlib.Path):
    """Test main completes successfully when there are no findings."""

    test_file = tmp_path / "test.c"
    test_file_text = tmp_path / "test.text"
    test_file_json = tmp_path / "test.json"
    test_clang_format = tmp_path / "clang-format"
    test_clang_format.touch()

    mocker.patch(
        "quality.private.clang_format.tool.clang_format_runner.parse_args",
        return_value=clang_format_runner.AspectArguments(
            target_files={test_file},
            tool_output_text=test_file_text,
            tool_output_json=test_file_json,
            refactor=False,
            compiler_executable=test_clang_format,
            config_file=pathlib.Path(".config_clang_format"),
        ),
    )
    mocker.patch(
        "quality.private.clang_format.tool.clang_format_runner.execute_subprocess",
        return_value=clang_format_runner.SubprocessInfo(
            stdout="",
            stderr="",
            return_code=0,
        ),
    )

    clang_format_runner.main()

    assert test_file_text.exists()
    assert test_file_json.exists()


@pytest.mark.parametrize(
    "aspect_arguments, expected_message",
    [
        (  # Compiler executable exist.
            {
                "target_files": {pathlib.Path("file.cpp")},
                "tool_output_text": pathlib.Path("out.txt"),
                "tool_output_json": pathlib.Path("out.json"),
                "refactor": True,
                "config_file": None,
            },
            "Compiler executable:",
        ),
        (  # No target files provided.
            {
                "target_files": {},
                "tool_output_text": pathlib.Path("out.text"),
                "tool_output_json": pathlib.Path("out.json"),
                "refactor": True,
                "config_file": None,
            },
            "No target files provided.",
        ),
        (  # Config file does exist
            {
                "target_files": {pathlib.Path("file.cpp")},
                "tool_output_text": pathlib.Path("out.txt"),
                "tool_output_json": pathlib.Path("out.json"),
                "refactor": True,
                "config_file": pathlib.Path(".config_clang_format"),
            },
            "Config file: .config_clang_format",
        ),
    ],
)
def test_aspectarguments_post_init(tmp_path, aspect_arguments: dict, expected_message: str, caplog) -> None:
    """Tests AspectArguments __post_init__ method."""

    caplog.set_level("DEBUG")
    compiler_executable = tmp_path / "clang-format"
    compiler_executable.touch()
    aspect_arguments["compiler_executable"] = compiler_executable

    clang_format_runner.AspectArguments(**aspect_arguments)

    assert any(expected_message in record.message for record in caplog.records)


def test_aspectarguments_post_init_file_error(tmp_path) -> None:
    """Tests AspectArguments __post_init__ method."""

    aspect_arguments = {
        "target_files": {pathlib.Path("file.cpp")},
        "tool_output_text": pathlib.Path("out.txt"),
        "tool_output_json": pathlib.Path("out.json"),
        "refactor": True,
        "compiler_executable": tmp_path / "not_existing_path",
        "config_file": None,
    }

    with pytest.raises(FileNotFoundError):
        clang_format_runner.AspectArguments(**aspect_arguments)
