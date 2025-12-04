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
This module implements the tidy configuration.
"""

load("@bazel_skylib//lib:paths.bzl", "paths")
load("@bazel_skylib//rules:common_settings.bzl", "BuildSettingInfo")
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_providers.bzl",
    "ClangTidyConfigInfo",
    "ClangTidyForcedIncludesInfo",
    "ClangTidyIncludeDirectoryInfo",
    "ClangTidyPriorityIncludesInfo",
)

def _quality_clang_tidy_config_impl(ctx):
    return [
        ClangTidyConfigInfo(
            additional_flags = ctx.attr.additional_flags,
            autodetermine_builtin_include_directories = ctx.attr.autodetermine_builtin_include_directories,
            clang_tidy_binary = ctx.attr.clang_tidy_binary,
            clang_tidy_enable_features = ctx.attr.clang_tidy_enable_features,
            clang_tidy_files = ctx.attr.clang_tidy_files,
            clang_tidy_forced_includes = ctx.attr.clang_tidy_forced_includes,
            clang_tidy_priority_includes = ctx.attr.clang_tidy_priority_includes,
            default_feature = ctx.attr.default_feature,
            dependency_attributes = ctx.attr.dependency_attributes,
            deps = ctx.attr.deps,
            exclude_types = ctx.attr.exclude_types,
            exclude_types_including_deps = ctx.attr.exclude_types_including_deps,
            excludes = ctx.attr.excludes,
            excludes_override = ctx.attr.excludes_override,
            feature_mapping = ctx.attr.feature_mapping,
            feature_mapping_c = ctx.attr.feature_mapping_c,
            feature_mapping_cpp = ctx.attr.feature_mapping_cpp,
            header_filter = ctx.attr.header_filter,
            suppress_patterns = ctx.attr.suppress_patterns,
            system_headers = ctx.attr.system_headers,
            target_types = ctx.attr.target_types,
            unsupported_flags = ctx.attr.unsupported_flags,
        ),
    ]

quality_clang_tidy_config = rule(
    implementation = _quality_clang_tidy_config_impl,
    attrs = {
        "additional_flags": attr.string_list(default = []),
        "autodetermine_builtin_include_directories": attr.bool(default = False, mandatory = False),
        "clang_tidy_binary": attr.label(cfg = "exec", mandatory = True),
        "clang_tidy_enable_features": attr.string_list(
            default = [],
        ),
        "clang_tidy_files": attr.label(
            cfg = "exec",
            mandatory = False,
            default = "//quality/private/clang_tidy/support:clang_tidy_files",
        ),
        "clang_tidy_forced_includes": attr.label(
            cfg = "target",
            providers = [ClangTidyForcedIncludesInfo],
        ),
        "clang_tidy_priority_includes": attr.label(
            cfg = "target",
            providers = [ClangTidyPriorityIncludesInfo],
        ),
        "default_feature": attr.string(mandatory = True),
        "dependency_attributes": attr.string_list(
            mandatory = False,
            default = ["<NONE>"],
            allow_empty = True,
        ),
        "deps": attr.label_list(
            cfg = "target",
            mandatory = False,
            allow_files = True,
        ),
        "exclude_types": attr.string_list(
            default = [],
            allow_empty = True,
        ),
        "exclude_types_including_deps": attr.string_list(
            default = [],
            allow_empty = True,
        ),
        "excludes": attr.string_list(default = []),
        "excludes_override": attr.string_list(default = []),
        "feature_mapping": attr.label_keyed_string_dict(
            mandatory = True,
            default = {},
            allow_files = True,
        ),
        "feature_mapping_c": attr.label_keyed_string_dict(
            default = {},
            allow_files = True,
        ),
        "feature_mapping_cpp": attr.label_keyed_string_dict(
            default = {},
            allow_files = True,
        ),
        "header_filter": attr.label(
            mandatory = False,
            providers = [BuildSettingInfo],
        ),
        "suppress_patterns": attr.string_list(default = []),
        "system_headers": attr.bool(
            default = False,
            doc = "Display the errors from system headers.",
        ),
        "target_types": attr.string_list(
            mandatory = False,
            default = ["<NONE>"],
            allow_empty = True,
        ),
        "unsupported_flags": attr.string_list(default = []),
    },
)

_C_HEADER_ENDINGS = [".h", ".hh", ".inc"]
_CPP_HEADER_ENDINGS = _C_HEADER_ENDINGS + [".h++", ".hpp", ".hxx"]

def _quality_clang_tidy_forced_includes_config_impl(ctx):
    return [
        ClangTidyForcedIncludesInfo(
            c_compile = ctx.attr.c_compile,
            cpp_compile = ctx.attr.cpp_compile,
        ),
    ]

quality_clang_tidy_forced_includes_config = rule(
    implementation = _quality_clang_tidy_forced_includes_config_impl,
    attrs = {
        "c_compile": attr.label_list(
            cfg = "target",
            mandatory = True,
            allow_empty = True,
            allow_files = _C_HEADER_ENDINGS,
        ),
        "cpp_compile": attr.label_list(
            cfg = "target",
            mandatory = True,
            allow_empty = True,
            allow_files = _CPP_HEADER_ENDINGS,
        ),
    },
)

def _quality_clang_tidy_priority_includes_config_impl(ctx):
    return [
        ClangTidyPriorityIncludesInfo(
            c_compile = ctx.attr.c_compile,
            cpp_compile = ctx.attr.cpp_compile,
        ),
    ]

quality_clang_tidy_priority_includes_config = rule(
    implementation = _quality_clang_tidy_priority_includes_config_impl,
    attrs = {
        "c_compile": attr.label_list(
            mandatory = True,
            allow_empty = True,
            providers = [ClangTidyIncludeDirectoryInfo],
        ),
        "cpp_compile": attr.label_list(
            mandatory = True,
            allow_empty = True,
            providers = [ClangTidyIncludeDirectoryInfo],
        ),
    },
)

def _quality_clang_tidy_include_files_config_impl(ctx):
    selected_input_files = ctx.files.source_files

    if ctx.attr.select_files:
        selected_input_files = []
        for select_file in ctx.attr.select_files:
            file_found = False
            for input_file in ctx.files.source_files:
                if input_file.path.endswith(paths.join(ctx.attr.select_directory, select_file)):
                    if file_found:
                        fail(
                            "Selecting file from `source_files` of //{}:{} failed.".format(ctx.label.package, ctx.label.name),
                            "Requested file selection '{}' resulted in multiple matches in `source_files`: {} vs. {}.".format(paths.join(ctx.attr.select_directory, select_file), selected_input_files[-1].path, input_file.path),
                        )
                    selected_input_files.append(input_file)
                    file_found = True
            if not file_found:
                fail(
                    "Selecting file from `source_files` of //{}:{} failed.".format(ctx.label.package, ctx.label.name),
                    "Requested file selection '{}' did not match anything in `source_files`.".format(paths.join(ctx.attr.select_directory, select_file)),
                )

    # within same directory, create a symlink for each of the selected include files
    include_files = []
    for input_file in selected_input_files:
        include_file = ctx.actions.declare_file(paths.join(ctx.attr.include_prefix, input_file.basename))
        ctx.actions.symlink(output = include_file, target_file = input_file)
        include_files.append(include_file)

    # determine the include path to be used as compiler argument for finding such include files
    directory_path = include_files[0].dirname  # since all include_files reside in the same directory (cf. symlink creation above)
    if directory_path.endswith(ctx.attr.include_prefix):
        # remove the user-provided include_prefix from the include path since otherwise the include files
        # won't get found by the compiler (example: `#include "<include_prefix>/header.h"`)
        # see also clang_tidy/test/priority_includes/BUILD and corresponding tests
        include_path = directory_path.removesuffix(ctx.attr.include_prefix)
    else:
        include_path = directory_path

    return [
        DefaultInfo(
            files = depset(include_files),
        ),
        ClangTidyIncludeDirectoryInfo(
            path = include_path,
        ),
    ]

quality_clang_tidy_include_files_config = rule(
    implementation = _quality_clang_tidy_include_files_config_impl,
    attrs = {
        "include_prefix": attr.string(mandatory = False, default = ""),
        "select_directory": attr.string(mandatory = False, default = ""),
        "select_files": attr.string_list(mandatory = False, allow_empty = False),
        "source_files": attr.label_list(
            mandatory = True,
            allow_empty = False,
            allow_files = _CPP_HEADER_ENDINGS,
        ),
    },
)
