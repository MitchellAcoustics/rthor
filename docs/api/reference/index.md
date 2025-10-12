# Backend Reference

This section documents the internal modules and functions used in the `rthor` package.

## Module Structure

- **[`rthor`](../rthor.md)**: Main user-facing module containing `test()` and `compare()` functions
- **[`_core`](core.md)**: Core statistical algorithm implementations
- **[`_input`](input.md)**: Input processing and correlation matrix handling
- **[`_permutations`](permutations.md)**: Permutation generation and application
- **[`_validation`](validation.md)**: Input validation utilities
- **[`_vectorized`](vectorized.md)**: Vectorized numerical operations

Modules prefixed with underscore (`_`) are internal implementation details. The main `rthor` module provides the public API.
