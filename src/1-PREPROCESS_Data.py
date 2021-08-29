import warnings
warnings.filterwarnings(action='ignore')
from tqdm import tqdm
import pandas as pd
import seaborn as sns
sns.set_style("whitegrid")
pd.set_option('display.max_columns', None )
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', None )
import pickle
from konlpy.tag import Okt
from collections import Counter
import matplotlib.pyplot as plt



##############################################
####################### MERGE DATA
##############################################

def merge_data(x):
    d = pd.DataFrame(  columns=['page', 'date', 'tags', 'questions', 'questions_add', 'answers', 'N_answer', 'url', 'category'])

    for i, j in zip( ['2020','2020','2020','2020','2020','2020','2020',
                      '2021','2021','2021','2021','2021','2021','2021','2021'],
                     ['06', '07', '08', '09', '10', '11', '12',
                      '01', '02', '03', '04', '05', '06', '07'] )  :

        df = pd.read_csv('/Users/janechoi/PycharmProjects/vaccine/final/['+str(i)+'.'+str(j)+']crawling.csv')
        print('/Users/janechoi/PycharmProjects/vaccine/final/['+str(i)+'.'+str(j)+']crawling.csv', df.shape)
        d = pd.concat([d, df], axis=0)
        d = d.drop_duplicates(['date', 'questions', 'questions_add','answers'])
        print('total data shape is ', d.shape)

    d.to_csv('/Users/janechoi/PycharmProjects/vaccine/final/final_data.csv',index=False)
    # with open("0824_naver_org_data", "wb") as file:
    #     pickle.dump(d, file)

##############################################
####################### PREPROCESS DATASET (INCLUDE/EXCLUDE WORDS)
##############################################

def pre_process():
    data =pd.read_csv('/Users/janechoi/PycharmProjects/vaccine/final/final_data.csv')

    data = data.sort_values('date')
    data['date']  = pd.to_datetime(data['date'])
    data = data[data['date'] >= '2020-06-27']
    data = data[data['date'] <= '2021-06-27']
    data.reset_index(inplace = True , drop = True )
    print(data.shape) #(60130, 9)
    vaccine_words = 'pcr(?i)(?:\s)*(검사)*|트래블(?:\s)*버블|vaccine(?i)|coronavac(?i)|astrazeneca(?i)|moderna(?i)|pfizer(?i)|아스트라|시노(팜|백)|(?:\s|^)재난(?:\s|\-)*지원(?:\s)*금(?:\s|$)|(?:\s|^)질병(?:\s|\-)*관리(본부|청)(?:\s|$)|(?:\s|^)(C|c)(O|o)(V|v)(I|i)(d|D)(?:\s|\-)*(19)*(?:\s|$)|(?:\s|^)(C|c)(O|o)(R|r)(o|O)(n|N)(A|a)(?:\s|\-)*(19)*(?:\s|$)|(?:\s|^)(코로나|코비드)(?:\s|\-)*(19)*(?:\s|$)|아스트라제(네|니)카|얀센|모더나|화이자|(A|a)(Z|z)|(?:\s|^)사전(?:\s)*예약(?:\s|$)|(?:\s|^)(자가)*(?:\s)*격리(?:\s|$)|(?:\s|^)10(?:\s)*부제(?:\s|$)|확진|완치|마스크'
    stop_words = '트위치|영작|수행(?:\s)*평가|\#문제풀이|가상(?:\s)*화폐|(유방|간|갑상선|췌장|대장)(?:\s)*암|금리|랜섬(?:\s)*웨어|(영어)*(?:\s)*(해석|작문)|대상포진|(파이썬|(P|p)(y|Y)(T|t)(h|H)(o|O)(n|N))|(?:\s|^)(알레르기성)*(?:\s)*피부염(?:\s|$)|(?:\s|^)셀트(?:\s)*(리온)*(?:\s|$)|(?:\s|^)(미국)*(?:\s)*증시(?:\s|$)|(?:\s|^)매(수|도)(?:\s|$)|(?:\s|^)파상풍(?:\s)*(주사)*(?:\s|$)|(?:\s|^)꿈(?:\s)*(해몽)*(?:\s|$)|(?:\s|^)(일본)*(?:\s)*뇌염(?:\s|$)|독감|헤르페스|(?:\s|^)(h|H)(p|P)(V|v)(?:\s|$)|(강아지|고양이)|(?:\s|^)펀드(?:\s)*(투자)*(?:\s|$)|흑사병|(?:\s|^)컴(퓨)*터(?:\s|$)|노트북|(?:\s|^)주(식|가)(?:\s|$)|산부인과|곤지름|(?:\s|^)알(콜|코올)(?:\s|$)|햄버거병'
    cat = ['questions_add','questions', 'answers']
    for c in cat:    data.loc[data[c].str.contains(vaccine_words, regex=True, na = False), 'INCLUDE'] =True
    print(data[data['INCLUDE']==True].shape)  #(35751, 10)
    for c in cat:  data.loc[data[c].str.contains(stop_words, regex=True, na=False), 'INCLUDE'] = False
    print(data[data['INCLUDE']==True])
    data= data[data['INCLUDE']==True]
    data = data.fillna('')
    print(data.head(50))
    print(data.tail(50))
    print(data.shape) #26987
    data.to_csv('preprocess_naver_data.csv', index=False )
    with open( "0825_naver_preprocessed_data", "wb" ) as file: pickle.dump(data, file)

