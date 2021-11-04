from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
senti_model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")

def sentiment_analysis (model, answer) :
    
    tokens = tokenizer.encode_plus(answer, add_special_tokens = False, return_tensors = 'pt')
    token_size = (len(tokens['input_ids'][0]))
    try :
        if token_size > 128 :
            ##split token into 128, 128,,rest of it \

            input_id_chunks = tokens['input_ids'][0].split(126)
            mask_chunks = tokens['attention_mask'][0].split(126)

            '''
            need paddign to satisfy 128 tensor length
            pretrained data is set to 128 tensor -> need to fit this

            1) slice upon 128 length
            2) compute mean of each sentiment,positive, negative and neutral
            3) voting among semtiment means

            '''
            input_id_chunks = list(input_id_chunks)
            mask_chunks = list(mask_chunks)

            for i in range(len(input_id_chunks)) :
                pad_len = 128 - input_id_chunks[i].shape[0]

                if pad_len > 0 :
                    input_id_chunks[i] = torch.cat([
                        input_id_chunks[i], torch.Tensor([0] * pad_len) ])
                    mask_chunks[i] = torch.cat([
                        mask_chunks[i], torch.Tensor([0] * pad_len) ])

            input_ids = torch.stack(input_id_chunks)
            attention_mask = torch.stack(mask_chunks)

            input_dict = {
                'input_ids' : input_ids.long(),
                'attention_mask' : attention_mask.long()
            }
            outputs = model( **input_dict)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=-1)
            probabilities = probabilities.mean(dim = 0)
            winner = torch.argmax(probabilities).item()

        else :
            output = model(**tokens)
            probability = torch.nn.functional.softmax(output[0], dim=-1)
            winner = torch.argmax(probability).item()
    except :
        winner = 3
        pass
    
    return winner

def sentiment_decision(model, df_ans,idx) :
    key1 = 'POSITIVE'
    key2 = 'NEGATIVE'
    key3 = 'NEUTRAL'
    key4 = 'UNKNOWN'
    
    total = {'week': idx,key1 :0, key2:0, key3:0, key4 :0}
    cnt = 0 
    for answer in tqdm(df_ans) : 
        #print(answer)
        result = sentiment_analysis(model, answer)

        label = ['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'UNKNOWN'][result]
        if label == key1 :
            total[key1] +=1
        elif label == key2 :
            total[key2] +=1
        elif label == key3 :
            total[key3] +=1
        else :
            total[key4] +=1
        cnt +=1
        if cnt % 10 == 0 :
            print(total)
    with open('result/top2vec/sent_best_ans.pkl', 'wb') as f :
        pickle.dump(total, f, protocol = pickle.HIGHEST_PROTOCOL)

    return total

def data_prep(idx) :
    #name = 'df_'+str(idx)+'th_by3phase.pkl'
    with open("result/top2vec/topic_sorted_{}.pkl".format(idx), 'rb') as f : 
        df = pickle.load(f)
    df_ans = df['answers']
    
    return df_ans 

def add_new_col(df):
    df["Pos"] = np.nan
    df["Neg"] = np.nan
    df["Neu"] = np.nan
    return df

def percent(row) :
    pos_val = row["POSITIVE"]
    neg_val = row["NEGATIVE"]
    neu_val = row["NEUTRAL"]
    tol_val = pos_val+neg_val+neu_val

    row.at["Pos"] = (pos_val/tol_val) *100
    row.at["Neg"] = (neg_val/tol_val) *100
    row.at["Neu"] = (neu_val/tol_val)*100
    return row

def sentiment_execute(idx) :
    final = pd.DataFrame([])
    for i in range(idx):
        print("Processing...{}".format(i))
        name= 'sent_dict_'+str(i)
        df_ans = data_prep(i)
        sent_dict = sentiment_decision(senti_model, df_ans,i)
        temp_pd = pd.DataFrame([sent_dict])
        final = pd.concat([final, temp_pd], axis=0, ignore_index=1)
                
        with open('result/top2vec/bertweet_bestans'+name+'.pkl', 'wb') as f :
            pickle.dump(sent_dict, f, protocol = pickle.HIGHEST_PROTOCOL)

    return final

def visualize_pos_neg(data):
    
    #sns.set(rc = {'figure.figsize' :(20,12)})
    sns.set_theme(style="whitegrid",rc = {'figure.figsize' :(100,50)})
    dic = {0:'effects of vaccine', 1: 'visiting overseas', 2: 'variant', 3: 'different vaccines', 4:'government policy'}
    temp_df = data[['week','Pos','Neg']]
    new_dict = {"topic":[], "percent":[], "Sentiment":[]}
    for i in range(len(temp_df)):
        name = dic[i]
        new_dict["topic"].extend([name]*2)
        new_dict["percent"].extend([temp_df.iloc[i]['Pos'],temp_df.iloc[i]['Neg']])
        new_dict["Sentiment"].extend(["Positive","Negative"])
 
    new_df = pd.DataFrame.from_dict(new_dict)
    #print(new_df)   
   
    g = sns.catplot(y='topic', x='percent', hue='Sentiment', kind='bar',legend = False, data=new_df, 
                palette=sns.diverging_palette(250, 15, s=75, l=40,  n=2, center="dark"))
    g.fig.set_size_inches(10,5)
    #plt.xticks(range(0,70,10))
    
    plt.legend(loc='upper right')
    plt.xlabel("Percentage")
    plt.ylabel("Topic")
    plt.tight_layout()
    plt.savefig('result/top2vec/Q-percentage-plot.png', dpi=300)
    
    plt.show()
    return 


if __name__ == '__main__' :
    final_dict = sentiment_execute(5)
    final_df = add_new_col(final_dict)
    final_df = final_df.apply(percent, axis =1)
    with open('pkl/slice_pkl/two_week/bertweet_final_df_topics.pkl', 'wb') as f :
        pickle.dump(final_df, f, protocol = pickle.HIGHEST_PROTOCOL)
    #visualize in bar chart
    visualize_pos_neg(final_df)