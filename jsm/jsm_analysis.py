import itertools
import math
from bitarray import bitarray
import logging


class FactBase:
    def __init__(self, target_column, target_values):
        self.target_column = target_column
        self.target_values = target_values
        self.positives = {}
        self.negatives = {}
        self.properties = []
        self.num_events = 0

    def __str__(self):
        return 'FactBase for property {0} {1} ({2} props, {3} events: p={4}, n={5}):\n\t'.format(self.target_column,
                                                                                                 self.target_values,
                                                                                                 len(self.properties),
                                                                                                 self.num_events,
                                                                                                 len(self.positives),
                                                                                                 len(
                                                                                                     self.negatives)) + '\n\t'.join(
            [b.to01() for b in itertools.chain(self.positives.values(), self.negatives.values())])

    def __repr__(self):
        return 'FactBase for property {0} {1} (p={2}, n={3}):\n\t'.format(self.target_column, self.target_values,
                                                                          len(self.positives), len(self.negatives))

    def build(self, data, class_description):
        target_index = data.columns.get_loc(self.target_column)
        self.properties = [prop for i, prop in enumerate(class_description.properties) if
                           not prop.attr_name == self.target_column]
        self.num_events = len(data.values)
        dup_counter = 0
        miss_counter = 0
        for i, row in enumerate(data.values):
            data_value = row[target_index]
            if not math.isnan(float(data_value)):
                b = bitarray(len(self.properties))
                for j, prop in enumerate(self.properties):
                    value = row[prop.attr_id]
                    b[j] = False if math.isnan(float(value)) else int(value) in prop.values
                if int(data_value) in self.target_values and b not in self.positives.values():
                    self.positives[i] = b
                elif b not in self.negatives.values():
                    self.negatives[i] = b
                else:
                    dup_counter += 1
            else:
                miss_counter += 1
        logging.debug('\tDelete {0} duplicated events'.format(dup_counter))
        logging.debug('\tMiss {0} missing target column events'.format(miss_counter))

    def clear(self):
        counter = 0
        for key in list(self.negatives.keys()):
            if self.negatives[key] in self.positives.values():
                del self.negatives[key]
                counter += 1
        logging.debug('\tDelete {0} conflicted events'.format(counter))


class JSMHypothesis:
    def __init__(self, value, generator=None):
        self.value = value
        if generator:
            self.generator = generator
        else:
            self.generator = set()

    def __str__(self):
        return 'Hypothesis {0} by {1}'.format(self.value.to01(), self.generator)

    def __repr__(self):
        return self.value.to01()

    def __eq__(self, other):
        return self.value == other.value and self.generator == other.generator

    def __hash__(self):
        return 3 * hash(self.value.to01()) + 5 * hash(str(self.generator))


def search_norris(fb):
    pos_inters = _search_norris(fb.positives)
    neg_inters = _search_norris(fb.negatives)

    sparse = []
    for i, p_inter in enumerate(pos_inters):
        for n_inter in neg_inters:
            unit = p_inter.value | n_inter.value
            if len(p_inter.generator) < 2 or unit == p_inter.value or unit == n_inter.value:
                sparse.append(i)

    pos_inters = [pos_inters[i] for i in range(len(pos_inters)) if i not in sparse]
    return pos_inters


def _search_norris(positives):
    # Relation R=AxB, A - objects, B - features, Mk - maximal rectangles (maximal intersections)
    hypotheses = []
    for key, value in positives.items():
        # compute collection Tk={Ax(B intersect xkR): AxB in Mk-1}
        tmp_hyps = [JSMHypothesis(value & h.value, h.generator) for h in hypotheses if (value & h.value).any()]
        # eliminate the members of Tk which are proper subsets of other members of Tk;
        # remaining sets are the members of T'k
        spares = set()
        for i in range(len(tmp_hyps)):
            for j in range(len(tmp_hyps)):
                if not i == j and (tmp_hyps[i].value | tmp_hyps[j].value) == tmp_hyps[j].value and tmp_hyps[
                    j].generator >= tmp_hyps[i].generator:
                    spares.add(i)
        tmp_hyps = [tmp_hyps[i] for i in range(len(tmp_hyps)) if i not in spares]

        # for each CxD in    Mk-1
        new_hyps = []
        add_example = True
        for hyp in hypotheses:
            # if D subsetoreq xkR then (C unite xk)xD in Mk
            if (hyp.value | value) == value:
                hyp.generator.add(key)
            else:
                # if D not susetoreq xkR then CxD in Mk, and (C unite xk)x(D intersect xkR) in Mk
                # if and only if emptyset noteq Cx(D intersect xkR) in T'k
                new_hyp = JSMHypothesis(hyp.value & value, hyp.generator)
                if new_hyp.value.any() and new_hyp in tmp_hyps:
                    new_hyps.append(new_hyp)
            if not value.any() or (hyp.value | value) == hyp.value:
                add_example = False

        hypotheses.extend(new_hyps)
        if add_example:
            hypotheses.append(JSMHypothesis(value, {key}))
    return hypotheses


if __name__ == '__main__':
    fb = FactBase(0, '1')
    fb.positives = {1: bitarray('11000'), 2: bitarray('11010'), 3: bitarray('11100')}
    fb.negatives = {4: bitarray('00101'), 5: bitarray('00110'), 6: bitarray('00011')}

    hypotheses = search_norris(fb)
    print('\n'.join(map(str, hypotheses)))
