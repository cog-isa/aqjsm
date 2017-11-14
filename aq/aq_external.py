import subprocess
import sys, os
import re
import logging
import tempfile
from aq.aq_description import Fact, Rule, ClassDescription


def run_aq(data, class_column, column_names):
    input_text = _generate_input(data, class_column)

    f = tempfile.TemporaryFile(mode='w')
    f.write(input_text)
    f.close()

    ex_name = './aq/aq21' if sys.platform == 'linux' else 'aq/aq21.exe'
    logging.debug('Execute process: {0} {1}'.format(ex_name, f.name))
    output = subprocess.Popen([ex_name, f.name], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')

    os.remove(f.name)
    logging.debug('AQ output\n' + output)
    descriptions = _parse_result(output, column_names)

    return descriptions


def _generate_attrs(data):
    result = ''
    for column in data.columns:
        result += data[column].name
        if data[column].dtype.name == 'category':
            result += ' nominal {' + ', '.join(data[column].cat.categories) + '}'
        else:
            result += ' continuous ChiMerge 3'
        result += '\n'

    return result


def _generate_runs(data, class_column):
    result = ''
    for clazz in data[class_column].cat.categories:
        # Maxrule - количество ветвлений (чем меньше, тем быстрее работает)
        # Maxstar - // количество правил в памяти
        # Learning mode is used to select which algorithm will be used for rule learning. In TF (Theory
        # Formation) mode, learned rules are complete and consistent, while in PD (Pattern Discovery)
        # and ATF (Approximate Theory Formation) modes, they may be neither complete nor consistent.
        # Rules learned in PD and ATF modes are optimized according to value of Q(w). In the PD mode,
        # AQ21 optimizes rules while learning them (in the star generation phase), while in the ATF mode
        # initially complete and consistent rules are learned (as in the TF mode), but later the rules are
        # optimized according to their Q(w) measure, which may cause a loss of completeness and/or
        # consistency.
        result += """
    rules_for_{1}
    {{
        Ambiguity = IgnoreForLearning
        Consequent = [{0}={1}]
        Display_selectors_coverage = false
        Display_events_covered = false
        Maxrule = 5
        Maxstar = 2
        Mode = TF
    }}
        """.format(class_column, clazz)

    return result


def _generate_events(data):
    result = data.to_csv(None, sep=',', na_rep='?', index=False, header=False)
    return result


def _generate_input(data, class_column):
    text = """
Problem_description
{
	Building classRules for classes
}
Attributes
{
"""
    text += _generate_attrs(data)
    text += """
}

Runs
{
	Attribute_selection_method = promise
"""
    text += _generate_runs(data, class_column)
    text += """
}
Events
{
"""
    text += _generate_events(data)
    text += """
}
"""
    return text


def _parse_result(result, column_names):
    class_regex = re.compile(r'Output_Hypotheses rules_for_(\d+)\s+')
    num_regex = re.compile(r'Number of rules in the cover = (\d+)\s+')
    rule_regex = re.compile(r'# Rule (\d+)\s+<--([^:]+)')
    part_regex = re.compile(r'\s*\[' + Fact.canon_prefix + r'(\d+)=(\S+)\]')
    # For ATF mode
    # stat_regex = re.compile(r': p=(\d+),np=(\d+),n=(\d+),q=(\d+\.\d+),cx=(\d+),c=(\d+),s=(\d+) #')
    # For TF mode
    stat_regex = re.compile(r': p=(\d+),np=(\d+),u=(\d+),cx=(\d+),c=(\d+),s=(\d+) #')

    class_matcher = class_regex.findall(result)
    num_matcher = num_regex.findall(result)
    rule_matcher = rule_regex.findall(result)
    stat_matcher = stat_regex.findall(result)

    descriptions = {}
    if class_matcher and num_matcher and rule_matcher and stat_matcher:
        rule_nums = list(map(int, num_matcher))

        classes_for_rules = []
        for (name, nums) in zip(class_matcher, rule_nums):
            d = ClassDescription(name, [])
            descriptions[name] = d
            classes_for_rules.extend([d] * nums)
            logging.debug('For class {0} was found {1} rules'.format(name, nums))

        for i, ((rule_id, rule), (p, np, u, cx, c, s)) in enumerate(zip(rule_matcher, stat_matcher)):
            r = Rule(int(rule_id), [])
            r.covered_positives = int(p)
            # r.covered_negatives = int(n)
            r.complexity = int(cx)
            r.cost = int(c)
            r.significance = int(s)
            part_matcher = part_regex.findall(rule)
            if part_matcher:
                for (attr_id, value) in part_matcher:
                    f = Fact(int(attr_id), set(value.split(',')), column_names[int(attr_id)])
                    r.facts.append(f)

            classes_for_rules[i].rules.append(r)

    return descriptions
