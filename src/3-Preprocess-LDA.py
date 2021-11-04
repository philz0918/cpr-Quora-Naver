
import pandas as pd
import time
import pickle
import matplotlib.pyplot as plt
import re
from tqdm import tqdm
import numpy as np
import seaborn as sns
tqdm.pandas()
pd.set_option('display.max_columns', None )
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', None )
import warnings
warnings.filterwarnings('ignore')

from konlpy.tag import Mecab , Okt, Kkma, Komoran
from gensim import corpora,models
from gensim.models.ldamodel import LdaModel
from gensim.models.coherencemodel import CoherenceModel


def question_add():
    """
    (1) add up questions + qustions_add to 'questions_Full_text'
    (2) questions_preprocess : 한글, 영어, 숫자만 남기고 제거

    :return:
    """
    data = pd.read_csv('0828_only_best_answers.csv')
    print(data.shape) #(18204, 10)

    data['q'] = data.progress_apply(lambda x: 1 if x['questions_add'] not in [np.nan, 'NaN'] else 0, axis= 1 )
    print(data)

    data.loc[data['q'] == 1 , 'question_full_text'] = data['questions'] +' '+ data['questions_add']
    data.loc[data['q'] == 0 , 'question_full_text'] = data['questions']

    def clean_data(x):
        x= x.replace(".", " ").strip()
        x= x.replace("·", " ").strip()
        x = re.sub(pattern='[^ ㄱ-ㅣ가-힣|0-9|a-zA-Z]+', repl='', string=x)
        return x
    data['question_full_text']= data['question_full_text'].progress_apply(lambda x : clean_data(x))
    print(data[['questions', 'questions_add','question_full_text']])

    return data


def tokenize(data):
    """

    (1) question_reduced : 단어의 길이가 2이상인 명사, 형용사, 외국어, 감탄사, 부사, 관형사, 동사 만 수집
    """
    tokenizer = Komoran()
    def reduce(x):
        # print(x)
        tagged = tokenizer.pos(x)
        nouns=[]
        l =  ['NN', 'NNG' , 'NNP', # 명사, 보통명사, 고유 명사
               'VA', 'VV', 'VX' #형용사, 동사
                'XR', 'SL','NA' #어근/ 외국어,  감정 / 분리안된 단어들
            ]
        # print(tagged)
        for s,t in tagged:
            if t in l:
                if t in ['VA','VV','VX']:  s+='다'
                if t in ['XR'] : s+= '하다'
                if s == '아스트라' : s+='제네카'
                if (s=='모') and (t == 'NNG') : s+='더나'
                if (s != '카') and (s!= '안녕하세요')\
                        and (s!= '하다')and (s!= '있다')\
                        and (s!= '없다') and (s!= '되다'): nouns.append(s)

        # print(nouns)
        return nouns

    data['question_reduced']= data['question_full_text'].progress_apply(lambda x: reduce(x))
    print(data[['question_full_text', 'question_reduced']].head(50))

    # data.to_csv('0913_tokenized_data.csv', index=False)

    return data

def make_dictionary(data):
    """
    1) make dictionary for words included in column --find optimal n for topics
    """

    #1 : delete words according to occurance -- see how many are deleted
    dictionary = corpora.Dictionary(data['question_reduced'])
    # print(len(dictionary))  #21546

    # dictionary.filter_extremes(no_below=2)  #filter according : n_count >2
    print(len(dictionary)) #10192

    corpus = [dictionary.doc2bow(w) for w in data['question_reduced']]
    # print('Number of unique tokens: %d' % len(dictionary))
    # print('Number of documents: %d' % len(corpus))


    # print(dictionary.token2id)
    # print(data.loc[0,'question_reduced'])
    # print(corpus[0])
    # ['전문가', '말', '내년', '2월', '달', '마스크', '벗', '있다', '하다']
    # [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1)]
    # dictionary : {word:index}
    #corpus :{index, num_counts}

    #check frequency of words in graph
    # vocab_tf = {}
    # for i in corpus:
    #     for item, count in dict(i).items():
    #         if item in vocab_tf:  vocab_tf[item] += count
    #         else:  vocab_tf[item] = count
    # vocab_tf= sorted(vocab_tf.items(), key=lambda vocab_tf: vocab_tf[1], reverse=True)
    # # print(vocab_tf[:20])
    # # print(dictionary[47]) #백신
    # # print(dictionary[11]) #코로나
    # N = [c for i,c in vocab_tf]
    # print(np.min(N))
    # print(np.max(N))
    # print(np.percentile(N, [0, 25, 50, 75, 100], interpolation='nearest'))
    # #[    1     1     2     6 21618]
    # sns.boxplot(N)
    # plt.show()

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    return dictionary, corpus, corpus_tfidf,  data

