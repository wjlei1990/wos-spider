import re

import requests
import xlrd
from bs4 import BeautifulSoup


class SpiderMain(object):
    def __init__(self,sid,kanming):
        self.hearders={
            'Origin':'https://apps.webofknowledge.com',
            'Referer':'https://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=R1ZsJrXOFAcTqsL6uqh&preferencesSaved=',
            'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
            'Content-Type':'application/x-www-form-urlencoded'
        }
        self.form_data={
            'fieldCount':2,
            'action':'search',
            'product':'WOS',
            'search_mode':'GeneralSearch',
            'SID':sid,
            'max_field_count':25,
            'formUpdated':'true',
            'value(input1)':kanming,
            'value(select1)':'SO',
            'value(hidInput1)':'',
            'value(bool_1_2)':'AND',
            'value(input2)':'2013-2014',
            'value(select2)':'PY',
            'value(hidInput2)':'',
            'limitStatus':'collapsed',
            'ss_lemmatization':'On',
            'ss_spellchecking':'Suggest',
            'SinceLastVisit_UTC':'',
            'period':'Range Selection',
            'range':'ALL',
            'startYear':'1900',
            'endYear':'2016',
            'update_back2search_link_param':'yes',
            'ssStatus':'display:none',
            'ss_showsuggestions':'ON',
            'ss_query_language':'auto',
            'ss_numDefaultGeneralSearchFields':1,
            'rs_sort_by':'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A'
        }
        self.form_data2={
            'product':'WOS',
            'prev_search_mode':'CombineSearches',
            'search_mode':'CombineSearches',
            'SID':sid,
            'action':'remove',
            'goToPageLoc':'SearchHistoryTableBanner',
            'currUrl':'https://apps.webofknowledge.com/WOS_CombineSearches_input.do?SID='+sid+'&product=WOS&search_mode=CombineSearches',
            'x':48,
            'y':9,
            'dSet':1
		}

    def craw(self, root_url):
        try:
            s = requests.Session()
            r = s.post(root_url,data=self.form_data,headers=self.hearders)
            soup = BeautifulSoup(r.text, 'html.parser')
            result_article=soup.find_all('input', value="DocumentType_ARTICLE")
            if result_article==[]:
                article_num=0
            else:
                article_num=int(re.findall(r"\d+",result_article[0].text.replace(',',''))[0])
            result_review=soup.find_all('input', value="DocumentType_REVIEW")
            if result_review==[]:
                review_num=0
            else:
                review_num=int(re.findall(r"\d+",result_review[0].text.replace(',',''))[0])
            a_and_r=article_num+review_num
            report_link=soup.find('a', alt="View Citation Report")
            true_link="https://apps.webofknowledge.com"+report_link['href']
            r2=s.get(true_link)
            soup2= BeautifulSoup(r2.text, 'html.parser')
            refer=soup2.find_all('span',id="CR_HEADER_3")
            refer_num=int(re.findall(r"\d+",refer[0].text)[0])
            flag=0
            error='no error'
        except Exception as e:
            # 出现错误，再次try，以提高结果成功率
            try:
                s = requests.Session()
                r = s.post(root_url,data=self.form_data,headers=self.hearders)
                soup = BeautifulSoup(r.text, 'html.parser')
                result_article=soup.find_all('input', value="DocumentType_ARTICLE")
                if result_article==[]:
                    article_num=0
                else:
                    article_num=int(re.findall(r"\d+",result_article[0].text.replace(',',''))[0])
                result_review=soup.find_all('input', value="DocumentType_REVIEW")
                if result_review==[]:
                    review_num=0
                else:
                    review_num=int(re.findall(r"\d+",result_review[0].text.replace(',',''))[0])
                a_and_r=article_num+review_num
                report_link=soup.find('a', alt="View Citation Report")
                true_link="https://apps.webofknowledge.com"+report_link['href']
                r2=s.get(true_link)
                soup2= BeautifulSoup(r2.text, 'html.parser')
                refer=soup2.find_all('span',id="CR_HEADER_3")
                refer_num=int(re.findall(r"\d+",refer[0].text)[0])
                flag=0
                error='no error'

            except Exception as e:
                print(e)
                a_and_r=0
                refer_num=0
                flag=1
                error=str(e)
        return a_and_r, refer_num,flag,error

    def delete_history(self):
        murl='https://apps.webofknowledge.com/WOS_CombineSearches.do'
        s = requests.Session()
        s.post(murl,data=self.form_data2,headers=self.hearders)


if __name__=="__main__":
    root_url = 'https://apps.webofknowledge.com/WOS_GeneralSearch.do'
    #sid='W1OZtZW2eSwnTmvSLev'

    root='http://www.webofknowledge.com/'
    s=requests.get(root)
    sid=re.findall(r'SID=\w+&',s.url)[0].replace('SID=','').replace('&','')

    data = xlrd.open_workbook('2015排序.xlsx')
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    ctype = 1
    xf = 0

    for i in range(1,nrows):
        if i%100==0:
            # 每一百次更换sid
            s=requests.get(root)
            sid=re.findall(r'SID=\w+&',s.url)[0].replace('SID=','').replace('&','')
        csv=open('res.csv','a')
        fail=open('fail.txt','a')
        kanming=table.cell(i,2).value
        obj_spider = SpiderMain(sid,kanming)
        ar,ref,fl,er=obj_spider.craw(root_url)
        csv.write(str(i+1)+","+kanming+','+str(ar)+','+str(ref)+'\n')
        if fl==0:
            print('cell'+str(i+1)+' '+kanming+' finished')
        else:
            print('cell'+str(i+1)+' '+kanming+' failed'+' '+er)
            fail.write(str(i+1)+' '+kanming+' failed'+' '+er+'\n')
        csv.close()
        fail.close()
        #obj_spider.delete_history()
        # 更换sid后不必删除历史记录
