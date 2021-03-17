from pascalpart import *
import tensorflow as tf
import random, os, pdb
import logictensornetworks as ltn
import sys


print(sys.version)
print(tf.VERSION)

ltn.default_optimizer = "rmsprop"

# swith between GPU and CPU
config = tf.ConfigProto(device_count={'GPU': 1})

number_of_positive_examples_x_types=250
number_of_negative_examples_x_types=250
number_of_positive_example_x_partof=250
number_of_negative_example_x_partof=250
number_of_pairs_for_axioms = 1000

train_data, pairs_of_train_data, types_of_train_data, partOf_of_pairs_of_train_data, _, _ = get_data("train",max_rows=1000000000)

# computing positive and negative exampls for types and partof

idxs_of_positive_examples_of_types = {}
idxs_of_negative_examples_of_types = {}

for type in selected_types:
    idxs_of_positive_examples_of_types[type] = np.where(types_of_train_data == type)[0]
    idxs_of_negative_examples_of_types[type] = np.where(types_of_train_data != type)[0]

idxs_of_positive_examples_of_partOf = np.where(partOf_of_pairs_of_train_data)[0]
idxs_of_negative_examples_of_partOf = np.where(partOf_of_pairs_of_train_data == False)[0]

existing_types = [t for t in selected_types if idxs_of_positive_examples_of_types[t].size > 0]

print("non empty types in train data", existing_types)
print("finished to upload and analyze data")
print("Start model definition")

# domain definition

clauses_for_positive_examples_of_types = \
    [ltn.Clause([ltn.Literal(True,isOfType[t],objects_of_type[t])],label="examples_of_"+t,weight=1.0) for t in existing_types]

clauses_for_negative_examples_of_types = \
    [ltn.Clause([ltn.Literal(False,isOfType[t],objects_of_type_not[t])],label="examples_of_not_"+t,weight=1.0) for t in existing_types]

clause_for_positive_examples_of_partOf = [ltn.Clause([ltn.Literal(True, isPartOf, object_pairs_in_partOf)], label="examples_of_object_pairs_in_partof_relation", weight=1.0)]

clause_for_negative_examples_of_partOf = [ltn.Clause([ltn.Literal(False, isPartOf, object_pairs_not_in_partOf)], label="examples_of_object_pairs_not_in_part_of_relation", weight=1.0)]

