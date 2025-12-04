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
Module to filter clang-tidy results.
"""

import logging
import re
from collections import namedtuple
from os import path
from pathlib import Path

import ruamel.yaml
from termcolor import colored

from quality.private.clang_tidy.tools import common

FindingOutput = namedtuple("FindingOutput", "diagnostic finding")


def filter_findings(patterns, diagnostics, findings):
    """Filter out findings which match any pattern in the pattern list."""
    filtered_warnings = []
    filtered_errors = []

    for index, diagnostic in enumerate(diagnostics):
        is_counting_finding = True
        msg = diagnostic["DiagnosticMessage"]["Message"]
        if any(re.match(pattern, msg) for pattern in patterns):
            is_counting_finding = False

        file_path = Path(diagnostic["DiagnosticMessage"]["FilePath"])

        if is_counting_finding:
            finding_string = findings[index].replace(
                findings[index].split(":")[0],
                "\n" + colored(path.realpath(file_path), "white", attrs=["bold"]),
            )
            # Assuming diagnostic level could be either error or warning
            if diagnostic["Level"] == "Error":
                filtered_errors.append(FindingOutput(diagnostic, finding_string))
            else:
                filtered_warnings.append(FindingOutput(diagnostic, finding_string))

    logging.debug(
        f"Filtered {len(filtered_warnings)} warning(s) {len(filtered_errors)} error(s)",
    )
    return filtered_warnings, filtered_errors


def filter_stdout(stdout, config_path_or_pattens, fixes_path, uses_color):
    """Applies a filter on the clang-tidy output. Currently only macros are filtered."""
    fixes_content = read_fixes_file(fixes_path)
    diagnostics = parse_fixes_file(fixes_content)

    # Defense programming: In case there are no valid diagnostics, fall back to the original output
    if not diagnostics:
        logging.debug("No valid diagnostics found, falling back to original output")
        return stdout, None

    # From the stdout we parse the actual warning output which can later be presented to the user
    findings = parse_warnings(stdout, uses_color)

    # It is crucial that both length do match, everything else would be a internal error
    logging.debug(f"Number of diagnostic entries: {len(diagnostics)}")
    logging.debug(f"Number of parsed findings: {len(findings)}")
    assert len(diagnostics) == len(findings), "Number of diagnostic items do not match number of findings"

    if isinstance(config_path_or_pattens, list):
        filtered_warnings, filtered_errors = filter_findings(config_path_or_pattens, diagnostics, findings)
    else:
        config_content = config_path_or_pattens
        ignored_macros = get_ignored_macros(config_content)

        filtered_warnings, filtered_errors = filter_warnings(ignored_macros, diagnostics, findings)

    filtered_findings = filtered_warnings + filtered_errors
    write_filtered_warnings_to_fixes_file(fixes_content, filtered_findings, fixes_path)
    filtered_stdout = "".join([finding.finding for finding in filtered_findings])

    # Some fields are irrelevant and we use the tidy_findings only as the "diff"
    # between the unfiltered results and the filtered results
    tidy_findings = common.TidyFindings(
        errors=len(filtered_errors),
        warnings=len(filtered_warnings),
        suppressions=len(findings) - len(filtered_findings),
        nolints=0,  # irrelevant
        counting=len(filtered_findings),
    )

    logging.debug(f"Filtered output has {len(filtered_stdout)} line(s)")
    logging.debug(f"Result after filtering {tidy_findings}")

    return filtered_stdout, tidy_findings


def write_filtered_warnings_to_fixes_file(file_content, filtered_warnings, fixes_path):
    """Writes filtered warnings to fixes file."""
    logging.debug(f"Writing filtered warnings to {fixes_path}")
    if filtered_warnings:
        filtered_diagnostics = [warning.diagnostic for warning in filtered_warnings]
        for diag in filtered_diagnostics:
            if "BuildDirectory" in diag:
                diag["BuildDirectory"] = "Omitted"
        file_content["Diagnostics"] = filtered_diagnostics
        remove_symlinks(file_content)
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml.explicit_start = True
        yaml.explicit_end = True
        yaml.width = 500
        stream = ruamel.yaml.compat.StringIO()
        yaml.dump(file_content, stream)
        yaml_content = stream.getvalue()
    else:
        yaml_content = common.NO_FIXES_REQUIRED
    with open(fixes_path, mode="w", encoding="utf-8") as fixes_file:
        fixes_file.write(yaml_content)


def remove_symlinks(content):
    """Remove symlinks from path if real path can be determined."""
    keys = ["FilePath", "MainSourceFile"]

    def remove_symlinks_from_keys() -> None:
        for key in keys:
            if key in content:
                content[key] = path.realpath(content[key])

    if isinstance(content, dict):
        remove_symlinks_from_keys()
        for _, value in content.items():
            remove_symlinks(value)

    if isinstance(content, list):
        for value in content:
            remove_symlinks(value)


def read_fixes_file(fixes_path):
    """Parses fixes yaml."""
    logging.debug(f"Reading fixes file from {fixes_path}")
    with open(fixes_path, encoding="utf-8") as the_file:
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml.preserve_quotes = True
        fixes = yaml.load(the_file)
    return fixes


def parse_fixes_file(fixes_content):
    """Finds the root tree of the fixes file yaml."""
    if "Diagnostics" in fixes_content:
        return fixes_content["Diagnostics"]
    return None


def is_diagnostic_message(message):
    """Return true if the clang-tidy message is a diagnostic."""
    return message.startswith("clang-diagnostic-")


def filter_warnings(ignored_macros, diagnostics, warnings):
    """Browses the fixes files content and matches ignored macros."""
    filtered_warnings = []
    filtered_errors = []
    for index, diagnostic in enumerate(diagnostics):
        is_counting_warning = counting_warning(diagnostic, ignored_macros)

        file_path = Path(diagnostic["DiagnosticMessage"]["FilePath"])
        message = diagnostic["DiagnosticName"]

        # Every diagnostic message should have a valid file path, except for the special category
        # of "clang-diagnostic-" checks, which are basically compiler errors.
        if not file_path.is_file() and not is_diagnostic_message(message):
            logging.warning(
                (
                    "No valid file path found in fixes.yaml reported by a clang-tidy checker.\n"
                    "This is treated as a clang-tidy bug and will be ignored from the analysis result.\n"
                )
            )
            is_counting_warning = False
        if is_counting_warning or is_diagnostic_message(message):
            warning_string = warnings[index].replace(
                warnings[index].split(":")[0],
                "\n" + colored(path.realpath(file_path), "white", attrs=["bold"]),
            )
            if diagnostic.get("Level") == "Error":
                filtered_errors.append(FindingOutput(diagnostic, warning_string))
            else:
                filtered_warnings.append(FindingOutput(diagnostic, warning_string))

    logging.debug(f"Filtered {len(filtered_warnings)} warning(s) {len(filtered_errors)} error(s)")
    return filtered_warnings, filtered_errors


def counting_warning(diagnostic, ignored_macros):
    """Decides whether to count a warning or not."""
    is_counting_warning = True
    if "Notes" in diagnostic and "" not in ignored_macros:
        notes = diagnostic["Notes"]
        for note in notes:
            message = note["Message"]
            if "expanded from macro" in message:
                for ignored_macro in ignored_macros:
                    if ignored_macro in message:
                        is_counting_warning = False
    return is_counting_warning


def build_indices(clang_tidy_output_lines, matches):
    """Returns a list of line-number-indices in which warning have been found."""
    start_line_of_warning_indices = []
    for i, line in enumerate(clang_tidy_output_lines):
        for match in matches:
            if match in line:
                start_line_of_warning_indices.append(i)
                break
    logging.debug(f"Warnings start at indices {start_line_of_warning_indices}")
    return start_line_of_warning_indices


def build_warning_output(extracted_warning, index):
    """Apply some colors and escapes to each warning output."""
    # Unused, it would add a unique ID per translation unit
    _ = [colored("ID: " + f"{(index + 1):04d}", attrs=["dark"])]

    # You need this as we possibly are ignoring warnings messing up the termcolor escapes
    escape_color = ["\x1b[0m"]
    built_warning = "\n".join(escape_color + extracted_warning)
    return built_warning


def build_warning_list(indices, input_lines):
    """Prepares the output the user will see in the end."""
    warnings = []
    for index, _ in enumerate(indices[0:-1]):
        extracted_warning = input_lines[indices[index] : indices[index + 1]]
        warning = build_warning_output(extracted_warning, index)
        warnings.append(warning)

    extracted_warning = input_lines[indices[-1] :]
    warning = build_warning_output(extracted_warning, len(indices) - 1)
    warnings.append(warning)

    logging.debug(f"Warning list has {len(warnings)} item(s)")
    return warnings


def parse_warnings(clang_tidy_output, uses_color):
    """Takes the vanilla clang-tidy output and returns a list of found warnings."""
    warnings = []

    if uses_color:
        # This pattern exploits the fact that "warning" and "error" is printed using term colors, which end with an "m"
        regex_string = r"((?:m)warning|(?:m)error)\:"
    else:
        # This is supposed to be the right pattern but it fails in edge cases
        regex_string = r"(\:\d+\:\d+\:(?:.*|\s*|\S*)(?:warning|error)\:)"

    regex = re.compile(regex_string, re.MULTILINE)
    matches = regex.findall(clang_tidy_output)

    clang_tidy_output_lines = clang_tidy_output.split("\n")
    logging.debug(f"Clang-tidy output has {len(clang_tidy_output_lines)} line(s)")

    if matches:
        logging.debug(f"Regex matched {len(matches)} item(s)")
        indices = build_indices(clang_tidy_output_lines, matches)
        assert len(indices) == len(matches), "Number of indices do not match number of regex matches"
        warnings = build_warning_list(indices, clang_tidy_output_lines)
        assert len(warnings) == len(indices), "Number of warnings do not match number of indices"
    else:
        logging.debug("No matches in clang-tidy output")
    return warnings


def read_config_file(config_file):
    """Parses the .clang-tidy config yaml."""
    logging.debug(f"Reading .clang-tidy config file from {config_file}")
    with open(config_file, encoding="utf-8") as file:
        config = ruamel.yaml.YAML(typ="safe", pure=True).load(file)
    return config


def get_ignored_macros(config):
    """Returns a list of ignored macros from the .clang-tidy yaml."""
    macros = []
    if "CheckOptions" in config:
        for entry in config["CheckOptions"]:
            if entry["key"] == "IgnoredMacros":
                macros = entry["value"]
                macros = macros.split(",")
    macros = list(filter(len, macros))
    logging.debug(f"Ignored macros {macros}")
    return macros
