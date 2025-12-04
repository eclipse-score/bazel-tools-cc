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

"""Aspect to run clang-format on C/C++ source/header files."""

load("@bazel_skylib//lib:paths.bzl", "paths")
load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("@score_bazel_tools_cc//quality/private/clang_format:clang_format_providers.bzl", "ClangFormatConfigInfo")
load(
    "@score_bazel_tools_cc//quality/private/common:cc_helper.bzl",
    "cc_aspect_get_files",
    "cc_get_toolchain_binary",
)

def _aspect_return(direct_outputs, transitive_outputs):
    """Returns the default output of this aspect.

    Args:
        direct_outputs: List of objects.
        transitive_outputs: List of depsets.
    Returns:
        OutputGroupInfo: The default output provider augmented with clang_format_output.
    """
    return [OutputGroupInfo(clang_format_output = depset(direct_outputs, transitive = transitive_outputs))]

def _is_target_excluded(target, excludes, excludes_override):
    """Returns whether a certain target is excluded or not given a list of exclusions and overrided exclusions.

    Args:
        target: The aspect respective target.
        excludes: A list of path names (string) to exclude.
        excludes_override: A list of path names (string) to include nonetheless.
    Returns:
        True if the path is excluded, and False otherwise.
    """
    for inclusion in excludes_override:
        if paths.starts_with(target.label.workspace_root, inclusion):
            return False
    for exclusion in excludes:
        if paths.starts_with(target.label.workspace_root, exclusion):
            return True
    return False

def _collect_transitive_outputs(ctx):
    """Collects transitive outputs from the context."""
    transitive_outputs = []
    for dep in getattr(ctx.rule.attr, "deps", []):
        if "clang_format_output" in dep[OutputGroupInfo]:
            transitive_outputs.append(dep[OutputGroupInfo].clang_format_output)
    return transitive_outputs

def _clang_format_aspect_implementation(target, ctx):
    """Clang-format aspect implementation."""

    outputs = []
    transitive_outputs = _collect_transitive_outputs(ctx)

    is_valid_target = CcInfo in target
    clang_format_config = ctx.attr._clang_format_config[ClangFormatConfigInfo]
    has_target_type_attribute = clang_format_config.target_types != ["<NONE>"]
    has_supported_target_type = ctx.rule.kind in clang_format_config.target_types

    if has_target_type_attribute and not has_supported_target_type:
        is_valid_target = False

    if ctx.rule.kind in clang_format_config.exclude_types:
        is_valid_target = False

    if _is_target_excluded(target, clang_format_config.excludes, clang_format_config.excludes_override):
        is_valid_target = False

    if not is_valid_target:
        return _aspect_return([], transitive_outputs)

    toolchain = find_cpp_toolchain(ctx)
    sources = cc_aspect_get_files(ctx, "srcs")
    headers = cc_aspect_get_files(ctx, "hdrs")

    if not sources:
        return _aspect_return([], transitive_outputs)

    for header in target[CcInfo].compilation_context.headers.to_list():
        if header not in headers:
            headers.append(header)

    inputs = headers + sources
    config_file = getattr(clang_format_config, "config_file", None)
    basename = target.label.name + ".clang_format_findings"
    findings_text_file = ctx.actions.declare_file(basename + ".txt")
    outputs.append(findings_text_file)
    findings_json_file = ctx.actions.declare_file(basename + ".json")
    outputs.append(findings_json_file)

    args = ctx.actions.args()
    if config_file:
        args.add("--config-file", config_file.path, format = "%s")
        inputs.append(config_file)
    args.use_param_file("@%s", use_always = True)
    args.set_param_file_format("multiline")
    args.add_all("--target-files", headers + sources, format_each = "%s")
    args.add("--tool-output-text", findings_text_file.path, format = "%s")
    args.add("--tool-output-json", findings_json_file.path, format = "%s")

    file_refactor = "false"
    if "refactor" in ctx.features:
        args.add("--refactor", True, format = "%s")
        file_refactor = "true"

    # The specific source file used to obtain `toolchain_executable` is not important,
    # as it serves only as a reference point for locating the `clang-format` executable.
    toolchain_executable = cc_get_toolchain_binary(ctx, sources[0])
    args.add("--compiler-executable", toolchain_executable, format = "%s")

    ctx.actions.run(
        inputs = inputs,
        outputs = outputs,
        arguments = [args],
        tools = [ctx.executable._runner, toolchain.all_files],
        executable = ctx.executable._runner,
        progress_message = "Running clang-format on: {target_name}".format(target_name = target.label.name),
        execution_requirements = {"no-sandbox": file_refactor},
        mnemonic = "ClangFormat",
    )

    return _aspect_return(outputs, transitive_outputs)

def _clang_format_aspect_instance():
    """Clang-format aspect instance.

    Provides a default instance of the clang-format aspect.

    Returns:
        An aspect instance.
    """
    return aspect(
        implementation = _clang_format_aspect_implementation,
        required_providers = [CcInfo],
        attr_aspects = ["deps"],
        attrs = {
            "_clang_format_config": attr.label(
                default = Label("@score_bazel_tools_cc//quality:clang_format_config"),
                providers = [ClangFormatConfigInfo],
            ),
            "_runner": attr.label(
                executable = True,
                cfg = "exec",
                default = Label("@score_bazel_tools_cc//quality/private/clang_format/tool:clang_format"),
            ),
        },
        fragments = ["cpp"],
        toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
    )

clang_format_aspect = _clang_format_aspect_instance()
