"""
Custom error handling mechanisms for the CLI.

This module contains classes and functions that handle error presentation
in the CLI, providing user-friendly error messages without technical details
unless debug mode is enabled.
"""
import functools
import sys
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

import click

from src.core.errors import AppError, SystemError, UserError


class ExceptionWrapper(click.ClickException):
    """
    A wrapper around Click's exception handling.

    Hide the original exception name and traceback from being shown.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)

    def show(self, file: str = None) -> None:
        """Override to completely control how the error is displayed."""
        click.echo(self.message, file=file)

    def format_message(self) -> str:
        """Override to return just the message without any class names."""
        return self.message


class ErrorHandlingGroup(click.Group):
    """
    Custom Click Group that automatically applies error handling to all commands.

    This eliminates the need to decorate each command function with @handle_error.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._original_command_class = self.command_class
        # Override command_class to use our own custom command class
        self.command_class = ErrorHandlingCommand

    def group(self, *args, **kwargs) -> Callable[..., "ErrorHandlingGroup"]:
        """Ensure subgroups also use error handling."""
        kwargs.setdefault("cls", ErrorHandlingGroup)
        return super().group(*args, **kwargs)


class ErrorHandlingCommand(click.Command):
    """Custom Click Command that wraps the callback function with error handling."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Wrap the callback with our error handler
        if self.callback is not None:
            self.callback = wrap_with_error_handler(self.callback)

# Define type variables for the function parameters and return type
P = ParamSpec('P')  # Represents the parameter specification of the wrapped function
R = TypeVar('R')    # Represents the return type of the wrapped function


def wrap_with_error_handler(f: Callable[P, R]) -> Callable[[click.Context, Any, Any], R]:
    """
    Wrap a function with error handling logic.

    Completely suppresses exception class names and tracebacks.
    This can be used as a standalone decorator or internally by ErrorHandlingCommand.
    """

    @functools.wraps(f)
    @click.pass_context
    def wrapper(ctx: click.Context, *args, **kwargs) -> R:
        try:
            return ctx.invoke(f, *args, **kwargs)
        except UserError as e:
            # Format the user error message
            message = e.message
            if hasattr(e, 'fix_instructions') and e.fix_instructions:
                message += f"\n\nTo fix this issue:\n{e.fix_instructions}"
            # Use click's built-in exception wrapper but with our custom formatting
            raise ExceptionWrapper(click.style(message, fg='yellow')) from e
        except SystemError as e:
            # Format the system error message
            message = e.message
            if ctx.obj and ctx.obj.get('debug', False) and e.debug_info:
                message += f"\n\nDebug information: {e.debug_info}"
                if e.original_error:
                    message += f"\n\nOriginal error: {str(e.original_error)}"
            else:
                message += "\n\nRun with --debug for more information."
            raise ExceptionWrapper(click.style(message, fg='red')) from e
        except AppError as e:
            # Format the application error message
            raise ExceptionWrapper(click.style(e.message, fg='red')) from e
        except Exception as e:
            # Format unexpected errors
            error_message = str(e)
            if not ctx.obj or not ctx.obj.get('debug', False):
                # Strip the exception class name if present (e.g., "ValueError: actual message")
                if ': ' in error_message:
                    error_message = error_message.split(': ', 1)[1]
                error_message += "\n\nRun with --debug for more information."
                raise ExceptionWrapper(click.style(error_message, fg='red')) from e
            else:
                # In debug mode, let Click handle it normally to show traceback
                raise

    return wrapper


# Alias for backward compatibility - can be used as a decorator
handle_error = wrap_with_error_handler


def configure_error_handling(debug: bool = False) -> None:
    """
    Configure global error handling settings.

    Args:
        debug (bool): Whether to enable debug mode
    """
    if debug:
        # In debug mode, we want to see the traceback
        sys.tracebacklimit = None
    else:
        # Suppress the default traceback display from Python
        sys.tracebacklimit = 0
