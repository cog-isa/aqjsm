# coding=utf8
import numpy as np

import gaaq.ga_parameters as gap
from gaaq.population import cpopulation


# from multiprocessing import Pool

# Author: Alexander Shvets
# Date: 29.06.2016

class ccoevolution:
    def __init__(self, processed_data, numval_per_gen, pos_index, neg_index, uncov_pos):
        self.cn = gap.num_pop
        self.n = gap.pops_size
        self.pop = []
        self.buffpop = []
        for i in range(self.cn - 1):
            p = cpopulation()
            p.init(int(self.n / self.cn), processed_data, numval_per_gen, pos_index, neg_index, uncov_pos,
                   gap.ga_type[i], gap.sel_type[i], gap.tour_size[i], gap.elitism[i], gap.rec_type[i],
                   gap.pop_part_rec[i], gap.nmut_bits[i], gap.pop_part_distr[i])
            self.pop.append(p)
        p = cpopulation()
        p.init(int(self.n / self.cn) + int(self.n % self.cn), processed_data, numval_per_gen, pos_index, neg_index,
               uncov_pos,
               gap.ga_type[-1], gap.sel_type[-1], gap.tour_size[-1], gap.elitism[-1], gap.rec_type[-1],
               gap.pop_part_rec[-1], gap.nmut_bits[-1], gap.pop_part_distr[-1])
        self.pop.append(p)
        self.socialcard = int(0.05 * (self.n))
        self.socialfine = int(0.04 * (self.n / self.cn))
        self.ngen = gap.ngen
        self.nadapt = gap.nadapt
        self.coevbestgenotype = []
        self.coevbestgenotypefit = - np.inf
        self.coev_popstop = False
        self.generalgroup = cpopulation()
        self.losematrix = np.zeros((self.cn, self.cn), dtype=int)
        self.penlty = np.zeros((self.cn), dtype=int)

    def adaptation(self):
        # def adaptation_period(self, p):
        #    p.adaptfits = []
        #    for g in range(self.nadapt):
        #        p.one_ga_step()        
        # pl = Pool(self.cn)
        # pl.map(adaptation_period, self.pop)

        # slower on 35-40% then running one algorithm

        for pind, p in enumerate(self.pop):
            p.adaptfits = []
            for g in range(self.nadapt):
                p.one_ga_step()
                # print(pind, p.bestfit)
        '''
        def worker(pind):
            self.pop[pind].adaptfits = []
            for g in range(self.nadapt):
                self.pop[pind].one_ga_step()
            print(pind, self.pop[pind].bestfit)
                
        with ThreadPoolExecutor(max_workers=self.cn) as pool:
            print(len(self.pop))
            [pool.submit(worker, pind) for pind in range(self.cn)]
        '''
        for p in self.pop:
            p.rating = 0.0;
        for g in range(self.nadapt):
            bestalgfit = - np.inf
            bestalgindexes = []
            for ind, p in enumerate(self.pop):
                if (p.adaptfits[g] > bestalgfit):
                    bestalgfit = p.adaptfits[g]
                    bestalgindexes = [ind]
                elif (p.adaptfits[g] == bestalgfit):
                    bestalgindexes.append(ind)
            for balg in bestalgindexes:
                self.pop[balg].rating += (g + 1) * 1.0 / (self.nadapt - g)
        return

    def moveToGeneralGroup(self):
        data_indexes = []
        for i in range(self.cn):
            for j in range(self.pop[i].psize):
                data_indexes.append((i, j))
        sorted_indexes = range(self.n)
        sorted_indexes = sorted(sorted_indexes, key=lambda i: -self.pop[data_indexes[i][0]].fits[
            data_indexes[i][1]])  # descending order

        generalgroup = np.copy(self.pop[data_indexes[sorted_indexes[0]][0]].data[data_indexes[sorted_indexes[0]][1]])
        generalfits = np.copy(self.pop[data_indexes[sorted_indexes[0]][0]].fits[data_indexes[sorted_indexes[0]][1]])
        for ind in sorted_indexes[1:]:
            generalgroup = np.vstack((generalgroup, np.copy(self.pop[data_indexes[ind][0]].data[data_indexes[ind][1]])))
            generalfits = np.hstack((generalfits, np.copy(self.pop[data_indexes[ind][0]].fits[data_indexes[ind][1]])))

        return generalgroup, generalfits

    def moveOutOfGeneralGroup(self, generalgroup, generalfits):
        for p in self.pop:
            p.data = np.copy(generalgroup[:p.psize])
            p.fits = np.copy(generalfits[:p.psize])
            if p.bestgenotypefit < generalfits[0]:
                p.bestgenotype = np.copy(generalgroup[0])
                p.bestgenotypefit = generalfits[0]
            if self.coevbestgenotypefit < p.bestgenotypefit:
                self.coevbestgenotype = np.copy(p.bestgenotype)
                self.coevbestgenotypefit = p.bestgenotypefit
        return

    def moveOutOfGeneralGroup2(self, generalgroup, generalfits):
        for p in self.pop:
            sorted_indexes = range(p.prevpsize)
            sorted_indexes = sorted(sorted_indexes, key=lambda i: -p.fits[i])  # descending order
            if (p.psize < p.prevpsize):
                p.data[sorted_indexes[(p.psize - int(self.socialcard / 2.0)):p.psize]] = np.copy(
                    generalgroup[:int(self.socialcard / 2.0)])
                p.fits[sorted_indexes[(p.psize - int(self.socialcard / 2.0)):p.psize]] = np.copy(
                    generalfits[:int(self.socialcard / 2.0)])
                p.data = np.delete(p.data, sorted_indexes[p.psize:], axis=0)
                p.fits = np.delete(p.fits, sorted_indexes[p.psize:])
            else:
                while (len(p.data) < p.psize):
                    p.data = np.vstack((p.data, np.copy(p.data[sorted_indexes[:(p.psize - p.prevpsize)]])))
                    p.fits = np.hstack((p.fits, np.copy(p.fits[sorted_indexes[:(p.psize - p.prevpsize)]])))
                p.data[sorted_indexes[(p.prevpsize - int(self.socialcard / 2.0)):p.prevpsize]] = np.copy(
                    generalgroup[:int(self.socialcard / 2.0)])
                p.fits[sorted_indexes[(p.prevpsize - int(self.socialcard / 2.0)):p.prevpsize]] = np.copy(
                    generalfits[:int(self.socialcard / 2.0)])
            if p.bestgenotypefit < generalfits[0]:
                p.bestgenotype = np.copy(generalgroup[0])
                p.bestgenotypefit = generalfits[0]
            if self.coevbestgenotypefit < p.bestgenotypefit:
                self.coevbestgenotype = np.copy(p.bestgenotype)
                self.coevbestgenotypefit = p.bestgenotypefit
        return

    def changeResourses(self):
        generalgroup, generalfits = self.moveToGeneralGroup()

        for p in self.pop:
            p.prevpsize = p.psize

        self.losematrix = np.zeros((self.cn, self.cn), dtype=int)
        self.penlty = np.zeros((self.cn), dtype=int)
        for i in range(self.cn):
            numwins = 0
            for j in range(self.cn):
                if (self.pop[i].rating < self.pop[j].rating):
                    self.losematrix[i][j] = 1
                    numwins += 1

            if (self.pop[i].psize > self.socialcard):
                if ((self.pop[i].psize - (numwins * self.socialfine)) <= self.socialcard):
                    self.penlty[i] = int((self.pop[i].psize - self.socialcard) * 1.0 / numwins)
                else:
                    self.penlty[i] = self.socialfine

        for i in range(self.cn):
            for j in range(self.cn):
                if (self.losematrix[i][j] == 1):
                    self.pop[i].psize -= self.penlty[i]  # probably penalties should be less
                    self.pop[j].psize += self.penlty[i]

        # self.MoveOutOfGeneralGroup(generalgroup, generalfits)
        self.moveOutOfGeneralGroup2(generalgroup, generalfits)
        return

        # END OF CLASS CCOEVOLUTION


def run_coev_gaaq(processed_data, numval_per_gen, pos_index, neg_index, uncov_pos):
    coev_pop = ccoevolution(processed_data, numval_per_gen, pos_index, neg_index, uncov_pos)
    for i in range(gap.ngen):
        coev_pop.adaptation()
        coev_pop.changeResourses()
        print(i, coev_pop.coevbestgenotypefit)

    if len(coev_pop.coevbestgenotype):
        neg_cov, num_new_covered, num_all_not_miss, num_miss, rule_coverage, rule_exactcoverage, genes_has_ones = \
            coev_pop.pop[0].check_coverage(coev_pop.coevbestgenotype)
    else:
        neg_cov = num_new_covered = num_all_not_miss = num_miss = 0
        rule_coverage = []
        rule_exactcoverage = []
        genes_has_ones = []
    return neg_cov, num_new_covered, num_all_not_miss, num_miss, rule_coverage, rule_exactcoverage, genes_has_ones, coev_pop.coevbestgenotype, coev_pop.coevbestgenotypefit
