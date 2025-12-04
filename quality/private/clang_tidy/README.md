# Clang-Tidy

This module offers a bazel integrated, fully cachable and configurable clang-tidy runner.

- [Clang-Tidy](#clang-tidy)
  - [Toolchain](#toolchain)
    - [Using the Software Factory toolchain](#using-the-software-factory-toolchain)
  - [Bazelrc](#bazelrc)
  - [Configuration](#configuration)
    - [Built in features](#built-in-features)
    - [Clang-tidy configuration file](#clang-tidy-configuration-file)
    - [Configuration details](#configuration-details)
  - [Running](#running)
  - [Example](#example)

## Toolchain

In order to run the clang-tidy aspect successfully, the clang-tidy bazel runner requires a clang toolchain. This toolchain must define a `clang-tidy` binary label shipped with it. Additionally, all required runfiles for the clang-tidy binary (for example stdlib header) must be exposed by a filegroup target.

### Using the Software Factory toolchain

In case you want to use the clang toolchain provided by Software Factory, you need bzlmod and thus a `MODULE.bazel` file.
Add this to your `MODULE.bazel` file.

```python
bazel_dep(name = "bazel-toolchains-llvm15", version = "15.0.1-1")
bazel_dep(name = "host-x86_64-linux-llvm15-pkg", version = "15.0.1-1")
```

## Bazelrc

Having both [Bazel Tools CC Bazel dependency](../../../README.md#how-to-use-btcc) and [toolchain](#toolchain) resolved, it's convenient to add a clang-tidy bazel aspect configuration to the `.bazelrc` file:

```bazel
build:clang_tidy --experimental_enable_bzlmod
build:clang_tidy --aspects=@score_bazel_tools_cc//quality:defs.bzl%quality_clang_tidy_aspect
build:clang_tidy --output_groups=clang_tidy_output
build:clang_tidy --build_tag_filters="-tidy_suite"
build:clang_tidy --force_pic
build:clang_tidy --incompatible_enable_cc_toolchain_resolution
build:clang_tidy --verbose_failures
```

The first three lines are related to the toolchain. The other ones are specific to the clang-tidy runner.

## Configuration

The aspect [default configuration](../../BUILD#L6) can be modified by overloading the target given by the `--@score_bazel_tools_cc//quality:quality_clang_tidy_config` label.

To achieve that, a custom target must be created using the [`quality_clang_tidy_config`](../../defs.bzl#L58) rule.

The [default configuration](../../BUILD#L6) can be used as a template, modify it to suit your needs and copy it into one BUILD file.

Finally, the following target overload shortcut can be added to the `.bazelrc` file:

```bazel
build:clang_tidy --@score_bazel_tools_cc//quality:quality_clang_tidy_config=//:awesome_clang_tidy_config
```

The clang-tidy runner also offers a set of built-in features and a way to map clang-tidy configuration files.

### Built in features

The build-in features can be activated by handing over the command line `--features` or setting the `features` attribute in a BUILD file rule. Features can also be disabled when pre-pending with a `-` sign. They are:

- `recursive_clang_tidy`: Runs on the given target + all dependencies and transitive dependencies of it.
- `verbose_clang_tidy`: Output more verbose logs (The log level is DEBUG).
- `silent_clang_tidy`: Output less verbose logs (The log level is WARNING).
- `treat_clang_tidy_warnings_as_errors`: Fails and stops on the first occurrence of a clang-tidy violation.
- `use_action_inputs_for_sources`: Uses action.inputs.to_list to get the sources for rules that do not have srcs as part of attrs.
- `allow_analyzer_alpha_checkers_clang_tidy`: Enables to use of clang-analyzer alpha checkers (they are likely to have false positives).

### Clang-tidy configuration file

One can define own features (to be specific: features which map to a clang-tidy configuration files).

To do so, add a clang-tidy configuration file to any location in your repo and name it as you like. Then, this must be referenced in the previously created `quality_clang_tidy_config` using the `feature_mapping` parameter, where the key is the location of the file and the value is the name of the feature.

There is also a `feature_mapping_c` and a `feature_mapping_cpp` parameter, which are specific for C and CPP targets. These specific parameters overwrite the default `feature_mapping`.

The [test workspace clang-tidy configuration file](../../../test/awesome_config.yaml) can be used as template.

### Configuration details

More information can be found in the [`quality_clang_tidy_config` rule definition](tidy_config.bzl#L45) or in the [ClangTidyConfigInfo Provider](tidy_providers.bzl#L7).

## Running

Run this from your (test) workspace, assuming that you have at least on target which implements the `CcInfo` bazel provider (i.e. cc_library)

```bash
bazel build //... --config=clang_tidy
```

## Example

This pattern is applied as an example in the directory `test` assuming you check out this repository stand-alone.

The tests are not shipped when connecting it via bazel third-party dependencies.

```bash
git clone git@github.com:eclipse-score/bazel-tools-cc.git
cd bazel-rules-quality/test
bazel build //... --config=clang_tidy
```

will result in:

```bash
INFO: 1 counting clang-tidy finding(s)
INFO: ---
/tmp/bazel-rules-quality/test/test.cpp:3:15: error: floating point literal has suffix 'f', which is not uppercase [readability-uppercase-literal-suffix,-warnings-as-errors]
    float f = 1.0f;
              ^  ~
                 F

At least one clang-tidy finding was treated as error
```
