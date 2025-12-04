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

"""A runner that interfaces the tool aspect and runs clang-format on a list of files."""

import argparse
import dataclasses
import enum
import json
import logging
import pathlib
import re
import subprocess
import typing as t


class Severity(str, enum.Enum):
    """Enum for severity types."""

    WARN = "WARN"
    ERROR = "ERROR"
    INFO = "INFO"


class FindingsJSONEncoder(json.JSONEncoder):
    """Encodes dataclass objects using asdict and other objects as strings."""

    def default(self, o):
        """Overrides default encoding."""
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return str(o)


@dataclasses.dataclass
class Finding:
    """Defines a finding."""

    path: pathlib.Path
    message: str
    severity: Severity
    tool: str
    rule_id: str
    line: int = 1
    column: int = 1

    def __str__(self):
        output = f"{self.path}"
        output += f":{self.line}" if self.line else ""
        output += f":{self.column}" if self.line and self.column else ""
        output += f": {self.message} [{self.tool}:{self.rule_id}]"
        return output


class Findings(t.List[Finding]):
    """Defines a list of findings."""

    def to_text_file(self, file: pathlib.Path) -> None:
        """Dumps a list of findings to a .txt file."""
        file.write_text(str(self), encoding="utf-8")

    def to_json_file(self, file: pathlib.Path) -> None:
        """Dumps a list of findings to a .json file."""
        file.write_text(json.dumps(self, cls=FindingsJSONEncoder, indent=2), encoding="utf-8")

    def __str__(self) -> str:
        return "\n".join([str(finding) for finding in self])


class LinterFindingAsError(SystemExit):
    """Raised when a linter finds a finding treats it as an error."""

    def __init__(self, tool_name: str, findings: Findings, outputs: t.List[pathlib.Path]):
        self.findings = findings
        message = f'\nTool "{tool_name}" found findings and stored them at:\n- '
        message += "\n- ".join([str(output) for output in outputs])
        message += f"\nThe following findings were found:\n{self.findings}\n"
        super().__init__(message)


class LinterSubprocessError(Exception):
    """Raised when a linter subprocess fails."""

    def __init__(
        self,
        commands: t.List[str],
        return_code: t.Union[str, int],
        stdout: str,
        stderr: str,
    ):
        self.commands = commands
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(
            f'The command "{self.commands}" returned code "{self.return_code}"'
            f" and the following error message:\n{stderr or stdout}"
        )


@dataclasses.dataclass
class SubprocessInfo:
    """Class that provides a clean interface to the subprocess output."""

    stdout: str
    stderr: str
    return_code: t.Union[str, int]


def execute_subprocess(commands: t.List[str]) -> SubprocessInfo:
    """Function that calls a subprocess and expects a zero return code."""

    result = subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,
        shell=False,
        universal_newlines=True,
    )

    return SubprocessInfo(
        stdout=result.stdout,
        stderr=result.stderr,
        return_code=result.returncode,
    )


@dataclasses.dataclass
class AspectArguments:
    """Class that provides a clean and verified interface between aspect and runner."""

    target_files: t.Set[pathlib.Path]
    config_file: t.Optional[pathlib.Path]
    tool_output_text: pathlib.Path
    tool_output_json: pathlib.Path
    refactor: bool
    compiler_executable: pathlib.Path

    def __post_init__(self):
        if self.compiler_executable.exists():
            logging.debug(f"Compiler executable: {self.compiler_executable}")
        else:
            raise FileNotFoundError(f"Compiler executable does not exist: {self.compiler_executable}")
        if not self.target_files:
            logging.debug("No target files provided.")
        if not self.config_file:
            logging.debug(f"Config file does not exist: {self.config_file} using default clang-format config.")
        else:
            logging.debug(f"Config file: {self.config_file}")


def parse_args() -> AspectArguments:
    """Parse and return arguments."""
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")

    parser.add_argument(
        "--target-files",
        type=str,
        action="extend",
        nargs="+",
        default=[],
        help="",
    )
    parser.add_argument(
        "--compiler-executable",
        type=pathlib.Path,
        required=True,
        help="",
    )
    parser.add_argument(
        "--config-file",
        type=pathlib.Path,
        required=False,
        help="",
    )
    parser.add_argument(
        "--tool-output-text",
        type=pathlib.Path,
        required=True,
        help="",
    )
    parser.add_argument(
        "--tool-output-json",
        type=pathlib.Path,
        required=True,
        help="",
    )
    parser.add_argument(
        "--refactor",
        type=bool,
        default=False,
        help="",
    )

    return AspectArguments(**vars(parser.parse_args()))


def match_issue_line(issue: str) -> t.Optional[re.Match]:
    """Return a regex match object for a clang-format warning line."""
    issue_pattern = re.compile(
        r"^(?P<path>.+?)"
        r":(?P<line>\d+)"
        r":(?P<column>\d+)"
        r": (?P<severity>[a-z]+)"
        r": (?P<message>.*?)"
        r"\s+\[(?P<rule_id>[\w-]+)\]"
    )
    return issue_pattern.match(issue)


def get_clang_format_command(aspect_arguments: AspectArguments, clang_format: pathlib.Path) -> t.List[str]:
    """Create a clang-format command based on the given aspect arguments."""
    command = [str(clang_format)]
    if aspect_arguments.config_file:
        command += [f"-style=file:{aspect_arguments.config_file.resolve()}"]
    command += [str(pathlib.Path(file).resolve()) for file in aspect_arguments.target_files]
    command += ["-i" if aspect_arguments.refactor else "--dry-run"]
    return command


def clang_format_output_parser(tool_output: SubprocessInfo) -> Findings:
    """Parses `tool_output` to get the findings returned from the tool execution."""

    findings = Findings()
    issues = tool_output.stderr.splitlines()

    for issue in issues:
        if "should be clang-formatted" not in issue:
            continue
        match = match_issue_line(issue)
        if not match:
            raise ValueError(f"Unexpected output format from clang-format: {issue}")
        path = pathlib.Path(match.group("path"))
        line = int(match.group("line"))
        column = int(match.group("column"))
        message = match.group("message").strip()
        rule_id = match.group("rule_id").strip()
        findings.append(
            Finding(
                path=path,
                message=message,
                severity=Severity.ERROR,
                tool="clang-format",
                rule_id=rule_id,
                line=line,
                column=column,
            )
        )
    return findings


def main():
    """Main entry point."""

    args = parse_args()

    clang_format = list(args.compiler_executable.parent.glob("clang-format"))[0]

    subprocess_list = get_clang_format_command(args, clang_format)

    tool_output = execute_subprocess(subprocess_list)

    findings = clang_format_output_parser(tool_output)

    findings.to_text_file(args.tool_output_text)
    findings.to_json_file(args.tool_output_json)
    if findings:
        raise LinterFindingAsError(
            tool_name="clang-format",
            findings=findings,
            outputs=[
                args.tool_output_text,
                args.tool_output_json,
            ],
        )


if __name__ == "__main__":  # pragma: no cover
    main()
