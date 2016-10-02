import itertools
import logging

import pandas as pd
from bitarray import bitarray
from aq.aq_description import Fact


class FactBase:
    def __init__(self, target_prop):
        self.target_prop = target_prop
        self.positives = {}
        self.negatives = {}
        self.properties = []
        self.num_events = 0
        self.num_props = 0

    def __str__(self):
        return 'FactBase for property {0} ({1} props, {2} events: p={3}, n={4}):\n\t'.format(self.target_prop,
                                                                                             len(self.properties),
                                                                                             self.num_events,
                                                                                             len(self.positives),
                                                                                             len(
                                                                                                 self.negatives)) + '\n\t'.join(
            [b.to01() for b in itertools.chain(self.positives.values(), self.negatives.values())])

    def __repr__(self):
        return 'FactBase for property {0} (p={1}, n={2}):\n\t'.format(self.target_prop,
                                                                      len(self.positives), len(self.negatives))

    def build(self, data, class_description):
        target_index = data.columns.get_loc(self.target_prop.canon_attr_name)
        self.properties = [prop for prop in class_description.properties if not prop == self.target_prop]
        self.num_props = len(self.properties)
        dup_counter = 0
        miss_counter = 0
        for i, row in data.iterrows():
            data_value = row[target_index]
            if not pd.isnull(data_value):
                b = bitarray(self.num_props)
                for j, prop in enumerate(self.properties):
                    value = row[prop.attr_id]
                    b[j] = False if pd.isnull(value) else value in prop.values
                if data_value in self.target_prop.values and b not in self.positives.values():
                    self.positives[i] = b
                elif data_value not in self.target_prop.values and b not in self.negatives.values():
                    self.negatives[i] = b
                else:
                    dup_counter += 1
            else:
                miss_counter += 1
        self.num_events = len(self.positives) + len(self.negatives)
        logging.debug('\tDelete {0} duplicated events'.format(dup_counter))
        logging.debug('\tMiss {0} missing target column events'.format(miss_counter))

    def clear(self):
        counter = 0
        for key in list(self.negatives.keys()):
            if self.negatives[key] in self.positives.values():
                del self.negatives[key]
                counter += 1
        self.num_events -= counter
        logging.debug('\tDelete {0} conflicted events'.format(counter))


class JSMHypothesis:
    def __init__(self, value, generator):
        self.value = value
        self.generator = generator

    def __str__(self):
        return 'Hypothesis {0} by {1}'.format(self.value.to01(), [i for i, x in enumerate(self.generator) if x])

    def __repr__(self):
        return self.value.to01()

    def __eq__(self, other):
        return self.value == other.value and self.generator == other.generator

    def __ge__(self, other):
        return ((self.value | other.value) == self.value) and ((self.generator | other.generator) == self.generator)

    def __hash__(self):
        return 3 * hash(self.value.to01()) + 5 * hash(str(self.generator))


def search_norris(fb):
    if fb.positives:
        pos_inters = _search_norris(fb.positives)
        neg_inters = _search_norris(fb.negatives)

        logging.debug('\tIt was found {0} pos and {1} neg hypothesis'.format(len(pos_inters), len(neg_inters)))
        conf_counter, dup_counter = 0, 0
        for p_inter in pos_inters[:]:
            for n_inter in neg_inters:
                unit = p_inter.value | n_inter.value
                if len(p_inter.generator) < 2 or unit == p_inter.value or unit == n_inter.value:
                    pos_inters.remove(p_inter)
                    conf_counter += 1
                    break

        l = pos_inters[:]
        for i, tmp1 in enumerate(l):
            for j, tmp2 in enumerate(l):
                if not i == j and (tmp1.value | tmp2.value) == tmp1.value:
                    pos_inters.remove(tmp1)
                    dup_counter += 1
                    break

        logging.debug('\tIt were deleted {0} conflicted and {1} surplus hypothesis'.format(conf_counter, dup_counter))

        return pos_inters
    else:
        logging.debug('\tThere is no positives examples in FB')
        return None


def _search_norris(positives):
    # Relation R=AxB, A - objects, B - features, Mk - maximal rectangles (maximal intersections)
    hypotheses = []
    b = bitarray(max(positives.keys()) + 1)
    b.setall(0)
    for key, value in positives.items():  # find object xkR
        # compute collection Tk={Ax(B intersect xkR): AxB in Mk-1}
        tmp_gen = [JSMHypothesis(value & h.value, h.generator.copy()) for h in hypotheses]
        # eliminate the members of Tk which are proper subsets of other members of Tk;
        # remaining sets are the members of T'k

        tmp_hyps = []
        for i, tmp1 in enumerate(tmp_gen):
            if tmp1.value.any():
                for j, tmp2 in enumerate(tmp_gen):
                    if not i == j and tmp2 >= tmp1:
                        tmp_hyps.append(None)
                        break
                else:
                    tmp_hyps.append(tmp1)
            else:
                tmp_hyps.append(None)

        # for each CxD in    Mk-1
        new_hyps = []
        add_example = True
        for i, hyp in enumerate(hypotheses):
            # if D subsetoreq xkR then (C unite xk)xD in Mk
            if (hyp.value | value) == value:
                hyp.generator[key] = 1
            else:
                # if D not susetoreq xkR then CxD in Mk, and (C unite xk)x(D intersect xkR) in Mk
                # if and only if emptyset noteq Cx(D intersect xkR) in T'k
                new_hyp = tmp_hyps[i]
                if new_hyp:
                    new_hyp.generator[key] = 1
                    new_hyps.append(new_hyp)
            if not value.any() or (hyp.value | value) == hyp.value:
                add_example = False

        hypotheses.extend(new_hyps)
        # xk x xkR in Mk if and only if emptyset noteq xkR notsubsetoreq D for all XxD in Mk - 1
        if add_example:
            c = b.copy()
            c[key] = 1
            hypotheses.append(JSMHypothesis(value, c))
    return hypotheses


def test1():
    fb = FactBase(Fact(0, {'1'}))
    fb.positives = {1: bitarray('11000'), 2: bitarray('11010'), 3: bitarray('11100')}
    fb.negatives = {4: bitarray('00101'), 5: bitarray('00110'), 6: bitarray('00011')}

    hypotheses = search_norris(fb)
    hyp1 = hypotheses
    # print('\n'.join(map(str, hypotheses)))
    return hyp1


def test2():  # square
    fb = FactBase(Fact(0, {'1'}))
    fb.positives = {1: bitarray('111100100'), 2: bitarray('010101010'), 3: bitarray('011001101')}
    fb.negatives = {4: bitarray('111010011'), 5: bitarray('100011011'), 6: bitarray('011001011')}

    hypotheses = search_norris(fb)
    hyp2 = hypotheses
    # print('\n'.join(map(str, hypotheses)))
    return hyp2


def test3():  # my test
    fb = FactBase(Fact(0, {'1'}))
    fb.positives = {1: bitarray('11100'), 2: bitarray('10011'), 3: bitarray('11011')}
    fb.negatives = {4: bitarray('10001'), 5: bitarray('01110'), 6: bitarray('01010')}

    hypotheses = search_norris(fb)
    hyp3 = hypotheses
    # print('\n'.join(map(str, hypotheses)))
    return hyp3


if __name__ == '__main__':
    # print('\nStart test 1 :')
    # t1 = test1()
    print('\nStart test 2 :')
    t2 = test2()
    print(t2)
    # print('\nStart test 3 :')
    # t3 = test3()
