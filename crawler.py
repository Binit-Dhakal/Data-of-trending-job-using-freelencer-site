from bs4 import BeautifulSoup
import csv 
import re 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import os

selectors_dict={
    'email':'.LoginForm > fl-input:nth-child(4) > fl-bit:nth-child(1) > fl-bit:nth-child(1) > input:nth-child(1)',
    'password':'/html/body/app-root/app-logged-out-shell/app-login-page/fl-container/fl-bit/app-login/app-credentials-form/form/fl-input[2]/fl-bit/fl-bit/input',
    'login_button':'/html/body/app-root/app-logged-out-shell/app-login-page/fl-container/fl-bit/app-login/app-credentials-form/form/app-login-signup-button/fl-button/button',
    'browse_project':'/html/body/app-root/app-logged-in-shell/div/div[2]/ng-component/app-dashboard-home/fl-page-layout/main/fl-container/fl-grid/fl-col[1]/fl-page-layout-primary/fl-bit/app-dashboard-home-my-projects/fl-card/fl-bit/fl-bit[2]/fl-bit/app-dashboard-home-my-projects-empty-state/fl-button/a',
    'clear_skill':'/html/body/div[2]/main/section/fl-search/div/div[1]/form/ol[2]/fl-projects-filter/li/ul/li[2]/div[2]/button',
    'page_loaded_check':'/html/body/div[2]/main/section/fl-search/div/div[2]/div/ul/li[1]/a/div'
}

driver=webdriver.Firefox()
driver.get('https://www.freelancer.com/dashboard')

def IsLoaded(selector,content,time=20):
    if selector=="css":
        selector=By.CSS_SELECTOR
    elif selector=="xpath":
        selector=By.XPATH

    try:
        web=WebDriverWait(driver,time).until(EC.presence_of_element_located((selector,content)))  
    except TimeoutException:
        web=None
        print("Loading took too much time")
    return web

#EMAIL INPUT
email=IsLoaded('css',selectors_dict['email'])
email.send_keys(os.getenv('EMAIL'))

#PASSWORD INPUT
password=driver.find_element_by_xpath(selectors_dict['password'])
password.send_keys(os.getenv('PASSWORD'))

#LOGIN
driver.find_element_by_xpath(selectors_dict['login_button']).click()

#Browse projects
IsLoaded('xpath',selectors_dict['browse_project'],20).click()

#Clear skills
IsLoaded('xpath',selectors_dict['clear_skill'],20).click()


##Now the work of beautiful soup###
jobs_lists=[]


def scrape(jobs_lists):
    html=driver.page_source
    soup=BeautifulSoup(html,"html.parser")

    jobs_total=soup.findAll('div',attrs={'class':'search-result-item'})

    for job in jobs_total:
        row={}
        row['job_title']=re.sub(r"^\s+|\s+$","",job.h2.text.replace('\n',''),re.UNICODE)
        row['job_description']=re.sub(r"^\s+|\s+$","",job.find('p',attrs={'class':'info-card-description'}).text.replace('\n',''),flags=re.UNICODE) 
        row['price']=re.sub(r"\s{2,}","",job.select('div.info-card-price>span')[0].text.replace('\n',''),re.UNICODE)
        row['skills']=[i.text for i in job.select('div.info-card-skills>span')]
        jobs_lists.append(row)
    return jobs_lists

#checking if it is loaded
IsLoaded('xpath',selectors_dict['page_loaded_check'],20)
jobs_lists=scrape(jobs_lists)

#NEXT BTN CLICK 
for i in range(10000):     
    if i<5:
        x_path='/html/body/div[2]/main/section/fl-search/div/div[2]/div/div[2]/ul/li[9]/a'
    else:
        x_path='/html/body/div[2]/main/section/fl-search/div/div[2]/div/div[2]/ul/li[10]/a'
        
    pages=driver.find_element_by_xpath(x_path).click()
    IsLoaded('xpath',selectors_dict['page_loaded_check'],30)
    jobs_lists=scrape(jobs_lists)

with open('jobs.csv','w',newline='') as f:
    w=csv.DictWriter(f,['job_title','job_description','price','skills'])
    w.writeheader()
    for jobs in jobs_lists:
        w.writerow(jobs)
    