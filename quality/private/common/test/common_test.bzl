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
This module tests the common module.
"""

load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("@score_bazel_tools_cc//quality/private/common:common.bzl", "is_valid_target_filter")

def _is_valid_target_filter_test_impl(ctx):
    env = unittest.begin(ctx)

    asserts.equals(env, True, is_valid_target_filter(["/external"], [], struct(path = "/base/path")))
    asserts.equals(env, True, is_valid_target_filter(["/external", "path"], [], struct(path = "/base/path")))
    asserts.equals(env, False, is_valid_target_filter(["/external"], [], struct(path = "/external/path")))
    asserts.equals(env, False, is_valid_target_filter(["/external", "something"], [], struct(path = "something.bad")))
    asserts.equals(env, True, is_valid_target_filter(["/external"], struct(path = "/base/path")))
    asserts.equals(env, True, is_valid_target_filter(["/external", "path"], struct(path = "/base/path")))
    asserts.equals(env, True, is_valid_target_filter(["/external"], ["external/important"], struct(path = "/external/important/file")))
    asserts.equals(env, True, is_valid_target_filter(["/external", "something"], ["something.good"], struct(path = "something.good")))
    asserts.equals(env, False, is_valid_target_filter(["/external", "something"], ["something.good"], struct(path = "something.bad")))

    return unittest.end(env)

is_valid_target_filter_test = unittest.make(_is_valid_target_filter_test_impl)

def tidy_aspect_test_suite(name):
    unittest.suite(name, is_valid_target_filter_test)
