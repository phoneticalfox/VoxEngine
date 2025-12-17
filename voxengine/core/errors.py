"""Custom error types for predictable CLI/API behavior."""

from __future__ import annotations


class VoxEngineError(Exception):
    """Base class for expected VoxEngine errors with exit codes."""

    exit_code = 1

    def __init__(self, message: str, *, exit_code: int | None = None):
        super().__init__(message)
        self.exit_code = exit_code or self.exit_code


class UserConfigError(VoxEngineError):
    """Raised when user input or configuration is invalid."""

    exit_code = 2


class MissingDependencyError(VoxEngineError):
    """Raised when a required backend, executable, or model is missing."""

    exit_code = 3
