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

"""Second level of the third-party dependency definition for llvm."""

load("@toolchains_llvm//toolchain:deps.bzl", "bazel_toolchain_dependencies")
load("@toolchains_llvm//toolchain:rules.bzl", "llvm_toolchain")

def llvm_toolchain_dep1():
    bazel_toolchain_dependencies()

    llvm_toolchain(
        name = "llvm_toolchain",
        llvm_version = "15.0.2",
        stdlib = {"linux-x86_64": "stdc++"},
    )
