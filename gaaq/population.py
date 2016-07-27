# coding=utf8
import numpy as np
import numpy.random as rand
import gaaq.ga_parameters as gap


# Author: Alexander Shvets
# Date: 29.06.2016

def fast_random_bool(shape):
    n = np.prod(shape)
    nb = -(-n // 8)  # ceiling division
    b = np.fromstring(np.random.bytes(nb), np.uint8, nb)
    return np.unpackbits(b)[:n].reshape(shape)


class cpopulation:
    def __init__(self):
        self.data = []
        self.fits = []
        self.bestfit = - np.inf
        self.adaptfits = []
        self.bestgenotype = []
        self.bestgenotypefit = - np.inf
        self.bestgenotype_pos_coverage = []
        self.rating = 0.0

    def init(self, psize, processed_data, numval_per_gen, pos_index, neg_index, uncov_pos,
             ga_type, sel_type, tour_size, elitism, rec_type, pop_part_rec, nmut_bits, pop_part_distr):
        self.processed_data = processed_data
        self.pos_index = pos_index
        self.neg_index = neg_index
        self.uncov_pos = uncov_pos
        self.numval_per_gen = numval_per_gen
        self.numgen = int(len(numval_per_gen))
        self.numbit = int(sum(numval_per_gen))
        self.cum_gens = np.cumsum(numval_per_gen)
        self.cum_gens = np.concatenate(([0], self.cum_gens))
        self.psize = psize
        self.prevpsize = psize
        self.sel_type = sel_type
        self.tour_size = tour_size
        self.elitism = elitism
        self.rec_type = rec_type
        self.pop_part_rec = pop_part_rec  # for which part of population best children (not random) will be chosen (best child from 2 generated children for each pair of parents)
        self.mut_prob = (1.0 * nmut_bits) / self.numbit  # probability of bit to be inverse during mutation process
        self.pop_part_distr = pop_part_distr
        self.ga_type = ga_type
        self.data = fast_random_bool((self.psize, self.numbit))
        self.set_fits()
        self.parents = []
        self.children = np.zeros((self.psize, self.numbit), dtype=np.int)

        # check_covarage

    def check_coverage(self, bits):
        neg_cov = num_new_covered = num_all_not_miss = num_miss = 0
        coverage = []
        exactcoverage = []
        genes_has_ones = [j for j in range(self.numgen) if (1 in bits[self.cum_gens[j]:self.cum_gens[j + 1]])]
        # does genotype cover negative examples? if yes return 0
        for aNeg in self.processed_data[self.neg_index]:
            found = True
            for j in genes_has_ones:
                if (aNeg[j] == aNeg[j]) and (bits[self.cum_gens[j] + int(aNeg[j])] == 0):
                    found = False
                    break
            if found:
                neg_cov = 1
                return neg_cov, num_new_covered, num_all_not_miss, num_miss, coverage, exactcoverage, genes_has_ones

        # how many positive examples are covered (with at least one meaningful value covered)
        for pind in self.pos_index:
            aPos = self.processed_data[pind]
            found = True
            significant = False
            missingvalue = False
            for j in genes_has_ones:
                if aPos[j] == aPos[j]:  # if genotype covers at least one meaningful value (# not np.isnan(aPos[j]))
                    if bits[self.cum_gens[j] + int(aPos[j])] == 0:
                        found = False
                        break
                    significant = True
                else:  # check if genotype covers any missing value
                    missingvalue = True
            if found and significant:
                coverage.append(pind)
                if pind in self.uncov_pos:
                    num_new_covered += 1
                if not missingvalue:
                    num_all_not_miss += 1
                    exactcoverage.append(pind)
                else:
                    num_miss += 1

        return neg_cov, num_new_covered, num_all_not_miss, num_miss, coverage, exactcoverage, genes_has_ones

    def fitness_function(self, bits):
        neg_cov, num_new_covered, num_all_not_miss, num_miss, coverage, exactcoverage, genes_has_ones = self.check_coverage(
            bits)
        if neg_cov:
            return -np.inf
        num_ones = np.sum(bits)
        bigV = 1000.0
        if num_new_covered != 0:
            fit = (num_all_not_miss * bigV) + (num_miss * 0.25 * bigV) + num_new_covered - (
                num_ones * 1.0 / bigV)  # fit = num_uncov * 1000.0 + num0 - num_ones / 1000.0;
        else:
            fit = num_all_not_miss - (num_ones * 1.0 / bigV)
        return fit

    def set_fits(self):
        # self.fits = np.array([self.fitness(d) for d in self.data]) - should be slow
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.apply_along_axis.html
        self.fits = np.apply_along_axis(self.fitness_function, 1, self.data)
        maxindex = np.argmax(self.fits)
        self.bestfit = self.fits[maxindex]
        self.adaptfits.append(self.bestfit)

        if self.bestgenotypefit < self.bestfit:
            self.bestgenotype = np.copy(self.data[maxindex])
            self.bestgenotypefit = self.bestfit

    def selection(self):
        def proportional(sorted_indexes):
            # sorted_fits, sorted_indexes = zip(*sorted(zip(self.fits, range(self.psize))))
            # if all examples have the same fitness, then they have the equal probabilities to be chosen,
            # otherwise they have probabilities proportional to the increase of fitness relatively to the worse example
            if self.fits[sorted_indexes[0]] == self.fits[sorted_indexes[-1]]:
                self.parents = [rand.randint(self.psize) for i in range(2 * self.psize)]
            else:
                for i in range(self.psize):  # -INF could be
                    if self.fits[sorted_indexes[i]] != -np.inf:
                        min_not_inf = i
                        break
                self.fits[sorted_indexes[min_not_inf:]] -= self.fits[sorted_indexes[min_not_inf]]
                self.fits[sorted_indexes[min_not_inf:]] = self.fits[sorted_indexes[min_not_inf:]] / self.fits[
                    sorted_indexes[-1]]
                # after normalizing, 0-fits occur. To have chance to choose 0-examples,
                # set fit to them as the first nonzero-fit divided between all 0-examples equally.
                # do the same with -inf-examples
                for i in range(min_not_inf + 1, self.psize):
                    if self.fits[sorted_indexes[i]] > 0:
                        self.fits[sorted_indexes[min_not_inf:i]] = self.fits[sorted_indexes[i]] * 1.0 / (
                            i - min_not_inf)
                        if min_not_inf != 0:
                            self.fits[sorted_indexes[0:min_not_inf]] = self.fits[sorted_indexes[
                                min_not_inf]] * 1.0 / min_not_inf
                        break
                prob = np.cumsum(self.fits[sorted_indexes])
                prob = prob * 1.0 / prob[-1]

                for npar in range(2 * self.psize):
                    rand_value = rand.rand()
                    if rand_value <= prob[0]:
                        self.parents.append(sorted_indexes[0])
                    else:
                        for i in reversed(range(self.psize - 1)):
                            if (rand_value <= prob[i + 1]) and (rand_value > prob[i]):
                                self.parents.append(sorted_indexes[i + 1])
                                break
            return

        def rang(sorted_indexes):
            rangs_sum = (self.psize * (self.psize + 1)) / 2.0
            self.parents = [
                sorted_indexes[int(np.ceil((-1 + np.sqrt(1.0 + 8.0 * (rand.randint(int(rangs_sum)) + 1))) / 2.0) - 1)]
                for j in range(2 * self.psize)]
            return

        def tournament(sorted_indexes):
            self.parents = [sorted_indexes[max(rand.randint(self.psize) for i in range(self.tour_size))] for j in
                            range(2 * self.psize)]
            return

        del self.parents[:]
        sorted_indexes = range(self.psize)
        sorted_indexes = sorted(sorted_indexes, key=lambda i: self.fits[i])  # ascending order

        if self.elitism:
            self.data[sorted_indexes[-1]] = np.copy(self.bestgenotype)
            self.fits[sorted_indexes[-1]] = self.bestgenotypefit

        if self.sel_type == 0:
            proportional(sorted_indexes)
        elif self.sel_type == 1:
            rang(sorted_indexes)
        else:
            tournament(sorted_indexes)

        return

    def recombination(self):
        def onepointcut():
            buff1 = np.empty((1, self.numbit), dtype=int)
            buff2 = np.empty((1, self.numbit), dtype=int)
            for p_index in range(self.psize):
                cut = rand.randint(self.numbit)
                pop_part = self.pop_part_rec  # if fitness function is too hard, then it could be faster to take best children only for some part of population
                # When pop_part = 1.0 it is slower, but based on few tests it's better to leave the children with max fit. Maybe with some probability?
                if p_index < self.psize * pop_part:
                    # it is slower, but based on few tests it's better to leave the children with max fit. Maybe with some probability?
                    buff1[0, 0:cut] = self.data[self.parents[2 * p_index], 0:cut]
                    buff1[0, cut:self.numbit] = self.data[self.parents[2 * p_index + 1], cut:self.numbit]
                    buff2[0, 0:cut] = self.data[self.parents[2 * p_index + 1], 0:cut]
                    buff2[0, cut:self.numbit] = self.data[self.parents[2 * p_index], cut:self.numbit]
                    if self.fitness_function(buff1[0]) > self.fitness_function(buff2[0]):
                        self.children[p_index] = buff1[0]
                    else:
                        self.children[p_index] = buff2[0]
                else:
                    # choose just first child, not necessarily the best
                    self.children[p_index, 0:cut] = self.data[self.parents[2 * p_index], 0:cut]
                    self.children[p_index, cut:self.numbit] = self.data[self.parents[2 * p_index + 1], cut:self.numbit]
            del buff1
            del buff2
            return

        def twopointscut():
            buff1 = np.empty((1, self.numbit), dtype=int)
            buff2 = np.empty((1, self.numbit), dtype=int)
            for p_index in range(self.psize):
                cut = np.sort([rand.randint(self.numbit), rand.randint(self.numbit)])
                pop_part = self.pop_part_rec  # if fitness function is too hard, then it could be faster to take best children only for some part of population
                # When pop_part = 1.0 it is slower, but based on few tests it's better to leave the children with max fit. Maybe with some probability?
                if p_index < self.psize * pop_part:
                    buff1[0, 0:cut[0]] = self.data[self.parents[2 * p_index], 0:cut[0]]
                    buff1[0, cut[0]:cut[1]] = self.data[self.parents[2 * p_index + 1], cut[0]:cut[1]]
                    buff1[0, cut[1]:self.numbit] = self.data[self.parents[2 * p_index], cut[1]:self.numbit]
                    buff2[0, 0:cut[0]] = self.data[self.parents[2 * p_index + 1], 0:cut[0]]
                    buff2[0, cut[0]:cut[1]] = self.data[self.parents[2 * p_index], cut[0]:cut[1]]
                    buff2[0, cut[1]:self.numbit] = self.data[self.parents[2 * p_index + 1], cut[1]:self.numbit]
                    if self.fitness_function(buff1[0]) > self.fitness_function(buff2[0]):
                        self.children[p_index] = buff1[0]
                    else:
                        self.children[p_index] = buff2[0]
                else:
                    # choose just first child, not necessarily the best
                    self.children[p_index, 0:cut[0]] = self.data[self.parents[2 * p_index], 0:cut[0]]
                    self.children[p_index, cut[0]:cut[1]] = self.data[self.parents[2 * p_index + 1], cut[0]:cut[1]]
                    self.children[p_index, cut[1]:self.numbit] = self.data[self.parents[2 * p_index],
                                                                 cut[1]:self.numbit]
            del buff1
            del buff2
            return

        def uniform():
            bits_to_get = fast_random_bool((self.psize, self.numbit))
            pop_part = self.pop_part_rec  # if fitness function is too hard, then it could be faster to take best children only for some part of population
            # When pop_part = 1.0 it is slower, but based on few tests it's better to leave the children with max fit. Maybe with some probability?
            bound = int(self.psize * pop_part)
            buff1 = np.empty((1, self.numbit), dtype=int)
            buff2 = np.empty((1, self.numbit), dtype=int)
            for p_index in range(bound):
                buff1[0] = (self.data[self.parents[2 * p_index]] & bits_to_get[p_index]) + (
                    self.data[self.parents[2 * p_index + 1]] & (np.invert(bits_to_get[p_index]) + 2))
                buff2[0] = (self.data[self.parents[2 * p_index + 1]] & bits_to_get[p_index]) + (
                    self.data[self.parents[2 * p_index]] & (np.invert(bits_to_get[p_index]) + 2))
                if self.fitness_function(buff1[0]) > self.fitness_function(buff2[0]):
                    self.children[p_index] = buff1[0]
                else:
                    self.children[p_index] = buff2[0]
            if bound != self.psize:
                # choose just first child, not necessarily the best
                self.children[bound:self.psize] = (self.data[self.parents[2 * bound::2]] & bits_to_get[
                                                                                           bound:self.psize]) + (
                                                      self.data[self.parents[2 * bound + 1::2]] & (
                                                          np.invert(bits_to_get[bound:self.psize]) + 2))
            del buff1
            del buff2
            return

        self.children.resize(self.psize, self.numbit)
        if self.rec_type == 0:
            onepointcut()
        elif self.rec_type == 1:
            twopointscut()
        else:
            uniform()

        return

    def mutation(self):
        mut = np.random.binomial(1, self.mut_prob, self.psize * self.numbit).reshape((self.psize, self.numbit))
        self.children = np.bitwise_xor(self.children, mut)

    # written almost without revision
    def getByDistr(self):
        gsize = int(self.psize * self.pop_part_distr)
        distr = np.zeros(self.numbit)  # probabilities for bits
        probsel = np.zeros(gsize)  # selection probabilities

        sorted_indexes = range(self.psize)
        sorted_indexes = sorted(sorted_indexes, key=lambda i: -self.fits[i])  # descending order

        if self.elitism:
            self.data[sorted_indexes[0]] = np.copy(self.bestgenotype)
            self.fits[sorted_indexes[0]] = self.bestgenotypefit

        if self.sel_type == 0:
            sum1 = 0.0
            dbuff = -self.fits[sorted_indexes[gsize - 1]] + 0.01
            for i in range(gsize):
                if self.fits[sorted_indexes[i]] == -np.inf:
                    if i != 0:
                        dbuff = self.fits[sorted_indexes[i - 1]]
                    break
            for i in range(gsize):
                if self.fits[sorted_indexes[i]] != -np.inf:
                    sum1 += 100 * (self.fits[sorted_indexes[i]] + dbuff)
                else:
                    sum1 += 1
                    break
            probsel = np.array([100.0 * (self.fits[sorted_indexes[i]] + dbuff) / sum1 if self.fits[sorted_indexes[
                i]] != -np.inf  else 1.0 / sum1 for i in range(gsize)])
        if self.sel_type == 1:
            sum1 = int(((1 + gsize) * gsize) / 2.0)
            probsel = np.array([(1.0 * (gsize - i) / sum1) for i in range(gsize)])
        elif self.sel_type == 2:
            # faster without taking into account similar fits
            denom = gsize ** self.tour_size
            probsel = np.array(
                [(((gsize - i) ** self.tour_size) - ((gsize - i - 1) ** self.tour_size)) * 1.0 / denom for i in
                 range(gsize)])

        for i in range(self.numbit):
            for h in range(gsize):
                distr[i] += self.data[sorted_indexes[h]][i] * probsel[h]
            distr[i] = distr[i] * (1 - self.mut_prob) + (1 - distr[i]) * self.mut_prob  # taking mutation into account

        for h in range(self.psize):
            for i in range(self.numbit):
                self.data[h][i] = int(rand.rand() <= distr[i])  # np.random.binomial would probably be faster

    # classical GA
    def one_ga_step(self):
        if self.ga_type == 0:
            self.selection()  # fill self.parents
            self.recombination()  # fill self.children
            self.mutation()  # mutation of self.children

            buf = self.data
            self.data = self.children
            self.children = buf
            buf = None

        elif self.ga_type == 1:
            self.getByDistr()

        self.set_fits()

        # END OF CLASS CPOPULATION


def run_gaaq(processed_data, numval_per_gen, pos_index, neg_index, uncov_pos):
    pop = cpopulation()
    pop.init(gap.pops_size, processed_data, numval_per_gen, pos_index, neg_index, uncov_pos,
             gap.ga_type[2], gap.sel_type[2], gap.tour_size[2], gap.elitism[2], gap.rec_type[2], gap.pop_part_rec[2],
             gap.nmut_bits[2], gap.pop_part_distr[2])
    for i in range(gap.nadapt * gap.ngen):
        pop.one_ga_step()
        print(pop.bestfit)
    print("best", pop.bestgenotypefit)

    if len(pop.bestgenotype != 0):
        neg_cov, num_new_covered, num_all_not_miss, num_miss, rule_coverage, rule_exactcoverage, genes_has_ones = pop.check_coverage(
            pop.bestgenotype)
    else:
        neg_cov = num_new_covered = num_all_not_miss = num_miss = 0
        rule_coverage = []
        rule_exactcoverage = []
        genes_has_ones = []
    return neg_cov, num_new_covered, num_all_not_miss, num_miss, rule_coverage, rule_exactcoverage, genes_has_ones, pop.bestgenotype, pop.bestgenotypefit
