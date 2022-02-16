# -*- coding:utf-8 -*-
from krwordrank.sentence import make_vocab_score, MaxScoreTokenizer
from numpy.core.numeric import NaN
from numpy.lib.npyio import save
import pandas as pd
import numpy as np
from keys.keyword_lib import *
from krwordrank.word import *
from keys.keysentence_lib import *
import db
from datetime import datetime
import time


today_path=db.today_path()

time_list=[]                                                    # exe time check
error_list=[]                                                   # error check list

def total(df):
    '''
    전체 키워드/핵심문장 추출 
    '''
    anal03_col_name=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","KEYWORD_GUBUN","RLT_VALUE_01","RLT_VALUE_02","RLT_VALUE_03","RLT_VALUE_04","RLT_VALUE_05",
    "RLT_VALUE_06","RLT_VALUE_07","RLT_VALUE_08","RLT_VALUE_09","RLT_VALUE_10"]
    data_anal03=pd.DataFrame(columns=anal03_col_name)

    df_id=df[['PART_SUB_ID','PART_ID']]
    df_id=df_id.drop_duplicates(ignore_index=True)

    id_list=[]
    for index, row in df_id.iterrows():
        id_list.append(row.tolist())
    
    total_time_start=time.time()
    review_count=0
    #stopwords
    stopword=db.TB_stopwords()

    for i in id_list: # id_list=[[sub_id,part_id],[sub_id,part_id]]
        sub_id=i[0]
        part_id=i[1]

        df_per_part_id=df[(df['PART_SUB_ID']==sub_id) & (df['PART_ID']==part_id)]     
        
        df_per_part_id = db.TB_join(df_per_part_id)
        df_per_part_id['REVIEW'] = df_per_part_id['REVIEW'].str.replace(pat=r'[^\w\s]', repl=r' ', regex=True)
 
        print(df_per_part_id)
        
        site=df_per_part_id.iloc[0,0]
        part_group_id=df_per_part_id.iloc[0,1]
        part_sub_id=df_per_part_id.iloc[0,2]
        part_id=df_per_part_id.iloc[0,3]

        review_count+=len(df_per_part_id)
        review_content=df_per_part_id['REVIEW'].tolist()
 
        # 전체 키워드
        # 리뷰 5개 이하면 키워드 분석은 하지 않고, 리뷰를 최신순으로 핵심문장으로 출력
        if 0<len(df_per_part_id)<6:
            list5 = df_per_part_id.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
            list5 = list5['REVIEW'].values.tolist()
            
            list_review=[]
            for index in range(5):
                try:
                    list_review.append(list5[index])
                except:
                    list_review.append('')
            
            total_sentence=total_sent(site, part_group_id,part_sub_id,part_id,list_review)
                
            # analysis result add (anal03에 추가)
            data_anal03=pd.concat([data_anal03,total_sentence],ignore_index=True)
        
        # 리뷰가 6개 이상이면, 키워드/핵심문장 분석
        elif len(df_per_part_id)>5:
            print('전체리뷰 키워드 분석 시작')
            try: # 전체 키워드
                all_keyword,error=keyword_minCount(review_content, stopword)
                if '오류없음' not in error:                           # 오류 발생
                    all_keyword_result_df=key_df_error(site, part_group_id,part_sub_id,part_id)
                    error_list.append(f'{part_sub_id}_{part_id} / site: {site} 전체리뷰 키워드 오류1\t{error}')
                    print(f"{part_sub_id}_{part_id} / site: {site} 전체리뷰 키워드 오류1\t{error}")
                else:
                    All_keywordList=list(all_keyword.keys())
                    All_keywordGradeList=list(all_keyword.values())
                    All_keywordGradeList = (np.round(All_keywordGradeList,2)).tolist() # 소수점 둘째자리까지 반올림

                    # List(빈칸처리)
                    key_list=noValueToBlank(All_keywordList)
                    grade_list=noValueToBlank(All_keywordGradeList)
                    result_list=key_list+grade_list
                    all_keyword_result_df=total_key_df_result(site, part_group_id,part_sub_id,part_id,result_list)

                    print(f"part_id: {part_sub_id}_{part_id} / site_no: {site} 전체리뷰 키워드 완료\n총 리뷰수:{len(df_per_part_id)}")

            except Exception as e:
                error_list.append(f"{part_sub_id}_{part_id} / site: {site} 전체리뷰 키워드 오류2\t{e}")
                print(f"{e}\n{part_sub_id}_{part_id} / site: {site} 전체리뷰 키워드 오류2")
                all_keyword_result_df=key_df_error(site, part_group_id,part_sub_id,part_id)
                all_keyword={}
                pass
        
            #전체핵심문장
            try:
                print("전체리뷰 핵심문장 분석 시작")        
                if not all_keyword: # keyword 가 없을때, 리뷰의 최신순으로 핵심문장 출력
                    list5 = df_per_part_id.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
                    list5 = list5['REVIEW'].values.tolist()
                    
                    list_review=[]
                    for index in range(5):
                        try:
                            list_review.append(list5[index])
                        except:
                            list_review.append('')
                    
                    total_sentence=total_sent(site, part_group_id,part_sub_id,part_id,list_review)

                else:
                    keysentence_list_all, error=keys_list(all_keyword,stopword,review_content)
                    error_list.append(f"code: {part_sub_id}_{part_id} / site: {site} 전체 핵심문장 오류3\t{error}")

                    if len(keysentence_list_all)==0:                        # 핵심문장이 출력되지 않으면 리뷰 최신순으로 출력
                        list5 = df_per_part_id.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
                        list5 = list5['REVIEW'].values.tolist()
                        
                        list_review=[]
                        for index in range(5):
                            try:
                                list_review.append(list5[index])
                            except:
                                list_review.append('')
                        
                        total_sentence=total_sent(site, part_group_id,part_sub_id,part_id,list_review)
                    else:
                        keys_list_fin=noValueToBlank(keysentence_list_all)
                        all_keysentece_result_df=total_sent(site, part_group_id,part_sub_id,part_id, keys_list_fin)

                    print(f"id : {part_sub_id}_{part_id} / site_no: {site} 전체리뷰 핵심문장 완료\n총 리뷰수: {len(df_per_part_id)}")
            
            except Exception as e:
                error=e
                error_list.append(f"{part_sub_id}_{part_id} / site: {site} 전체리뷰 핵심문장 오류4\t{error}")
                print("{}_{} 전체리뷰 핵심문장 오류4".format(sub_id, part_id))
                all_keysentece_result_df=keys_df_error(site, part_group_id,part_sub_id,part_id)
                pass
        
            data_anal03 = pd.concat([data_anal03,all_keyword_result_df,all_keysentece_result_df],ignore_index=True)
            del all_keyword_result_df
            del all_keysentece_result_df

    # Time check
    now=datetime.now().strftime('%y%m%d_%H%M')
    total_time_end=time.time()
    total_time=total_time_end-total_time_start
    # 분석날짜, 분류(total/emo), 분석제품수, 총 리뷰수, 분석시간
    time_list=[now,"total_key",len(id_list),review_count,total_time]
    
    # save
    db.time_txt(time_list,f'{today_path}/time_check')
    db.save_txt(error_list,f'{today_path}/errorList')
    data_anal03.to_csv(f'{today_path}/{now}_anal03_result.csv', index=None)
        
    return data_anal03

