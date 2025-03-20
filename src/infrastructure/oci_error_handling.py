
import functools
import logging
import oci.exceptions

logger = logging.getLogger(__name__)


class OCIServiceError(Exception):
    """Custom exception for OCI service errors with context."""

    def __init__(self, operation, original_error, **context):
        self.operation = operation
        self.original_error = original_error
        self.status = getattr(original_error, 'status', None)
        self.code = getattr(original_error, 'code', None)
        self.context = context

        message = f"OCI operation '{operation}' failed: {original_error}"
        if context:
            message += f" (Context: {context})"

        super().__init__(message)


def handle_oci_errors(operation_name=None):
    """
    Decorator to handle OCI service errors uniformly.

    Args:
        operation_name: Name of the operation being performed.
                       If None, uses the function name.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            try:
                return func(*args, **kwargs)
            except oci.exceptions.ServiceError as e:
                logger.error(
                    f"OCI service error in {op_name}: {e.message}",
                    extra={
                        "status": e.status,
                        "code": e.code,
                        "operation": op_name,
                        "request_id": getattr(e, "request_id", None),
                        "opc_request_id": getattr(e, "opc_request_id", None),
                    }
                )

                context = {}
                if args and hasattr(args[0], '__class__'):
                    relevant_args = args[1:]
                else:
                    relevant_args = args

                for i, arg in enumerate(relevant_args):
                    if isinstance(arg, (str, int, bool, float)):
                        context[f"arg{i}"] = arg

                for key, value in kwargs.items():
                    if isinstance(value, (str, int, bool, float)):
                        context[key] = value

                raise OCIServiceError(op_name, e, **context) from e
            except Exception as e:
                logger.exception(f"Unexpected error in {op_name}")
                raise

        return wrapper

    return decorator