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

load("@bazel_skylib//rules:common_settings.bzl", "string_flag")
load("@rules_cc//cc:defs.bzl", "cc_import", "cc_library")
load("@score_bazel_tools_cc//quality:defs.bzl", "quality_clang_tidy_config")
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_suite.bzl",
    "tidy_suite",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy/test:custom_tidy_suites.bzl",
    "tidy_suite_using_tidy_config_with_deps",
    "tidy_suite_using_tidy_config_with_empty_dependency_attributes",
    "tidy_suite_using_tidy_config_with_enabled_features",
    "tidy_suite_using_tidy_config_with_exclude_cc_import",
    "tidy_suite_using_tidy_config_with_exclude_cc_import_including_deps",
    "tidy_suite_using_tidy_config_with_exclude_cc_library",
    "tidy_suite_using_tidy_config_with_forced_includes",
    "tidy_suite_using_tidy_config_with_header_filter_and_system_headers_matching_something",
    "tidy_suite_using_tidy_config_with_header_filter_matching_nothing",
    "tidy_suite_using_tidy_config_with_header_filter_matching_something",
    "tidy_suite_using_tidy_config_with_priority_includes",
    "tidy_suite_using_tidy_config_with_unknown_dependency_attributes",
    "tidy_suite_using_tidy_config_without_dependency_attributes",
)
load("@score_bazel_tools_cc//quality/private/clang_tidy/test:tidy_helper_test.bzl", "tidy_aspect_test_suite")
load("@score_bazel_tools_cc//quality/private/clang_tidy/test:tidy_suite_validation.bzl", "tidy_suite_test")

tidy_aspect_test_suite(name = "tidy_aspect_tests")

filegroup(
    name = "tidy_evaluator",
    srcs = ["tidy_evaluator.sh"],
)

##############################################
### cc_library definitions for later tests ###
##############################################

cc_library(
    name = "lib_summary",
    srcs = ["lib_summary.cpp"],
)

cc_library(
    name = "lib_no_finding",
    srcs = ["lib_no_finding.cpp"],
)

cc_library(
    name = "lib_one_finding",
    srcs = ["lib_one_finding.cpp"],
)

cc_library(
    name = "lib_one_finding1",
    srcs = ["lib_one_finding.cpp"],
)

cc_library(
    name = "lib_one_finding2",
    srcs = ["lib_one_finding.cpp"],
)

cc_library(
    name = "lib_one_finding3",
    srcs = ["lib_one_finding.cpp"],
)

cc_library(
    name = "lib_one_finding4",
    srcs = ["lib_one_finding.cpp"],
)

cc_library(
    name = "lib_one_finding5",
    srcs = ["lib_one_finding.cpp"],
)

cc_import(
    name = "lib_one_finding_in_data",
    data = [":lib_one_finding1"],
    features = ["recursive_clang_tidy"],
)

cc_library(
    name = "lib_one_finding_in_import",
    features = ["recursive_clang_tidy"],
    deps = [":lib_one_finding_in_data"],
)

cc_library(
    name = "lib_one_finding_in_header1",
    srcs = [
        "lib_one_finding_via_included_header.cpp",
    ],
    deps = [
        "//quality/private/clang_tidy/test/base_includes:cpp_headers",
    ],
)

cc_library(
    name = "lib_one_finding_in_header2",
    srcs = [
        "lib_one_finding_via_included_header.cpp",
    ],
    deps = [
        "//quality/private/clang_tidy/test/base_includes:cpp_headers",
    ],
)

cc_library(
    name = "lib_one_finding_in_system_header",
    srcs = [
        "lib_one_finding_via_system_header.cpp",
    ],
    includes = ["base_includes"],
    deps = [
        "//quality/private/clang_tidy/test/base_includes:cpp_system_headers",
    ],
)

alias(
    name = "lib_single_header_only",
    actual = "//quality/private/clang_tidy/test/base_includes:cpp_headers",
)

cc_library(
    name = "lib_special_finding_in_header_within_ifdef",
    defines = ["ENABLE_SPECIAL_CLANG_TIDY_FINDING_IN_HEADER"],
    deps = [
        "//quality/private/clang_tidy/test/base_includes:cpp_headers",
    ],
)

cc_library(
    name = "lib_special_finding_within_ifdef_of_header_implementation_deps",
    srcs = ["lib_one_finding_via_included_header.cpp"],
    implementation_deps = [":lib_special_finding_in_header_within_ifdef"],
    tags = ["manual"],
)

