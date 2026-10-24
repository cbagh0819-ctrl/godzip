"""Tests verifying block deduplication."""

from godzip.dedup.index import DeduplicationIndex
from godzip.integrity.hasher import Hasher


def test_dedup_index():
    index = DeduplicationIndex()
    block_a = b"Common repeated chunk content" * 10
    hash_a = Hasher.compute(block_a)

    assert index.lookup(hash_a) is None

    index.register(hash_a, block_id=0, uncompressed_size=len(block_a))
    lookup_res = index.lookup(hash_a)
    assert lookup_res is not None
    assert lookup_res[0] == 0
    assert lookup_res[1] == len(block_a)
