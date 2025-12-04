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
Main clang-tidy runner module.
"""

import argparse
import glob
import json
import logging
import os
import re
import subprocess
import sys
from os import name as os_name
from pathlib import Path

import ruamel.yaml
from termcolor import colored

from quality.private.clang_tidy.tools import (
    clang_tidy_configs,
    clang_tidy_result_filter,
    common,
)
from quality.private.common.tools.utils import escape_quotes


def get_result_count(regex, output):
    """Helper to apply regex in clang-tidy result stdout."""
    count = 0
    results = re.search(regex, output)
    if results:
        count = int(results.groups()[0])
    return count


def check_output(output):
    """Parse outpout from clang-tidy for judgment of pass/fail."""
    errors_count = get_result_count(r"(\d+) error(?:s)*", output)
    warnings_count = get_result_count(r"(\d+) warning(?:s)* (generated|and)", output)
    suppressions_count = get_result_count(r"Suppressed (\d+) warnings", output)
    nolint_count = get_result_count(r"(\d+) NOLINT", output)
    counting = errors_count + warnings_count - suppressions_count + nolint_count

    return common.TidyFindings(errors_count, warnings_count, suppressions_count, nolint_count, counting)


def patch_protobuf_include(arguments):
    """Patches the clang-tidy arguments with a filtered version."""
    # Currently `cc_proto_library` sets the include path with `-I` and thus leak
    # the warnings into our code:
    # https://github.com/bazelbuild/bazel/issues/8761
    pattern = re.compile(r"-I(\s+[^\s]+\/_virtual_includes\/[^\s]+_proto)")
    filtered_arguments = re.sub(pattern, r"-isystem\1", arguments)
    return filtered_arguments


def prepare_compile_commands_args(arguments, src_file, compile_commands_file):
    """Prepare arguments for compile_commands.json"""
    filtered_arguments = patch_protobuf_include(arguments)
    processed_arguments = escape_quotes(filtered_arguments)

    compile_commands_args = []
    for splitted_arg in processed_arguments.split(";"):
        compile_commands_args.append(splitted_arg)

    compile_commands_file_path = os.path.dirname(os.path.abspath(compile_commands_file))

    content = {
        "directory": os.getcwd(),
        "file": src_file,
        "arguments": compile_commands_args,
    }

    with open(compile_commands_file, "w", encoding="utf-8") as compile_commands_file_handle:
        json.dump([content], compile_commands_file_handle, indent=4)

    logging.debug(f"Compile Commands file content:\n{colored(content, 'magenta')}")

    return compile_commands_file_path


def build_command(  # pylint: disable=too-many-arguments,too-many-locals
    src_file,
    clang_tidy_args,
    compile_commands_file,
    checks,
    fixes,
    tool_bin,
    config_file,
    header_filter,
    system_headers,
    treat_clang_tidy_warnings_as_errors,
    allow_enabling_analyzer_alpha_checkers,
):
    """Prepare a valid call to the clang-tidy binary."""
    commands = []
    commands.append(tool_bin)

    # Either use a config file or overwrite if checks are provided
    if checks:
        commands.extend(["--checks", "".join(checks)])
    else:
        commands.extend(["--config-file", config_file])

    if header_filter:
        commands.extend(["--header-filter", header_filter])
    elif checks:
        commands.extend(["--header-filter", ".*"])

    if system_headers:
        commands.append("--system-headers")

    # Exports a fixes file when this attribute (via rule only) is active
    if fixes:
        commands.extend(["--export-fixes", fixes])

    # Controls whether the warnings will result in a build failure
    if treat_clang_tidy_warnings_as_errors:
        all_warnings_string = "*"
        # Special handling for windows which requires escaping the "*"
        if os_name == "nt":
            all_warnings_string = "'*'"
        commands.extend(["--warnings-as-errors", all_warnings_string])

    if allow_enabling_analyzer_alpha_checkers:
        commands.extend(
            [
                "--allow-enabling-analyzer-alpha-checkers",
                "--extra-arg=-Xclang",
                "--extra-arg=-analyzer-config",
                "--extra-arg=-Xclang",
                "--extra-arg=aggressive-binary-operation-simplification=true",
            ]
        )

    commands.append("--use-color")
    commands.append(src_file)

    # Write arguments into a compilation_database file.
    compile_commands_file_path = prepare_compile_commands_args(clang_tidy_args, src_file, compile_commands_file)
    commands.extend(["-p", compile_commands_file_path])

    return commands


def write_results(findings, src_file, arguments, checks, command, result):  # pylint: disable=too-many-arguments
    """Write results to a file, one per translation unit."""
    with open(findings, mode="w", encoding="utf-8") as the_output:
        # Write a summary to the top of the file
        the_output.write(colored(f"File: '{src_file.strip()}'\n", attrs=["dark"]))
        the_output.write(colored(f"Arguments: '{arguments.strip()}'\n", attrs=["dark"]))
        the_output.write(colored(f"Checks: '{checks.strip() if checks else 'None'}'\n", attrs=["dark"]))

        command_presentation = command.strip()
        the_output.write(colored(f"Command: '{command_presentation}'\n\n", attrs=["dark"]))

        # Write stdout and stderr
        if result.stderr:
            the_output.write(f"{result.stderr}\n")
        if result.stdout:
            the_output.write(f"{result.stdout}\n")
        else:
            the_output.write("No clang-tidy finding(s)\n")


def print_version_info(clang_tidy_bin_path):
    """Prints version info of the used clang tidy binary."""
    result = subprocess.run(
        [clang_tidy_bin_path, "--version"],
        shell=False,
        check=False,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    logging.debug(f"LLVM Version:\n{colored(result.stdout, 'blue')}")


def run_clang_tidy(  # pylint: disable=too-many-arguments,too-many-locals
    src_file,
    clang_tidy_args,
    compile_commands_file,
    checks,
    fixes,
    tool_bin,
    treat_clang_tidy_warnings_as_errors,
    module_type,
    config_files,
    header_filter,
    system_headers,
    suppress_patterns,
    verbose,
    allow_enabling_analyzer_alpha_checkers,
):
    """Build the clang-tidy command, execute via subprocess and present results."""

    custom_option_dict = {"key": "ModuleType", "value": module_type} if module_type else {}

    configs = []
    for config_name in config_files:
        _, config = load_configuration(config_name, custom_option_dict)
        configs.append(config)

    try:
        merged_config = clang_tidy_configs.merge_configs(configs)
    except common.ConfigException:
        sys.exit(1)

    yaml = ruamel.yaml.YAML(typ="rt")

    config_file = Path(".clang-tidy-merged")
    with open(config_file, mode="w", encoding="utf-8") as config_file_handle:
        yaml.dump(merged_config, config_file_handle)

    logging.debug(f"Config file located in {colored(config_file.resolve(), 'yellow')}")

    clang_tidy_bin_path = tool_bin
    env = os.environ

    # Special handlings when on Windows.
    # There is no available hermetic clang toolchain (yet).
    # We patch the clang-tidy path and set it hardcoded to the expected path.
    # Additionally, investigations showed that some environment vars must be set in order
    # that LLVM correctly detected the stdlib from Visual Studio.
    if os_name == "nt":
        env.update({"PROGRAMDATA": "C:\\ProgramData", "SYSTEMROOT": "C:\\WINDOWS", "WINDIR": "C:\\WINDOWS"})

    print_version_info(clang_tidy_bin_path)

    # The config file is present as a runfile data attribute, read it
    command = build_command(
        src_file,
        clang_tidy_args,
        compile_commands_file,
        checks,
        fixes,
        clang_tidy_bin_path,
        str(config_file),
        header_filter,
        system_headers,
        treat_clang_tidy_warnings_as_errors,
        allow_enabling_analyzer_alpha_checkers,
    )

    if verbose:
        command_string = "\n".join(command)
        logging.debug(colored(f"Running command:\n{command_string}", "cyan"))

    # Create a empty fixes file for the case where clang-tidy did not find warnings
    if fixes:
        with open(fixes, mode="w", encoding="utf-8") as the_output:
            the_output.write(common.NO_FIXES_REQUIRED)

    # The actual clang-tidy invocation returning information via stdout and stderr
    result = subprocess.run(
        command,
        shell=False,
        check=False,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    logging.debug(f"Unfiltered stderr has {len(result.stderr.split(os.linesep))} line(s)")
    logging.debug(f"Unfiltered stdout has {len(result.stdout.split(os.linesep))} line(s)")
    logging.debug(f"Unfiltered stderr:\n{result.stderr.split(os.linesep)}")
    logging.debug(f"Unfiltered stdout:\n{result.stdout.split(os.linesep)}")

    # Parse the clang-tidy stderr to obtain meta info
    tidy_findings = check_output(result.stderr)
    logging.debug(f"Unfiltered result: {tidy_findings}")

    # Filter result and assign it to the "normal" stdout, only if active and a fixes file is provided
    # It is still possible to use the vanilla clang-tidy results
    if common.SHALL_USE_FILTER and fixes:
        logging.debug("Using warnings filter")
        tidy_findings = filter_results(result, fixes, tidy_findings, merged_config, suppress_patterns)
        no_tidy_findings = tidy_findings.counting == 0
    else:
        no_tidy_findings = has_no_problem(tidy_findings, result.returncode)

    no_tidy_errors = tidy_findings.errors == 0

    # when `treat_clang_tidy_warnings_as_errors`, if any clang-tidy finding is found, fail the check,
    # Otherwise, allow clang-tidy warnings, fail the check only when clang-tidy error is found.
    is_success = no_tidy_errors
    if treat_clang_tidy_warnings_as_errors:
        is_success = no_tidy_findings

    if not no_tidy_findings:
        # Report the clang-tidy checker output to the caller if there's any finding
        present_output(tidy_findings, result)

    # Clang-Tidy returns a non-zero exit code when there has been an internal problem, or when there was
    # at least one clang-tidy error. The filtering of clang-tidy findings in
    # a post-processing step would allow for a succeeding check even though clang-tidy exits with non-zero.
    # Therefore, we exclude the error matching pattern `(\d+) (warning|error)(?:s)*` from clang-tidy's internal
    # problem
    if result.returncode != 0:
        if re.match(r"(\d+) (warning|error)(?:s)*", result.stderr):
            return is_success
        logging.error(result.stderr)
        return False

    return is_success


def filter_results(result, fixes, tidy_findings, merged_config, suppress_patterns):
    """Calls the filter module and returns a updated result set."""
    if suppress_patterns:
        logging.info("filtering findings by pattern")
        config_path_or_pattens = suppress_patterns
    else:
        config_path_or_pattens = merged_config

    filtered_results, tidy_filtered_findings = clang_tidy_result_filter.filter_stdout(
        result.stdout, config_path_or_pattens, fixes, uses_color=True
    )
    if not tidy_filtered_findings:
        tidy_filtered_findings = tidy_findings

    # Redirect to filtered output + ansi color reset escape
    result.stdout = filtered_results + "\033[0m"
    logging.debug(tidy_filtered_findings)
    # Patch the findings set with filtered results
    tidy_findings = common.TidyFindings(
        errors=tidy_filtered_findings.errors,
        warnings=tidy_filtered_findings.warnings,
        suppressions=tidy_filtered_findings.suppressions,
        nolints=tidy_findings.nolints,
        counting=tidy_filtered_findings.counting,
    )
    return tidy_findings


def has_no_problem(tidy_findings, returncode):
    """Apply some logic to find whether we shall report success of failure."""
    if (
        tidy_findings.errors == 0
        and tidy_findings.warnings == 0
        and tidy_findings.suppressions == 0
        and tidy_findings.nolints == 0
        and tidy_findings.counting == 0
    ):
        return returncode == 0

    counting_warnings = tidy_findings.suppressions - tidy_findings.nolints
    expected_warning_counts_to_succeed = (0, counting_warnings)

    return tidy_findings.errors == 0 and tidy_findings.warnings in expected_warning_counts_to_succeed


def present_output(tidy_findings, result):
    """Some noteworthy output during execution."""
    # When clang-tidy was not successful (it did not report any warnings or meta problem)
    # stderr will have data, otherwise it will be empty
    logging.info(colored(f"{tidy_findings.counting} counting clang-tidy finding(s)", "cyan"))
    if result.stdout:
        logging.info(f"---{result.stdout}")


def present_stdoutputs(result):
    """Helper for vanilla clang-tidy output."""
    if result.stderr:
        logging.info(colored(f"Output from clang-tidy stderr:\n\n{result.stderr}", "cyan"))
        if result.stdout:
            logging.info(colored(f"Output from clang-tidy stdout:\n{result.stdout}", "cyan"))


def present_summary(src_file, tidy_findings, findings):
    """Some colorful outputs."""
    logging.info(colored(f"SUMMARY for '{src_file}'", attrs=["dark"]))

    if tidy_findings.errors > 0:
        logging.error(colored(f"{tidy_findings.errors} error(s) during clang-tidy execution", "red"))

    # Block for warnings, suppressions and warnings in user code
    user_findings = tidy_findings.warnings - tidy_findings.suppressions + tidy_findings.nolints
    external_findings = tidy_findings.suppressions - tidy_findings.nolints

    logging.info(
        colored(
            f"{tidy_findings.warnings + tidy_findings.nolints} total clang-tidy finding(s)",
            "cyan",
        )
    )
    logging.info(colored(f"{user_findings} counting clang-tidy finding(s) in user code", "yellow"))
    logging.info(
        colored(
            f"{external_findings} suppressed clang-tidy finding(s) in external code",
            "blue",
        )
    )
    logging.info(
        colored(
            f"{tidy_findings.nolints} suppressed clang-tidy finding(s) via NOLINT",
            "blue",
        )
    )

    logging.info(f"For detailed logs see {colored(f'$(bazel info workspace)/{findings}', attrs=['underline'])}")


def find_clang_tidy_config(config_name):
    """Searches .clang-tidy file assuming it is part of the runfiles directory."""
    config_files = glob.glob(f"**/{config_name}", recursive=True)
    logging.debug(f"Found these config files {config_files}")

    if len(config_files) == 0:
        msg = f"No file named {config_name} found"
        logging.error(msg)
        sys.exit(msg)
    if len(config_files) > 1:
        msg = f"Multiple files with name {config_name} found"
        logging.debug(msg)
    return config_files[0]


def add_custom_config_values(yaml_config, custom_option_dict):
    """Patch the clang-tidy config with custom values."""
    if custom_option_dict:
        if "CheckOptions" in yaml_config:
            yaml_config["CheckOptions"].append(custom_option_dict)
        else:
            yaml_config["CheckOptions"] = [custom_option_dict]


def load_configuration(config_name, custom_option_dict):
    """
    Reads and pre-processes the config file used as a command line
    "--config" argument for clang-tidy.
    """
    # Find the .clang-tidy file in the current runfiles directory
    config_file_location = find_clang_tidy_config(config_name)

    with open(config_file_location, encoding="utf-8") as config_file:
        config = config_file.read()
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml_config = yaml.load(config)
        add_custom_config_values(yaml_config, custom_option_dict)

    yaml = ruamel.yaml.YAML(typ="rt")
    stream = ruamel.yaml.compat.StringIO()
    yaml.dump(yaml_config, stream)
    return stream.getvalue(), yaml_config


def parse_args():
    """Parses arguments."""

    class ExtendAction(argparse.Action):  # pylint: disable=too-few-public-methods
        """Adds action "extend" for backwards compatibility with python 3.7"""

        def __call__(self, parser, namespace, values, option_string=None):
            items = getattr(namespace, self.dest) or []
            items.extend(values)
            setattr(namespace, self.dest, items)

    parser = argparse.ArgumentParser(fromfile_prefix_chars="@")
    parser.register("action", "extend", ExtendAction)

    parser.add_argument(
        "--src_file",
        type=str,
        help="A comma separated list of src files.",
        required=True,
    )
    parser.add_argument(
        "--arguments",
        type=str,
        help="A comma separated list of compiler arguments per file.",
        required=False,
    )
    parser.add_argument(
        "--compile_commands_file",
        type=str,
        help="A compile_commands.json file to pack compile command per file.",
        required=False,
    )
    parser.add_argument(
        "--checks",
        type=str,
        help="A comma separated list of checks, ignored when a config is used.",
        required=False,
    )
    parser.add_argument(
        "--fixes",
        type=str,
        help="Absolute file path where the fixes.yaml is created.",
        required=True,
    )
    parser.add_argument(
        "--tool_bin",
        type=str,
        help="Absolute file path to the clang-tidy binary.",
        required=True,
    )
    parser.add_argument(
        "--treat_clang_tidy_warnings_as_errors",
        action="store_true",
        default=False,
        help="If true, the tool will return a non-zero exit code in case of at least one clang-tidy violation",
    )
    parser.add_argument(
        "--module_type",
        type=str,
        help="The module to which the translation unit belongs. It is determined based on the bazel C/C++ rule.",
        choices=["executable", "dynamic_library", "static_library"],
        required=False,
    )
    parser.add_argument(
        "--config_file",
        help="The name of the clang-tidy config file.",
        required=True,
        action="extend",
        dest="config_files",
        nargs="+",
    )
    parser.add_argument(
        "--header_filter",
        type=str,
        help=(
            "Regex pattern used to restrict clang-tidy findings from header files to specific ones only."
            "Overrides 'HeaderFilterRegex' option from clang-tidy config file, if any."
        ),
        required=False,
    )
    parser.add_argument(
        "--system_headers",
        action="store_true",
        help="Display the errors from system headers.",
        default=False,
    )
    parser.add_argument(
        "--suppress_patterns",
        type=str,
        nargs="+",
        help="List of regex patterns used to suppress clang-tidy findings.",
        required=False,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Sets logging level to DEBUG.",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        default=False,
        help="Sets logging level to WARNING.",
    )
    parser.add_argument(
        "--allow-enabling-analyzer-alpha-checkers",
        action="store_true",
        default=False,
        help="If true, the tool will be able to enable clang analyzer alpha checkers.",
    )
    args = parser.parse_args()
    return args


def main():
    """Main entry point."""
    args = parse_args()

    log_level = common.DEFAULT_LOG_LEVEL

    if args.silent:
        log_level = common.SILENT_LOG_LEVEL
    if args.verbose:
        log_level = common.VERBOSE_LOG_LEVEL

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    success = run_clang_tidy(
        args.src_file,
        args.arguments,
        args.compile_commands_file,
        args.checks,
        args.fixes,
        args.tool_bin,
        args.treat_clang_tidy_warnings_as_errors,
        args.module_type,
        args.config_files,
        args.header_filter,
        args.system_headers,
        args.suppress_patterns,
        args.verbose,
        args.allow_enabling_analyzer_alpha_checkers,
    )

    if success:
        return 0

    if args.treat_clang_tidy_warnings_as_errors:
        logging.error(
            colored("At least one clang-tidy finding was treated as error.\n", "magenta"),
        )

    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