cc_library(
    name = "lib_one_finding_in_header_implementation_deps",
    srcs = ["lib_one_finding_via_included_header.cpp"],
    implementation_deps = [":lib_single_header_only"],
    tags = ["manual"],
)

cc_library(
    name = "lib_special_finding_within_ifdef_of_header_deps",
    srcs = ["lib_one_finding_via_included_header.cpp"],
    deps = [":lib_special_finding_in_header_within_ifdef"],
)

cc_library(
    name = "lib_one_finding_in_header_deps",
    srcs = ["lib_one_finding_via_included_header.cpp"],
    deps = [":lib_single_header_only"],
)

cc_library(
    name = "lib_one_finding_in_deps",
    features = ["recursive_clang_tidy"],
    deps = [":lib_one_finding2"],
)

cc_library(
    name = "lib_one_finding_in_implementation_deps",
    features = ["recursive_clang_tidy"],
    implementation_deps = [":lib_one_finding3"],
    tags = ["manual"],
)

cc_library(
    name = "lib_no_findings_due_to_no_deps",
    features = ["recursive_clang_tidy"],
)

cc_library(
    name = "lib_no_findings_due_to_unknown_deps_in_clang_tidy_config",
    features = ["recursive_clang_tidy"],
    deps = [":lib_one_finding4"],
)

cc_library(
    name = "lib_no_findings_due_to_missing_recursive_clang_tidy_feature",
    deps = [":lib_one_finding5"],
)

cc_library(
    name = "lib_one_finding_due_to_enabled_features_in_clang_tidy_config",
    srcs = ["lib_one_finding.cpp"],
)

cc_library(
    name = "lib_one_finding_within_cpp_priority_include",
    srcs = ["lib_one_finding_via_included_header.cpp"],
    deps = ["//quality/private/clang_tidy/test/base_includes:cpp_headers"],
)

cc_library(
    name = "lib_one_finding_within_c_priority_include",
    srcs = ["lib_one_finding_via_included_header.c"],
    deps = ["//quality/private/clang_tidy/test/base_includes:c_headers"],
)

cc_library(
    name = "lib_one_finding_within_cpp_forced_include",
    srcs = ["lib_no_finding.cpp"],
)

cc_library(
    name = "lib_one_finding_within_c_forced_include",
    srcs = ["lib_no_finding.c"],
)

cc_library(
    name = "lib_one_finding_via_conditional_include",
    srcs = ["lib_one_finding_via_conditional_include.cpp"],
)

##############################################
### tidy suite definitions for later tests ###
##############################################

tidy_suite(
    name = "tidy_summary",
    checks = ["bugprone-*"],
    summary = False,
    deps = [":lib_summary"],
)

tidy_suite(
    name = "tidy_no_finding",
    checks = ["*,-llvmlibc-*"],
    summary = False,
    deps = [":lib_no_finding"],
)

tidy_suite(
    name = "tidy_one_finding",
    checks = ["bugprone-*"],
    summary = False,
    deps = [":lib_one_finding"],
)

tidy_suite_using_tidy_config_without_dependency_attributes(
    name = "tidy_one_finding_in_header_deps",
    summary = False,
    deps = [":lib_one_finding_in_header_deps"],
)

tidy_suite_using_tidy_config_without_dependency_attributes(
    name = "tidy_special_finding_within_ifdef_of_header_deps",
    summary = False,
    deps = [":lib_special_finding_within_ifdef_of_header_deps"],
)

tidy_suite_using_tidy_config_without_dependency_attributes(
    name = "tidy_one_finding_in_header_implementation_deps",
    summary = False,
    tags = ["manual"],
    deps = [":lib_one_finding_in_header_implementation_deps"],
)

tidy_suite_using_tidy_config_without_dependency_attributes(
    name = "tidy_special_finding_within_ifdef_of_header_implementation_deps",
    summary = False,
    tags = ["manual"],
    deps = [":lib_special_finding_within_ifdef_of_header_implementation_deps"],
)

tidy_suite_using_tidy_config_without_dependency_attributes(
    name = "tidy_one_finding_in_data_due_to_autodetected_dependency_attributes",
    summary = False,
    deps = [":lib_one_finding_in_data"],
)

tidy_suite_using_tidy_config_without_dependency_attributes(
    name = "tidy_one_finding_in_deps_due_to_autodetected_dependency_attributes",
    summary = False,
    deps = [":lib_one_finding_in_deps"],
)