'''
# defining axioms from the partOf ontology

parts_of_whole, wholes_of_part = get_part_whole_ontology()

w1 = {}
p1 = {}
w2 = {}
p2 = {}
p1w1 = {}
p2w2 = {}
oo = ltn.Domain((number_of_features-1)*2+2, label="same_object_pairs")
o = ltn.Domain(number_of_features-1, label="a_generi_object")

w0 = ltn.Domain(number_of_features - 1, label="whole_of_part_whole_pair")
p0 = ltn.Domain(number_of_features - 1, label="part_of_part_whole_pair")
p0w0 = ltn.Domain((number_of_features - 1) * 2 + 2, label="part_whole_pair")
w0p0 = ltn.Domain((number_of_features - 1) * 2 + 2, label="whole_part_pair")

for t in selected_types:
    w1[t] = ltn.Domain(number_of_features-1, label="whole_predicted_objects_for_"+t)
    p1[t] = ltn.Domain(number_of_features-1, label="part_predicted_objects_for_"+t)
    w2[t] = ltn.Domain(number_of_features - 1, label="whole_predicted_objects_for_" + t)
    p2[t] = ltn.Domain(number_of_features - 1, label="part_predicted_objects_for_" + t)
    p1w1[t] = ltn.Domain((number_of_features-1)*2+2, label="potential_part_whole_object_pairs_for_"+t)
    p2w2[t] = ltn.Domain((number_of_features-1)*2+2, label="potential_whole_part_object_pairs_for_"+t)

partOf_is_antisymmetric = [ltn.Clause([ltn.Literal(False, isPartOf, p0w0), ltn.Literal(False, isPartOf, w0p0)],
                                      label="part_of_is_antisymmetric", weight=0.37)]

partof_is_irreflexive = [ltn.Clause([ltn.Literal(False, isPartOf, oo)],
                                   label = "part_of_is_irreflexive", weight = 0.37)]

# Leg and partOf(Leg,o) -> Cat or Dog ....
clauses_for_parts_of_wholes = [ltn.Clause([ltn.Literal(False, isOfType[w], w1[w]),
                                           ltn.Literal(False, isPartOf, p1w1[w])] + \
                                          [ltn.Literal(True, isOfType[p], p1[w]) for p in parts_of_whole[w]],
                                          label = "parts_of_" + w) for w in parts_of_whole.keys()]

# Cat and part(p,Cat) -> Head or Leg or Muzzle or ...
clauses_for_wholes_of_parts = [ltn.Clause([ltn.Literal(False, isOfType[p], p2[p]),
                                           ltn.Literal(False, isPartOf, p2w2[p])] +
                                          [ltn.Literal(True, isOfType[w], w2[p]) for w in wholes_of_part[p]],
                                          label="wholes_of_" + p) for p in wholes_of_part.keys()]

# P -> Q
# Cat -> not Dog
# P -> Q == not P or not Q
clauses_for_disjoint_types = [ltn.Clause([ltn.Literal(False,isOfType[t],o),
                                          ltn.Literal(False,isOfType[t1],o)],label=t+"_is_not_"+t1) for t in selected_types for t1 in selected_types if t < t1]

clause_for_at_least_one_type = [ltn.Clause([ltn.Literal(True,isOfType[t],o) for t in selected_types], label="an_object_has_at_least_one_type")]
'''
def add_noise_to_data(noise_ratio):
    if noise_ratio > 0:
        freq_other = {}

        for t in selected_types:
            freq_other[t] = {}
            number_of_not_t = len(idxs_of_negative_examples_of_types[t])
            for t1 in selected_types:
                if t1 != t:
                    freq_other[t][t1] = np.float(len(idxs_of_positive_examples_of_types[t1]))/number_of_not_t

        noisy_data_idxs = np.random.choice(range(len(train_data)), int(len(train_data) * noise_ratio),replace=False)

        for idx in noisy_data_idxs:
            type_of_idx = types_of_train_data[idx]
            not_types_of_idx = np.setdiff1d(selected_types,type_of_idx)
            types_of_train_data[idx] = np.random.choice(not_types_of_idx,
                                                        p=np.array([freq_other[type_of_idx][t1] \
                                                                    for t1 in not_types_of_idx]))

        noisy_data_pairs_idxs = np.append(np.random.choice(np.where(partOf_of_pairs_of_train_data)[0],
                                                 int(partOf_of_pairs_of_train_data.sum() * noise_ratio * 0.5)),
                                          np.random.choice(np.where(np.logical_not(partOf_of_pairs_of_train_data))[0],
                                                           int(partOf_of_pairs_of_train_data.sum() * noise_ratio* 0.5)))

        for idx in noisy_data_pairs_idxs:
            partOf_of_pairs_of_train_data[idx] = not (partOf_of_pairs_of_train_data[idx])

    idxs_of_noisy_positive_examples_of_types = {}
    idxs_of_noisy_negative_examples_of_types = {}

    for type in selected_types:
        idxs_of_noisy_positive_examples_of_types[type] = np.where(types_of_train_data == type)[0]
        idxs_of_noisy_negative_examples_of_types[type] = np.where(types_of_train_data != type)[0]

    idxs_of_noisy_positive_examples_of_partOf = np.where(partOf_of_pairs_of_train_data)[0]
    idxs_of_noisy_negative_examples_of_partOf = np.where(partOf_of_pairs_of_train_data == False)[0]

    print("I have introduces the followins errors")
    for t in selected_types:
        print("wrong positive", t, len(np.setdiff1d(idxs_of_noisy_positive_examples_of_types[t],
                                                    idxs_of_positive_examples_of_types[t])))
        print("wrong negative", t, len(np.setdiff1d(idxs_of_noisy_negative_examples_of_types[t],
                                                    idxs_of_negative_examples_of_types[t])))

    print("wrong positive partof", len(np.setdiff1d(idxs_of_noisy_positive_examples_of_partOf,
                                                    idxs_of_positive_examples_of_partOf)))
    print("wrong negative partof", len(np.setdiff1d(idxs_of_noisy_negative_examples_of_partOf,
                                                    idxs_of_negative_examples_of_partOf)))

    return idxs_of_noisy_positive_examples_of_types, \
           idxs_of_noisy_negative_examples_of_types, \
           idxs_of_noisy_positive_examples_of_partOf, \
           idxs_of_noisy_negative_examples_of_partOf,


