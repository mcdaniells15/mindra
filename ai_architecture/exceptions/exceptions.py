class AIArchitectureError(Exception):
    """Base exception class for AI Architecture."""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class DocumentProcessingError(AIArchitectureError):
    """Exception raised when there is an error processing a document."""
    def __init__(self, message: str, file_path: str = None, stage: str = None, details: dict = None):
        self.file_path = file_path
        self.stage = stage
        super().__init__(
            message,
            details={
                "file_path": file_path,
                "processing_stage": stage,
                **(details or {})
            }
        )

class APIError(AIArchitectureError):
    """Exception raised when there is an error with API operations."""
    def __init__(self, message: str, status_code: int = None, endpoint: str = None, details: dict = None):
        self.status_code = status_code
        self.endpoint = endpoint
        super().__init__(
            message,
            details={
                "status_code": status_code,
                "endpoint": endpoint,
                **(details or {})
            }
        )

class RateLimitError(AIArchitectureError):
    """Exception raised when API rate limits are exceeded."""
    def __init__(self, message: str, retry_after: int = None, limit_type: str = None, details: dict = None):
        self.retry_after = retry_after
        self.limit_type = limit_type
        super().__init__(
            message,
            {
                "retry_after": retry_after,
                "limit_type": limit_type,
                **(details or {})
            }
        )

class ValidationError(AIArchitectureError):
    """Exception raised when input validation fails."""
    def __init__(self, message: str, field: str = None, value: str = None, details: dict = None):
        self.field = field
        self.value = value
        super().__init__(
            message,
            details={
                "field": field,
                "invalid_value": value,
                **(details or {})
            }
        ) 