tidy_suite_using_tidy_config_without_dependency_attributes(
    name = "tidy_one_finding_in_implementation_deps_due_to_autodetected_dependency_attributes",
    summary = False,
    tags = ["manual"],
    deps = [":lib_one_finding_in_implementation_deps"],
)

tidy_suite_using_tidy_config_with_empty_dependency_attributes(
    name = "tidy_no_finding_in_data_due_to_empty_dependency_attributes",
    summary = True,
    deps = [":lib_one_finding_in_data"],
)

tidy_suite_using_tidy_config_with_empty_dependency_attributes(
    name = "tidy_no_finding_in_deps_due_to_empty_dependency_attributes",
    summary = True,
    deps = [":lib_one_finding_in_deps"],
)

tidy_suite_using_tidy_config_with_empty_dependency_attributes(
    name = "tidy_no_finding_in_implementation_deps_due_to_empty_dependency_attributes",
    summary = True,
    tags = ["manual"],
    deps = [":lib_one_finding_in_implementation_deps"],
)

tidy_suite_using_tidy_config_with_unknown_dependency_attributes(
    name = "tidy_no_findings_due_to_no_deps_in_cc_library",
    summary = True,
    deps = [":lib_no_findings_due_to_no_deps"],
)

tidy_suite_using_tidy_config_with_unknown_dependency_attributes(
    name = "tidy_no_findings_due_to_dependency_attributes_not_present",
    summary = True,
    deps = [":lib_no_findings_due_to_unknown_deps_in_clang_tidy_config"],
)

tidy_suite_using_tidy_config_with_unknown_dependency_attributes(
    name = "tidy_no_findings_due_to_missing_recursive_clang_tidy_feature",
    summary = True,
    deps = [":lib_no_findings_due_to_missing_recursive_clang_tidy_feature"],
)

tidy_suite_using_tidy_config_with_forced_includes(
    name = "tidy_one_finding_within_c_forced_include",
    summary = False,
    deps = [":lib_one_finding_within_c_forced_include"],
)

tidy_suite_using_tidy_config_with_forced_includes(
    name = "tidy_one_finding_within_cpp_forced_include",
    summary = False,
    deps = [":lib_one_finding_within_cpp_forced_include"],
)

tidy_suite_using_tidy_config_with_priority_includes(
    name = "tidy_one_finding_within_c_priority_include",
    summary = False,
    deps = [":lib_one_finding_within_c_priority_include"],
)

tidy_suite_using_tidy_config_with_priority_includes(
    name = "tidy_one_finding_within_cpp_priority_include",
    summary = False,
    deps = [":lib_one_finding_within_cpp_priority_include"],
)

tidy_suite_using_tidy_config_with_deps(
    name = "tidy_one_finding_via_conditional_include",
    summary = False,
    deps = [":lib_one_finding_via_conditional_include"],
)

tidy_suite_using_tidy_config_with_enabled_features(
    name = "tidy_one_finding_due_to_enabled_features_in_clang_tidy_config",
    summary = False,
    deps = [":lib_one_finding_due_to_enabled_features_in_clang_tidy_config"],
)

tidy_suite_using_tidy_config_with_exclude_cc_library(
    name = "tidy_no_finding_in_deps_due_to_excluded_cc_library",
    summary = True,
    deps = [":lib_one_finding_in_data"],
)

tidy_suite_using_tidy_config_with_exclude_cc_import(
    name = "tidy_one_finding_in_deps_due_to_excluded_cc_import_but_not_its_deps",
    summary = False,
    deps = [":lib_one_finding_in_import"],
)

tidy_suite_using_tidy_config_with_exclude_cc_import_including_deps(
    name = "tidy_no_finding_in_deps_due_to_excluded_cc_import_including_its_deps",
    summary = True,
    deps = [":lib_one_finding_in_import"],
)

tidy_suite_using_tidy_config_with_header_filter_matching_nothing(
    name = "tidy_no_finding_in_header_due_to_header_filter_matching_nothing",
    summary = False,
    deps = [":lib_one_finding_in_header1"],
)

tidy_suite_using_tidy_config_with_header_filter_matching_something(
    name = "tidy_one_finding_in_header_due_to_header_filter_matching_something",
    summary = False,
    deps = [":lib_one_finding_in_header2"],
)

tidy_suite_using_tidy_config_with_header_filter_and_system_headers_matching_something(
    name = "tidy_one_finding_in_header_due_to_header_filter_and_system_headers_matching_something",
    summary = False,
    deps = [":lib_one_finding_in_system_header"],
)