##############################################
####################### SIMPLE EDA PURPOSE
##############################################

def eda():
    with open( "0825_naver_preprocessed_data", "rb" ) as file: data = pickle.load(file)
    print(data)
    print(data['url'][:20])

    # 1. Boxplot n_answer
    # sns.boxplot(y= 'N_answer',   data= data)
    # plt.title('[NAVER] Stats for total number of answer')
    # plt.savefig('box_n_answer_naver.png',dpi =300)
    # plt.show()

    # 2. scatter_n_answer
    # sns.scatterplot(y= 'N_answer', x='date' , data= data,s=15, alpha = 0.5 )
    # plt.title('[NAVER] Total number of answers')
    # plt.savefig('scatter_n_answer_naver.png',dpi =300)
    # plt.tight_layout()
    # plt.show()

    # 3. mean of n_answer by 2weeks
    # data.set_index('date', inplace=True)
    # df = pd.DataFrame(data.N_answer.resample('2W').mean())
    # df.columns = ['Mean_N_answer']
    # print(df)
    # sns.lineplot(x = 'date', y = 'Mean_N_answer', data= df)
    # plt.axvline(pd.to_datetime('2021-02-26') ,color= 'red')
    # plt.savefig('mean_of_a_2k_naver.png',dpi =300)
    # plt.tight_layout()
    # plt.show()



    # 4. median of n_answer by 2weeks
    # data.set_index('date', inplace=True)
    # df = pd.DataFrame(data.N_answer.resample('2W').median())
    # df.columns = ['Median_N_answer']
    # print(df)
    # sns.lineplot(x = 'date', y = 'Median_N_answer', data= df)
    # plt.axvline(pd.to_datetime('2021-02-26') ,color= 'red')
    # plt.savefig('median_of_a_2k_naver.png',dpi =300)
    # plt.tight_layout()
    # plt.show()



    # 5. n of questions by 2weeks
    # df = pd.DataFrame(data.groupby('date')['questions'].nunique())
    # df.columns =['n_questions']
    #
    # df = pd.DataFrame(df.n_questions.resample('2W').sum())
    # df.columns = ['Sum_n_questions']
    # print(df)
    # sns.lineplot(x = 'date', y = 'Sum_n_questions', data= df)
    # plt.axvline(pd.to_datetime('2021-02-26') ,color= 'red')
    # plt.savefig('n_of_q_2k_naver.png',dpi =300)
    # plt.tight_layout()
    # plt.show()


##############################################
####################### KOREAN WORDS FREQ CHECK
##############################################

def korean_words_frequency(data):
    q = ''.join(data['questions'])
    r = ''.join(data['questions_add'])
    l = ''.join(data['answers'])
    d = q+r+l
    def count_okt(t):
        okt = Okt() #twitter
        noun = okt.nouns(t)
        c = Counter(noun)
        for i,v  in c.most_common(50) :
            if len(i) >=  2  :  print(i,v)


    print(' ')
    print('questions')
    count_okt(q)

    print(' ')
    print('questions add')
    count_okt(r)

    print(' ')
    print('answers')
    count_okt(l)

    print('all together ')
    count_okt(d)



if __name__ == "__main__":
    # merge_data(x)
    # pre_process()
    eda() # 26987,10


