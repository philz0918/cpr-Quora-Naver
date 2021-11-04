#Quora Crawling 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from tqdm import tqdm
import pickle
import numpy as np 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


    
def find_main(driver) :  
    time.sleep(20)
    #element = driver.find_elements_by_xpath('//*[@id="mainContent"]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[contains(@class,"spacing_log_answer_content")]')
    element = driver.find_elements_by_xpath('//*[@id="mainContent"]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[contains(@class, "spacing_log_answer_content")]')
    if element :
        return element
    else :
        return False

def find_tag(driver) :
    element= driver.find_elements_by_xpath('//*[@id="mainContent"]/div/div/div/div/a/div/div/span')
    if element :
        return element
    else :
        return False
    

if __name__ == "__main__" :


	with open ('pkl/df_concat3.pkl','rb') as f :
	    df_sorted = pickle.load(f)

		chrome_options = Options()
		chrome_options.add_argument("--incognito")
		chrome_options.add_argument("--headless")

		still_null = []
		for url in tqdm(url_temp) :
		    
		    chk_null = df_sorted[df_sorted["url"] == url]["N_answer"].isnull()
		    
		    if list(chk_null)[0] == False :
		        continue
		    else :
		    
		        try:

		            tags = []
		            ans_list= []
		            try :
		                driver = webdriver.Chrome(executable_path ='/Users/macbookpro/Project/Vaccine/chromedriver', options = chrome_options)
		            except :
		                driver = webdriver.Chrome(executable_path = '/Users/macbookpro/Project/Vaccine/chromedriver_2', options = chrome_options)
		            driver.get(url)

		            #page = driver.page_source

		            time.sleep(3)

		            while True :

		                try :
		                    driver.find_element_by_css_selector('#mainContent > div > div > div.q-box.Placeholder___StyledBox2-sc-14cvkoj-3.fenZeA').click()
		                    time.sleep(20)

		                except :
		                    break

		            while True :

		                try :
		                    driver.find_element_by_xpath('//*[@id="mainContent"]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/span/div/div/div/button').click()
		                    time.sleep(20)

		                except :
		                    break

		            #get number of answer
		            num_ans = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div/div/div/div/div/div')
		            num_= num_ans.text    

		            #get answers
		            target = WebDriverWait(driver,30).until(find_main)
		            #print(target)
		            try :
		                for t in target :
		                    try :
		                        #print(t.text)
		                        ans_list.append(t.text)
		                        i +=1
		                    except :
		                        pass
		            except :
		                pass

		            time.sleep(20)

		            driver.find_element_by_xpath('//*[@id="root"]/div/div/div/div/div/div/div/div/button').click()
		            driver.find_element_by_xpath('//*[@id="root"]/div/div/div/div/div/div/div/span/span/div').click()

		            email= WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.NAME, "email")))
		            email.send_keys('enteryouremail')
		            pword = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.NAME, "password")))
		            pword.send_keys('password')

		            #click login
		            driver.find_element_by_xpath('//*[@id="root"]/div/div/div/div/div/div/div/button/div/div/div').click()

		            try :
		                WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#mainContent > div.q-box.qu-borderBottom > div > div.q-flex.qu-flexWrap--wrap.qu-alignItems--center > div > div > div > div"))).click()

		            except :
		                pass

		            #get tags
		            try :
		                hash_tag = WebDriverWait(driver,3).until(find_tag)
		                time.sleep(20)

		                try :
		                    for h in hash_tag :
		                        try :
		                            #print(h.text)
		                            tags.append(h.text)
		                        except :
		                            pass
		                except :
		                    pass

		            except : 
		                pass

		            #data frame 

		            idx = df_sorted[df_sorted["url"]==url].index.values.astype(int)[0]
		            #answer
		            df_sorted.at[idx, 'answer'] = ans_list
		            #tag
		            df_sorted.at[idx, 'tags'] = tags
		            #number of answer
		            df_sorted.at[idx,'N_answer'] = num_

		            #get mid point
		            #if m_point % 10 == 0 :
		            df_sorted.to_csv("df_concat3.csv", index =  False)
		            with open('pkl/df_concat3.pkl', 'wb') as f :
		                pickle.dump(df_sorted, f, protocol = pickle.HIGHEST_PROTOCOL)
		           # else :
		           #     pass

		            driver.close()
		            time.sleep(3)

		        except :
		            still_null.append(url)
		            pass
		    
		driver.quit()
		    
		        #print('='*130)

		    

