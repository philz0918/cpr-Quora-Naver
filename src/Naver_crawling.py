
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re
from tqdm import tqdm

def crawling_process(start, end, query):
    """
    k : page number
    i : question number
    n : answer number

    :param start: start date
    :param end: end date
    :param query: query such as vaccine
    :return: dataframe of values

    different types :
    (1) original (ex) https://kin.naver.com/qna/detail.naver?d1id=7&dirId=710&docId=362120501&qb=67Cx7Iug&enc=utf8&section=kin&rank=121&search_sort=3&spq=1
    (2) FAQ mark (ex) https://kin.naver.com/qna/detail.naver?d1id=7&dirId=70307&docId=370497385&qb=67Cx7Iug&enc=utf8&section=kin&rank=485&search_sort=3&spq=0
    (3) 내공 mark Q 200 (ex) https://kin.naver.com/qna/detail.naver?d1id=1&dirId=10206&docId=362120315&qb=67Cx7Iug&enc=utf8&section=kin&rank=122&search_sort=3&spq=1
    (4) Today's question (ex) https://kin.naver.com/qna/todayDetail.nhn?d1id=8&dirId=814&docId=362118361&qb=67Cx7Iug&enc=utf8&section=kin&rank=123&search_sort=3&spq=1

    """
    #create dataframe
    df = pd.DataFrame(columns = ['page','date','tags','questions','questions_add', 'answers','N_answer', 'url' , 'category' ])
    not_working= pd.DataFrame(columns=['url', 'exit'])
    #basic set-up
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("headless")
    driver = webdriver.Chrome(executable_path='/Users/janechoi/PycharmProjects/vaccine/chromedriver',
                              options=chrome_options)
    tabs = driver.window_handles
    driver.switch_to.window(tabs[0])
    k = 1
    try :
        while True :
            print('Current Page' , k )
            #k :  page number

            url = 'https://kin.naver.com/search/list.nhn?&section=kin&query=' + str(query) + '&period=' + str(start) + '%7C' + str(end) + '&section=kin&page=' + str(k) +'&sort=date'
            driver.get(url)
            print(url)

            # i: i'th question
            for i in tqdm(range(1,11)): #max question is 10 for each page
                date = tag = question = content = ans = urls = cat = None

                #open page 1~ 10 with new window
                target = driver.find_element_by_xpath('//*[@id="s_content"]/div[3]/ul/li['+str(i)+']/dl/dt/a')
                urls = target.get_attribute('href')
                target.send_keys(Keys.CONTROL +"\n")
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(.5)

                #collect quesion title & date
                # type 3 : 내공 제공
                try: question = driver.find_element_by_class_name('title').text
                except: #오늘의 질문은 패스!
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    date = tag = question = content = ans = urls = cat = None
                    continue
                print('question: ', question)


                # If the question has extra explanation
                try:content= driver.find_element_by_xpath('// *[ @ id = "content"] / div[1] / div / div[1] / div[3]').text
                except: content = None
                # print('content:', content)

                try: date = driver.find_element_by_css_selector('#content > div.question-content > div > div.c-userinfo > div.c-userinfo__left > span:nth-child(2)').text.split('\n')[1]
                #type 2: FAQ mark
                except: date = driver.find_element_by_css_selector('#content > div.question-content > div > div.c-userinfo > div.c-userinfo__left > span:nth-child(1)').text.split('\n')[1]
                # print('date: ', date)

                #collect category & tag
                time.sleep(.5)
                l = driver.find_elements_by_xpath('// *[ @ id = "content"] / div[1] / div / div[2] / a')
                tag = []
                for c in l:
                    try: cat = c.text.strip().split('Ξ')[1].strip()
                    except:
                        try:tag.append(c.text.strip().split('#')[1])
                        except:pass
                # print(cat, tag)

                #click if next page available
                time.sleep(.5)
                while True:
                    try: driver.find_element_by_xpath('//*[@id="nextPageButton"]/span').click()
                    except: break

                #collect the answers : num = answer cnt
                num = int(driver.find_element_by_css_selector('#answerArea > div.answer-content__inner > div.c-classify.c-classify--sorting > div.c-classify__title-part > h3 > em').text)
                ans = []
                # n: n'th answer

                # print('num:', num)
                for n in range(1,num+1):
                    try:
                        try: answer = driver.find_element_by_css_selector('#answer_'+str(n)+' > div._endContents.c-heading-answer__content > div._endContentsText.c-heading-answer__content-user > div.se-viewer.se-theme-default > div.se-main-container > div.se-component.se-text.se-l-default> div.se-component-content> div.se-secion.se-section-text.se-l-defalut').text
                        # print('try answer', answer )
                        except: answer =  driver.find_element_by_css_selector('#answer_'+str(n)+' > div._endContents.c-heading-answer__content > div._endContentsText.c-heading-answer__content-user').text
                        ans.append(answer)

                        # add tags from answers too (if available)
                        try: tag.append( driver.find_element_by_xpath('//*[@id="answer_' + str(n) + '"]/div[2]/div[2]/a').text)
                        except: pass
                    except: pass
                    time.sleep(.2)

                # save to dataframe
                # print('answers: ', ans)
                df = df.append({'page': k,'date': date, 'tags': tag ,  'questions': question, 'questions_add': content, 'answers': ans,
                                'N_answer': len(ans) , 'url' : urls , 'category': cat }, ignore_index = True )


                # find weird urls
                if (question == None ) or (len(ans) == 0) :
                    print('NOT WORKING URL', urls)
                    # not_working= not_working.append({'url': urls , 'exit': False} ,ignore_index=True )

                #close tab & reset values
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                date = tag = question = content = ans = urls = cat = None

            #move to next page
            k+=1
            time.sleep(1)
            df.to_csv('['+str(start)+'-'+str(end)+']crawling.csv', index=False)

    except:
        print('EXIT URL', urls)
        print(date, tag, question, content, ans, cat)
        pass
    df.sort_values(by='date', inplace=True)
    df.to_csv('['+str(start)+'-'+str(end)+']crawling.csv', index=False)
    # not_working.to_csv('not_working.csv', index=False)
    return df

