"""
Error definitions for the application.

These help categorize errors and provide clear guidance for end users.
"""


class AppError(Exception):
    """Base exception class for all application errors."""

    def __init__(self, message: str, original_error: str = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class UserError(AppError):
    """
    Error that can be fixed by the end user.

    This error type should be used when the user needs to take action,
    such as updating configuration, refreshing tokens, etc.
    """

    def __init__(self, message: str, fix_instructions: str = None, original_error: str = None):
        self.fix_instructions = fix_instructions
        super().__init__(message, original_error)

    def __str__(self):
        error_msg = f"{self.message}"
        if self.fix_instructions:
            error_msg += f"\n\nTo fix this issue:\n{self.fix_instructions}"
        return error_msg


class SystemError(AppError):
    """
    Error related to system issues that users cannot fix.

    This error type should be used for problems that require developer intervention
    or system administrator action.
    """

    def __init__(self, message: str, debug_info: str = None, original_error: str = None):
        self.debug_info = debug_info
        super().__init__(message, original_error)

    def __str__(self):
        error_msg = f"SYSTEM ERROR: {self.message}"
        if self.debug_info:
            error_msg += f"\n\nDebug information: {self.debug_info}"
        return error_msg

class AuthenticationError(UserError):
    """Error related to authentication failures."""
    pass


class ConfigurationError(UserError):
    """Error related to configuration issues."""
    pass
