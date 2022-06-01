import pickle
import pandas as pd 
import numpy as np  
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim import corpora , models
import nltk
import gensim
import nltk.stem as stemmer
from tqdm import tqdm
import matplotlib.pyplot as plt


nltk.download('wordnet')


#find optimal number of topics

def find_optimal_n_topic(dictionary, corpus, data):
    """
    Coherence score: measures the relative distance between words within a topic
    """
    coherence_values,model_list = [], []
    for num_topics in tqdm(range(2, 50, 3)):
        model = gensim.models.LdaMulticore(corpus, num_topics = num_topics, id2word = dictionary ,passes = 2, workers =4)
        model_list.append(model)
        coherencemodel = gensim.models.coherencemodel.CoherenceModel(model=model, texts=data, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())

    print(coherence_values)
    x = range(2, 50, 3)
    plt.plot(x, coherence_values)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend(("coherence_values"), loc='best')
    plt.show()

def topic_df(topic_list, num_topic) :
    t_list = []
    for topic in topic_list :
        sub_list = []
        sub_topic = topic.split("+")
        sub_list = [t.split("*")[1] for t in sub_topic]
        t_list.append(sub_list)

    topic_df_dict = {}
    for i in range(len(t_list)):
        name = "topic "+str(i)
        topic_df_dict[name] = t_list[i]
    
    topic_df = pd.DataFrame(topic_df_dict)

    filename = str(num_topic)+ " topics"
    with open ("pkl/"+filename+".pkl", "wb") as f :
        pickle.dump(topic_df, f)

    topic_df.to_csv("result/"+filename+".csv")

    return topic_df

def find_word(keyword) :
    idx = 0 
    idx_list = []
    for q in lemma :
        if keyword in q[0] :
            idx_list.append(idx)
        idx +=1

    return idx_list

def find_question(idx_list) :
    q_list = []
    for idx in idx_list :
        q_list.append(questions[idx])

    return q_list 

if __name__ == "__main__" :

    #lda-tf_idf model
    lda_with_tfidf = gensim.models.LdaMulticore(corpus_tf_idf, num_topics = 10, id2word = dict_word_idx ,passes = 2, workers =4)
    topic_list = []
    for idx , topic in lda_with_tfidf.print_topics(-1):
        print('Topic : {} \n Words: {}'.format(idx,topic))
        topic_list.append(topic)

    topic_df(topic_list, "number of topics ex)10")

    #new_df from 2-Q-PREPROCESS_data.py

    lemma = new_df['Lemma_sent']
    questions = [q for q in new_df['questions']]