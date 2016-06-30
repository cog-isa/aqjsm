#coding=utf8
import arff, numpy as np
import numpy.random as rand
from collections import Counter, defaultdict
import population
import coevolution
import cProfile, pstats
import io

# Author: Alexander Shvets
# Date: 29.06.2016

def load_data(arff_file):
    return arff.load(open(arff_file, 'r'))
  
def preprocess_data(dataset, NumRealIntervals):
    data = np.array(dataset['data'], dtype=np.float)
    class_labels = np.array(data[:,-1], dtype = int)
    
    numAttr = len(dataset['attributes'])-1 #minus 1 - for class
    
    real_values = np.array(list(i for i, attr in enumerate(dataset['attributes']) if attr[1] == 'REAL'))
    min_real = np.nanmin(data[:, real_values], axis=0)
    max_real = np.nanmax(data[:, real_values], axis=0)
    inter_size = (max_real - min_real)*1.0 / NumRealIntervals

    real_mins = np.zeros(numAttr+1)
    real_inters = np.zeros(numAttr+1)
    real_mins[real_values] = min_real
    real_inters[real_values] = inter_size

    numval_per_gen = np.array([len(attr[1]) if attr[1] != 'REAL' else NumRealIntervals for attr in dataset['attributes'][:-1]]) # sizes of features

    processed_data = []
    for d in data:
        d0 = d[:-1]
        for rv in real_values:
            if(not np.isnan(d0[rv])):
                for numi in range(NumRealIntervals):
                    if(d0[rv] <= real_mins[rv]+(numi+1)*1.0*real_inters[rv]):
                        d0[rv] = numi
                        break
        processed_data.append(d0)
    processed_data = np.array(processed_data)  
    print("Data have been loaded and preprocessed.", Counter(list(d for d in class_labels)))
    return processed_data, class_labels, numval_per_gen

def get_examples_indexes(processed_data, class_labels, classLabel):
    numAttr = len(processed_data[0])
    #pos_index = np.array([int(d[-1])==int(classLabel) for d in data])
    #neg_index = np.invert(pos_index)

    pos_index = np.array([i for i,d in enumerate(class_labels) if d==classLabel])
    neg_index = np.array([i for i,d in enumerate(class_labels) if d!=classLabel])

    #remove conflict fobj
    to_del = []
    for i, aNeg in enumerate(processed_data[neg_index]):
        found = False
        for aPos in processed_data[pos_index]:
            found = True
            for j in range(numAttr):
                if ((not np.isnan(aNeg[j])) and ((aPos[j] != aNeg[j]) or (np.isnan(aPos[j])))):
                    found = False
                    break
            if (found):
                to_del.append(i)
                break
    print(("Found and deleted %d conflict negative objects (" % len(to_del)) + (" ".join(str(k) for k in neg_index[to_del])) + ")")
    neg_index = np.delete(neg_index, to_del)

    uncov_pos = defaultdict(lambda:1) # left positive examples that are still not covered
    for pind in pos_index:
        uncov_pos[pind]
    
    return pos_index, neg_index, uncov_pos

#temporary
class AQRule():
    def __init__(self):
        self.id = 0
        self.forceCoverage = 0
        self.features = []

