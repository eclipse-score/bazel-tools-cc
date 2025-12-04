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

"""Third-party dependency definition for rules_cc."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@score_bazel_tools_cc//bazel:github.bzl", "github_url")

_VERSION = "0.1.1"  # Update `README.md` if you change this.
_PATH = "bazelbuild/rules_cc/releases/download/{version}/rules_cc-{version}.tar.gz".format(version = _VERSION)

def rules_cc():
    maybe(
        http_archive,
        name = "rules_cc",
        sha256 = "712d77868b3152dd618c4d64faaddefcc5965f90f5de6e6dd1d5ddcd0be82d42",
        strip_prefix = "rules_cc-{version}".format(version = _VERSION),
        url = github_url(_PATH),
    )