def emo(df):
    '''
    긍정/부정리뷰의 키워드/핵심문장 추출
    '''
    col_name2=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","KEYWORD_GUBUN","KEYWORD_POSITIVE","RLT_VALUE_01","RLT_VALUE_02","RLT_VALUE_03","RLT_VALUE_04","RLT_VALUE_05",
    "RLT_VALUE_06","RLT_VALUE_07","RLT_VALUE_08","RLT_VALUE_09","RLT_VALUE_10"]
    data_anal02=pd.DataFrame(columns=col_name2)

    df_id=df[['PART_SUB_ID','PART_ID']]
    df_id=df_id.drop_duplicates(ignore_index=True)

    id_list=[]
    for index, row in df_id.iterrows():
        id_list.append(row.tolist())
    
    emo_time_start=time.time()
    review_count=0
    # stopwords
    stopword=db.TB_stopwords()

    for i in id_list: # id_list=[[sub_id,part_id],[sub_id,part_id]]
        sub_id=i[0]
        part_id=i[1]
        
        # review+anal00 join data
        # df_columns=site_gubun, part_group_id, part_sub_id, part_id, review_doc_no, review, rlt_value_03
        # df=db.TB_join(sub_id,part_id)

        df_per_part_id=df[(df['PART_SUB_ID']==sub_id) & (df['PART_ID']==part_id)]
        df_per_part_id = db.TB_join(df_per_part_id)
        df_per_part_id['REVIEW'] = df_per_part_id['REVIEW'].str.replace(pat=r'[^\w\s]', repl=r' ', regex=True)

        site=df_per_part_id.iloc[0,0]
        part_group_id=df_per_part_id.iloc[0,1]
        part_sub_id=df_per_part_id.iloc[0,2]
        part_id=df_per_part_id.iloc[0,3]

        # 긍정 키워드
        pos_df=df_per_part_id[df_per_part_id['RLT_VALUE_03']>3]
        review_count+=len(pos_df)


        if 0<len(pos_df)<6:
            # 긍정 리뷰 리스트
            list5 = pos_df.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
            list5 = list5['REVIEW'].values.tolist()

            list_pos_review=[]
            for index in range(5):
                try:
                    list_pos_review.append(list5[index])
                except:
                    list_pos_review.append('')

            pos_sentence=emo_pos_sent(site,part_group_id,part_sub_id,part_id,list_pos_review)
            data_anal02=pd.concat([data_anal02,pos_sentence],ignore_index=True)
        
        elif len(pos_df)>5:
            print('긍정리뷰 키워드/핵심문장 분석 시작')
            pos_review_list=pos_df['REVIEW'].tolist()
            try:
                pos_keyword,error=keyword_minCount(pos_review_list, stopword)
                if '오류없음' not in error:                           # 오류 발생
                    pos_keyword_result_df=pos_key_error(site, part_group_id,part_sub_id,part_id)
                    error_list.append(f'{part_sub_id}_{part_id} / site: {site} 긍정키워드 오류1\t{error}')
                    print(f"{part_sub_id}_{part_id} / site: {site} 긍정키워드 오류1\t{error}")
                else:
                    pos_keywordList=list(pos_keyword.keys())
                    pos_keywordGradeList=list(pos_keyword.values())
                    pos_keywordGradeList = (np.round(pos_keywordGradeList,2)).tolist() # 소수점 둘째자리까지 반올림

                    # List(빈칸처리)
                    pos_key_list=noValueToBlank(pos_keywordList)
                    pos_grade_list=noValueToBlank(pos_keywordGradeList)
                    pos_result_list=pos_key_list+pos_grade_list
                    pos_keyword_result_df=pos_key_result(site, part_group_id,part_sub_id,part_id,pos_result_list)

                    print(f"id: {part_sub_id}_{part_id} / site_no: {site} 긍정키워드 완료\t긍정 리뷰수:{len(pos_df)}")

            except Exception as e:
                error_list.append(f"{part_sub_id}_{part_id} / site: {site} 긍정키워드 오류2\t{e}")
                print(f"{e}\n{part_sub_id}_{part_id} / site: {site} 긍정키워드 오류2")
                pos_keyword_result_df=pos_key_error(site, part_group_id,part_sub_id,part_id)
                pos_keyword={}
                pass

            #긍정핵심문장
            try:
                print("긍정리뷰 핵심문장 분석 시작")
                if not pos_keyword: # keyword 가 없을때, 리뷰의 최신순으로 핵심문장 출력
                    list5 = pos_df.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
                    list5 = list5['REVIEW'].values.tolist()
                    
                    list_pos_review=[]
                    for index in range(5):
                        try:
                            list_pos_review.append(list5[index])
                        except:
                            list_pos_review.append('')
                    
                    pos_keys_result_df=emo_pos_sent(site, part_group_id,part_sub_id,part_id,list_pos_review)

                else:
                    keysentence_list_pos, error=keys_list(pos_keyword,stopword,pos_review_list)

                    if '오류없음' not in error:
                        error_list.append(f"{part_sub_id}_{part_id} / site: {site} 긍정핵심문장 에러3\t{error}")

                    if len(keysentence_list_pos)==0:    # 최신순으로 출력
                        list5 = pos_df.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
                        list5 = list5['REVIEW'].values.tolist()
                                
                        list_pos_review=[]
                        for index in range(5):
                            try:
                                list_pos_review.append(list5[index])
                            except:
                                list_pos_review.append('')

                        pos_keys_result_df=emo_pos_sent(site,part_group_id,part_sub_id,part_id,list_pos_review)       
                    else:
                        pos_keys_fin=noValueToBlank(keysentence_list_pos)
                        pos_keys_result_df=emo_pos_sent(site,part_group_id,part_sub_id,part_id,pos_keys_fin)

            except Exception as e:
                error_list.append(f"{part_sub_id}_{part_id} / site: {site} 긍정 핵심문장 오류4\t{e}")
                print(f"{part_sub_id}_{part_id} 긍정핵심문장 오류4\t{e}")
                pos_keys_result_df=pos_sent_error(site,part_group_id,part_sub_id,part_id)
                pass 

            data_anal02=pd.concat([data_anal02,pos_keyword_result_df,pos_keys_result_df],ignore_index=True)
            del pos_keyword_result_df
            del pos_keys_result_df

            print(f'{part_sub_id}_{part_id}_긍정리뷰 완료')     
        else:
            print(f'{part_sub_id}_{part_id}_긍정리뷰 없음')
            error_list.append(f'{part_sub_id}_{part_id} site:{site} 긍정리뷰 없음')

        

        neg_df=df_per_part_id[df_per_part_id['RLT_VALUE_03']<3]
        review_count+=len(neg_df)

        
        if 0<len(neg_df)<6:
            # 부정 리뷰 리스트
            list5 = neg_df.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
            list5 = list5['REVIEW'].values.tolist()

            list_neg_review=[]
            for index in range(5):
                try:
                    list_neg_review.append(list5[index])
                except:
                    list_neg_review.append('')

            neg_sentence=emo_neg_sent(site,part_group_id,part_sub_id,part_id,list_neg_review)
            data_anal02=pd.concat([data_anal02,neg_sentence],ignore_index=True)
        
        elif len(neg_df)>5:
            print("부정키워드 분석 시작")
            neg_review_list=neg_df['REVIEW'].tolist()
            try:
                neg_keyword,error=keyword_minCount(neg_review_list, stopword)
                if '오류없음' not in error:                           # 오류 발생
                    neg_keyword_result_df=neg_key_error(site, part_group_id,part_sub_id,part_id)
                    error_list.append(f'{part_sub_id}_{part_id} / site: {site} 부정키워드 오류1\t{error}')
                else:
                    neg_keywordList=list(neg_keyword.keys())
                    neg_keywordGradeList=list(neg_keyword.values())
                    neg_keywordGradeList = (np.round(neg_keywordGradeList,2)).tolist() # 소수점 둘째자리까지 반올림

                    # List(빈칸처리)
                    neg_key_list=noValueToBlank(neg_keywordList)
                    neg_grade_list=noValueToBlank(neg_keywordGradeList)
                    neg_result_list=neg_key_list+neg_grade_list
                    neg_keyword_result_df=neg_key_result(site, part_group_id,part_sub_id,part_id,neg_result_list)

                    print(f"id: {part_sub_id}_{part_id} / site_no: {site} 부정키워드 완료\t부정 리뷰수:{len(neg_df)}")

            except Exception as e:
                error_list.append(f"{part_sub_id}_{part_id} / site: {site} 부정키워드 오류2\t{e}")
                print(f"{e}\n{part_sub_id}_{part_id} / site: {site} 부정키워드 오류2")
                neg_keyword_result_df=neg_key_error(site, part_group_id,part_sub_id,part_id)
                neg_keyword={}
                pass

            #부정핵심문장
            try:
                print("부정리뷰 핵심문장 분석 시작")
                if not neg_keyword: # keyword 가 없을때, 리뷰의 최신순으로 핵심문장 출력
                    list5 = neg_df.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
                    list5 = list5['REVIEW'].values.tolist()
                    
                    list_neg_review=[]
                    for index in range(5):
                        try:
                            list_neg_review.append(list5[index])
                        except:
                            list_neg_review.append('')
                    
                    neg_keys_result_df=emo_neg_sent(site, part_group_id,part_sub_id,part_id,list_neg_review)

                else:
                    keysentence_list_neg, error=keys_list(neg_keyword,stopword,neg_review_list)
                    error_list.append(f"{part_sub_id}_{part_id} / site: {site} 부정핵심문장 오류3\t{error}")

                    if len(keysentence_list_neg)==0:    # 최신순으로 출력
                        list5 = neg_df.sort_values(by=['REVIEW_DOC_NO'],axis=0, ascending=False)
                        list5 = list5['REVIEW'].values.tolist()
                                
                        list_neg_review=[]
                        for index in range(5):
                            try:
                                list_neg_review.append(list5[index])
                            except:
                                list_neg_review.append('')

                        neg_keys_result_df=emo_neg_sent(site,part_group_id,part_sub_id,part_id,list_neg_review)
                            
                    else:
                        neg_keys_fin=noValueToBlank(keysentence_list_neg)
                        neg_keys_result_df=emo_neg_sent(site,part_group_id,part_sub_id,part_id,neg_keys_fin)

            except Exception as e:
                error_list.append(f"{part_sub_id}_{part_id} / site: {site} 부정핵심문장 오류4\t{e}")
                print(f"{part_sub_id}_{part_id} 부정핵심문장 오류4\t{e}")
                neg_keys_result_df=neg_sent_error(site,part_group_id,part_sub_id,part_id)
                pass 

            data_anal02=pd.concat([data_anal02,neg_keyword_result_df,neg_keys_result_df],ignore_index=True)
            del neg_keyword_result_df
            del neg_keys_result_df

            print(f'{part_sub_id}_{part_id}_부정리뷰 완료')   
        else:
            print(f'{part_sub_id}_{part_id}_부정리뷰 없음')
            error_list.append(f'{part_sub_id}_{part_id} site:{site} 부정리뷰 없음')

    now=datetime.now().strftime('%y%m%d_%H%M')
    emo_total_end=time.time()
    emo_total_time=emo_total_end-emo_time_start
    # 분석날짜, 분류(total/emo), 분석제품수, 총 리뷰수, 분석시간
    time_list=[now, "emo",len(id_list),review_count,emo_total_time]

    # save
    db.time_txt(time_list,f'{today_path}/time_check')
    db.save_txt(error_list,f'{today_path}/errorList')
    data_anal02.to_csv(f'{today_path}/{now}_anal02_result.csv', index=None)
        
    return data_anal02

 