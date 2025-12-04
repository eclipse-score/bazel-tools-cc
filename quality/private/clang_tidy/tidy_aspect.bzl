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
This module is the main implementation of the tidy_aspect.
"""

load("@bazel_skylib//lib:paths.bzl", "paths")
load("@bazel_skylib//rules:common_settings.bzl", "BuildSettingInfo")
load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "ACTION_NAMES")
load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_checks.bzl",
    "AVAILABLE_CHECKS_COMBINED",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_helper.bzl",
    "determine_module_type",
    "get_fixes_filename",
    "tidy_aspect_init",
    "tidy_get_enabled_features",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_providers.bzl",
    "ClangTidyAspectOutputInfo",
    "ClangTidyConfigInfo",
    "ClangTidyForcedIncludesInfo",
    "ClangTidyIncludeDirectoryInfo",
    "ClangTidyPriorityIncludesInfo",
)
load(
    "@score_bazel_tools_cc//quality/private/common:cc_helper.bzl",
    "cc_aspect_get_compiler_flags",
    "cc_aspect_is_c_source",
    "cc_aspect_is_cpp_source",
    "cc_aspect_is_source",
    "cc_get_action",
    "cc_get_toolchain_flags",
)
load(
    "@score_bazel_tools_cc//quality/private/common:common.bzl",
    "is_feature_active",
    "is_valid_target_filter",
)

def _tidy_aspect_return(outputs, cc_aspect_ctx):
    """Return helper for aspects

    Args:
        outputs: Desired aspect outputs
        cc_aspect_ctx: Aspect Context
    Returns:
        A output group depset
    """

    # It is very important to be aware of the returned providers.
    # If those do not contain any action results (such as created files),
    # bazel will not execute the action.
    # It is noteworthy that bazel has multiple stages and these outputs groups
    # are being checked during the analysis phase before the execution.
    return [
        ClangTidyAspectOutputInfo(
            outputs = outputs,
            srcs = cc_aspect_ctx["srcs"],
            hdrs = cc_aspect_ctx["hdrs"],
        ),
        OutputGroupInfo(clang_tidy_output = outputs),
    ]

def _tidy_aspect_construct_compiler_flags(ctx, src, target, cc_toolchain):
    """Finds compiler flags from source and toolchain origin"""

    clang_tidy_config = ctx.attr._clang_tidy_config[ClangTidyConfigInfo]
    clang_tidy_enable_features = clang_tidy_config.clang_tidy_enable_features
    toolchain_flags = cc_get_toolchain_flags(ctx, src, clang_tidy_enable_features)
    source_flags = cc_aspect_get_compiler_flags(ctx, target)

    compiler_flags = []
    compiler_flags.extend(source_flags)
    compiler_flags.extend(toolchain_flags)

    # This is required, as clang-tidy cannot find default headers such as <memory>
    # It should be investigated why this works for clang-tidy runs
    # TODO Use `resource-dir=` when invoking clang-tidy
    sysroot_arg = "--sysroot=external/sysroot"
    if sysroot_arg in compiler_flags:
        compiler_flags.remove(sysroot_arg)

    if hasattr(ctx.rule.attr, "copts"):
        for copt in ctx.rule.attr.copts:
            # Remove all blanks from copt which is required that the compilation database approach works
            compiler_flags.append(copt.replace(" ", ""))

    # Remove them the compiler flags which can not be understood by Clang, to allow users to run clang-tidy,
    # without having a clang toolchain configured (that would produce a good command line with --compiler clang)
    unsupported_flags = clang_tidy_config.unsupported_flags
    filtered_compiler_flags = [flag for flag in compiler_flags if flag not in unsupported_flags]

    # Autodetermine builtin include directories, if requested
    builtin_include_directories = []
    if clang_tidy_config.autodetermine_builtin_include_directories:
        if len(cc_toolchain.built_in_include_directories) == 0:
            # buildifier: disable=print
            print("NOTE: ClangTidyConfigInfo has `autodetermine_builtin_include_directories` set but the determined toolchain " +
                  "`{}` for bazel target `{}` does not contain any of such directories!".format(cc_toolchain.toolchain_id, ctx.rule.attr.name))
        builtin_include_directories = cc_toolchain.built_in_include_directories

    # Create flags for all builtin include directories
    builtin_include_directories_flags = ["-isystem%s" % directory for directory in builtin_include_directories]

    # Create list of all forced include files
    forced_include_file_paths = []
    if clang_tidy_config.clang_tidy_forced_includes:
        action_name = cc_get_action(src)
        forced_includes_info = clang_tidy_config.clang_tidy_forced_includes[ClangTidyForcedIncludesInfo]
        populate_forced_include_file_paths_from = (lambda targets: forced_include_file_paths.extend([file.path for target in targets for file in target.files.to_list()]))
        if action_name == ACTION_NAMES.cpp_compile:
            populate_forced_include_file_paths_from(forced_includes_info.cpp_compile)
        if action_name == ACTION_NAMES.c_compile:
            populate_forced_include_file_paths_from(forced_includes_info.c_compile)

    # Create flags for all the forced include files
    forced_include_flags = ["-include%s" % file for file in forced_include_file_paths]

    # Create list of all priority include directories
    priority_include_directories = []
    if clang_tidy_config.clang_tidy_priority_includes:
        action_name = cc_get_action(src)
        priority_includes_info = clang_tidy_config.clang_tidy_priority_includes[ClangTidyPriorityIncludesInfo]
        populate_priority_include_directories_from = (lambda targets: priority_include_directories.extend([target[ClangTidyIncludeDirectoryInfo].path for target in targets]))
        if action_name == ACTION_NAMES.cpp_compile:
            populate_priority_include_directories_from(priority_includes_info.cpp_compile)
        if action_name == ACTION_NAMES.c_compile:
            populate_priority_include_directories_from(priority_includes_info.c_compile)
    priority_include_directories = {directory: None for directory in priority_include_directories}  # removes duplicates

    # Create flags for all the priority include directories
    priority_include_directories_flags = ["-I%s" % directory for directory in priority_include_directories]

    # Append workaround flags to the end
    additional_flags = clang_tidy_config.additional_flags

    return forced_include_flags + priority_include_directories_flags + builtin_include_directories_flags + filtered_compiler_flags + additional_flags

def _tidy_aspect_prepare_arguments(ctx, src, target, clang_tidy_path, cc_toolchain):
    compiler_flags = _tidy_aspect_construct_compiler_flags(ctx, src, target, cc_toolchain)

    clang_tidy_fixes_file = ctx.actions.declare_file(paths.join(
        "_tidy",
        target.label.name,
        get_fixes_filename("{}.fixes.yaml".format(src.path.replace("/", "_"))),
    ))

    args = ctx.actions.args()
    if hasattr(ctx.attr, "checks"):
        if ".clang-tidy" not in ctx.attr.checks:
            # Required for argument parsing
            checks = " " + ctx.attr.checks
            args.add_all(["--checks", checks])

    compiler_flags.insert(0, clang_tidy_path)

    args.use_param_file("@%s", use_always = True)
    args.set_param_file_format("multiline")

    compile_commands_file = ctx.actions.declare_file(paths.join(
        "_tidy",
        target.label.name,
        get_fixes_filename("{}_compile_commands".format(src.short_path.lower().replace("/", "_"))),
        "compile_commands.json",
    ))

    args.add_all(["--compile_commands", compile_commands_file])

    args.add_all(["--src_file", src.path])
    args.add_joined("--arguments", compiler_flags, join_with = ";")
    args.add_all(["--fixes", clang_tidy_fixes_file])
    args.add_all(["--tool_bin", clang_tidy_path])

    module_type = determine_module_type(ctx)
    if module_type:
        args.add_all(["--module_type", module_type])

    extra_features = tidy_get_enabled_features(ctx)
    if is_feature_active(ctx, "treat_clang_tidy_warnings_as_errors", extra_features):
        args.add("--treat_clang_tidy_warnings_as_errors")

    if is_feature_active(ctx, "verbose_clang_tidy", extra_features):
        args.add("--verbose")

    if is_feature_active(ctx, "silent_clang_tidy", extra_features):
        args.add("--silent")

    if is_feature_active(ctx, "allow_analyzer_alpha_checkers_clang_tidy", extra_features):
        args.add("--allow-enabling-analyzer-alpha-checkers")

    clang_tidy_config = ctx.attr._clang_tidy_config[ClangTidyConfigInfo]
    feature_mapping = clang_tidy_config.feature_mapping

    if clang_tidy_config.feature_mapping_c and cc_aspect_is_c_source(src):
        feature_mapping = clang_tidy_config.feature_mapping_c

    if clang_tidy_config.feature_mapping_cpp and cc_aspect_is_cpp_source(src):
        feature_mapping = clang_tidy_config.feature_mapping_cpp

    default_feature = clang_tidy_config.default_feature

    config_file = None
    has_at_least_one_custom_feature_active = False
    default_feature_config_file = None

    for config_label, feature_name in feature_mapping.items():
        config_file_name = config_label.files.to_list()[0].basename
        if feature_name == default_feature:
            config_file = config_file_name
            default_feature_config_file = config_file

        if is_feature_active(ctx, feature_name):
            has_at_least_one_custom_feature_active = True
            config_file = config_file_name
            args.add_all(["--config_file", config_file])

    if not has_at_least_one_custom_feature_active:
        args.add_all(["--config_file", default_feature_config_file])

    header_filter = clang_tidy_config.header_filter
    if header_filter:
        args.add_all(["--header_filter", header_filter[BuildSettingInfo].value])

    if clang_tidy_config.system_headers:
        args.add("--system_headers")

    suppress_patterns = clang_tidy_config.suppress_patterns
    if suppress_patterns:
        args.add_all("--suppress_patterns", suppress_patterns)

    return args, feature_mapping, clang_tidy_fixes_file, compile_commands_file

def _tidy_get_transitivity(ctx):
    transitive_outputs = []
    extra_features = tidy_get_enabled_features(ctx)
    if is_feature_active(ctx, "recursive_clang_tidy", extra_features):
        clang_tidy_config = ctx.attr._clang_tidy_config[ClangTidyConfigInfo]
        if clang_tidy_config.dependency_attributes == ["<NONE>"]:
            # consider all attributes as dependency attributes (except internal ones starting with "_")
            dependency_attributes = [
                attribute
                for attribute in dir(ctx.rule.attr)
                if not str(attribute).startswith("_") and str(attribute) not in ["applicable_licenses", "licenses"]
            ]
        else:
            # determine relevant dependency attributes by filtering via the user-provided ones
            dependency_attributes = [
                attribute
                for attribute in dir(ctx.rule.attr)
                if attribute in clang_tidy_config.dependency_attributes
            ]
        for dependency_attribute in dependency_attributes:
            dependencies = getattr(ctx.rule.attr, dependency_attribute)
            dependencies = dependencies if type(dependencies) == "list" else [dependencies]
            for dependency in dependencies:
                if not dependency or type(dependency) != "Target":
                    continue

                if OutputGroupInfo in dependency and hasattr(dependency[OutputGroupInfo], "clang_tidy_output"):
                    transitive_outputs.append(dependency[OutputGroupInfo].clang_tidy_output)

    return transitive_outputs

def _tidy_get_clang_tidy_binary(ctx):
    # Search and return the clang-tidy binary inside the list of files of the clang_tidy_binary label
    clang_tidy_binary_info = ctx.attr._clang_tidy_config[ClangTidyConfigInfo].clang_tidy_binary
    if clang_tidy_binary_info:
        if clang_tidy_binary_info.files_to_run.executable:
            return clang_tidy_binary_info.files_to_run.executable
        for tool in clang_tidy_binary_info.files.to_list():
            if tool.basename == "clang-tidy":
                return tool
    fail(
        "Cannot find clang-tidy binary.",
        "Make sure the `clang_tidy_binary` attribute of the ClangTidyConfigInfo is correct and has exactly one executable to run.",
    )

def _tidy_aspect_aspect_impl(target, ctx):
    """Aspect implementation preparing the call to the clang-tidy runner and checks validity"""
    aspect_ctx = tidy_aspect_init(target, ctx)

    all_outputs = []

    srcs = aspect_ctx["srcs"]
    hdrs = aspect_ctx["hdrs"]

    cc_toolchain = find_cpp_toolchain(ctx)

    clang_tidy_binary = _tidy_get_clang_tidy_binary(ctx)
    clang_tidy_config = ctx.attr._clang_tidy_config[ClangTidyConfigInfo]
    clang_tidy_files = clang_tidy_config.clang_tidy_files.files.to_list()

    if ctx.rule.kind in clang_tidy_config.exclude_types_including_deps:
        return _tidy_aspect_return(depset(direct = all_outputs), aspect_ctx)

    transitive_outputs = _tidy_get_transitivity(ctx)

    # Returning an empty list of outputs will not trigger any execution for this target
    early_return_depset = depset(direct = all_outputs, transitive = transitive_outputs)

    has_target_type_attribute = clang_tidy_config.target_types != ["<NONE>"]
    has_supported_target_type = ctx.rule.kind in clang_tidy_config.target_types

    is_valid_target = CcInfo in target
    if has_target_type_attribute and not has_supported_target_type:
        is_valid_target = False

    if ctx.rule.kind in clang_tidy_config.exclude_types:
        is_valid_target = False

    has_third_party_warning_feature = "third_party_warnings" in ctx.rule.attr.features

    if not is_valid_target or has_third_party_warning_feature:
        return _tidy_aspect_return(early_return_depset, aspect_ctx)

    for src in srcs:
        excludes = clang_tidy_config.excludes
        excludes_override = clang_tidy_config.excludes_override
        if not is_valid_target_filter(excludes, excludes_override, src) or not cc_aspect_is_source(src) or src.is_directory:
            continue

        # Prepare outputs files and arguments
        args, feature_mapping, clang_tidy_fixes_file, compile_commands_file = _tidy_aspect_prepare_arguments(
            ctx,
            src,
            target,
            clang_tidy_binary.path,
            cc_toolchain,
        )

        all_outputs.append(clang_tidy_fixes_file)

        feature_mapping_conig_file_labels = feature_mapping.keys()

        action_name = cc_get_action(src)
        extract_files_list_from = (lambda targets: [target.files.to_list() for target in targets])
        populate_include_files_list_from = (lambda include_files_provider: extract_files_list_from(include_files_provider.c_compile) if action_name == ACTION_NAMES.c_compile else extract_files_list_from(include_files_provider.cpp_compile) if action_name == ACTION_NAMES.cpp_compile else [])

        priority_include_files_list = []
        if clang_tidy_config.clang_tidy_priority_includes:
            priority_include_files_list = populate_include_files_list_from(clang_tidy_config.clang_tidy_priority_includes[ClangTidyPriorityIncludesInfo])

        forced_include_files_list = []
        if clang_tidy_config.clang_tidy_forced_includes:
            forced_include_files_list = populate_include_files_list_from(clang_tidy_config.clang_tidy_forced_includes[ClangTidyForcedIncludesInfo])

        config_files_list = [config_files.files.to_list() for config_files in feature_mapping_conig_file_labels]
        deps_files_list = [deps_files.files.to_list() for deps_files in clang_tidy_config.deps]

        priority_include_files = [priority_include_file for priority_include_files in priority_include_files_list for priority_include_file in priority_include_files]
        forced_include_files = [forced_include_file for forced_include_files in forced_include_files_list for forced_include_file in forced_include_files]
        config_files = [config_file for config_files in config_files_list for config_file in config_files]
        dep_files = [dep_file for deps_files in deps_files_list for dep_file in deps_files]

        # The action invoking the clang-tidy runner (python) which has all required
        # arguments derived from the source file (i.e. compiler flags) to eventually call
        # the clang-tidy binary
        ctx.actions.run(
            inputs = [clang_tidy_binary] + clang_tidy_files + srcs + hdrs + dep_files + config_files + forced_include_files + priority_include_files,
            executable = ctx.executable._clang_tidy_runner,
            outputs = [clang_tidy_fixes_file, compile_commands_file],
            arguments = [args],
            tools = [clang_tidy_binary, ctx.executable._clang_tidy_runner, cc_toolchain.all_files],
            progress_message = "Running clang-tidy on file " + src.path + " from target " + str(target.label),
            mnemonic = "ClangTidyAnalysis",
        )

    accumulated_outputs = depset(direct = all_outputs, transitive = transitive_outputs)

    return _tidy_aspect_return(accumulated_outputs, aspect_ctx)

def _tidy_aspect_instance(
        attributes = {},
        tidy_config = "@score_bazel_tools_cc//quality:quality_clang_tidy_config",
        tidy_runner = "@score_bazel_tools_cc//quality/private/clang_tidy/tools:clang_tidy_runner",
        feature_mapping = {},
        default_feature = "NO_FEATURE"):
    attrs = {
        # Use the current toolchain for clang-tidy
        "_cc_toolchain": attr.label(
            default = "@bazel_tools//tools/cpp:current_cc_toolchain",
        ),
        "_clang_tidy_config": attr.label(
            default = Label(tidy_config),
            providers = [ClangTidyConfigInfo],
        ),
        # The wrapped or runner which helps in invoking clang-tidy correctly
        "_clang_tidy_runner": attr.label(
            executable = True,
            cfg = "exec",  # See https://docs.bazel.build/versions/main/skylark/lib/attr.html#label
            allow_files = True,
            default = Label(tidy_runner),
        ),
        "_default_feature": attr.string(default = default_feature, values = feature_mapping.keys()),
        "_feature_mapping": attr.string_dict(default = feature_mapping),
    }
    attrs.update(attributes)

    return aspect(
        implementation = _tidy_aspect_aspect_impl,
        attr_aspects = ["*"],
        attrs = attrs,
        fragments = ["cpp"],
        incompatible_use_toolchain_transition = True,
        toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
    )

# The aspect definition when used via a command line call with --aspects. Must not have attributes
tidy_aspect = _tidy_aspect_instance()

# Available attributes only when called via a rule.
# Those can only be of type "string" and all possible values must be provided
rule_attributes = {
    "checks": attr.string(values = AVAILABLE_CHECKS_COMBINED),
}

# The aspect definition when used via a rule, propagated to all dependency targets
tidy_suite_aspect = _tidy_aspect_instance(rule_attributes)

def quality_clang_tidy_aspect_factory(
        tidy_config,
        tidy_runner = "@score_bazel_tools_cc//quality/private/clang_tidy:score_clang_tidy_tidy_runner",
        feature_mapping = {},
        default_feature = "NO_FEATURE"):
    return _tidy_aspect_instance(
        tidy_config = tidy_config,
        tidy_runner = tidy_runner,
        feature_mapping = feature_mapping,
        default_feature = default_feature,
    )
