# BASED ON https://github.com/markmliu/solve_wordle/blob/main/solve_wordle.py

from os.path import exists
from scipy.stats import entropy
from itertools import product
import pickle
import tqdm


def read_dataset(file):
    dataset = []
    with open(file, 'r') as f:
        for line in f:
            dataset.append(line.strip('\n'))

    dataset.sort()
    return dataset


def does_not_have_letter(word, letter, pos):
    return word.find(letter) == -1


def has_letter_at_pos(word, letter, pos):
    return word[pos] == letter


def has_letter_not_at_pos(word, letter, pos):
    if has_letter_at_pos(word, letter, pos):
        return False

    return word.find(letter) != -1


def calculate_entropy(query, word_list):
    counts = []
    for comb in product([has_letter_at_pos, has_letter_not_at_pos, does_not_have_letter], repeat=5):
        count = 0
        for word in word_list:
            if all([comb[i](word, query[i], i) for i in range(5)]):
                count += 1
        counts.append(count)

    probs = [float(count)/len(word_list) for count in counts]

    return entropy(probs, base=2)


def best_guess(word_list, use_cache):
    entrop_dict = {}

    if exists('entropy.pickle') and use_cache:
        with open('entropy.pickle', 'rb') as f:
            entrop_dict = pickle.load(f)

    count = len(entrop_dict)
    for query in tqdm.tqdm(word_list):
        if entrop_dict.get(query) != None:
            continue

        entrop_dict[query] = calculate_entropy(query, word_list)
        if count % 10 == 0 and use_cache:
            with open('entropy.pickle', 'wb') as f:
                pickle.dump(entrop_dict, f, pickle.HIGHEST_PROTOCOL)
        count += 1

    best_word = max(entrop_dict, key=entrop_dict.get)
    entrop = entrop_dict[best_word]
    return (best_word, entrop)


def constrained_dataset(dataset, query, constraints):
    constraint_dict = {
        'x': does_not_have_letter,
        'o': has_letter_not_at_pos,
        't': has_letter_at_pos
    }

    out_set = []
    for word in dataset:
        const = [constraint_dict[c](word, query[i], i)
                 for i, c in enumerate(constraints)]

        if all(const):
            out_set.append(word)

    return out_set


if __name__ == '__main__':
    while(True):
        dataset = read_dataset('wordle.txt')
        use_cache = True

        while len(dataset) > 1:
            guess = best_guess(dataset, use_cache)

            print(f"Best guess {guess[0]} (entropy: {guess[1]})")
            constraint = input(
                f"Contraints of guess {guess[0].upper()}: ").lower()

            dataset = constrained_dataset(dataset, guess[0], constraint)

            use_cache = False
