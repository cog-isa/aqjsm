class Fact:
    canon_prefix = 'attr_'

    def __init__(self, attr_id, values, attr_name=''):
        self.attr_id = attr_id
        self.values = frozenset(values)
        self.attr_name = attr_name
        self.coverage = 0
        self.canon_attr_name = Fact.canon_prefix + str(attr_id)

    def __str__(self):
        value = ''
        if self.values == {'1'}:
            value = 'o__'
        if self.values == {'2'}:
            value = '_o_'
        if self.values == {'3'}:
            value = '__o'
        if self.values == {'1', '2'}:
            value = 'oo_'
        if self.values == {'2', '3'}:
            value = '_oo'
        if self.values == {'1', '3'}:
            value = 'o_o'
        return '"{1}"={0}'.format(value, self.attr_name)

    def __hash__(self):
        return 3*self.attr_id + 5*hash(self.values)

    def __repr__(self):
        return '{0}={1}'.format(self.canon_attr_name, self.values)

    def __eq__(self, other):
        return self.attr_id == other.attr_id and self.values == other.values


class Rule:
    def __init__(self, rid, facts, covered_positives=0, covered_negatives=0,
                 complexity=0, cost=0, significance=0):
        self.rid = rid
        if facts:
            self.facts = facts
        else:
            self.facts = []

        self.covered_positives = covered_positives
        self.covered_negatives = covered_negatives
        self.complexity = complexity
        self.cost = cost
        self.significance = significance

    def __str__(self):
        return 'Rule {0} (p={1},n={2},cx={3},c={4},s={5}):\n\t'.format(self.rid,
                                                                       self.covered_positives, self.covered_negatives,
                                                                       self.complexity, self.cost,
                                                                       self.significance) + '\n\t'.join(
            [str(fact) for fact in self.facts])

    def __repr__(self):
        return '(' + ' '.join(repr(fact) for fact in self.facts) + ')'


class ClassDescription:
    def __init__(self, class_name, rules):
        self.class_name = class_name

        if rules:
            self.rules = rules
        else:
            self.rules = []
        self.properties = []

    def __str__(self):
        return 'Description of class {0} ({1} properties):\n\t'.format(self.class_name,
                                                                       len(self.properties)) + '\n\t'.join(
            ['{0:>3}: '.format(r.coverage) + str(r) for r in self.properties])

    def __repr__(self):
        return '[{0}]'.format(' '.join([repr(r) for r in self.properties]))

    def build(self, max_universe_size):
        for rule in self.rules:
            coverage = rule.covered_positives
            for fact in rule.facts:
                fact.coverage = coverage
                for prop in self.properties[:]:
                    if prop.attr_id == fact.attr_id:
                        appended = prop
                        if fact.values > prop.values or (not fact.values < prop.values and fact.coverage > prop.coverage):
                            self.properties.remove(prop)
                            self.properties.append(fact)
                            appended = fact
                        appended.coverage = max(prop.coverage, fact.coverage)
                        break
                else:
                    self.properties.append(fact)

        self.properties.sort(key=lambda x: (x.coverage, x.attr_name), reverse=True)
        self.properties = self.properties[:max_universe_size]