def find_optimal_n_topic(dictionary, corpus, data):
    """
    2) Coherence score: measures the relative distance between words within a topic

    """
    a, b, c = 5,15,1
    coherence_values,model_list = [], []
    for num_topics in tqdm(range(a, b, c)):
        model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, random_state=2021 )
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=data['question_reduced'], dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())

    print(coherence_values)
    x = range(a, b, c)
    plt.plot(x, coherence_values)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend(("coherence_values"), loc='best')
    plt.show()




def model(corpus, data, k):
    lda_model = LdaModel(corpus, id2word=dictionary, num_topics=k ,random_state=2021)
    topics = lda_model.print_topics(num_words=50)
    t = pd.DataFrame()
    t.to_csv('0927_LDA_naver_keywords.csv' ,index=False, encoding='utf-8-sig')
    for topic in topics: print(topic)


    #compute Coherence score
    coherence_model_lda = CoherenceModel(model=lda_model, texts=data['question_reduced'], dictionary=dictionary, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()
    print('\nCoherence Score (c_v): ', coherence_lda)


    return lda_model


def lda_result(lda_model,data,corpus ):
    # for i, topic_list in enumerate(lda_model[corpus]):
    #     if i == 5: break
    #     print(i, '번째 문서의 topic 비율은', topic_list)


    for i, topic_list in tqdm(enumerate(lda_model[corpus])) :

        # print(i, topic_list)
        doc = topic_list[0] if lda_model.per_word_topics else topic_list
        doc = sorted(doc, key=lambda x: (x[1]), reverse=True)

        for  j, (topic_num, prob) in  enumerate(doc):
            if j == 0 :
                data.loc[i,'topic'] = int(topic_num)
                data.loc[i, 'probability'] = round(prob,4)
                # data.at[i, 'topic_probs'] = topic_list
            else : break
    print(data.head(30))
    print(data.tail(30))

    return data


if __name__ == "__main__":
    data= question_add()
    data = tokenize(data)

    # data = pd.read_csv('./0913_tokenized_data.csv',converters={'question_reduced':eval})
    # print(data.shape)
    # dictionary, corpus, corpus_tfidf, data= make_dictionary(data)
    # find_optimal_n_topic(dictionary, corpus_tfidf, data)


    # k = 11
    # lda_model = model(corpus_tfidf, data, k)
    # data = lda_result(lda_model,data,corpus_tfidf)
    #
    # d = pd.DataFrame()
    # for i in range(k):
    #     d= d.append(data[data['topic'] == i ], ignore_index=True)
    # d= d[['question_full_text', 'question_reduced', 'topic','probability']]
    # d.to_csv('0927_naver_k_11_data_classification.csv' ,index=False, encoding='utf-8-sig')


    #휴가 관련 단어
    # for c in ['questions', 'questions_add','best_answers'] : data.loc[data[c].str.contains('휴가', regex=True, na=False), 'include'] = True
    #
    # d= data[data['include'] == True ]
    # print(d.shape)
    # print(d)
    # d[['question_full_text', 'best_answers']].to_csv('d.csv', index=False, encoding='utf-8-sig')