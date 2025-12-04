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
This module is the main implementation of the tidy_suite.
"""

load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_aspect.bzl",
    "tidy_suite_aspect",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_checks.bzl",
    "AVAILABLE_CHECKS",
    "AVAILABLE_CHECKS_COMBINED",
)

def _tidy_suite_rule_action(ctx, transitive_outputs, outputs):
    """Collects all intermediate results and aggregates"""
    commands = []

    # Only aggregate all transitive rule outputs if the actual rule requests an output file
    if outputs:
        summary = outputs[0]
        commands.append("touch " + summary.path)
        commands.append("echo 'Aggregated clang-tidy output' >" + summary.path)

        all_files = ",".join([file_name.basename for file_name in transitive_outputs])
        commands.append("echo 'Aggregating " +
                        str(len(transitive_outputs)) +
                        " result file(s): '" +
                        all_files +
                        " >>" + summary.path)

        commands.append("echo '' >>" + summary.path)
        for transitive_output in transitive_outputs:
            commands.append("cat " + transitive_output.path + " >>" + summary.path)

        if not transitive_outputs:
            commands.append("echo 'No outputs have been generated for any target' >>" + summary.path)

        # This runs after all aspects have been finished for all targets
        # Build a summary for the invoked rule
        ctx.actions.run_shell(
            command = "; ".join(commands),
            tools = [],
            inputs = transitive_outputs,
            outputs = outputs,
            arguments = [],
            mnemonic = "ClangTidySuite",
        )

def tidy_suite_rule_impl(ctx):
    """Rule implementation of tidy_suite handling the transitive calls to deps

    Args:
        ctx: Context
    Returns:
        DefaultInfo containing the output files
    """
    outputs = []

    # For the time being, it is not allowed to use the tidy_suite rule directly, other than
    # for testing the aspect in this package.
    if not ctx.build_file_path.startswith("quality/private/clang_tidy"):
        fail("You are not allowed to instantiate a tidy_suite rule")

    # Create a summary for the entire rule, if active
    if ctx.attr.summary:
        summary = ctx.actions.declare_file(ctx.attr.name + ".clang_tidy.summary.out")
        outputs.append(summary)

    transitive_outputs = depset(transitive = [target[OutputGroupInfo].clang_tidy_output for target in ctx.attr.deps]).to_list()
    _tidy_suite_rule_action(ctx, transitive_outputs, outputs)

    return [DefaultInfo(files = depset(outputs + transitive_outputs))]

# The rule definition, main entry point
tidy_suite_rule = rule(
    attrs = {
        # The string ".clang-tidy" indicates to use the configuration file instead of user defined checks
        "checks": attr.string(default = ".clang-tidy"),
        "deps": attr.label_list(
            aspects = [tidy_suite_aspect],
        ),
        "summary": attr.bool(default = True),
    },
    implementation = tidy_suite_rule_impl,
)

def tidy_suite(
        name = None,
        deps = None,
        tags = None,
        checks = None,
        summary = None):
    """Macro redirection of tidy_suite to enable adding default tags

    Args:
        name: Target name
        deps: Dependencies (must be cc_library) on which clang-tidy runs
        tags: List of tags, will always add a "tidy_suite" tag
        checks: List of activated checks. Note that this is very limited
        summary:  Either True or False to control exporting a summary file
    """
    tidy_suite_tags = ["tidy_suite"]
    if tags:
        tidy_suite_tags.extend(tags)

    checks_as_string = None
    if checks:
        checks_as_string_proposal = ",".join(checks)
        if checks_as_string_proposal not in AVAILABLE_CHECKS_COMBINED:
            print(
                "The tidy_suite target must have a value for 'check' which is any permutation of those available checks:",
            )  # buildifier: disable=print
            print("\n" + "\n".join(AVAILABLE_CHECKS))  # buildifier: disable=print
            fail()
        else:
            checks_as_string = checks_as_string_proposal

    # Forward call to the tidy_suite rule
    tidy_suite_rule(
        name = name,
        deps = deps,
        tags = tidy_suite_tags,
        checks = checks_as_string,
        summary = summary,
    )
