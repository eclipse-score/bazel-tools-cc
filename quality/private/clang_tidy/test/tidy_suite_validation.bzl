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
This module is a bazel rule implementation for testing tidy_suite rule outputs
"""

def _tidy_suite_validation_test_impl(ctx):
    """Test Runner which executes the evaluation script on the rule outputs"""
    target = ctx.file.target

    substitutions = {"%TARGET%": target.short_path}
    substitutions.update({"%EXPECTED%": ";".join(ctx.attr.expected)})

    ctx.actions.expand_template(
        output = ctx.outputs.executable,
        template = ctx.file._script,
        is_executable = True,
        substitutions = substitutions,
    )
    return [DefaultInfo(runfiles = ctx.runfiles(files = [target]))]

def _tidy_suite_test_impl(test):
    """Test rule implementation"""
    return rule(
        implementation = _tidy_suite_validation_test_impl,
        attrs = {
            "expected": attr.string_list(),
            "target": attr.label(allow_single_file = True),
            "_cc_toolchain": attr.label(
                default = "@bazel_tools//tools/cpp:current_cc_toolchain",
            ),
            "_script": attr.label(
                allow_single_file = True,
                default = Label(test),
            ),
        },
        test = True,
        toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
    )

# Rule for testing tidy_suite rule.
tidy_suite_test = _tidy_suite_test_impl("@score_bazel_tools_cc//quality/private/clang_tidy/test:tidy_evaluator")
