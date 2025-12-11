# Bazel Tools CC

This repository contains custom bazel quality tooling for C/C++.

- [Offered Tools](#offered-tools)
- [How to use bazel-tools-cc](#how-to-use-btcc)
  - [Requirements](#requirements)
  - [Select python pip hub version](#select-python-pip-hub-version)
  - [Using WORKSPACE](#using-workspace)
  - [Using bzlmod](#using-bzlmod)
- [Contributing](#contributing)

## Offered Tools

Each offered tool has its own README document and can be independently activated and configured.

|                          Tool                          |      Tool Type       | Bazel Type | Supported Languages | Workspace | Bzlmod |
| :----------------------------------------------------: | :------------------: | :--------: | :-----------------: | :-------: | :----: |
|   [clang-tidy](quality/private/clang_tidy/README.md)   | Static code analyzer |   aspect   |       C, C++        |    yes    |  yes   |
| [clang-format](quality/private/clang_format/README.md) |    Code formatter    |   aspect   |       C, C++        |    yes    |  yes   |

## How to use Bazel Tools CC

The [test subdirectory](test) is a workspace with a fully working setup.

The next sections explain the steps to achieve a proper config for each Bazel dependency manager but it is recommended to either use the test workspace blueprint and copy-paste what is needed.

### Requirements

It's important to note that this repository does not supply python toolchains but only its pip dependencies. Therefore one must set up its own python toolchain. This repository supports major python versions from `3.8` to `3.12`.

Additionaly, one must have the following bazel repositories already in place:

- bazel_skylib >= 1.7.1
- rules_python >= 1.4.1
- rules_shell >= 0.6.1
- rules_cc >= 0.1.1 (only for Bazel 8)
- com_google_protobuf >= v29.0 (only for Bazel 8 with Workspace mode)
- score_bazel_tools_python >= 0.1.3

### Select python pip hub version

To select the correct python dependecy version one only needs to set a `string_flag` under one's `.bazelrc` file.

For example if one is using python `3.10`, one should select our python `3.10` dependencies by adding the following lines to the respective `.bazelrc` file.

```python
# .bazelrc

common --flag_alias=python=@rules_python//python/config_settings:python_version
common --python=3.10
```

### Using WORKSPACE

Add this to your `WORKSPACE` file.

```python
# WORKSPACE

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "score_bazel_tools_cc",
    sha256 = "<omitted>",
    urls = ["<ommited>"],
)

load("@score_bazel_tools_cc//third_party:dependencies.bzl", score_bazel_tools_cc_dependencies = "dependencies")

score_bazel_tools_cc_dependencies()

load("@score_bazel_tools_cc//third_party:python_toolchains.bzl", score_bazel_tools_cc_python_toolchains = "python_toolchains")

score_bazel_tools_cc_python_toolchains()

load("@score_bazel_tools_cc//third_party:python_pip_parse.bzl", score_bazel_tools_cc_python_pip_parse = "python_pip_parse")

score_bazel_tools_cc_python_pip_parse()

load("@score_bazel_tools_cc//third_party:python_pip_hub.bzl", score_bazel_tools_cc_python_pip_hub = "python_pip_hub")

score_bazel_tools_cc_python_pip_hub()
```

### Using bzlmod

Add the https://raw.githubusercontent.com/eclipse-score/bazel_registry/main/ registry to your known registries and add `score_bazel_tools_cc` to your `MODULE.bazel` file.

```python
# .bazelrc

common --registry https://raw.githubusercontent.com/eclipse-score/bazel_registry/main/
```

```python
# MODULE.bazel

bazel_dep(name = "score_bazel_tools_cc", version = "<version>")
```

## Testing

To run the tests, simply execute:

```bash
./scripts/run_all_tests.sh
```

This will run all the tests, linters, formaters, and checks to ensure everything is functioning correctly.

Example Output:

```
Command Name                          | Status
------------------------------------- | ----------
tests (bzlmod mode and python 3.12)   | SUCCEEDED
tests (bzlmod mode)                   | SUCCEEDED
tests (bzlmod mode with experimental_cc_implementation_deps) | SUCCEEDED
clang-format                          | SUCCEEDED
ruff_check                            | SUCCEEDED
ruff_format                           | SUCCEEDED
pylint                                | SUCCEEDED
black                                 | SUCCEEDED
isort                                 | SUCCEEDED
mypy                                  | SUCCEEDED
tests (in test workspace)             | SUCCEEDED
buildifier                            | SUCCEEDED
eclipse copyright check               | SUCCEEDED
security scan                         | SUCCEEDED
------------------------------------- | ----------
```

## Contributing

Please check our [contributing guide](CONTRIBUTION.md).
