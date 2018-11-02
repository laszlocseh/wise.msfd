DEFAULT_RANGES = [
    [76, 100],
    [51, 75],
    [26, 50],
    [1, 25],
    [0, 1],
]


def get_percentage(values):
    """ Compute percentage of True values in the list
    """
    trues = len([x for x in values if x is True])

    return (trues * 100.0) / len(values)


def alternative_based(args):
    true_values = map(int, filter(None, args.strip().split(' ')))

    def calculate(values):
        acc = []

        for v in values:
            if v in true_values:
                acc.append(True)
            else:
                acc.append(False)

        p = get_percentage(acc)

        for x, r in enumerate(reversed(DEFAULT_RANGES)):
            if (p >= r[0]) and (p <= r[1]):
                return x

        # TODO: offer default value here as return?

    return calculate


CONCLUSIONS = [
    'Very good',
    'Good',
    'Poor',
    'Very poor',
    'Not reported',
]


def compute_score(question, descriptor, values):
    raw_score = question.score_method(values)

    weight = question.score_weights.get(descriptor, 10.0)
    score = raw_score * weight / 4
    conclusion = list(reversed(CONCLUSIONS))[raw_score]

    return conclusion, raw_score, score
