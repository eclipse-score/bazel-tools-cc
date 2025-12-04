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
This module tests the cc_helper module.
"""

load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts", "unittest")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("@score_bazel_tools_cc//quality/private/common:cc_helper.bzl", "cc_aspect_get_compiler_flags", "cc_aspect_is_c_source", "cc_aspect_is_cpp_source", "cc_aspect_is_header", "cc_aspect_is_source")

def _cc_aspect_is_cpp_source_test_impl(ctx):
    """Test the cc_aspect_is_cpp_source method with mocked files."""
    env = unittest.begin(ctx)

    mock_file = struct(extension = "cpp")
    asserts.equals(env, True, cc_aspect_is_cpp_source(mock_file))

    mock_file = struct(extension = "cc")
    asserts.equals(env, True, cc_aspect_is_cpp_source(mock_file))

    mock_file = struct(extension = "cxx")
    asserts.equals(env, True, cc_aspect_is_cpp_source(mock_file))

    mock_file = struct(extension = "c")
    asserts.equals(env, False, cc_aspect_is_cpp_source(mock_file))

    return unittest.end(env)

def _cc_aspect_is_header_test_impl(ctx):
    """Test the cc_aspect_is_header method with mocked files."""
    env = unittest.begin(ctx)

    mock_file = struct(extension = "h")
    asserts.equals(env, True, cc_aspect_is_header(mock_file))

    mock_file = struct(extension = "hpp")
    asserts.equals(env, True, cc_aspect_is_header(mock_file))

    mock_file = struct(extension = "hxx")
    asserts.equals(env, True, cc_aspect_is_header(mock_file))

    mock_file = struct(extension = "hh")
    asserts.equals(env, True, cc_aspect_is_header(mock_file))

    mock_file = struct(extension = "hcc")
    asserts.equals(env, False, cc_aspect_is_header(mock_file))

    return unittest.end(env)

def _cc_aspect_is_c_source_test_impl(ctx):
    """Test the cc_aspect_is_c_source method with mocked files."""
    env = unittest.begin(ctx)

    mock_file = struct(extension = "c")
    asserts.equals(env, True, cc_aspect_is_c_source(mock_file))

    mock_file = struct(extension = "cpp")
    asserts.equals(env, False, cc_aspect_is_c_source(mock_file))

    return unittest.end(env)

def _cc_aspect_is_source_test_impl(ctx):
    """Test the cc_aspect_is_source method with mocked files."""
    env = unittest.begin(ctx)

    mock_file = struct(extension = "c")
    asserts.equals(env, True, cc_aspect_is_source(mock_file))

    mock_file = struct(extension = "cpp")
    asserts.equals(env, True, cc_aspect_is_source(mock_file))

    mock_file = struct(extension = "py")
    asserts.equals(env, False, cc_aspect_is_source(mock_file))

    return unittest.end(env)

def _create_mock_file(ctx, filename, file_content):
    """Declare a mock file and return a depset of its file."""
    out = ctx.actions.declare_file(filename)
    ctx.actions.write(
        output = out,
        content = file_content,
    )
    return depset([out])

ImplementationDepsInfo = provider(
    doc = "Collection of implementation_deps.",
    fields = {
        "implementation_deps": "List of implementation_deps to use for testing.",
    },
)

def _cc_info_rule_impl(ctx):
    """Rule implementation that returns a known CcInfo provider."""
    _ignore = [ctx]  # @unused
    cc_info = CcInfo(
        compilation_context = cc_common.create_compilation_context(
            defines = depset(["FOO", "BAR"]),
            local_defines = depset(["BAZ"]),
            system_includes = depset(["/usr/include"]),
            quote_includes = depset(["/src/quote"]),
            framework_includes = depset(["/framework/include"]),
            includes = depset(["/src/include"]),
            headers = _create_mock_file(ctx, "header.hpp", "#include <string.h>"),
        ),
    )
    implementation_deps_info = ImplementationDepsInfo(
        implementation_deps = ctx.attr.implementation_deps,
    )
    return [cc_info, implementation_deps_info]

def _cc_info_rule_first_impl(ctx):
    """Rule implementation that returns a known CcInfo provider."""
    _ignore = [ctx]  # @unused
    cc_info = CcInfo(
        compilation_context = cc_common.create_compilation_context(
            defines = depset(["FOO_FIRST", "BAR_FIRST"]),
            local_defines = depset(["BAZ_FIRST"]),
            system_includes = depset(["/usr/include/first"]),
            quote_includes = depset(["/src/quote/first"]),
            framework_includes = depset(["/framework/include/first"]),
            includes = depset(["/src/include/first"]),
            headers = _create_mock_file(ctx, "first_header.hpp", "#include <string.h>"),
        ),
    )
    return [cc_info]

def _cc_info_rule_second_impl(ctx):
    """Rule implementation that returns a known CcInfo provider."""
    _ignore = [ctx]  # @unused
    cc_info = CcInfo(
        compilation_context = cc_common.create_compilation_context(
            defines = depset(["FOO_SECOND", "BAR_SECOND"]),
            local_defines = depset(["BAZ_SECOND"]),
            system_includes = depset(["/usr/include/second"]),
            quote_includes = depset(["/src/quote/second"]),
            framework_includes = depset(["/framework/include/second"]),
            includes = depset(["/src/include/second"]),
            headers = _create_mock_file(ctx, "second_header.hpp", "#include <string.h>"),
        ),
    )
    return [cc_info]

def _cc_info_rule_third_impl(ctx):
    """Rule implementation that returns a known CcInfo provider."""
    _ignore = [ctx]  # @unused
    cc_info = CcInfo(
        compilation_context = cc_common.create_compilation_context(
            defines = depset(["FOO_THIRD", "BAR_THIRD"]),
            local_defines = depset(["BAZ_THIRD"]),
            system_includes = depset(["/usr/include/third"]),
            quote_includes = depset(["/src/quote/third"]),
            framework_includes = depset(["/framework/include/third"]),
            includes = depset(["/src/include/third"]),
            headers = _create_mock_file(ctx, "third_header.hpp", "#include <string.h>"),
        ),
    )
    return [cc_info]

cc_info_rule = rule(
    implementation = _cc_info_rule_impl,
    attrs = {
        "implementation_deps": attr.label_list(),
    },
)
cc_info_rule_first = rule(implementation = _cc_info_rule_first_impl)
cc_info_rule_second = rule(implementation = _cc_info_rule_second_impl)
cc_info_rule_third = rule(implementation = _cc_info_rule_third_impl)

def _cc_aspect_get_compiler_flags_test_impl(ctx):
    """Test the cc_aspect_get_compiler_flags method with a mocked target that has CcInfo."""
    env = analysistest.begin(ctx)

    target_under_test = analysistest.target_under_test(env)

    expected_compiler_flags = [
        "-DFOO",
        "-DBAR",
        "-DBAZ",
        "-isystem/usr/include",
        "-iquote/src/quote",
        "-F/framework/include",
        "-I/src/include",
    ]

    mock_ctx = struct(rule = struct(kind = "cc_library", attr = struct(implementation_deps = [])))
    asserts.equals(env, expected_compiler_flags, cc_aspect_get_compiler_flags(mock_ctx, target_under_test))

    return analysistest.end(env)

def _cc_aspect_get_compiler_flags_for_target_having_implementation_deps_test_impl(ctx):
    """Test the cc_aspect_get_compiler_flags method with a mocked target that has CcInfo providers contained in its implementation_deps."""
    env = analysistest.begin(ctx)

    target_under_test = analysistest.target_under_test(env)

    expected_compiler_flags = [
        "-DFOO",
        "-DBAR",
        "-DBAZ",
        "-isystem/usr/include",
        "-iquote/src/quote",
        "-F/framework/include",
        "-I/src/include",
        "-DFOO_FIRST",
        "-DBAR_FIRST",
        "-isystem/usr/include/first",
        "-iquote/src/quote/first",
        "-F/framework/include/first",
        "-I/src/include/first",
        "-DFOO_SECOND",
        "-DBAR_SECOND",
        "-isystem/usr/include/second",
        "-iquote/src/quote/second",
        "-F/framework/include/second",
        "-I/src/include/second",
        "-DFOO_THIRD",
        "-DBAR_THIRD",
        "-isystem/usr/include/third",
        "-iquote/src/quote/third",
        "-F/framework/include/third",
        "-I/src/include/third",
    ]

    mock_ctx = struct(rule = struct(kind = "cc_library", attr = struct(implementation_deps = target_under_test[ImplementationDepsInfo].implementation_deps)))
    asserts.equals(env, expected_compiler_flags, cc_aspect_get_compiler_flags(mock_ctx, target_under_test))

    return analysistest.end(env)

def _empty_rule_impl(ctx):
    """Rule implementation that returns an empty provider list."""
    _ignore = [ctx]  # @unused
    return []

empty_rule = rule(
    implementation = _empty_rule_impl,
)

def _cc_aspect_get_compiler_flags_empty_test_impl(ctx):
    """Test the cc_aspect_get_compiler_flags method with target that has no CcInfo."""
    env = analysistest.begin(ctx)
    target_under_test = analysistest.target_under_test(env)

    expected_options_empty = []

    asserts.equals(env, expected_options_empty, cc_aspect_get_compiler_flags(ctx, target_under_test))

    return analysistest.end(env)

cc_aspect_get_compiler_flags_test = analysistest.make(
    _cc_aspect_get_compiler_flags_test_impl,
)

cc_aspect_get_compiler_flags_for_target_having_implementation_deps_test = analysistest.make(
    _cc_aspect_get_compiler_flags_for_target_having_implementation_deps_test_impl,
)

cc_aspect_get_compiler_flags_empty_test = analysistest.make(
    _cc_aspect_get_compiler_flags_empty_test_impl,
)

cc_aspect_is_cpp_source_test = unittest.make(_cc_aspect_is_cpp_source_test_impl)
cc_aspect_is_header_test = unittest.make(_cc_aspect_is_header_test_impl)
cc_aspect_is_c_source_test = unittest.make(_cc_aspect_is_c_source_test_impl)
cc_aspect_is_source_test = unittest.make(_cc_aspect_is_source_test_impl)

# buildifier: disable=unnamed-macro
def cc_helper_test_suite():
    """Creates the test targets and test suite for passing cc_helper.bzl tests."""
    unittest.suite(
        "cc_helper_unittest_suite",
        cc_aspect_is_cpp_source_test,
        cc_aspect_is_header_test,
        cc_aspect_is_c_source_test,
        cc_aspect_is_source_test,
    )

    cc_info_rule(name = "CcInfo_target")
    cc_aspect_get_compiler_flags_test(
        name = "cc_aspect_get_compiler_flags_test",
        target_under_test = ":CcInfo_target",
    )

    cc_info_rule_first(name = "first_dependency")
    cc_info_rule_second(name = "second_dependency")
    cc_info_rule_third(name = "third_dependency")
    cc_info_rule(
        name = "CcInfo_target_having_implementation_deps",
        implementation_deps = [":first_dependency", ":second_dependency", ":third_dependency"],
    )
    cc_aspect_get_compiler_flags_for_target_having_implementation_deps_test(
        name = "cc_aspect_get_compiler_flags_for_target_having_implementation_deps_test",
        target_under_test = ":CcInfo_target_having_implementation_deps",
    )

    empty_rule(name = "empty_target")
    cc_aspect_get_compiler_flags_empty_test(
        name = "cc_aspect_get_compiler_flags_empty_test",
        target_under_test = ":empty_target",
    )