def evaluate_AQ_rules(processed_data, class_labels, numval_per_gen):
    numAttr = len(processed_data[0])
    labels_set = set(class_labels)
    cum_gens = np.cumsum(numval_per_gen)
    cum_gens = np.concatenate(([0], cum_gens))
    rand.seed()
    for classLabel in labels_set:
        pos_index, neg_index, uncov_pos = get_examples_indexes(processed_data, class_labels, classLabel)
        print("Class Label: %d, positive: %d, negative: %d" % (classLabel, len(pos_index), len(neg_index)))
        num_objects = []
        num_miss_objects = []
        num_new_objects = []
        essential = []
        obj_cov_by_rule = []
        exactobj_cov_by_rule = []
        newobj_cov_by_rule = []
        covered_objects = 0

        classRules = []
        rule_genotypes = []
        without_result = 0
        breakWithoutResult = 5
        
        while (len(uncov_pos) != 0):
            #GA           
            #neg_cov, num_new_covered, num_all_not_miss, num_miss, rule_coverage, rule_exactcoverage, genes_has_ones, best_bits, best_fit = population.run_gaaq(processed_data, numval_per_gen, pos_index, neg_index, uncov_pos)
            #Coevolutionary GA
            neg_cov, num_new_covered, num_all_not_miss, num_miss, rule_coverage, rule_exactcoverage, genes_has_ones, best_bits, best_fit = coevolution.run_coev_gaaq(processed_data, numval_per_gen, pos_index, neg_index, uncov_pos)
            
            if(num_new_covered == 0):
                print("No new positive example has been covered")
            if(neg_cov):
                print("Decision is not appropriate. Negative examples have been covered")
            if((num_new_covered == 0) or (neg_cov)):
                without_result += 1
                if (without_result == breakWithoutResult):
                    break
                else:
                    continue
            without_result = 0
            
            #if the feature covers any meaningful value in positive example (covered by rule)
                #and there exist different value of this feature in other positive example (not necessary covered by rule), then this feature could be essential
            #if all positive examples have the same or missing value of this feature or positive examples covered by rule have only missing values for this feature,
                    #then the feature is not essential in this rule in case that there is no different value for this feature in negative examples
            ess = []
            for j in genes_has_ones:
                ess_bool = False
                for aPos in processed_data[rule_coverage]:
                    if (aPos[j]==aPos[j]):
                        ess_bool = True
                        break
                if(ess_bool):
                    ess_bool = False
                    for aPos in processed_data[pos_index]:
                        if ((aPos[j]==aPos[j]) and (best_bits[cum_gens[j]+int(aPos[j])] == 0)):
                            ess_bool = True
                            break
                if(not ess_bool):#not else!
                    for aNeg in processed_data[neg_index]:
                        if ((aNeg[j]==aNeg[j]) and (best_bits[cum_gens[j]+int(aNeg[j])] == 0)):
                            ess_bool = True
                            break
                if(ess_bool):
                    ess.append(j)
            essential.append(ess)

            newobj_cov = []
            for rc in rule_coverage:
                if(rc in uncov_pos):
                    newobj_cov.append(rc)
                    del uncov_pos[rc]                        

            num_objects.append(num_all_not_miss + num_miss)
            num_miss_objects.append(num_miss)
            num_new_objects.append(num_new_covered)
            obj_cov_by_rule.append(rule_coverage)
            exactobj_cov_by_rule.append(rule_exactcoverage)
            newobj_cov_by_rule.append(newobj_cov)
            covered_objects += num_new_covered
            print("new_objects = %d" % num_new_covered)
            print("all_objects = %d" % (num_all_not_miss + num_miss))
            print("objects_with_missing_value = %d" % num_miss)
            print("covered_objects = %d" % covered_objects)
            print("left_objects = %d" % (len(pos_index)-covered_objects))

            rule_genotypes.append((best_bits, best_fit))
            #end of while-cycle
            
        result = ""
        result += ("NUM_UNCOVERED_LEFT_OBJECTS = %d (" % len(uncov_pos)) +  " ".join(str(k) for k in uncov_pos) + ")\n"
        for i in range(len(rule_genotypes)):
            result += "RULE_%d:\n" % (i+1)
            result += ("\tNUM_NEW_OBJECTS: %d (" % (num_new_objects[i])) +  " ".join(str(k) for k in newobj_cov_by_rule[i]) + ")\n"
            result += ("\tNUM_OBJECTS: %d (" % (num_objects[i])) +  " ".join(str(k) for k in obj_cov_by_rule[i]) + ")\n"
            result += ("\tNUM_EXACT_OBJECTS: %d (" % (num_objects[i] - num_miss_objects[i])) + " ".join(str(k) for k in exactobj_cov_by_rule[i]) + ")\n"
            result += "\tNUM_MISS_OBJECTS: %d\n" % (num_miss_objects[i])
            rule = AQRule() # AQRule rule = new AQRule();
            rule.id = i # rule.setId(bp);
            rule.forceCoverage = num_objects[i] # rule.setForceCoverage(num_objects.get(bp));
            for j in essential[i]:
                genbits = rule_genotypes[i][0][cum_gens[j]:cum_gens[j+1]]
                ones_pos = [k+1 for k in range(len(genbits)) if (genbits[k]==1)] # k+1 because positions in AQRules are numerated from 1
                rule.features.append((j, ones_pos)) #rule.getTokens().put(featureMap.get(i), ones_pos_limited); # no need to evaluate ones_pos_limited now
                result += ("\tattr_%d = " % (j)) + " ".join(str(k) for k in ones_pos) + "\n" # attributes for some reason are numerated from 0
            classRules.append(rule)
            result += "\n"
        
        #Collections.sort(classRules);
        #classMapDescriptions.put(className, AQClassDescription.createFromRules(classRules, maximumDescriptionSize, className));
        print(result)
        #end of for-cycle   
    return
            
            
if __name__ == '__main__':            
    #start profiling
    pr = cProfile.Profile()
    pr.enable()
    
    NumRealIntervals = 3 # number of intervals into which we will map real values
    dataset = load_data("class_17_without_missing_16and18.arff")
    processed_data, class_labels, numval_per_gen = preprocess_data(dataset, NumRealIntervals)
    evaluate_AQ_rules(processed_data, class_labels, numval_per_gen)

    #stop profiling
    pr.disable()
    s = io.StringIO()
    sortby = 'time'#'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print(s.getvalue())
    