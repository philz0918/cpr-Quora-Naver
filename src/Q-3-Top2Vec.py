from top2vec import Top2Vec

class Top2vec():

    def __init__(self, model) :
        self.model = model
    
    def get_num_topics(self) :
        return self.model.get_num_topics()
    
    def get_topic_sizes(self):
        topic_sizes, topic_nums = self.model.get_topic_sizes()
        return topic_sizes, topic_nums
    
    def get_topics(self):
        topic_words, word_scores, topic_nums = self.model.get_topics()
        return topic_words, word_scores, topic_nums
    
    def document_by_topic(self, topic_num, num_docs):
        documents, document_scores, documents_ids = self.model.search_documents_by_topic(topic_num = topic_num, num_docs = num_docs)
        return documents, document_scores, documents_ids
    
    def search_by_topic(self, keywords,num_topics):
        topic_words, word_scores, topic_scores, topic_nums = self.model.search_topics(keywords=[keywords], num_topics=num_topics)
        return topic_words, word_scores, topic_scores, topic_nums
    
    def document_by_keyword(self, keyword, num_docs) :
        documents, document_scores, document_ids = self.model.search_documents_by_keywords(keywords = keyword, num_docs = num_docs)
        return documents, document_scores, document_ids
    
    def topic_dict(self, topic_words) :
        topic_dict = {}
        for idx, topic in enumerate(topic_words) :
            topic_dict[idx] = topic
        df_topics = pd.DataFrame(topic_dict)
        df_topics.to_csv("result/top2vec/df_topics0.csv")
        return df_topics
    
    def keyword_split(self, data) :
        data.loc[:,'topic'] = False
        data.loc[:,'topic_prob'] = False
        
        keyword_list = [["safe", "trust","refuse","effect", "feel", "effective"],["passport","available", "travel", "country"],["variant","virus"],["dose","moderna", "johnson", "pfizer", "astrazeneca"]
                       ,["trump", "biden", "require"]] # effct, variant, safe, kinds of vaccines, government, overseas

        for idx, keyword in enumerate(keyword_list) :
            print(idx, keyword)
            try :
                documents, document_scores, document_ids = self.model.search_documents_by_keywords(keywords=keyword, num_docs=3925)
            except :
                print("error", keyword)
                continue
            else :
                for n, i in enumerate(document_ids):
                    if data.loc[i, "topic_prob"] == False :
                        data.loc[i, "topic"] = idx
                        data.loc[i, "topic_prob"] = document_scores[n]
                    else: 
                        if data.loc[i, "topic_prob"] < document_scores[n] :
                            data.loc[i, "topic"] = idx
                            data.loc[i, "topic_prob"] = document_scores[n]
        data.sort_values(by=["topic_prob"], inplace = True, ascending = False)
        
        return data

def get_percent(row) :
    #%.2f" % round(a, 2)
    row.at["proportion"]  = round((row.at['num']/sum_topic),2)
    return row

if __name__ =="__main__" :
    
    #sorted_df from 2-Q-PREPROCESS_data.py

    df_questions = list(sorted_df["questions"])
    model = Top2Vec(documents = df_questions,speed = "deep-learn",min_count = 10, workers = 8)

    T2V = Top2vec(model)
    key_split = T2V.keyword_split(data)
    
    for i in range(len(list(set(key_split['topic'])))) :
        key_split[key_split['topic']== i].to_csv("result/top2vec/topic_{}.csv".format(i), index = False)

    length_dict = {}
    topic = ["effect", "travel", "variant", "vaccines", "government"]
    for i in range(5) : 
        name = "topic_{}.csv".format(i)
        data = pd.read_csv("result/top2vec/"+name)
        data_remove = data.drop(data[data.topic_prob <= 0].index)
        data_remove.to_csv("result/top2vec/topic_sorted_{}.csv".format(i), index = False)
        #with open("result/top2vec/topic_sorted_{}.pkl".format(i), 'wb') as f : 
        #    pickle.dump(data_remove, f)
        length_dict[i] = len(data_remove)

    len_df = pd.DataFrame(length_dict.items(),columns= ["topic", "num"])

    sum_topic = np.sum(len_df['num'])
    len_df = len_df.apply(get_percent,axis = 1)