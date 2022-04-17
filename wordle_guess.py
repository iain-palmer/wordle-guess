import random
from enum import Enum
from functools import lru_cache
from typing import Counter

from words import WORDS_LIST, WORDS_SET


class MatchType(Enum):
    NOMATCH = "0"
    MATCH = "1"
    PRESENT = "2"
    NOMATCH_ZERO = 0
    NOMATCH_ONE = 1
    NOMATCH_TWO = 2
    NOMATCH_THREE = 3
    NOMATCH_FOUR = 4
    PRESENT_ONE = 10
    PRESENT_TWO = 20
    PRESENT_THREE = 30
    PRESENT_FOUR = 40


@lru_cache
def evaluate_multiple_guesses(
    guesses: tuple[
        str,
    ]
) -> set:
    possible_sets = [evaluate_single_guess(guess) for guess in guesses]
    return set.intersection(*map(set, possible_sets))


def evaluate_match_types(guess):
    letters = guess[0::2]
    match_types = [MatchType(match_type) for match_type in guess[1::2]]
    new_match_types = list(match_types)
    for pos, (letter, match_type) in enumerate(zip(letters, match_types)):
        if match_type is MatchType.NOMATCH:
            n_matches = list(zip(letters, match_types)).count(
                (letter, MatchType.MATCH)
            ) + list(zip(letters, match_types)).count((letter, MatchType.PRESENT))
            new_match_types[pos] = MatchType(n_matches)
        elif match_type is MatchType.PRESENT:
            n_matches = list(zip(letters, match_types)).count(
                (letter, MatchType.MATCH)
            ) + list(zip(letters, match_types)).count((letter, MatchType.PRESENT))
            new_match_types[pos] = MatchType(n_matches * 10)
    return new_match_types


@lru_cache()
def evaluate_single_guess(guess: str) -> set:
    match_types = evaluate_match_types(guess)
    possible_set = WORDS_SET

    for match_types_to_evaluate in (
        (MatchType.MATCH,),
        (
            MatchType.PRESENT_ONE,
            MatchType.PRESENT_TWO,
            MatchType.PRESENT_THREE,
            MatchType.PRESENT_FOUR,
        ),
        (
            MatchType.NOMATCH_ZERO,
            MatchType.NOMATCH_ONE,
            MatchType.NOMATCH_TWO,
            MatchType.NOMATCH_THREE,
            MatchType.NOMATCH_FOUR,
        ),
    ):
        for pos, (letter, match_type) in enumerate(zip(guess[0::2], match_types)):
            if match_type in match_types_to_evaluate:
                possible_set = evaluate_single_letter(
                    pos, letter, MatchType(match_type), possible_set
                )

    return possible_set


@lru_cache()
def get_present(pos, letter, current_set, existing_matches):
    return frozenset(
        [
            word
            for word in current_set
            if word.count(letter) >= existing_matches and word[pos] != letter
        ]
    )


@lru_cache()
def get_matches(pos, letter, current_set):
    return frozenset([word for word in current_set if word[pos] == letter])


@lru_cache()
def get_nomatches(pos, letter, current_set, existing_matches):
    if existing_matches == 0:
        return frozenset([word for word in current_set if letter not in word])
    return frozenset(
        [
            word
            for word in current_set
            if word.count(letter) == existing_matches and word[pos] != letter
        ]
    )


@lru_cache()
def evaluate_single_letter(
    pos: int,
    letter: str,
    match_type: MatchType,
    current_set: frozenset = frozenset(WORDS_SET),
):
    match match_type:
        case MatchType.NOMATCH_ZERO:
            return get_nomatches(pos, letter, current_set, 0)
        case MatchType.NOMATCH_ONE:
            return get_nomatches(pos, letter, current_set, 1)
        case MatchType.NOMATCH_TWO:
            return get_nomatches(pos, letter, current_set, 2)
        case MatchType.NOMATCH_THREE:
            return get_nomatches(pos, letter, current_set, 3)
        case MatchType.NOMATCH_FOUR:
            return get_nomatches(pos, letter, current_set, 4)
        case MatchType.MATCH:
            return get_matches(pos, letter, current_set)
        case MatchType.PRESENT_ONE:
            return get_present(pos, letter, current_set, 1)
        case MatchType.PRESENT_TWO:
            return get_present(pos, letter, current_set, 2)
        case MatchType.PRESENT_THREE:
            return get_present(pos, letter, current_set, 3)
        case MatchType.PRESENT_FOUR:
            return get_present(pos, letter, current_set, 4)


def give_result_for_guess(guess, word):
    result = [f"{letter}" for letter in guess]
    guess_count = Counter(word)
    word_count = Counter()
    for pos, letter in enumerate(guess):
        if letter not in word:
            result[pos] += "0"
        elif letter == word[pos]:
            result[pos] += "1"
            word_count[letter] += 1
    for pos, letter in enumerate(guess):
        if letter in word and letter != word[pos]:
            if word_count[letter] < guess_count[letter]:
                result[pos] += "2"
                word_count[letter] += 1
            else:
                result[pos] += "0"
    return "".join(i for i in result)


def evaluate_next_guesses(guesses):
    next_guesses = evaluate_multiple_guesses(guesses)
    evaluations = []
    for guess in next_guesses:
        options = 0
        for word in next_guesses:
            try_guesses = list(guesses) + [give_result_for_guess(guess, word)]
            options += len(evaluate_multiple_guesses(tuple(try_guesses)))
        evaluations.append([guess, options / len(next_guesses)])
    return sorted(evaluations, key=lambda x: (x[1], x[0]))


def main(starter_word="crane", n_games=100):
    counter = Counter()
    for i in range(n_games):
        word = random.choice(WORDS_LIST)
        next_guess = starter_word
        guesses = []
        results = []
        attempts = 1
        while True:
            guess = give_result_for_guess(next_guess, word)
            guesses.append(next_guess)
            if next_guess == word:
                break
            results.append(guess)
            next_guess = evaluate_next_guesses(tuple(results))[0][0]
            attempts += 1
        print(i, word, attempts, guesses)
        counter[attempts] += 1
    return counter


if __name__ == "__main__":
    random.seed(0)
    counter_raise = main(starter_word="raise", n_games=500)
    random.seed(0)
    counter_crane = main(starter_word="crane", n_games=500)
    random.seed(0)
    counter_dealt = main(starter_word="dealt", n_games=500)
    counter_mean = (
        lambda counter: sum(key * count for key, count in counter.items())
        / counter.total()
    )
    print("raise", counter_raise, counter_mean(counter_raise))
    print("crane", counter_crane, counter_mean(counter_crane))
    print("dealt", counter_dealt, counter_mean(counter_dealt))
