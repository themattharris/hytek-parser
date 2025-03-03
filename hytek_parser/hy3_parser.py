from typing import Any

from hytek_parser.hy3 import HY3_LINE_PARSERS
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.types import StrOrBytesPath
from hytek_parser._utils import validate_checksum, calculate_checksum


def parse_hy3(
    file: StrOrBytesPath, validate_checksums: bool = False, default_country: str = "USA"
) -> ParsedHytekFile:
    """Parse a Hytek MeetManager .hy3 file.

    Args:
        file (StrOrBytesPath): A path to the file to parse.
        validate_checksums (bool, optional): Validate line checksums. Defaults to False.
        default_country (str, optional): Default country for meet. Defaults to "USA".

    Returns:
        ParsedHytekFile: The parsed file.
    """

    # Set options dict
    opts: dict[str, Any] = {
        "validate_checksums": validate_checksums,
        "default_country": default_country,
    }

    # Read file
    with open(file) as f:
        lines = [line.strip() for line in f]

    # Make sure this is the right kind of file
    if lines[0][0:2] != "A1":
        raise ValueError("Not a Hytek file!")

    # Add terminator to file
    if lines[-1][0:2] != "Z0":
        terminator_line = "Z0".ljust(128, " ")  # Ensure correct padding
        checksum = calculate_checksum(terminator_line + "00") # add placeholder checksum
        lines.append(terminator_line + checksum)

    # Start parsing
    parsed_file = ParsedHytekFile()

    warnings = 0
    errors = 0
    for line in lines:
        if validate_checksums:
            validate_checksum(line)

        code = line[0:2]

        if code == "Z0":
            # End of file
            break

        try:
            line_parser = HY3_LINE_PARSERS.get(code)

            if line_parser is None:
                print(f"Invalid line code: {code}")  # TODO: raise an actual warning
                continue

            parsed_file = line_parser(line, parsed_file, opts)
        except Exception as e:
            msg = "Exception while parsing, please open an issue with full traceback at https://github.com/SwimComm/hytek-parser/issues/new/choose"
            raise RuntimeError(msg) from e  # TODO: actual error handling

    # logger.success(
    #     f"Parse completed with {warnings} warning(s) and {errors} error(s)."
    # )
    return parsed_file
