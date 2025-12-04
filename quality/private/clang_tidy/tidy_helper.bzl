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
A collection of helper functions for the tidy aspect.
"""

load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("@score_bazel_tools_cc//quality/private/clang_tidy:tidy_providers.bzl", "ClangTidyConfigInfo")
load(
    "@score_bazel_tools_cc//quality/private/common:cc_helper.bzl",
    "cc_aspect_get_compilation_contexts_of_implementation_deps",
    "cc_aspect_get_files",
    "cc_aspect_is_header",
    "cc_aspect_is_source",
)
load("@score_bazel_tools_cc//quality/private/common:common.bzl", "is_feature_active")

def determine_module_type(ctx):
    """Determines the module types taking some properties into account.

    Args:
        ctx: Context.
    Returns:
        Any of static_library, dynamic_library or executable.
    """
    if ctx.rule.kind == "cc_library":
        if ctx.rule.attr.linkstatic:
            return "static_library"
        else:
            return "dynamic_library"
    if ctx.rule.kind == "cc_binary":
        if ctx.rule.attr.linkshared:
            return "dynamic_library"
        else:
            return "executable"
    if ctx.rule.kind == "cc_test":
        return "executable"
    return None

def get_fixes_filename(filename, max_length = 215, suffix_length = 150):
    """Returns the filename of the fixes files. Reduces the filename length if it exceeds 215 characters.\
       Bazel appends a prefix at the end of the yaml. e.g. -0.params.sandbox18.virtualinputlock. To not exceed \
       the 255 limit threshold, a max_length of 215 is set


    Args:
        filename: filename of the fixes file
        max_length: set the overall max length of the filename
        suffix_length: length of the string when reading from right to left
    Returns:
        A splitted filename if necessary
    """
    new_filename = filename
    redacted_string = "_<shortend>_"
    if len(new_filename) > max_length:
        max_prefix_length = max_length - len(redacted_string) - suffix_length
        new_filename = filename[:max_prefix_length] + redacted_string + filename[-suffix_length:]

    return new_filename

def tidy_get_src_files(ctx, target):
    """Get source files from the target actions if the tidy feature is active.

    Args:
        ctx: Context
        target: The analyzed target
    Returns:
        Source file list from the target actions
    """
    files = []
    extra_features = tidy_get_enabled_features(ctx)
    if is_feature_active(ctx, "use_action_inputs_for_sources", extra_features):
        relevant_actions = [action for action in target.actions if action.mnemonic in ["CcCompile", "CppCompile"]]
        files = [
            src
            for action in relevant_actions
            for src in action.inputs.to_list()
            if cc_aspect_is_source(src) or cc_aspect_is_header(src)
        ]

    return files

def tidy_aspect_init(target, ctx):
    """Initialize a tidy aspect for source and header files

    Args:
        target: The analyzed target
        ctx: Context
    Returns:
        A dictionary of important target properties
    """
    if hasattr(ctx.rule.attr, "srcs"):
        srcs = cc_aspect_get_files(ctx, "srcs")
    else:
        srcs = tidy_get_src_files(ctx, target)

    hdrs = []
    if CcInfo in target:
        hdrs += target[CcInfo].compilation_context.headers.to_list()

    # we also need to collect the headers for each "implementation dep[endency]" (if
    # any) individually since these are not contained in the target's compilation_context
    for compilation_context in cc_aspect_get_compilation_contexts_of_implementation_deps(ctx):
        hdrs += compilation_context.headers.to_list()

    return {
        "ctx": ctx,
        "hdrs": hdrs,
        "srcs": srcs,
    }

def tidy_get_enabled_features(ctx):
    """Returns enabled features in config info.

    Args:
        ctx: Context.
    Returns:
        A list of enabled features.
    """
    if hasattr(ctx.attr, "_clang_tidy_config"):
        return ctx.attr._clang_tidy_config[ClangTidyConfigInfo].clang_tidy_enable_features
    return []