date_range = ['01','02','03','04','05','06','07', '08','09','10',
              '11','12','13','14','15','16', '17', '18', '19', '20',
              '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
date = ['15','16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
def month(x):
    if x == '02' :
        for i, j in zip(date[:-3][::2], date[1:-2][::2]) :
            df = crawling_process(start='2021.'+str(x)+'.'+str(i)+'.', end='2021.'+str(x)+'.'+str(j)+'.', query='백신')
    else :
        for i, j in zip(date_range[::2], date_range[1:][::2] ) :
            df = crawling_process(start='2021.'+str(x)+'.'+str(i)+'.', end='2021.'+str(x)+'.'+str(j)+'.', query='백신')
    if x in ['01', '03','05','07','08','10','12'] :
        df = crawling_process(start='2021.'+str(x)+'.'+str(31)+'.', end='2021.'+str(x)+'.'+str(31)+'.', query='백신')


df = crawling_process(start='2021.01.01.', end='2021.01.02.', query='백신')
for k in ['02','03','04','05','06','07' ] : month(k) #'01'


def month_agg(x):
    d = pd.DataFrame( columns=['page', 'date', 'tags', 'questions', 'questions_add', 'answers', 'N_answer', 'url', 'category'])
    if x == '02' :
        for i, j in zip(date_range[:-3][::2], date_range[1:-2][::2]) :
            print('['+'2021.'+str(x)+'.'+str(i)+'.-'+'2021.'+str(x)+'.'+str(j)+'.]'+'crawling.csv')
            df = pd.read_csv('['+'2021.'+str(x)+'.'+str(i)+'.-'+'2021.'+str(x)+'.'+str(j)+'.]'+'crawling.csv')
            d = pd.concat([d, df], axis=0)
            print(df.shape)
    else :
        for i, j in zip(date_range[::2], date_range[1:][::2] ) :
            print('['+'2021.'+str(x)+'.'+str(i)+'.-'+'2021.'+str(x)+'.'+str(j)+'.]'+'crawling.csv')
            df = pd.read_csv( '[' + '2021.' + str(x) + '.' + str(i) + '.-' + '2021.' + str(x) + '.' + str(j) + '.]' + 'crawling.csv')
            d = pd.concat([d, df], axis=0)
            print(df.shape)
    if x in ['01', '03','05','07','08','10','12'] :
        print('['+'2021.'+str(x)+'.'+str(31)+'.-'+'2021.'+str(x)+'.'+str(31)+'.]'+'crawling.csv')
        df = pd.read_csv( '[' + '2021.' + str(x) + '.' + str(31) + '.-' + '2021.' + str(x) + '.' + str(31) + '.]' + 'crawling.csv')
        d = pd.concat([d, df], axis=0)
        print(df.shape)
    # d = d.drop_duplicates(['questions','answers'])
    print(d.shape)
    d.to_csv('[' + '2021.' + str(x) + ']' + 'crawling.csv' )
    return d

# month_agg('03')