def train(number_of_training_iterations=2500,
          frequency_of_feed_dict_generation=250,
          with_constraints=False,
          noise_ratio=0.0,
          start_from_iter=1,
          saturation_limit=0.90):

    # add noise to train data
    idxs_of_noisy_positive_examples_of_types, \
    idxs_of_noisy_negative_examples_of_types, \
    idxs_of_noisy_positive_examples_of_partOf, \
    idxs_of_noisy_negative_examples_of_partOf = add_noise_to_data(noise_ratio)

    # defining the clauses of the background knowledge
    clauses = clauses_for_positive_examples_of_types + \
              clauses_for_negative_examples_of_types + \
              clause_for_positive_examples_of_partOf + \
              clause_for_negative_examples_of_partOf
    '''
    if with_constraints:
        clauses += partof_is_irreflexive + \
                   partOf_is_antisymmetric + \
                   clauses_for_wholes_of_parts + \
                   clauses_for_parts_of_wholes + \
                   clauses_for_disjoint_types + \
                   clause_for_at_least_one_type
    '''
    print('ciao')
    feed_dict = get_feed_dict(idxs_of_noisy_positive_examples_of_types,
                              idxs_of_noisy_negative_examples_of_types,
                              idxs_of_noisy_positive_examples_of_partOf,
                              idxs_of_noisy_negative_examples_of_partOf,
                              pairs_of_train_data,
                              with_constraints=True)
    # defining the label of the background knowledge

    kb_label = "KB_nc_nr_{}_{}".format(ltn.learning_rate,ltn.default_smooth_factor)

    # definint the KB
    KB = ltn.KnowledgeBase(kb_label,clauses,"models/")

    # start training
    init = tf.initialize_all_variables()
    sess = tf.Session(config=config)
    if start_from_iter == 1:
        sess.run(init)
    if start_from_iter > 1:
        KB.restore(sess)

    feed_dict = get_feed_dict(idxs_of_noisy_positive_examples_of_types,
                              idxs_of_noisy_negative_examples_of_types,
                              idxs_of_noisy_positive_examples_of_partOf,
                              idxs_of_noisy_negative_examples_of_partOf,
                              pairs_of_train_data,
                              with_constraints=with_constraints)
    train_kb = True
    for i in range(start_from_iter, number_of_training_iterations + 1):
        
        if i % frequency_of_feed_dict_generation == 0:
            if train_kb:
                KB.save(sess)
            else:
                train_kb = True
            feed_dict = get_feed_dict(idxs_of_noisy_positive_examples_of_types,
                              idxs_of_noisy_negative_examples_of_types,
                              idxs_of_noisy_positive_examples_of_partOf,
                              idxs_of_noisy_negative_examples_of_partOf,
                              pairs_of_train_data,
                              with_constraints=with_constraints)
        if train_kb:
            sat_level = sess.run(KB.tensor,feed_dict)
            loss = sess.run(KB.loss,feed_dict)
           # neptune.log_metric('loss',loss)
            if np.isnan(sat_level):
                train_kb = False
            if sat_level >= saturation_limit:
                KB.save(sess)
                train_kb = False
            else:
                KB.train(sess, feed_dict)
        print(str(i) + ' --> ' + str(sat_level))
    sess.close()


