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
This module tests the tidy_aspect module.
"""

load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("@score_bazel_tools_cc//quality/private/clang_tidy:tidy_helper.bzl", "determine_module_type", "get_fixes_filename")

def _determine_module_type_test_impl(ctx):
    env = unittest.begin(ctx)

    mock_ctx = struct(rule = struct(kind = "cc_library", attr = struct(linkstatic = True)))
    asserts.equals(env, "static_library", determine_module_type(mock_ctx))

    mock_ctx = struct(rule = struct(kind = "cc_library", attr = struct(linkstatic = False)))
    asserts.equals(env, "dynamic_library", determine_module_type(mock_ctx))

    mock_ctx = struct(rule = struct(kind = "cc_binary", attr = struct(linkshared = True)))
    asserts.equals(env, "dynamic_library", determine_module_type(mock_ctx))

    mock_ctx = struct(rule = struct(kind = "cc_binary", attr = struct(linkshared = False)))
    asserts.equals(env, "executable", determine_module_type(mock_ctx))

    mock_ctx = struct(rule = struct(kind = "cc_test"))
    asserts.equals(env, "executable", determine_module_type(mock_ctx))

    return unittest.end(env)

def _is_correct_filename_returned_test_impl(ctx):
    env = unittest.begin(ctx)
    max_length = 30
    long_filename = "bazel_teeeeeesssssssssttt_output_cpp.fixes.yaml"
    expected_filename = "bazel_te_<shortend>_fixes.yaml"

    # test reducing the string length
    asserts.equals(env, expected_filename, get_fixes_filename(long_filename, max_length, 10))
    asserts.equals(env, max_length, len(get_fixes_filename(long_filename, max_length, 10)))

    # increase max length and check if the string stays the same
    max_length = 200
    asserts.equals(env, long_filename, get_fixes_filename(long_filename, max_length, 10))

    # verify the default value of max_length when being applied to very long filenames exceeding get_fixes_filename's max_length
    long_filename = "a_very_long_filename_which_exceeds_the_default_threshold_of_max_length_as_defined_for_the_helper_method_get_fixes_filename."

    # a default max_length of 250 is expected here since appending the suffix ".tmp" must always be possible
    # this is required for the filename plus the suffix ".tmp" to not exceed the OS' threshold of 254
    asserts.equals(env, 215, len(get_fixes_filename(long_filename + long_filename + "fixes.yaml")))

    return unittest.end(env)

determine_module_type_test = unittest.make(_determine_module_type_test_impl)
is_correct_filename_returned_test = unittest.make(_is_correct_filename_returned_test_impl)

def tidy_aspect_test_suite(name):
    unittest.suite(
        name,
        determine_module_type_test,
        is_correct_filename_returned_test,
    )
