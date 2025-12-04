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
Definition of offered providers of the quality module.
"""

ClangTidyConfigInfo = provider(
    doc = "Configuration structure for the clang-tidy aspect.",
    fields = {
        "additional_flags": "List of additional compiler flags to be added.",
        "autodetermine_builtin_include_directories": "Automatically determine the builtin include directories from the underlying toolchain.",
        "clang_tidy_binary": "Label to a clang-tidy binary. If not provided, the aspect will attempt to auto-detect the clang-tidy binary from the toolchain.",
        "clang_tidy_enable_features": "List of additional bazel features to be enabled when invoking clang-tidy.",
        "clang_tidy_files": "Label to a clang-tidy files. If not provided, the aspect will attempt to auto-detect the clang-tidy files from the toolchain.",
        "clang_tidy_forced_includes": "Provider that maps supported bazel ACTION_NAMES to lists of files which shall be forcibly included into every artifact checked by clang-tidy. cf. https://clang.llvm.org/docs/ClangCommandLineReference.html#cmdoption-clang-include-file.",
        "clang_tidy_priority_includes": "Provider that maps supported bazel ACTION_NAMES to lists of files whose directories shall be added as first ones to the set of include directories where clang-tidy (i.e. clang) starts to look for include files.",
        "default_feature": "The default feature, mnust be one from the feature_mappings.",
        "dependency_attributes": "List of dependency attributes to traverse when in recursive mode. If not provided, all attributes of a rule will get traversed.",
        "deps": "List of build targets that have to succeed to be built for the target platform prior to clang-tidy performing its checks.",
        "exclude_types": "List of rule types clang-tidy should not consider. If not provided, it will run on all rule types listed in `target_types` or which implement the CCInfo Provider.",
        "exclude_types_including_deps": "List of rule types clang-tidy should not consider as well as each dependency a target declared with such rule type has. Useful for skipping e.g. `run_binary` when the target-platform to be checked for differs from the execution-platform under which `run_binary` will get invoked.",
        "excludes": "List of sources to be excluded from clang-tidy analysis.",
        "excludes_override": "List of excluded sources w.r.t. `excludes` to be included nonetheless.",
        "feature_mapping": "Deprecated feature name to clang-tidy configuration file mapping, use feature_mapping_c and feature_mapping_cpp instead. The config file must be part of the filegroups within the configs field.",
        "feature_mapping_c": "Optional value, similar to feature_mapping but only applied to c targets. If specified, it overwrites the mapping defined with feature_mapping.",
        "feature_mapping_cpp": "Optional value, similar to feature_mapping but only applied to c++ targets. If specified, it overwrites the mapping defined with feature_mapping.",
        "header_filter": "Label to bazel `string_flag` containing a regex pattern used to restrict clang-tidy findings from header files to specific ones only. Overrides 'HeaderFilterRegex' option from clang-tidy config file, if any.",
        "suppress_patterns": "List of regex patterns used to suppress clang-tidy findings.",
        "system_headers": "Display the errors from system headers.",
        "target_types": "List of rule types clang-tidy should consider, i.e. `cc_library`. If not provided, it will run on all targets which implement the CCInfo Provider.",
        "unsupported_flags": "List of unsupported compiler flags to be excluded.",
    },
)

# Required since bazel does not yet support `attr.string_keyed_label_list_dict` (cf. https://github.com/bazelbuild/bazel/issues/7989)
ClangTidyForcedIncludesInfo = provider(
    doc = "Definition of forced includes whereby supported bazel ACTION_NAMES get mapped to lists of files which shall be forcibly included into every artifact checked by clang-tidy.",
    fields = {
        "c_compile": "List of files to forcibly include in case of C compilation.",
        "cpp_compile": "List of files to forcibly include in case of C++ compilation.",
    },
)

ClangTidyPriorityIncludesInfo = provider(
    doc = "Definition of priority includes whereby the provided directories shall be added as first ones to the set of include directories where clang-tidy (i.e. clang) starts to look for include files.",
    fields = {
        "c_compile": "List of directories to treat as priority include ones in case of C compilation.",
        "cpp_compile": "List of directories to treat as priority include ones in case of C++ compilation.",
    },
)

ClangTidyIncludeDirectoryInfo = provider(
    doc = "Include directory which is relevant for every artifact checked by clang-tidy.",
    fields = {
        "path": "Full path to the include directory.",
    },
)

ClangTidyAspectOutputInfo = provider(
    doc = "The aspect output provider.",
    fields = ["outputs", "srcs", "hdrs"],
)
