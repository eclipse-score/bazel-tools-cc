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
This module contains helpers for bazel aspects.
"""

load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "ACTION_NAMES")
load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("@score_bazel_tools_cc//quality/private/common:common.bzl", "is_windows_os")

def cc_aspect_is_header(src):
    """Heuristic for headers from file name endings"""
    return src.extension in ["h", "hpp", "hxx", "hh"]

def cc_aspect_is_c_source(src):
    """Heuristic for C source files from file name endings"""
    return src.extension in ["c"]

def cc_aspect_is_cpp_source(src):
    """Heuristic for C++ source files from file name endings"""
    return src.extension in ["cc", "cpp", "cxx"]

def cc_aspect_is_source(src):
    """Heuristic for source files from file name endings"""
    return cc_aspect_is_cpp_source(src) or cc_aspect_is_c_source(src)

def cc_get_action(src):
    """Get the bazel action (compile, link, ...) used.

    Args:
        src: Source File
    Returns:
        bazel action name
    """
    action_name = ACTION_NAMES.c_compile
    if cc_aspect_is_cpp_source(src):
        action_name = ACTION_NAMES.cpp_compile
    return action_name

def cc_get_user_compile_flags(ctx, src):
    """Get compile flags from source.

    Args:
        ctx: Context
        src: Source File
    Returns:
        Compile flags from source
    """
    compile_flags = ctx.fragments.cpp.copts
    if cc_get_action(src) == ACTION_NAMES.cpp_compile:
        compile_flags += ctx.fragments.cpp.cxxopts

    return compile_flags

def cc_get_toolchain_configuration(ctx, additional_feature = []):
    """Get toolchain configuration.

    Args:
        ctx: Context
        additional_feature: Optional, request additional features
    Returns:
        Feature toolchain config
    """
    feature_configuration = cc_common.configure_features(
        ctx = ctx,
        cc_toolchain = find_cpp_toolchain(ctx),
        requested_features = ctx.features + additional_feature,
        unsupported_features = ctx.disabled_features,
    )
    return feature_configuration

def cc_get_toolchain_flags(ctx, src, additional_feature = []):
    """Fetches compiler flags from toolchain configuration.

    Args:
        ctx: Context
        src: Source File
        additional_feature: Optional, request additional features
    Returns:
        Compiler flags from toolchain config
    """
    pic_support = True
    if is_windows_os(ctx):
        pic_support = False

    feature_configuration = cc_get_toolchain_configuration(ctx, additional_feature)

    compile_variables = cc_common.create_compile_variables(
        feature_configuration = feature_configuration,
        cc_toolchain = find_cpp_toolchain(ctx),
        user_compile_flags = cc_get_user_compile_flags(ctx, src),
        use_pic = pic_support,
        source_file = src.path,
    )

    toolchain_flags = cc_common.get_memory_inefficient_command_line(
        feature_configuration = feature_configuration,
        action_name = cc_get_action(src),
        variables = compile_variables,
    )

    return toolchain_flags

def cc_get_toolchain_binary(ctx, src):
    """Fetches compiler binary from toolchain configuration.

    Args:
        ctx: Context
        src: Source File
    Returns:
        Compiler binary
    """
    feature_configuration = cc_get_toolchain_configuration(ctx)
    action_name = cc_get_action(src)

    # Bazel issue: https://github.com/bazelbuild/bazel/issues/4644
    # cc_common.get_tool_for_action does not respect action_name and returns cpp compiler
    # for both ACTION_NAMES.c_compile and ACTION_NAMES.cpp_compile
    binary = cc_common.get_tool_for_action(
        feature_configuration = feature_configuration,
        action_name = action_name,
    )
    if cc_aspect_is_c_source(src):
        binary = binary.replace("clang++", "clang")
        binary = binary.replace("g++", "gcc")
        binary = binary.replace("q++", "qcc")
    return binary

def _cc_aspect_derive_compiler_flags_from(compilation_context, consider_local_defines):
    """Fetches compiler flags from provided compilation context

    Args:
        compilation_context: The compilation context from which to derive the compiler flags
        consider_local_defines: Bool indicating whether the compilation context's local defines shall be considered
    Returns:
        compiler flags derived from provided compilation_context
    """
    options = []

    for define in compilation_context.defines.to_list():
        options.append("-D{}".format(define))

    if consider_local_defines == True:
        for define in compilation_context.local_defines.to_list():
            options.append("-D{}".format(define))

    for system_include in compilation_context.system_includes.to_list():
        options.append("-isystem{}".format(system_include))

    for quote_include in compilation_context.quote_includes.to_list():
        options.append("-iquote{}".format(quote_include))

    for framework_include in compilation_context.framework_includes.to_list():
        options.append("-F{}".format(framework_include))

    for include in compilation_context.includes.to_list():
        options.append("-I{}".format(include))

    return options

def cc_aspect_get_compilation_contexts_of_implementation_deps(ctx):
    """Collects the compilation contexts of the rules's implementation_deps, if any

    Args:
        ctx: The context of the current rule
    Returns:
        compilation contexts of the rules's implementation_deps, if any
    """
    compilation_contexts = []
    if hasattr(ctx, "rule"):
        rule = getattr(ctx, "rule")
        if hasattr(rule.attr, "implementation_deps"):
            compilation_contexts = [
                implementation_dep[CcInfo].compilation_context
                for implementation_dep in getattr(rule.attr, "implementation_deps")
                if CcInfo in implementation_dep
            ]

    return compilation_contexts

def cc_aspect_get_compiler_flags(ctx, target):
    """Fetches compiler flags from current compilation target

    Args:
        ctx: The context of the current rule
        target: Target to obtain the compiler flags
    Returns:
        compiler flags for compilation targets
    """
    options = []
    if CcInfo in target:
        options += _cc_aspect_derive_compiler_flags_from(target[CcInfo].compilation_context, consider_local_defines = True)

        # we also need to collect the above properties for each "implementation dep[endency]" (if any)
        # individually since their properties are not contained in the target's compilation_context
        for compilation_context in cc_aspect_get_compilation_contexts_of_implementation_deps(ctx):
            # compilation_context's local_defines do NOT get considered here since these are
            # defines which are concerning this dependency locally and are never propagated
            # to the dependency's transitive dependents (that is, any rules that depend on it)
            # cf. https://bazel.build/rules/lib/builtins/CompilationContext#local_defines
            options += _cc_aspect_derive_compiler_flags_from(compilation_context, consider_local_defines = False)

    return options

def cc_aspect_get_files(ctx, attr):
    """Get all the files of an attribute from the context rule.

    Args:
        ctx: context
        attr: attribute from rule (for cc rules that is usually srcs or hrds)
    Returns:
        List of the rule attribute files
    """
    if not hasattr(ctx.rule.attr, attr):
        return []

    srcs = getattr(ctx.rule.attr, attr)
    if type(srcs) != type([]):
        return []

    files = []
    for src in srcs:
        if not hasattr(src, "files"):
            continue
        if hasattr(src.files, "to_list"):
            files += src.files.to_list()
        else:
            files += src.files
    return files
