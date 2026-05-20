"""
BS Tag Converter — порт Java LongToCodeConverter для тегов Brawl Stars.
Чистая библиотека: только класс конвертера, без тестов/вывода.
"""
import ctypes
from typing import Optional, Tuple


class LongToCodeConverter:
    CONVERSION_CHARS: str = "0289PYLQGRJCUV"
    HASH_TAG: str = "#"
    TEAM_CONVERSION_CHARS: str = "QWERTYUPASDFGHJKLZCVBNM23456789"
    TEAM_TAG: str = "X"

    MASK32: int = 0xFFFF_FFFF
    MASK64: int = 0xFFFF_FFFF_FFFF_FFFF

    def __init__(
        self,
        code_suffix: Optional[str] = None,
        conversion_chars: Optional[str] = None,
    ) -> None:
        self.code_suffix = code_suffix if code_suffix is not None else self.HASH_TAG
        self.conversion_chars = conversion_chars if conversion_chars is not None else self.CONVERSION_CHARS

    @staticmethod
    def _java_int_to_long(hi_int: int, lo_int: int) -> int:
        hi_signed = ctypes.c_long(hi_int).value
        hi_64 = hi_signed & LongToCodeConverter.MASK64
        lo_unsigned = lo_int & LongToCodeConverter.MASK32
        unsigned_result = ((hi_64 << 32) | lo_unsigned) & LongToCodeConverter.MASK64
        return ctypes.c_longlong(unsigned_result).value

    @staticmethod
    def _java_int_to_long_s(hi_int: int, lo_int: int) -> int:
        hi_signed = ctypes.c_long(hi_int).value
        lo_signed = ctypes.c_long(lo_int).value
        hi_64 = hi_signed & LongToCodeConverter.MASK64
        lo_64 = lo_signed & LongToCodeConverter.MASK64
        unsigned_result = (hi_64 << 32) | lo_64
        return ctypes.c_longlong(unsigned_result).value

    @staticmethod
    def _java_long_to_unsigned(java_long: int) -> int:
        return java_long & LongToCodeConverter.MASK64

    def _convert(self, id_val: int) -> str:
        n = self._java_long_to_unsigned(id_val)
        tag_chars = []
        base = len(self.conversion_chars)
        while n > 0:
            char_index = n % base
            tag_chars.insert(0, self.conversion_chars[char_index])
            n = (n - char_index) // base
        return "".join(tag_chars)

    def to_code(self, high_int: int, low_int: int) -> Optional[str]:
        high_signed = ctypes.c_int(high_int).value
        low_signed = ctypes.c_int(low_int).value
        if high_signed < 0 or high_signed >= 256:
            return None
        hi_part = low_signed >> 24
        lo_part = high_signed | ((low_signed << 8) & LongToCodeConverter.MASK32)
        lo_part = ctypes.c_int(lo_part).value
        combined = self._java_int_to_long(hi_part, lo_part)
        encoded = self._convert(combined)
        return self.code_suffix + encoded

    def to_id(self, code: str) -> int:
        if len(code) >= 14:
            return self._java_int_to_long(-1, -1)
        code_substring = code[1:] if len(code) else ""
        if len(code_substring) == 0:
            return self._java_int_to_long(0, 0)
        base = len(self.conversion_chars)
        unk6 = 0
        unk7 = 0
        for ch in code_substring:
            sub_str_idx = self.conversion_chars.find(ch)
            if sub_str_idx < 0:
                return self._java_int_to_long(-1, -1)
            unk12 = ctypes.c_int(unk6 * base + sub_str_idx).value
            combined_unsigned = self._java_long_to_unsigned(
                self._java_int_to_long_s(unk7, unk6)
            )
            unk7 = ctypes.c_int((combined_unsigned * base + sub_str_idx) >> 32).value
            unk6 = unk12
        if (unk6 & unk7) != -1:
            v13_unsigned = self._java_long_to_unsigned(
                self._java_int_to_long_s(unk7, unk6)
            )
            v13 = v13_unsigned >> 8
            lo_int = ctypes.c_int(v13 & 0x7FFF_FFFF).value
            hi_int = unk6 & 0xFF
            return self._java_int_to_long(hi_int, lo_int)
        return self._java_int_to_long(-1, -1)

    def to_id_pair(self, code: str) -> Tuple[int, int]:
        packed = self.to_id(code)
        packed_unsigned = self._java_long_to_unsigned(packed)
        hi_int = ctypes.c_int((packed_unsigned >> 32) & LongToCodeConverter.MASK32).value
        lo_int = ctypes.c_int(packed_unsigned & LongToCodeConverter.MASK32).value
        return hi_int, lo_int

    @classmethod
    def team_converter(cls) -> "LongToCodeConverter":
        return cls(code_suffix=cls.TEAM_TAG, conversion_chars=cls.TEAM_CONVERSION_CHARS)

    @classmethod
    def player_converter(cls) -> "LongToCodeConverter":
        return cls(code_suffix=cls.HASH_TAG, conversion_chars=cls.CONVERSION_CHARS)