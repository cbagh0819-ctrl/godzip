"""Pre-compression transform filters: Delta, Multi-byte Stride, and BCJ."""

import struct
from ..common.constants import (
    FILTER_NONE,
    FILTER_DELTA_1,
    FILTER_DELTA_2,
    FILTER_DELTA_3,
    FILTER_DELTA_4,
    FILTER_CHANNEL_3,
    FILTER_CHANNEL_4,
    FILTER_BCJ,
)


class PreFilter:
    """Lossless reversible pre-filters to reduce data entropy before compression."""

    @staticmethod
    def delta_encode(data: bytes, stride: int = 1) -> bytes:
        """Applies byte-delta transformation with a configurable byte stride."""
        if len(data) <= stride:
            return data
        out = bytearray(data)
        for i in range(len(data) - 1, stride - 1, -1):
            out[i] = (out[i] - out[i - stride]) & 0xFF
        return bytes(out)

    @staticmethod
    def delta_decode(data: bytes, stride: int = 1) -> bytes:
        """Inverts the byte-delta transformation exactly."""
        if len(data) <= stride:
            return data
        out = bytearray(data)
        for i in range(stride, len(data)):
            out[i] = (out[i - stride] + out[i]) & 0xFF
        return bytes(out)

    @staticmethod
    def channel_split(data: bytes, stride: int) -> bytes:
        """Separates interleaved multi-channel data (e.g. RGB RGB -> RRR GGG BBB)."""
        if stride <= 1 or len(data) < stride * 4:
            return data
        n = len(data)
        channels = [bytearray() for _ in range(stride)]
        for i in range(0, n - (n % stride), stride):
            for c in range(stride):
                channels[c].append(data[i + c])
        tail = data[n - (n % stride):]
        res = bytearray()
        for c in range(stride):
            res.extend(channels[c])
        res.extend(tail)
        return bytes(res)

    @staticmethod
    def channel_merge(data: bytes, stride: int) -> bytes:
        """Inverts channel separation back to interleaved channels."""
        if stride <= 1 or len(data) < stride * 4:
            return data
        n = len(data)
        usable = n - (n % stride)
        chan_len = usable // stride
        res = bytearray(n)
        for c in range(stride):
            c_offset = c * chan_len
            for i in range(chan_len):
                res[i * stride + c] = data[c_offset + i]
        for i in range(usable, n):
            res[i] = data[i]
        return bytes(res)

    @staticmethod
    def x86_bcj_encode(data: bytes) -> bytes:
        """Translates relative x86/x64 CALL/JMP targets to absolute addresses."""
        if len(data) < 5:
            return data
        out = bytearray(data)
        i = 0
        limit = len(data) - 5
        while i < limit:
            b = out[i]
            if b in (0xE8, 0xE9):
                rel = struct.unpack_from("<i", out, i + 1)[0]
                if -0x01000000 <= rel <= 0x01000000:
                    abs_addr = (rel + i + 5) & 0xFFFFFFFF
                    struct.pack_into("<I", out, i + 1, abs_addr)
                    i += 4
            i += 1
        return bytes(out)

    @staticmethod
    def x86_bcj_decode(data: bytes) -> bytes:
        """Inverts x86/x64 CALL/JMP target address translation."""
        if len(data) < 5:
            return data
        out = bytearray(data)
        i = 0
        limit = len(data) - 5
        while i < limit:
            b = out[i]
            if b in (0xE8, 0xE9):
                abs_addr = struct.unpack_from("<I", out, i + 1)[0]
                rel = (abs_addr - (i + 5)) & 0xFFFFFFFF
                if rel >= 0x80000000:
                    rel -= 0x100000000
                if -0x01000000 <= rel <= 0x01000000:
                    struct.pack_into("<i", out, i + 1, rel)
                    i += 4
            i += 1
        return bytes(out)


def apply_filter(data: bytes, filter_id: int) -> bytes:
    """Applies the specified pre-filter transformation to the data."""
    if filter_id == FILTER_NONE or not data:
        return data
    elif filter_id == FILTER_DELTA_1:
        return PreFilter.delta_encode(data, 1)
    elif filter_id == FILTER_DELTA_2:
        return PreFilter.delta_encode(data, 2)
    elif filter_id == FILTER_DELTA_3:
        return PreFilter.delta_encode(data, 3)
    elif filter_id == FILTER_DELTA_4:
        return PreFilter.delta_encode(data, 4)
    elif filter_id == FILTER_CHANNEL_3:
        # Channel split + delta on each channel
        return PreFilter.delta_encode(PreFilter.channel_split(data, 3), 1)
    elif filter_id == FILTER_CHANNEL_4:
        return PreFilter.delta_encode(PreFilter.channel_split(data, 4), 1)
    elif filter_id == FILTER_BCJ:
        return PreFilter.x86_bcj_encode(data)
    return data


def invert_filter(data: bytes, filter_id: int) -> bytes:
    """Inverts the specified pre-filter transformation, returning exact original bytes."""
    if filter_id == FILTER_NONE or not data:
        return data
    elif filter_id == FILTER_DELTA_1:
        return PreFilter.delta_decode(data, 1)
    elif filter_id == FILTER_DELTA_2:
        return PreFilter.delta_decode(data, 2)
    elif filter_id == FILTER_DELTA_3:
        return PreFilter.delta_decode(data, 3)
    elif filter_id == FILTER_DELTA_4:
        return PreFilter.delta_decode(data, 4)
    elif filter_id == FILTER_CHANNEL_3:
        return PreFilter.channel_merge(PreFilter.delta_decode(data, 1), 3)
    elif filter_id == FILTER_CHANNEL_4:
        return PreFilter.channel_merge(PreFilter.delta_decode(data, 1), 4)
    elif filter_id == FILTER_BCJ:
        return PreFilter.x86_bcj_decode(data)
    return data
