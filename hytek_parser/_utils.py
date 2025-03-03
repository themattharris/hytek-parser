from typing import Any, Optional, Type, TypeVar
from hytek_parser._exceptions import ChecksumError, MalformedChecksumError

def extract(string: str, start: int, len_: int) -> str:
    """Extract a section of a certain length from a string.

    Args:
        string (str): The string to extract from.
        start (int): How many chars to move forward.
        len_ (int): The amount of chars to extract.

    Returns:
        str: The extracted string.
    """
    start -= 1
    return string[start : start + len_].strip()


def guess_age_group(swimmer_age: int) -> tuple[int, int]:
    """Guess the age group from a swimmer's age.

    Args:
        swimmer_age (int): The swimmer's age.

    Returns:
        tuple[int, int]: The age group in terms of (age_min, age_max).
    """
    if swimmer_age <= 8:
        # Probably 8&U
        return 0, 8
    elif 9 <= swimmer_age <= 10:
        # Probably 9-10
        return 9, 10
    elif 11 <= swimmer_age <= 12:
        # Probably 11-12
        return 11, 12
    elif 13 <= swimmer_age <= 14:
        # Probably 13-14
        return 13, 14
    else:
        # Probably open
        return 0, 109


def get_age_group(
    age_min: Optional[int], age_max: Optional[int], swimmer_age: int
) -> tuple[int, int]:
    """Get the correct age group for an event.

    Args:
        age_min (Optional[int]): The minimum age from the Hytek file.
        age_max (Optional[int]): The maximum age from the Hytek file.
        swimmer_age (int): The swimmer's age from the Hytek file.

    Returns:
        tuple[int, int]: The age group in terms of (age_min, age_max).
    """
    if age_min is not None and age_min < 0:
        # Incorrect
        age_min = None
    if age_max is not None and age_max > 109:
        # Incorrect
        age_max = None

    if age_min is not None and age_max is not None:
        # Everything is correct
        return age_min, age_max
    elif age_min is not None:
        # age_max is None
        if swimmer_age > age_min + 1:
            # Probably an over event
            return age_min, 109
        else:
            # Probably a limited event
            return age_min, age_min + 1
    elif age_max is not None:
        # age_min is None
        if swimmer_age < age_max - 1:
            # Probably an under event
            return 0, age_max
        else:
            # Probably a limited event
            return age_max - 1, age_max
    else:
        # Both are None, only have swimmer age to work with
        return guess_age_group(swimmer_age)


EnumType = TypeVar("EnumType")


def select_from_enum(enum: Type[EnumType], value: Any) -> EnumType:
    """Safely select a value from an enum.

    Args:
        enum (Any): The enum to select the value from.
        value (Any): The value to select.

    Returns:
        Any: The selected value from the enum.
    """
    try:
        # Errors are caught
        return enum(value)  # type: ignore[call-arg]
    except ValueError:
        # Every Enum has an UNKNOWN in enums.py
        return enum.UNKNOWN  # type: ignore[attr-defined]


CastType = TypeVar("CastType")


def safe_cast(type_: Type[CastType], value: Any, default: Any = None) -> CastType:
    """Safely cast a value to a type.

    Args:
        type_ (Type[CastType]): The type to cast to.
        value (Any): The value to cast.
        default (Any, optional): The default value to return. If None, use type default.
                                 Defaults to None.

    Returns:
        CastType: The casted variable or default if casting is not possible.
    """
    try:
        # TypeErrors are caught
        return type_(value)  # type: ignore[call-arg]
    except (TypeError, ValueError):
        if default:
            return default
        else:
            return type_()

def int_or_none(value:str|None) -> int|None:
    """Safely return either an int from a numeric string value, or None
    
    Args:
        value (str|None): The value to cast to int 
    
    Returns:
        int|None: Either the parsed int value or None"""
    return int(value) if value and value.isdigit() else None


def calculate_checksum(line:str) -> int:
    """Calculates the checksum for a given line.

    Args:
        line (str): The line from the .hy3 file.

    Returns:
        str: The calculated two-digit checksum.

    Example:
        >>> checksum = calculate_checksum("Z0")
        >>> print(checksum)
        07
    """
    line = line[:-2]  # Remove last two checksum characters

    # Compute ASCII values
    ord_chars = [ord(char) for char in line]

    # Split into odd/even indexed values
    odd_sum = sum(2 * ord_chars[i] for i in range(1, len(ord_chars), 2))
    even_sum = sum(ord_chars[i] for i in range(0, len(ord_chars), 2))

    # Compute checksum values
    sum_val = odd_sum + even_sum
    sum2 = (sum_val // 21) + 205

    # Extract last two digits
    checksum1 = sum2 % 10
    checksum2 = (sum2 // 10) % 10

    return f"{checksum1}{checksum2}"

def validate_checksum(line:str) -> bool:
    """Validates the checksum of a given line.

    Args:
        line (str): The line from the .hy3 file.

    Raises:
        MalformedChecksumError: If the checksum is missing or malformed.
        ChecksumError: If the checksum is invalid.
    """
    if len(line) < 2:
        raise MalformedChecksumError(line)

    actual_checksum = line[-2:]

    # Ensure the checksum consists of two digits
    if not actual_checksum.isdigit():
        raise MalformedChecksumError(line)

    expected_checksum = calculate_checksum(line)

    if actual_checksum != expected_checksum:
        raise ChecksumError(line, expected_checksum, actual_checksum)
    return True