
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import pickle
import re
from tqdm import tqdm
tqdm.pandas()
pd.set_option('display.max_columns', None )
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None )
import warnings
warnings.filterwarnings('ignore')


def re_crawl():
    # basic set-up
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("headless")

    with open( "0825_naver_preprocessed_data", "rb" ) as file: data = pickle.load(file)
    # print(data.head())
    df = pd.DataFrame(columns=['url', 'best_answer'])
    for x in tqdm(data['url'].unique() ) :

        time.sleep(.5)
        res  = []

        driver = webdriver.Chrome(executable_path='/Users/janechoi/PycharmProjects/vaccine/chromedriver',
                                  options=chrome_options)
        print(x)
        try:
            driver.get(x)
            ans_num = int(driver.find_element_by_css_selector( '#answerArea > div.answer-content__inner > div.c-classify.c-classify--sorting > div.c-classify__title-part > h3 > em').text)

            # 질문자 채택
            for i in range(1, ans_num + 1):
                try:
                    driver.find_element_by_css_selector('#answer_' + str(i) + '> div.c-heading-answer > div.c-heading-answer__body > div.adopt-check-box> span.adopt-check.adopt-check--question').text
                    res.append(i)
                    break
                except: pass
            if len(res) == 0: res.append(False)
            # 지식인 채택
            for i in range(1, ans_num + 1):
                try:
                    driver.find_element_by_css_selector('#answer_' + str(i) + '> div.c-heading-answer > div.c-heading-answer__body > div.adopt-check-box > span.adopt-check.adopt-check--intellect').text
                    res.append(i)
                    break
                except:  pass
            driver.close()
            if len(res) != 2:  res.append(False)

            # False , False -> 채택 된 답변이 없음
            # n != n -> 앞의 두개가 채택됨
            # n == n -> 0 번 채택
            # n , False / False, n -> 0번 채택
            if res[0] == res[1]:
                if res[0] == False:
                    print(res, str(False))
                    df = df.append({'url': x, 'best_answer':False } , ignore_index=True)
                else:  df = df.append({'url': x, 'best_answer':0 } , ignore_index=True) # same question has been selected
            else:  # 채택순이기 때문에 무조건 0 또는 1 임
                if (res[0] == False) or (res[1] == False):
                    print(res, str(0))
                    df = df.append({'url': x, 'best_answer':0} , ignore_index=True)  # 둘 중 하나가 False 이면 0번째 답변이 채택
                else:
                    print(res, str(1))
                    df = df.append({'url': x, 'best_answer':1 } , ignore_index=True)  # 둘다 false가 아니며 다른 질문인 경우

        except:
            print(x, 'not founnd')
            df = df.append({'url': x, 'best_answer': 'not found' } , ignore_index=True)
        df.to_csv('top_ans_add_0828.csv', index=False)
    #best answer
        # False -> 채택된 답변이 없음
        # 0 -> 0번째 답변만 채택
        # 1 -> 0,1 번째 답변 채택
    df.to_csv('top_ans_add_0828.csv', index=False)

def preprocess():
    df = pd.read_csv('top_ans_add_0828.csv')
    data = pd.read_csv('0825_naver_preprocessed_data.csv', converters= {'tags': eval, 'answers': eval} )
    # print(data.shape) #(26987, 10)
    # print(df.shape)  # (26987, 2)

    data = pd.merge(data,df,  on = 'url', how = 'right')
    # print(data.head())
    # print(data.isnull().sum()) #0
    def leave_best(x):
        if x['best_answer'] == False : return False
        elif x['best_answer'] == '0' : return x['answers'][0]
        elif x['best_answer'] == '1' : return x['answers'][:2]  # x== 1 -> 0, 1 answer leave
        else : return False

    data['best_answers'] = data.progress_apply(lambda x: leave_best(x), axis=1 )
    # print(data['best_answer'].value_counts())
    # 0            18003
    # False         8775
    # 1              201
    # not found        8

    data = data[data['best_answers'] != False ]
    # print(data.shape) #(18204, 12)

    data = data[['page', 'date', 'tags', 'questions', 'questions_add', 'best_answers', 'best_answer','N_answer', 'url', 'category']]
    data.rename(columns= {'best_answer': 'N_best_answer'}, inplace=True)
    data.to_csv('0828_only_best_answers.csv', index=False)
    print(data.head(10))

if __name__ == "__main__":
    # re_crawl()
    preprocess()