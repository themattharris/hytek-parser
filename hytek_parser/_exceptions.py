class ChecksumError(ValueError):
    """Raised when a line in the HY3 file has an invalid checksum."""
    def __init__(self, line: str, expected: str, actual: str):
        message = f"Invalid checksum on line: {line}. Expected: {expected}, Got: {actual}."
        super().__init__(message)

class MalformedChecksumError(ValueError):
    """Raised when a line does not contain a valid checksum."""
    def __init__(self, line: str):
        message = f"Malformed checksum on line: {line}. Expected a two-digit integer at the end."
        super().__init__(message)