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

"""First level of the third-party dependency definition for llvm."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@score_bazel_tools_cc//bazel:github.bzl", "github_url")

def llvm_toolchain_dep0():
    maybe(
        http_archive,
        name = "toolchains_llvm",
        canonical_id = "v1.4.0",
        sha256 = "fded02569617d24551a0ad09c0750dc53a3097237157b828a245681f0ae739f8",
        strip_prefix = "toolchains_llvm-v1.4.0",
        url = github_url("bazel-contrib/toolchains_llvm/releases/download/v1.4.0/toolchains_llvm-v1.4.0.tar.gz"),
    )
