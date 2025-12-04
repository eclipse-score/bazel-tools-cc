# Clang-Format

Clang-format is a standalone tool that can be used to format C/C++ and other types of codes.

This module provides Bazel-integrated, cacheable, and configurable C/C++ code formatting and linting using `clang-format`.

- [Clang-Format Aspect](#clang-format-aspect)
  - [Basic Usage](#basic-usage)
  - [How to Use Custom Configuration](#how-to-use-custom-configuration)
  - [Findings Output](#findings-output)
  - [Extra Features](#extra-features)
    - [Refactor](#refactor)

## Clang-Format Aspect

Bazel Tools CC integrates `clang-format` as an aspect, enabling automatic formatting and findings generation for C/C++ source and header files.

### Basic Usage

To run clang-format on your codebase, use:

```bash
bazel build --config=clang_format --keep_going [--features=refactor] -- //...
```

Where `--features=refactor` is optional and enables automatic code formatting.

You can also configure the aspect and output groups in your `.bazelrc`:

```bash
# .bazelrc
build:clang_format --output_groups=clang_format_output
build:clang_format --aspects=@score_bazel_tools_cc//quality:defs.bzl%clang_format_aspect
```

### How to Use Custom Configuration

By default, the aspect uses a [default clang-format configuration](/quality/BUILD#L59). However, it is possible to provide a custom configuration file (e.g., `.clang-format`) by creating a `clang_format_config` target:

```starlark
# path/to/BUILD
load("@score_bazel_tools_cc//quality:defs.bzl", "clang_format_config")
clang_format_config(
    name = "clang_format_config_default",
    config_file = "//:.clang_format",
    excludes = ["external/"],
    target_types = [
        "cc_binary",
        "cc_library",
        "cc_test",
    ],
    visibility = ["//visibility:public"],
)
```
- **Configuration File:** You can use a custom `.clang-format` file for formatting rules.
- **Target Types:** Restrict formatting to specific Bazel rule kinds via the config.
- **Excludes/Overrides:** Exclude or include files and targets using configuration attributes.

To override the default configuration, add the following to your `.bazelrc`:

```bash
# .bazelrc
build:clang_format --@score_bazel_tools_cc//quality:clang_format_config=//path/to:custom_clang_format_config
```

### Findings Output

The aspect generates findings in both text and JSON formats for review.

Available formats:
- `<target>.clang_format_findings.txt`: Human-readable findings report.
- `<target>.clang_format_findings.json`: Machine-readable findings report.


### Extra Features

#### Refactor

Automatic code refactor is enabled through the `--features=refactor` flag:

```bash
bazel build --config=clang_format --keep_going --features=refactor -- //...
```

This will apply formatting changes directly to your source files.

---

For more information on `clang-format`, see the [official documentation](https://clang.llvm.org/docs/ClangFormat.html).
For Bazel aspect usage, refer to the [Bazel documentation](https://bazel.build/extending/aspects).
