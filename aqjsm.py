import data.data_loading as dl
import aq.aq_external as aq
from jsm.jsm_analysis import FactBase, search_norris
from aq.aq_description import Fact
import sys, platform, datetime
import argparse
import logging
import cProfile
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

log_levels = ['debug', 'info', 'warning', 'error']

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='AQJSM causal relations miner',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument(dest='datafile')
    argparser.add_argument('-l', '--loglevel', choices=log_levels, default='info',
                           help='Logging level')
    argparser.add_argument('-s', '--reasonsize', type=int, default='3',
                           help='Maximum size of causes for filtering')
    argparser.add_argument('-u', '--univer', type=int, default='30',
                           help='Maximum size of the set of class properties')
    argparser.add_argument('-c', '--classid', type=int, required=True,
                           help='Index of class column in data file (starting from 0)')
    argparser.add_argument('-n', '--nominaldata',
                           help='Data string of information about nominal columns in format: <col_id1>:<nom1>,<nom2>,...;<col_id2>:<nom1>...')
    args = argparser.parse_args()

    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter('%(asctime)s %(levelname)-8s  %(message)s', datefmt='%H:%M:%S')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    fileHandler = logging.FileHandler('aqjsm.log', encoding='cp1251')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(args.loglevel.upper())

    logging.info('OS: {0}, date: {1}'.format(platform.platform(), datetime.datetime.now().strftime("%Y-%m-%d")))
    logging.info(args)
    max_universe_size = args.univer
    max_reason_length = args.reasonsize
    class_index = args.classid
    nominal_data = args.nominaldata

    data, class_column = dl.load_data(args.datafile, class_index, nominal_data)
    logging.info('Data file {0}: {2} columns, {3} objects, class column is "{1}"'.format(args.datafile,
                                                                                         dl.column_names[class_index],
                                                                                         *reversed(data.shape)))
    logging.debug('\n\t'.join(['"{0}": {1}'.format(key, dl.column_ranges[key]) for key in sorted(dl.column_ranges)]))

    class_descriptions = aq.run_aq(data, class_column, dl.column_names)
    for desc in class_descriptions.values():
        desc.build(max_universe_size)
    logging.info('\n'.join([str(class_descriptions[d]) for d in class_descriptions]))

    for klass in data[class_column].unique():
        logging.info('\n' * 3 + '*' * 5 + 'Start search reasons for class {0}'.format(klass) + '*' * 5)
        logging.info('Start search reasons for class property {0}'.format(klass))
        fb = FactBase(Fact(class_index, {klass}, 'class'))
        fb.build(data, class_descriptions[klass])
        fb.clear()


        def _search_in_fb(data_fb, target):
            hypotheses = search_norris(data_fb)
            reasons = []
            for hyp in hypotheses:
                if hyp.value.count() <= max_reason_length:
                    reasons.append((hyp.generator.count(),
                                    [data_fb.properties[i] for i in range(len(hyp.value)) if
                                     hyp.value[i]]))
            if reasons:
                reasons.sort(key=lambda x: x[0], reverse=True)
                logging.info('\tFound {0} reasons for {1}:\n\t'.format(len(reasons), target) + '\n\t'.join(
                    ['[{0}]: '.format(q) + ' & '.join([str(f) for f in r]) for q, r in reasons]))
            else:
                logging.debug('\tWas not found reasons for {0}'.format(target))


        # pr = cProfile.Profile()
        # pr.enable()
        # with PyCallGraph(output=GraphvizOutput()):
        _search_in_fb(fb, 'class ' + klass)
        # pr.disable()
        # pr.print_stats(sort="calls")
        # exit()

        for prop in class_descriptions[klass].properties:
            logging.info('Start search reasons for property {0}'.format(prop))
            fb = FactBase(prop)
            fb.build(data, class_descriptions[klass])
            fb.clear()

            _search_in_fb(fb, prop)
