#-*- coding: utf-8 -*-
from numpy.lib.function_base import select
import emp_class
import db
from keys.key import *
import argparse, os, time, traceback
from datetime import datetime
import glowpic

today=datetime.now().strftime('%Y%m%d')

# def time_txt(content_list):
#     file_name='./data/time.txt'
#     if not os.path.exists(file_name):
#         with open(file_name,'a',encoding='utf8') as f:
#             f.write('part_id\t리뷰수\t분석시간(초)\n')
            
#     with open(file_name,'a',encoding='utf8') as f:
#         for line in content_list:
#             f.write(f'{line}\t')
#         f.write("\n")

def analysis():
    # 1. load data
    part_id_list=db.TB_CRAW_top5_pid() # 카테고리별 top 5에 대한 part_id
    df=db.TB_review_part_id(part_id_list)

    if len(df)!=0:
        # 2. anal00(property+empathy result) insert
        '''gpu 사용'''
        anal00=emp_class.cos_model_pt(df)
        '''api_url 사용'''
        # anal00=emp_class.cos_model_api(df)

        # anal00 insert
        db.TB_anal00_insert(anal00)

    # 3. anal02/anal03(keyword/keysentence analysis) insert
    # anal00의 part_id 리스트

    part_id_df=db.anal00_part_id()
    key_df=db.TB_join(part_id_df)
    anal03=total(key_df)
    anal02=emo(key_df)

    db.TB_anal03_insert(anal03)
    db.TB_anal02_insert(anal02)

    # 4. anal01/04 review count insert
    db.TB_anal01_count()
    db.TB_anal04_count()

    finish_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{finish_time} 분석 완료")

def data_split():
    try: 
        start_time = time.time()
        # split할 폴더생성
        if not os.path.isdir("C:/glowpic_sentences"):
                os.makedirs("C:/glowpic_sentences")

        # split하기 전 데이터 3000개씩 나눔
        glowpic.split_before()
        # 3000개씩 나눈 데이터를 이용하여 split 및 레이블링기준포함여부
        glowpic.split_after()

        end_time = (time.time() - start_time)/60
        print('문장 split 및 레이블링기준포함여부 완료 --- {0:0.2f} 분 소요'.format(end_time))
    except Exception as e:
        print(e)

if __name__=='__main__':
    error_list=[]
    time_list=[]
    today_path=db.today_path()      # 백업을 위한 폴더 생성 

    try:
        start_time=time.time()
        data_split()
        analysis()
        end_time=time.time()
        all_time=end_time-start_time
        
        # 분석날짜, 분류(total/emo), 분석제품수, 총 리뷰수, 분석시간
        time_list=[datetime.now().strftime('%y%m%d'),"all_analy","-","-",all_time]
        db.time_txt(time_list,f'{today_path}/time_check')
        db.success_sendEmail()

    except Exception:
        err=traceback.format_exc()
        print(f'1번째 error\n{err}')
        now=datetime.now().strftime('%Y%m%d %H:%M')
        e=f'{now}\n{err}'
        error_list.append(e)
        db.save_txt(error_list,f'{today_path}/errorList')
        db.fail_sendEmail(e)
        #analysis()