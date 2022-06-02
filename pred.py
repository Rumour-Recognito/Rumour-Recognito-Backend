# ======================================================
# ===================pred.py============================
# ======================================================

# Adapted from https://github.com/uclmr/fakenewschallenge/blob/master/pred.py
# Original credit - @jaminriedel

# Import relevant packages and modules
from logging import WARNING
from model_prediction.util import FNCData, bow_train, pipeline_train, pipeline_test, save_predictions
import random
import tensorflow as tf
import numpy as np
import os

label_ref_rev = {0: 'agree', 1: 'disagree', 2: 'discuss', 3: 'unrelated',4: 'agree', 5: 'disagree', 6: 'discuss', 7: 'unrelated',8: 'agree', 9: 'disagree', 10: 'discuss', 11: 'unrelated'}

def load(test_headings_list, test_bodies_list):
    
    # Remove all tensorflow deprecation warnings and AVX warning
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    # Prompt for mode
    # mode = input('mode (load / train)? ')
    mode = 'load'
    print("Model execution started...")
    # Initialise hyperparameters
    r = random.Random()
    r.seed(123)
    lim_unigram = 5000
    target_size = 4
    hidden_size = 100

    l2_alpha = 0.00001
    # Set file names
    file_train_instances = "data/train_stances.csv"
    file_train_bodies = "data/train_bodies.csv"
    base_dir = './'
    # base_dir='split-data' #change to this directory when doing data-splitting tasks or K-fold cross validation
    # Load data sets

    raw_train = FNCData(base_dir, file_train_instances, file_train_bodies, [], [], "train")
    raw_test = FNCData(base_dir, "", "", test_headings_list, test_bodies_list, "test")
    n_train = len(raw_train.instances)  # the total number of entry instances

    bow_vectorizer, tfreq_vectorizer, tfidf_vectorizer = bow_train(
        raw_train, raw_test, lim_unigram=lim_unigram)

    # =====================
# Load model
# =====================
    if mode == 'load':
        # Define the weight for different class if needed
        weight_pred_1 = np.diag(np.ones(4))
        # weight_pred_1[0][0]=2
        weight_pred_2 = np.diag(np.ones(4))
        # weight_pred_2[2][2]=2
        weight_pred_3 = np.diag(np.ones(4))
        # weight_pred_3[3][3]=2

        test_prediction1 = restore_model(1, raw_test, bow_vectorizer, tfreq_vectorizer,
                                         tfidf_vectorizer, hidden_size, target_size, l2_alpha, base_dir)
        test_prediction2 = restore_model(2, raw_test, bow_vectorizer, tfreq_vectorizer,
                                         tfidf_vectorizer, hidden_size, target_size, l2_alpha, base_dir)
        test_prediction3 = restore_model(3, raw_test, bow_vectorizer, tfreq_vectorizer,
                                         tfidf_vectorizer, hidden_size, target_size, l2_alpha, base_dir)

        # =====ensemble for two========
        # final_pred=np.concatenate((np.matmul(test_prediction1,weight_pred_1),np.matmul(test_prediction2,weight_pred_2)),axis=1)
        # final_pred=np.matmul(test_prediction1,weight_pred_1)+np.matmul(test_prediction2,weight_pred_2)
        # ======ensemble for three======
        # Concatenation approach
        # final_pred=np.concatenate((np.matmul(test_prediction1,weight_pred_1),np.matmul(test_prediction2,weight_pred_2),np.matmul(test_prediction3,weight_pred_3)),axis=1)
        # Summation approach
        final_pred = np.matmul(test_prediction1, weight_pred_1)+np.matmul(
            test_prediction2, weight_pred_2)+np.matmul(test_prediction3, weight_pred_3)
        # =======no ensemble============
        # final_pred=test_prediction1
        # ==============================

        final_pred_index = np.argmax(final_pred, 1)

        predictions_list = []

        for item in final_pred_index:
            predictions_list.append(label_ref_rev[item])
        #print(predictions_list)
        #save_predictions(base_dir, final_pred_index, file_predictions)
        print("Model executed successfully!!!")
        return predictions_list




def restore_model(model_num, raw_test, bow_vectorizer, tfreq_vectorizer, tfidf_vectorizer, hidden_size, target_size, l2_alpha, base_dir):

    # Define graph
    tf.compat.v1.reset_default_graph()
    test_set = pipeline_test(
        model_num, raw_test, bow_vectorizer, tfreq_vectorizer, tfidf_vectorizer)
    feature_size = len(test_set[0])

    # Create placeholders
    features_pl = tf.compat.v1.placeholder(tf.float32, [None, feature_size], 'features')
    stances_pl = tf.compat.v1.placeholder(tf.int64, [None], 'stances')
    keep_prob_pl = tf.compat.v1.placeholder(tf.float32)

    # Infer batch size
    batch_size = tf.shape(features_pl)[0]

    # Define multi-layer perceptron
    hidden_layer = tf.nn.dropout(tf.nn.relu(tf.contrib.layers.linear(
        features_pl, hidden_size)), keep_prob=keep_prob_pl)
    logits_flat = tf.nn.dropout(tf.contrib.layers.linear(
        hidden_layer, target_size), keep_prob=keep_prob_pl)
    logits = tf.reshape(logits_flat, [batch_size, target_size])

    # Define L2 loss
    tf_vars = tf.compat.v1.trainable_variables()
    l2_loss = tf.add_n([tf.nn.l2_loss(v)
                        for v in tf_vars if 'bias' not in v.name]) * l2_alpha

    # Define overall loss
    loss = tf.reduce_sum(tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=logits, labels=stances_pl) + l2_loss)

    # Define prediction
    softmaxed_logits = tf.nn.softmax(logits)
    predict = softmaxed_logits

    with tf.compat.v1.Session() as sess:

        saver = tf.compat.v1.train.Saver()
        saver.restore(sess, base_dir+'/model/model%d/mymodel' % model_num)

        # Predict
        test_feed_dict = {features_pl: test_set, keep_prob_pl: 1.0}
        test_pred = sess.run(predict, feed_dict=test_feed_dict)

    return test_pred
