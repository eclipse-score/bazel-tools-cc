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

"""Parse pip requirements files for supported python version."""

load("@rules_python//python:pip.bzl", "pip_parse")
load("@score_bazel_tools_cc//bazel/toolchains/python:versions.bzl", "PYTHON_VERSIONS")

def python_pip_parse():
    """Parse pip requirements files for supported python version."""

    for version in PYTHON_VERSIONS:
        pip_parse(
            name = "score_bazel_tools_cc_pip_{}".format(version.replace(".", "_")),
            requirements_lock = "@score_bazel_tools_cc//third_party/pip:requirements_lock_{}.txt".format(version.replace(".", "_")),
            python_interpreter_target = "@score_bazel_tools_cc_python_{}_host//:python".format(version.replace(".", "_")),
            extra_pip_args = ["--no-cache-dir"],
        )
