class DataCollectionError(Exception):
    """Raised when GitHub data cannot be collected."""


class DataValidationError(Exception):
    """Raised when a data file is invalid."""


class AnalysisError(Exception):
    """Raised when trend analysis fails."""