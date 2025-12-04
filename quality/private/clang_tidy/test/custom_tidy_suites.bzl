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
This module is the main implementation of tidy_aspects to be tested together with tidy_configs.
"""

load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_aspect.bzl",
    "quality_clang_tidy_aspect_factory",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_suite.bzl",
    "tidy_suite_rule_impl",
)

# Tidy-aspect using a predefined clang_tidy_config which does not have any dependency_attributes provided
tidy_aspect_for_tidy_config_test_without_dependency_attributes = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_without_dependency_attributes",
)
tidy_suite_using_tidy_config_without_dependency_attributes = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_test_without_dependency_attributes],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config whose attribute dependency_attributes is empty
tidy_aspect_for_tidy_config_test_with_empty_dependency_attributes = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_empty_dependency_attributes",
)
tidy_suite_using_tidy_config_with_empty_dependency_attributes = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_test_with_empty_dependency_attributes],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config whose attribute dependency_attributes contains an unknown value
tidy_aspect_for_tidy_config_test_with_unknown_dependency_attributes = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_unknown_dependency_attributes",
)
tidy_suite_using_tidy_config_with_unknown_dependency_attributes = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_test_with_unknown_dependency_attributes],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute `priority_includes` assigned
tidy_aspect_for_tidy_config_test_with_priority_includes = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_priority_includes",
)
tidy_suite_using_tidy_config_with_priority_includes = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_test_with_priority_includes],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute `forced_includes` assigned
tidy_aspect_for_tidy_config_test_with_forced_includes = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_forced_includes",
)
tidy_suite_using_tidy_config_with_forced_includes = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_test_with_forced_includes],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute deps assigned
tidy_aspect_for_tidy_config_test_with_deps = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_deps",
)
tidy_suite_using_tidy_config_with_deps = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_test_with_deps],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute clang_tidy_enable_features assigned
tidy_aspect_for_tidy_config_test_with_enabled_features = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_enabled_features",
)
tidy_suite_using_tidy_config_with_enabled_features = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_test_with_enabled_features],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute exclude_types set to 'cc_import'
tidy_aspect_for_tidy_config_with_exclude_cc_import = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_exclude_cc_import",
)
tidy_suite_using_tidy_config_with_exclude_cc_import = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_with_exclude_cc_import],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute exclude_types set to 'cc_library'
tidy_aspect_for_tidy_config_with_exclude_cc_library = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_exclude_cc_library",
)
tidy_suite_using_tidy_config_with_exclude_cc_library = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_with_exclude_cc_library],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute exclude_types_including_deps set to 'cc_import'
tidy_aspect_for_tidy_config_with_exclude_cc_import_including_deps = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_exclude_cc_import_including_deps",
)
tidy_suite_using_tidy_config_with_exclude_cc_import_including_deps = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_with_exclude_cc_import_including_deps],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute header_filter set to an invalid value
tidy_aspect_for_tidy_config_with_header_filer_matching_nothing = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_header_filter_matching_nothing",
)
tidy_suite_using_tidy_config_with_header_filter_matching_nothing = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_with_header_filer_matching_nothing],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute header_filter set to a valid value
tidy_aspect_for_tidy_config_with_header_filer_matching_something = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_header_filter_matching_something",
)
tidy_suite_using_tidy_config_with_header_filter_matching_something = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_with_header_filer_matching_something],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)

# Tidy-aspect using a predefined clang_tidy_config which has the attribute header_filter set to a valid value and system_headers set to true
tidy_aspect_for_tidy_config_with_header_filer_and_system_headers_matching_something = quality_clang_tidy_aspect_factory(
    tidy_config = "//quality/private/clang_tidy/test:clang_tidy_config_with_header_filter_and_system_headers_matching_something",
)
tidy_suite_using_tidy_config_with_header_filter_and_system_headers_matching_something = rule(
    attrs = {
        "deps": attr.label_list(
            aspects = [tidy_aspect_for_tidy_config_with_header_filer_and_system_headers_matching_something],
        ),
        "summary": attr.bool(mandatory = True),
    },
    implementation = tidy_suite_rule_impl,
)
