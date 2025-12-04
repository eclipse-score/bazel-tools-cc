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

"""Load all python toolchains dependencies."""

load("@rules_python//python:repositories.bzl", "python_register_toolchains")
load("@score_bazel_tools_cc//bazel/toolchains/python:versions.bzl", "PYTHON_VERSIONS")

def python_toolchains():
    """Load all python toolchains dependencies."""

    for version in PYTHON_VERSIONS:
        python_register_toolchains(
            name = "score_bazel_tools_cc_python_{}".format(version.replace(".", "_")),
            python_version = version,
            # There are use cases in which .pyc files in hermetic toolchains can
            #  cause cache misses when running a build as root. However, our CI
            #  uses root users and thus there's the need to disable this check.
            # For more details see https://github.com/bazelbuild/rules_python/pull/713
            ignore_root_user_error = True,
            # We want to use the coverage tool that is shipped with the toolchain.
            register_coverage_tool = True,
            # We want to register the toolchains by ourselves to be able to modify
            #  some of its content, for example, coverage bootstrap file.
            register_toolchains = False,
        )