def get_feed_dict(idxs_of_pos_ex_of_types,
                  idxs_of_neg_ex_of_types,
                  idxs_of_pos_ex_of_partOf,
                  idxs_of_neg_ex_of_partOf,
                  pairs_data,
                  with_constraints=True):
    feed_dict = {}

    # positive and negative examples for types
    for t in existing_types:
        feed_dict[objects_of_type[t].tensor] = \
            train_data[np.random.choice(idxs_of_pos_ex_of_types[t],
                                        number_of_positive_examples_x_types)][:,1:]
        feed_dict[objects_of_type_not[t].tensor] = \
            train_data[np.random.choice(idxs_of_neg_ex_of_types[t],
                                        number_of_negative_examples_x_types)][:, 1:]

    # positive and negative examples for partOF
    feed_dict[object_pairs_in_partOf.tensor] = \
            pairs_of_train_data[np.random.choice(idxs_of_pos_ex_of_partOf,
                                                 number_of_positive_example_x_partof)]

    feed_dict[object_pairs_not_in_partOf.tensor] = \
            pairs_of_train_data[np.random.choice(idxs_of_neg_ex_of_partOf,
                                                 number_of_negative_example_x_partof)]

    '''
    # feed data for axioms
    tmp = pairs_data[np.random.choice(range(pairs_data.shape[0]), number_of_pairs_for_axioms)]
    feed_dict[o.tensor] = tmp[:,:number_of_features - 1]

    if with_constraints:
        for t in selected_types:
            feed_dict[p1w1[t].tensor] = tmp
            feed_dict[w1[t].tensor] = \
                feed_dict[p1w1[t].tensor][:,number_of_features-1:2*(number_of_features-1)]
            feed_dict[p1[t].tensor] = \
                feed_dict[p1w1[t].tensor][:,0:number_of_features - 1]
            feed_dict[p2w2[t].tensor] = tmp
            feed_dict[w2[t].tensor] = \
                feed_dict[p2w2[t].tensor][:, number_of_features - 1:2 * (number_of_features - 1)]
            feed_dict[p2[t].tensor] = \
                feed_dict[p2w2[t].tensor][:,:number_of_features - 1]

        feed_dict[oo.tensor] = np.concatenate([tmp[:,:number_of_features-1],
                                               tmp[:,:number_of_features-1],
                                               np.ones((tmp.shape[0],2),dtype=float)],axis=1)
        feed_dict[p0w0.tensor] = tmp
        feed_dict[w0.tensor] = \
            feed_dict[p0w0.tensor][:, number_of_features - 1:2 * (number_of_features - 1)]
        feed_dict[p0.tensor] = \
            feed_dict[p0w0.tensor][:,:number_of_features - 1]
        feed_dict[w0p0.tensor] = np.concatenate([
            feed_dict[w0.tensor],
            feed_dict[p0.tensor],
            feed_dict[p0w0.tensor][:, -1:-3:-1]], axis = 1)
    '''

    return feed_dict
#neptune.init('davidemiro/sandbox', api_token='eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vdWkubmVwdHVuZS5haSIsImFwaV91cmwiOiJodHRwczovL3VpLm5lcHR1bmUuYWkiLCJhcGlfa2V5IjoiYjI1NGI5OWItYjJjMC00MTY0LThkYTctOTdmMjYyMWZkNDEyIn0=')
for lr in [1e-2,1e-3]:
    for sm in [1e-4,1e-6,1e-8]:
        params ={
            'number_of_training_iterations':1000,
            'frequency_of_feed_dict_generation':100,
            'with_constraints':False,
            'noise_ratio':0.0,
            'saturation_limit':.95,
            'data':'official',
            'optimizer':"rmsprop",
            'learning_rate':lr,
            'decay':0.9,
            'default_layers':6,
            'default_smooth_factor':sm,
            'default_tnorm':'luk',
            'default_aggregator': "hmean",
            'default_positive_fact_penality':0,
            'default_clauses_aggregator': "hmean",
            
        }
        ltn.default_layers = params['default_layers']
        ltn.default_smooth_factor = params['default_smooth_factor']
        ltn.default_tnorm = params['default_tnorm']
        ltn.default_optimizer = params['optimizer']
        ltn.default_aggregator = params['default_aggregator']
        ltn.default_positive_fact_penality = params['default_positive_fact_penality']
        ltn.default_clauses_aggregator = params['default_clauses_aggregator']
        ltn.learning_rate = params['learning_rate']
        train(number_of_training_iterations=1000,
              frequency_of_feed_dict_generation=100,
              with_constraints=True,noise_ratio=0,
              saturation_limit=.95)
