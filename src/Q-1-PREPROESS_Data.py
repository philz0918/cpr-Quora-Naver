import pickle
import pandas
import numpy as np  
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
import gensim
'''
nltk.download('wordnet')
'''
# apply this into loaded data frame
def one_answer(row) :
    length = True
    idx = 0 
    while length == True :
        len_val = len(row.at['answers'][idx])
        if len_val >= 1:
            row.at['answers'] = row.at['answers'][idx]                        
            length = False
        else :
            idx +=1
    return row
def ans_sub(row) :
    row.at['answers'] = row.at['answers'].replace('\n'," ")
    return row 

'''
function for preprocessing dataframe
regularization, lemmatizing, tokenizing
'''

def preprocessing(answers) :
    
    try : 
        token_sent = []
        answers  = answers.split(".")
        for sent in answers :
            sent = sent.replace('\n', " ")
            sent = sent.replace('\\', ' ')
            sent = sent.replace('\ ', " ")
            sent = sent.replace('\\n', " ")
            sent = sent.lower()
      
            tokenized= word_tokenize(sent) 
            token_sent.append(tokenized)

            #print(token_sent)
    #case of nan
    except :
        pass
    
    return token_sent

def pre_lemma(answers) :
    
    try : 
        token_sent = []
        answers  = answers.split(".")
        for sent in answers :
            sent = sent.replace('\n', " ")
            sent = sent.replace('\\', ' ')
            sent = sent.replace('\ ', " ")
            sent = sent.replace('\\n', " ")
            sent = sent.lower()

            #get list of lemmatized words
            text = word_tokenize(sent)
            text_lemma = []
            for token in  text :

                if token == "vaccines" or token == "vaccinated" or token == "vaccination" or token == "vaccinations" :
                    token = "vaccine"
                if token == "covid" or token == "19":
                    token = "coronavirus"
                if token not in gensim.parsing.preprocessing.STOPWORDS :
                    text_lemma.append(lemmatize_stemming(token))
                    
            token_sent.append(text_lemma)

            #print(token_sent)
    #case of nan
    except :
        pass
    
    return token_sent

def get_number(number) :
    
    try :
        num = 0 
        num = number.split(' ')[0]
        
    except :
        pass
    
    return num

def lemmatize_stemming(text) :
    return WordNetLemmatizer().lemmatize(text, pos= 'v')

def add_token(df) :
    df['Token_sent'] = df['Token_sent'].apply(lambda x : preprocessing(x))
    
    return df

def add_token_sent(df, name) :
    df[name] = np.nan
    df[name] = df[name].astype('object')
    df[name] = df['questions']
    
    return  df 

def add_lemma(df) :
    
    df['Lemma_sent'] = df['Lemma_sent'].apply(lambda x : pre_lemma(x))
    
    return df

def add_qtoken(df) :
    df['Q_token'] = df['Q_token'].apply(lambda x : pre_lemma(x))
    
    return df
    
    
def add_num(df)  :
    df['N_answer'] = df['N_answer'].apply(lambda x : get_number(x))
    return  df


if __name__ == "__main__" :
    with open ("pkl/sorted_df.pkl", "rb") as f :
        sorted_df = pickle.load(f)

    sorted_df = sorted_df[['date','questions','answers']]
    sorted_df = sorted_df.apply(one_answer, axis = 1)
    sorted_df = sorted_df.apply(ans_sub,axis = 1)

    df_sorted = add_token_sent(df_sorted, "Lemma_sent")
    df_sorted = add_token_sent(df_sorted,'Token_sent')
    df_sorted = add_token_sent(new_df, 'Q_token')
    new_df =  add_token(df_sorted)
    new_df = add_lemma(new_df)
    new_df = add_qtoken(new_df)