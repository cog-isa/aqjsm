#coding=utf8

# Author: Alexander Shvets
# Date: 29.06.2016

num_pop = 5
pops_size = 100
ngen = 50
nadapt = 2
ga_type        = [1, 1, 1, 0, 1] # [GA, Probabilistic GA]
sel_type       = [0, 1, 2, 2, 2] # [proportional, rang, tournament]
tour_size      = [0, 0, 3, 3, 6] # valid only for tournament selection
elitism        = [1, 1, 1, 1, 1] # whether to put bestgenotype into each population or not
rec_type       = [1, 0, 1, 1, 2] # [onepointcut, twopointcut, uniform]
pop_part_rec   = [0.5, 0.5, 0.5, 0.5, 0.5] # for which part of population best children (not random) will be chosen (best child from 2 generated children for each pair of parents) 
nmut_bits      = [1.0, 0.333, 1.0, 1.0, 3.0] # the average number of bits to be inverted
pop_part_distr = [0.2, 0.2, 0.2, 0.2, 0.2] # part of population that participates in bits distribution building (valid only for probabilistic GA)