####################
### actual tests ###
####################

tidy_suite_test(
    name = "tidy_summary_test",
    expected = [
        "No fix(es) required or possible",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_summary",
)

tidy_suite_test(
    name = "tidy_no_findings_test",
    expected = [
        "No fix(es) required or possible",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_finding",
)

tidy_suite_test(
    name = "tidy_one_finding_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''call'' in comment does not match parameter name ''lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding",
)

tidy_suite_test(
    name = "tidy_no_finding_in_data_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_finding_in_data_due_to_empty_dependency_attributes",
)

tidy_suite_test(
    name = "tidy_no_finding_in_deps_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_finding_in_deps_due_to_empty_dependency_attributes",
)

tidy_suite_test(
    name = "tidy_no_finding_in_implementation_deps_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = [
        "manual",
        "tidy_suite",
    ],
    target = ":tidy_no_finding_in_implementation_deps_due_to_empty_dependency_attributes",
)

tidy_suite_test(
    name = "tidy_one_finding_in_data_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''call'' in comment does not match parameter name ''lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_in_data_due_to_autodetected_dependency_attributes",
)

tidy_suite_test(
    name = "tidy_one_finding_in_deps_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''call'' in comment does not match parameter name ''lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_in_deps_due_to_autodetected_dependency_attributes",
)

tidy_suite_test(
    name = "tidy_one_finding_in_implementation_deps_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''call'' in comment does not match parameter name ''lib'''",
    ],
    tags = [
        "manual",
        "tidy_suite",
    ],
    target = ":tidy_one_finding_in_implementation_deps_due_to_autodetected_dependency_attributes",
)

tidy_suite_test(
    name = "tidy_special_finding_within_ifdef_of_header_implementation_deps_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''special_call'' in comment does not match parameter name ''special_lib'''",
    ],
    tags = [
        "manual",
        "tidy_suite",
    ],
    target = ":tidy_special_finding_within_ifdef_of_header_implementation_deps",
)

tidy_suite_test(
    name = "tidy_one_finding_in_header_implementation_deps_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''cpp_call'' in comment does not match parameter name ''cpp_lib'''",
    ],
    tags = [
        "manual",
        "tidy_suite",
    ],
    target = ":tidy_one_finding_in_header_implementation_deps",
)

tidy_suite_test(
    name = "tidy_special_finding_within_ifdef_of_header_deps_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''special_call'' in comment does not match parameter name ''special_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_special_finding_within_ifdef_of_header_deps",
)

tidy_suite_test(
    name = "tidy_one_finding_in_header_deps_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''cpp_call'' in comment does not match parameter name ''cpp_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_in_header_deps",
)

tidy_suite_test(
    name = "tidy_no_findings_due_to_no_deps_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_findings_due_to_no_deps_in_cc_library",
)

tidy_suite_test(
    name = "tidy_no_findings_due_to_dependency_attributes_not_present_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_findings_due_to_dependency_attributes_not_present",
)

tidy_suite_test(
    name = "tidy_no_findings_due_to_missing_recursive_clang_tidy_feature_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_findings_due_to_missing_recursive_clang_tidy_feature",
)

