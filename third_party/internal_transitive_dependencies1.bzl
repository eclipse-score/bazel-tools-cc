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

"""Second set of internal transitive dependencies required for this module."""

load("@score_bazel_tools_cc//third_party/bazel_tools_python:dep2.bzl", "bazel_tools_python_dep2")
load("@score_bazel_tools_cc//third_party/llvm_toolchain:dep2.bzl", "llvm_toolchain_dep2")

def internal_transitive_dependencies1():
    """Load transitive macros of the internal dependencies."""

    bazel_tools_python_dep2()
    llvm_toolchain_dep2()
