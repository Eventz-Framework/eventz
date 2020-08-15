import pytest

from eventz.immutable_sequence import ImmutableSequence


def test_immutable_sequence_can_be_made_from_a_list():
    seq = ImmutableSequence([1, 2, 3, 4, 5])
    assert len(seq) == 5
    for idx, val in enumerate(seq):
        assert seq[idx] == idx + 1
    with pytest.raises(AttributeError):
        assert seq.append(6)
    with pytest.raises(AttributeError):
        assert seq.add(6)
    with pytest.raises(TypeError):
        seq[0] = 6


def test_immutable_sequence_can_be_made_from_a_set():
    seq = ImmutableSequence({1, 2, 3, 4, 5})
    assert len(seq) == 5


def test_immutable_sequence_can_be_made_from_a_tuple():
    seq = ImmutableSequence((1, 2, 3, 4, 5))
    assert len(seq) == 5


def test_two_immutable_sequences_with_the_same_data_are_equal():
    seq1 = ImmutableSequence((1, 2, 3, 4, 5))
    seq2 = ImmutableSequence((1, 2, 3, 4, 5))
    seq3 = ImmutableSequence((5, 4, 3, 2, 1))
    assert seq1 == seq2
    assert (seq1 != seq3) is True


def test_equality_with_others_types_works_correctly():
    seq1 = ImmutableSequence((1, 2, 3, 4, 5))
    assert seq1 != 1
    assert (seq1 == 1) is False


def test_repr():
    seq1 = ImmutableSequence((1, 2, 3, 4, 5))
    assert repr(seq1) == "ImmutableSequence(_items=(1, 2, 3, 4, 5))"
