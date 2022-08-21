import os
import struct
import typing


class Mio:
    """ Mini IO """

    @staticmethod
    def skip(byte_count: int, source: typing.BinaryIO):
        source.seek(source.tell() + byte_count)

    @staticmethod
    def read_integer(signed: bool, length: typing.Literal[1, 2, 4, 8], byteorder: typing.Literal['little', 'big'],
                     source: typing.BinaryIO) -> int:
        if byteorder not in ['little', 'big']:
            raise ValueError(f'Invalid byteorder: {byteorder}')
        if length not in [1, 2, 4, 8]:
            raise ValueError(f'Invalid int length: {length}')
        return int.from_bytes(source.read(length), byteorder, signed=signed)

    @staticmethod
    def read_float(length: typing.Literal[2, 4, 8], byteorder: typing.Literal['little', 'big'],
                   source: typing.BinaryIO) -> float:
        match byteorder:
            case 'little': format_string = '<'
            case 'big': format_string = '>'
            case _: raise ValueError(f'Invalid byteorder: {byteorder}')
        match length:
            case 2: format_string = format_string + 'e'
            case 4: format_string = format_string + 'f'
            case 8: format_string = format_string + 'd'
            case _: raise ValueError(f'Invalid float length: {length}')
        return struct.unpack(format_string, source.read(length))[0]

    @staticmethod
    def read_fixed_length_string(length: int, encoding: str, source: typing.BinaryIO) -> str:
        return source.read(length).decode(encoding)

    @staticmethod
    def read_prefixed_length_string(prefix_signed: bool, prefix_length: typing.Literal[1, 2, 4, 8],
                                    prefix_byteorder: typing.Literal['little', 'big'], encoding: str,
                                    source: typing.BinaryIO):
        starting_position = source.tell() if source.seekable() else None
        length = Mio.read_integer(prefix_signed, prefix_length, prefix_byteorder, source)
        if length < 0:
            # Try to go back to starting position of read if user wants to recover from exception
            if starting_position is not None:
                source.seek(starting_position)
            raise ValueError(f'Invalid string length to read: {length}')
        return source.read(length).decode(encoding)

    @staticmethod
    def read_null_terminated_string(encoding: str, source: typing.BinaryIO):
        """ This method stops after the first null byte.
        Using an encoding with a width of more than 1 byte won't check for consecutive null bytes
        with the length of the target encoding """
        result = bytearray()
        next_byte = source.read(1)
        while next_byte != b'\x00':
            result += next_byte
            next_byte = source.read(1)
        return result.decode(encoding)

    @staticmethod
    def is_eof(source: typing.BinaryIO):
        return source.tell() == os.fstat(source.fileno()).st_size

    # region read_integer permutations
    @staticmethod
    def read_int8(source: typing.BinaryIO) -> int:
        return Mio.read_integer(True, 1, 'little', source)  # endian doesn't matter for 1 byte

    @staticmethod
    def read_int16le(source: typing.BinaryIO) -> int:
        return Mio.read_integer(True, 2, 'little', source)

    @staticmethod
    def read_int16be(source: typing.BinaryIO) -> int:
        return Mio.read_integer(True, 2, 'big', source)

    @staticmethod
    def read_int32le(source: typing.BinaryIO) -> int:
        return Mio.read_integer(True, 4, 'little', source)

    @staticmethod
    def read_int32be(source: typing.BinaryIO) -> int:
        return Mio.read_integer(True, 4, 'big', source)

    @staticmethod
    def read_int64le(source: typing.BinaryIO) -> int:
        return Mio.read_integer(True, 8, 'little', source)

    @staticmethod
    def read_int64be(source: typing.BinaryIO) -> int:
        return Mio.read_integer(True, 8, 'big', source)

    @staticmethod
    def read_uint8le(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 1, 'little', source)

    @staticmethod
    def read_uint8be(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 1, 'big', source)

    @staticmethod
    def read_uint16le(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 2, 'little', source)

    @staticmethod
    def read_uint16be(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 2, 'big', source)

    @staticmethod
    def read_uint32le(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 4, 'little', source)

    @staticmethod
    def read_uint32be(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 4, 'big', source)

    @staticmethod
    def read_uint64le(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 8, 'little', source)

    @staticmethod
    def read_uint64be(source: typing.BinaryIO) -> int:
        return Mio.read_integer(False, 8, 'big', source)
    # endregion

    # region read_float permutations
    @staticmethod
    def read_float16le(source: typing.BinaryIO) -> float:
        return Mio.read_float(2, 'little', source)

    @staticmethod
    def read_float16be(source: typing.BinaryIO) -> float:
        return Mio.read_float(2, 'big', source)

    @staticmethod
    def read_float32le(source: typing.BinaryIO) -> float:
        return Mio.read_float(4, 'little', source)

    @staticmethod
    def read_float32be(source: typing.BinaryIO) -> float:
        return Mio.read_float(4, 'big', source)

    @staticmethod
    def read_float64le(source: typing.BinaryIO) -> float:
        return Mio.read_float(8, 'little', source)

    @staticmethod
    def read_float64be(source: typing.BinaryIO) -> float:
        return Mio.read_float(8, 'big', source)
    # endregion
