import pickle
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
import nltk
from nltk.stem import WordNetLemmatizer
from gensim.models import Word2Vec
from gensim.parsing.preprocessing import STOPWORDS
import matplotlib.pyplot as plt
import re
from tqdm import tqdm



def lemmatize_stemming(text) :
    return WordNetLemmatizer().lemmatize(text,pos='v')

def get_lemma_list(df) :

    total_ans = []
    total = 0
    #print(df['answers'])

    for ans in tqdm(df['answers']) :
        #print(ans)
        total_ans.append(ans)
        ## spliit by each answers
        #print(len(total_ans))

    total_sent = []
    #print(len(total_ans))

    for ans in tqdm(total_ans) : 
        ans_sents = []
        ans_sents = [sent for sent in ans.split(".")]
        
        total_sent.extend(ans_sents)
        #print(total_sent)
    tokenize_sent = []

    for sent in tqdm(total_sent) :
        sent = sent.replace('\n'," ")
        sent = sent.lower() 
        tokenize_sent.append(word_tokenize(sent))

    tokenize_sent = [sent for sent in tokenize_sent if sent != []]

    lemma_sent = [[lemmatize_stemming(word) for word in sent ] for sent in tokenize_sent]

    return lemma_sent 

def filter_sent(sent_list) : 

    filter_lemma = []

    for sent in lemma_sent :
        filter_sent = []
        for word in sent :
            if word == "vaccines" or word == "vaccination" or word == "vaccinate" or word == "vaccinations" or word == "vaccinates" :
                word = "vaccine"

            filter_sent.append(word)
        filter_lemma.append(filter_sent)

    return filter_lemma


def word2vec_model(filter_lemma,idx) :

    model = Word2Vec(filter_lemma, size = 300, window = 5, min_count = 100, workers = 3 , sg=1, iter = 5, negative = 5)
    model.save("result/top2vec/t"+str(idx)+"th.model")


def get_simlist(sim_list,name) :
    df = pd.DataFrame(sim_list.items(), columns  = ['Word', 'Similarity'])
    df.to_csv('result/top2vec/t'+name+'.csv', index = False)
    
    return df


def similar_words(model, keyword, topn,name) :
    sim_list = model.wv.similar_by_vector(keyword, topn=topn, restrict_vocab=None)
    sim_list_dict = {word :sim for word, sim in sim_list}

    df = get_simlist(sim_list_dict, name)
    
    return df

def remove_stopword(df) :

    sim_word = df['Word']
    idx_list = []
    for idx, word in enumerate(sim_word) :
        if word not in STOPWORDS :
            idx_list.append(idx)

    final_list = []
    for idx in idx_list :

        final_list.append(sim_word[idx])

    return final_list 

def get_filtered_df (N) :
    for idx in range(N)  :


        '''
        load model - get 300 similar word - remove stopword 
        output : data frame for 50 similar words with "vaccine" by each topic 
        '''

        with open('result/top2vec/t'+str(idx)+'th.model','rb') as f :
            model = pickle.load(f)
        df = similar_words(model,'vaccine',300,str(idx)+"th df")
        
        final_list = remove_stopword(df)
        #print(final_list)
        with open('result/top2vec/t'+str(idx)+'finalword_list.pkl','wb') as f:
            pickle.dump(final_list, f)
    dic = {0:'effects of vaccine', 1: 'visiting overseas', 2: 'variant', 3: 'different vaccines', 4:'government policy'}
    topic_list = list(dic.values())
    total_f_list =[]
    for idx in range(N) :

        with open('result/top2vec/t'+str(idx)+'finalword_list.pkl','rb') as f :
            f_list = pickle.load(f)

        if len(f_list) < 50 :
            for _ in range(len(f_list),50) :
                f_list.append("-")
        else : 
            f_list = f_list[:50]
        
        total_f_list.append(f_list)
    #print(total_f_list)
    df = pd.DataFrame(columns=topic_list, index = range(50))
    #print(df)
    for idx in range(N) :
        #print(total_f_list[idx])
        df[topic_list[idx]]= total_f_list[idx]
    
    return df

if __name__ == "__main__" :

    date_list = []

    '''
    input : answers data frame

    save 1 : lemmatizing sent and 
    save 2 : model for each topic at function word2vec_model

    '''

    for idx in range(5) :

        #lemmatiziang here 

        with open("result/top2vec/topic_sorted_{}.pkl".format(idx), 'rb') as f : 
            df = pickle.load(f)
        lemma_sent = get_lemma_list(df)
        
        with open('result/top2vec/ent_'+str(idx)+'by_topic.pkl', 'wb') as f:
            pickle.dump(lemma_sent, f)
            
        filter_lemma = filter_sent(lemma_sent)
        word2vec_model(filter_lemma,idx)

        # here, topic index is needed!       

        #date,_,_ = date_index(df)
        #date_list.append(date)

        df = get_filtered_df(5)
