import pytest

from wordle_guess import evaluate_single_guess, give_result_for_guess


@pytest.mark.parametrize(
    "guess,word,expected",
    (
        ("crane", "ample", "c0r0a2n0e1"),
        ("halve", "ample", "h0a2l2v0e1"),
        ("alike", "ample", "a1l2i0k0e1"),
        ("amble", "ample", "a1m1b0l1e1"),
        ("ample", "ample", "a1m1p1l1e1"),
        ("tweet", "ample", "t0w0e2e0t0"),
        ("tweet", "teddy", "t1w0e2e0t0"),
        ("ample", "algae", "a1m0p0l2e1"),
    ),
)
def test_give_result_for_word(guess, word, expected):
    assert give_result_for_guess(guess, word) == expected


@pytest.mark.parametrize(
    "guess, expected_set",
    (
        (
            "a1l2g2a0e1",
            {"agile"},
        ),
        (
            "c1r2a2n0e0",
            {"carol", "cargo", "cobra", "carat", "cigar", "circa", "coral", "carry"},
        ),
        (
            "t0w1e1e2t1",
            {},
        ),
        ("e2n0t2e2r0", {"theme", "tease", "teeth", "these"}),
    ),
)
def test_evaluate_single_guess(guess, expected_set):
    possible_set = evaluate_single_guess(guess)
    print(possible_set)
    assert possible_set == frozenset(expected_set)