tidy_suite_test(
    name = "tidy_one_finding_within_c_forced_include_test",
    expected = [
        "forced_include_functions.h",
        "bugprone-argument-comment",
        "'argument name ''c_call'' in comment does not match parameter name ''c_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_within_c_forced_include",
)

tidy_suite_test(
    name = "tidy_one_finding_within_cpp_forced_include_test",
    expected = [
        "forced_include_functions.hpp",
        "bugprone-argument-comment",
        "'argument name ''cpp_call'' in comment does not match parameter name ''cpp_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_within_cpp_forced_include",
)

tidy_suite_test(
    name = "tidy_one_finding_within_c_priority_include_test",
    expected = [
        "header_file_with_one_finding.h",
        "bugprone-argument-comment",
        "'argument name ''priority_c_call'' in comment does not match parameter name ''priority_c_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_within_c_priority_include",
)

tidy_suite_test(
    name = "tidy_one_finding_within_cpp_priority_include_test",
    expected = [
        "header_file_with_one_finding.hpp",
        "bugprone-argument-comment",
        "'argument name ''priority_cpp_call'' in comment does not match parameter name ''priority_cpp_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_within_cpp_priority_include",
)

tidy_suite_test(
    name = "tidy_one_finding_via_conditional_include_test",
    expected = [
        "header_file_with_one_finding.hpp",
        "bugprone-argument-comment",
        "'argument name ''cpp_call'' in comment does not match parameter name ''cpp_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_via_conditional_include",
)

tidy_suite_test(
    name = "tidy_one_finding_due_to_enabled_features_in_clang_tidy_config_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''call'' in comment does not match parameter name ''lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_due_to_enabled_features_in_clang_tidy_config",
)

tidy_suite_test(
    name = "tidy_no_finding_in_deps_due_to_excluded_cc_library_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_finding_in_deps_due_to_excluded_cc_library",
)

tidy_suite_test(
    name = "tidy_one_finding_in_deps_due_to_excluded_cc_import_but_not_its_deps_test",
    expected = [
        "bugprone-argument-comment",
        "'argument name ''call'' in comment does not match parameter name ''lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_in_deps_due_to_excluded_cc_import_but_not_its_deps",
)

tidy_suite_test(
    name = "tidy_no_finding_in_deps_due_to_excluded_cc_import_including_its_deps_test",
    expected = [
        "No outputs have been generated for any target",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_finding_in_deps_due_to_excluded_cc_import_including_its_deps",
)

tidy_suite_test(
    name = "tidy_no_finding_in_header_due_to_header_filter_matching_nothing_test",
    expected = [
        "No fix(es) required or possible",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_no_finding_in_header_due_to_header_filter_matching_nothing",
)

tidy_suite_test(
    name = "tidy_one_finding_in_header_due_to_header_filter_matching_something_test",
    expected = [
        "header_file_with_one_finding.hpp",
        "bugprone-argument-comment",
        "'argument name ''cpp_call'' in comment does not match parameter name ''cpp_lib'''",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_in_header_due_to_header_filter_matching_something",
)

tidy_suite_test(
    name = "tidy_one_finding_in_header_due_to_header_filter_and_system_headers_matching_something_test",
    expected = [
        "header_file_with_one_finding.hpp",
        "llvmlibc-callee-namespace",
        "'''Lib'' must resolve to a function declared within the ''__llvm_libc'' namespace'",
    ],
    tags = ["tidy_suite"],
    target = ":tidy_one_finding_in_header_due_to_header_filter_and_system_headers_matching_something",
)

###############################################
### clang tidy configs used for tests above ###
###############################################

quality_clang_tidy_config(
    name = "clang_tidy_config_without_dependency_attributes",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_empty_dependency_attributes",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    dependency_attributes = [],
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_unknown_dependency_attributes",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    dependency_attributes = ["foo_bar"],
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_forced_includes",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    clang_tidy_forced_includes = "//quality/private/clang_tidy/test/forced_includes",
    default_feature = "bugprone_checks",
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_priority_includes",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    clang_tidy_priority_includes = "//quality/private/clang_tidy/test/priority_includes",
    default_feature = "bugprone_checks",
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_deps",
    additional_flags = ["-DHEADER_FILE_INHERITED_VIA_CLANG_TIDY_CONFIG_DEPS"],
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
    deps = [
        "//quality/private/clang_tidy/test/base_includes:header_file_with_one_finding.hpp",
    ],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_enabled_features",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
        ".clang-tidy-no-checks": "no_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_exclude_cc_import",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    exclude_types = [
        "cc_import",
    ],
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_exclude_cc_library",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    exclude_types = [
        "cc_library",
    ],
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_exclude_cc_import_including_deps",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    exclude_types_including_deps = [
        "cc_import",
    ],
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    visibility = ["//visibility:public"],
)

string_flag(
    name = "invalid_header_filter",
    build_setting_default = "some/filter/that/matches/none/of/the/headers/here",
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_header_filter_matching_nothing",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    header_filter = ":invalid_header_filter",
    visibility = ["//visibility:public"],
)

string_flag(
    name = "valid_header_filter",
    build_setting_default = "clang_tidy/test/",
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_header_filter_matching_something",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "bugprone_checks",
    feature_mapping = {
        ".clang-tidy-bugprone-checks": "bugprone_checks",
    },
    header_filter = ":valid_header_filter",
    visibility = ["//visibility:public"],
)

string_flag(
    name = "all_header_filter",
    build_setting_default = ".*",
)

quality_clang_tidy_config(
    name = "clang_tidy_config_with_header_filter_and_system_headers_matching_something",
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "all_checks",
    excludes = [],
    feature_mapping = {
        ".clang-tidy-all-checks": "all_checks",
    },
    header_filter = ":all_header_filter",
    system_headers = True,
    visibility = ["//visibility:public"],
)
