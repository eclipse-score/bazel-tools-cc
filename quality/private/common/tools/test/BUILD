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

load("@bazel_tools_python//quality:defs.bzl", "py_pytest")
load("@score_bazel_tools_cc_pip_hub//:loaders.bzl", "pkg")

py_pytest(
    name = "test_utils",
    srcs = ["test_utils.py"],
    deps = [
        "//quality/private/common/tools:utils",
        pkg("jsonschema"),
        pkg("pyyaml"),
    ],
)
