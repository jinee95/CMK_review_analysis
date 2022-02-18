#-*- coding: utf-8 -*-
from typing_extensions import final
from warnings import catch_warnings
import pymssql
import pandas as pd
import os, smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

server = 'ASC-AI.iptime.org'
database = 'cosmeca'
username = 'cosmeca'
password = 'asc1234pw!'
today=datetime.now().strftime('%Y%m%d')

# DB 연결
def conn_utf8():
    try:
      conn = pymssql.connect(server, username, password, database, charset="utf8")
    except Exception as e:
        print("Error: ", e)
    return conn

def conn_cp949():
    try:
        conn = pymssql.connect(server, username, password, database, charset="cp949")
    except Exception as e:
        print("Error: ", e)
    return conn

# TB_REVIEW select per date (cp949)
def TB_REIVEW_qa(from_date, to_date):
    print('db_data_loading')
    try:
        conn=conn_cp949()
        cursor = conn.cursor()
        sql="exec dbo.P_MNG_CRW004 @section = 'QA', @from_date=%s, @to_date=%s,@site_gubun='N'"
        cursor.execute(sql,(from_date, to_date))
        row=cursor.fetchall()
        col_name=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","REVIEW_DOC_NO","ISRT_DATE","REVIEW_USER","REVIEW_DTTM","REVIEW_GRADE","REVIEW_AGE","REVIEW_SEX","REVIEW_SKIN_TYPE","REVIEW","REMARK","ISRT_USER","UPDT_USER","ISRT_DTTM","UPDT_DTTM"]
        ori_df=pd.DataFrame(row, columns=col_name)
        df=ori_df[['SITE_GUBUN','PART_GROUP_ID','PART_SUB_ID','PART_ID','REVIEW_DOC_NO','REVIEW']]
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
    return df

# TB_REVIEW select per part_id(cp949)
def TB_review_part_id(part_id_list):
    print('db_data_loading')
    try:
        conn=conn_cp949()
        df_concat=pd.DataFrame()
        for part_id in part_id_list:
            cursor=conn.cursor()
            sql="exec dbo.P_MNG_CRW004 @section = 'QC', @part_id=%s, @site_gubun='N'"
            cursor.execute(sql,(part_id))
            row=cursor.fetchall()
            col_name=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","REVIEW_DOC_NO","ISRT_DATE","REVIEW_USER","REVIEW_DTTM","REVIEW_GRADE","REVIEW_AGE","REVIEW_SEX","REVIEW_SKIN_TYPE","REVIEW","REMARK","ISRT_USER","UPDT_USER","ISRT_DTTM","UPDT_DTTM"]
            ori_df=pd.DataFrame(row, columns=col_name)
            df_concat=pd.concat([df_concat,ori_df],ignore_index=True)
        df=df_concat[['SITE_GUBUN','PART_GROUP_ID','PART_SUB_ID','PART_ID','REVIEW_DOC_NO','REVIEW']]
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
    return df

# 매일 카테고리별 1~5위까지의 part_sub_id/part_id 리스트
def TB_CRAW_top5_pid():
    print('top5_part_id_loading')
    try:
        conn=pymssql.connect(server, username, password, database, charset="cp949")
        cursor=conn.cursor()
        sql="select PART_GROUP_ID, PART_SUB_ID, CATEGORY_IDS,CLASS_NAME from dbo.TB_PART_GROUP (nolock) where SITE_GUBUN='N'"
        cursor.execute(sql)
        row=cursor.fetchall()
        col_name=['PART_GROUP_ID', 'PART_SUB_ID', 'CATEGORY_IDS','CLASS_NAME']
        df_ori=pd.DataFrame(row, columns=col_name)
        df=df_ori.copy()
    except Exception as e:
        print("error: ",e)
    finally:
        conn.close()
    
    matching_cate=df[['PART_SUB_ID']]
    cate_list=df['CATEGORY_IDS'].tolist()

    cate_count=[]
    for cate in cate_list:
        print(cate)
        count=cate.count(',')+1
        cate_count.append(count)
    matching_cate['cate_num']=cate_count
    matching_cate['num']=''
    num=0
    
    for index in range(len(matching_cate)):
        count=matching_cate.iloc[index,1]
        if count==0:
            continue
        elif count==1:
            num=5
        elif count==2:
            num=3
        elif count==3:
            num=2
        elif count>=4:
            num=1
        matching_cate.iloc[index,2]=num
    match_cate=matching_cate[['num','PART_SUB_ID']]
    match_cate['DATE']=today
    #match_cate_dict=dict([(i,a) for i, a in zip(matching_cate['PART_SUB_ID'],matching_cate['num'])])

    part_col=['PART_SUB_ID', 'PART_ID']
    top5_concat=pd.DataFrame(columns=part_col)
    try:
        conn=pymssql.connect(server, username, password, database, charset="cp949")
        cursor=conn.cursor()
        
        for i, df_row  in match_cate.iterrows:
            sql="select distinct part_sub_id, part_id from TB_CRAW_HIST A where PART_ID IN (select PART_ID from TB_CRAW_HIST where site_gubun='N' and CRAW_DATA_ID='05' and RSLT_DATA_01 <= %s and PART_SUB_ID=%s and isrt_date=%s)"
            cursor.execute(sql,(tuple(df_row)))
            row=cursor.fetchall()
            top5=pd.DataFrame(row, columns=part_col)
            top5_concat=pd.concat([top5_concat,top5])
        part_id_list=top5_concat['PART_ID'].values.tolist()
    except Exception as e:
        print("error: ",e)
    finally:
        conn.close()
    return part_id_list


# TB_REVIEW add review select per top5 part_sub_id, part_id(cp949)
def TB_review_part_id(part_id_list):
    print('db_data_loading')
    try:
        conn=conn_utf8()
        df_concat=pd.DataFrame()
        for part_id in part_id_list:
            cursor=conn.cursor()
            sql="select * from TB_REVIEW C where C.REVIEW_DOC_NO NOT IN (select A.REVIEW_DOC_NO from TB_REVIEW A join TB_REVIEW_ANAL_00 B on A.PART_ID=B.PART_ID and A.REVIEW_DOC_NO=B.REVIEW_DOC_NO) and part_id=%s"
            #sql="exec dbo.P_MNG_CRW004 @section = 'QC', @part_id=%s, @site_gubun='N'"
            cursor.execute(sql,(part_id))
            row=cursor.fetchall()
            col_name=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","REVIEW_DOC_NO","ISRT_DATE","REVIEW_USER","REVIEW_DTTM","REVIEW_GRADE","REVIEW_AGE","REVIEW_SEX","REVIEW_SKIN_TYPE","REVIEW","REMARK","ISRT_USER","UPDT_USER","ISRT_DTTM","UPDT_DTTM"]
            ori_df=pd.DataFrame(row, columns=col_name)
            df_concat=pd.concat([df_concat,ori_df],ignore_index=True)
        df=df_concat[['SITE_GUBUN','PART_GROUP_ID','PART_SUB_ID','PART_ID','REVIEW_DOC_NO','REVIEW']]
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
    return df

# 딕셔너리(part_sub_id : model_id) 반환 (cp949)
def TB_model_id():
    try:
        conn=conn_cp949()
        cursor=conn.cursor()
        sql='select PART_SUB_ID, MODEL_ID from TB_PART_GROUP'
        cursor.execute(sql)
        row=cursor.fetchall()
        col_name=['part_sub_id','model_id']
        df=pd.DataFrame(row, columns=col_name)
        df_dict=dict(df.values.tolist())
    except Exception as e:
        print("Error : ",e)
    finally:
        conn.close()
    return df_dict


# stopwords list 반환(utf8)
def TB_stopwords():
    try:
        conn=conn_utf8()
        cursor=conn.cursor()
        sql='select * from dbo.TB_UNUSE_KEYWORD'
        cursor.execute(sql)
        row=[item[0] for item in cursor.fetchall()]
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
    return row

# property_code - name dict 반환(cp949)
def TB_property_id():
    try:
        conn=conn_cp949()
        cursor=conn.cursor()
        sql="select CD_NM, SUB_CD from dbo.TB_CODE where GROUP_CD='PROPERTY_ID'"
        cursor.execute(sql)
        row=cursor.fetchall()
        col_name=['cd_nm','sub_cd']
        df=pd.DataFrame(row,columns=col_name)
        df_dict=dict(df.values.tolist())
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
    return df_dict

<<<<<<< Updated upstream

def anal00() :
=======
# anal00의 part_id 리스트
def anal00_part_id():
    col=['PART_ID']
    #col=['PART_SUB_ID', 'PART_ID']
    matching_id=pd.DataFrame(columns=col)
>>>>>>> Stashed changes
    try:
        conn = conn_cp949()
        cursor=conn.cursor()
        sql = "select distinct PART_ID,REVIEW_DOC_NO, RLT_VALUE_03 from TB_REVIEW_ANAL_00 (nolock)"
        cursor.execute(sql)
        row=cursor.fetchall()
<<<<<<< Updated upstream
        col_name=['PART_ID','REVIEW_DOC_NO','RLT_VALUE_03']
        anal00 = pd.DataFrame(row,columns=col_name)
=======
        col_name=['part_id']
        df=pd.DataFrame(row,columns=col_name)

        part_list = df['part_id'].values.tolist()
        for part_id in part_list:
            cursor=conn.cursor()
            sql = "select distinct PART_SUB_ID from TB_REVIEW WHERE SITE_GUBUN='N' AND PART_ID = %s"
            cursor.execute(sql,(part_id))
            row=cursor.fetchall()
            col=['PART_SUB_ID']
            sub_id_df = pd.DataFrame(row, columns=col)
            sub_id_df['PART_ID']=part_id
            matching_id=pd.concat([matching_id,sub_id_df],ignore_index=True)    
>>>>>>> Stashed changes
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
    return anal00

# anal00의 part_id 리스트
# def anal00_part_id():
#     col=['PART_SUB_ID', 'PART_ID']
#     matching_id=pd.DataFrame(columns=col)a
#     try:
#         conn=conn_cp949()
#         cursor=conn.cursor()
#         sql="select distinct PART_ID from TB_REVIEW_ANAL_00 (nolock)"
#         cursor.execute(sql)
#         row=cursor.fetchall()
#         col_name=['part_id']
#         df=pd.DataFrame(row,columns=col_name)

#         part_list = df['part_id'].values.tolist()
#         for part_id in part_list:
#             cursor=conn.cursor()
#             sql = "select distinct PART_SUB_ID from TB_REVIEW WHERE SITE_GUBUN='N' AND PART_ID = %s"    
#             cursor.execute(sql,(part_id))
#             row=cursor.fetchall()
#             col=['PART_SUB_ID']
#             sub_id_df = pd.DataFrame(row, columns=col)
#             sub_id_df['PART_ID']=part_id
#             matching_id=pd.concat([matching_id,sub_id_df],ignore_index=True)    
#     except Exception as e:
#         print("Error: ",e)
#     finally:
#         conn.close()
#     return matching_id
 
#### 키워드/센텐스 결과를 위한 리뷰 select
def TB_join(df):
    print('db_data_loading for keyword/sentence')
    try:
        anal00_part_id = df[['PART_ID']]
        part_id = anal00_part_id.drop_duplicates(ignore_index=True)
        review_col_name=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","REVIEW_DOC_NO","REVIEW"]
        df_review_concat=pd.DataFrame(columns=review_col_name)
   
        conn=conn_cp949()
        cursor = conn.cursor()

        for idx,row in part_id.iterrows():
            part_id_list = part_id.iloc[idx,0]
            sql1="select SITE_GUBUN, PART_GROUP_ID, PART_SUB_ID, PART_ID, REVIEW_DOC_NO, REVIEW from TB_REVIEW (nolock) where PART_ID=%s"
            cursor.execute(sql1, part_id_list)
            tb_review=cursor.fetchall()
            df_review=pd.DataFrame(tb_review, columns=review_col_name)
            df_review_concat=pd.concat([df_review_concat,df_review])
            print(df_review_concat)
            # part_id=df.iloc[i,1]
            # sql2="select REVIEW_DOC_NO, PART_ID, RLT_VALUE_03 from TB_REVIEW_ANAL_00 (nolock) where PART_ID=%s"
            # cursor.execute(sql2, (part_id))
            # row=cursor.fetchall()
            # df_anal00=pd.DataFrame(row, columns=anal00_col_name)
            # anal00_concat=pd.concat([anal00_concat,df_anal00])
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
<<<<<<< Updated upstream

    result=pd.merge(df_review_concat,df,how='outer',on=['PART_ID','REVIEW_DOC_NO'])
    # df_columns=site_gubun, part_group_id, part_sub_id, part_id, review_doc_no, review, rlt_value_03
    return result 
=======
    result=pd.merge(df_review_concat,anal00_concat,on=['REVIEW_DOC_NO','PART_ID'])

    # df_columns=site_gubun, part_group_id, part_sub_id, part_id, review_doc_no, review, rlt_value_03
    return result

#### 키워드/센텐스 결과를 위한 리뷰 select
def TB_join():
    print('db_data_loading for keyword/sentence')
    try:
        review_col_name=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","REVIEW_DOC_NO","REVIEW"]
        df_review_concat=pd.DataFrame(columns=review_col_name)
        anal00_col_name=["REVIEW_DOC_NO","PART_ID","RLT_VALUE_03"]
        anal00_concat=pd.DataFrame(columns=anal00_col_name)
        conn=conn_cp949()
        cursor = conn.cursor()
        sql1="select SITE_GUBUN, PART_GROUP_ID, PART_SUB_ID, PART_ID, REVIEW_DOC_NO, REVIEW from TB_REVIEW (nolock) where PART_SUB_ID=%s and PART_ID=%s"
        cursor.execute(sql1, tuple(part))
        tb_review=cursor.fetchall()
        df_review=pd.DataFrame(tb_review, columns=review_col_name)
        df_review_concat=pd.concat([df_review_concat,df_review])
            
            sql2="select REVIEW_DOC_NO, PART_ID, RLT_VALUE_03 from TB_REVIEW_ANAL_00 (nolock) where PART_ID=%s"
            cursor.execute(sql2, (part_id))
            row=cursor.fetchall()
            df_anal00=pd.DataFrame(row, columns=anal00_col_name)
            anal00_concat=pd.concat([anal00_concat,df_anal00])
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()
    result=pd.merge(df_review_concat,anal00_concat,on=['REVIEW_DOC_NO','PART_ID'])

    # df_columns=site_gubun, part_group_id, part_sub_id, part_id, review_doc_no, review, rlt_value_03
    return result
>>>>>>> Stashed changes


'''DB insert'''
def TB_anal00_insert(df):
    try:
        conn=conn_utf8()
        for i, row in df.iterrows():
            cursor=conn.cursor()
            sql="exec dbo.P_MNG_ANA000 @section='SA', @review_doc_no=%s, @part_id=%s, @rlt_value_01=%s, @rlt_value_02=%s,@rlt_value_03=%s"
            cursor.execute(sql, tuple(row))
            conn.commit()
        print("anal00_insert완료")
    except Exception as e:
        print("Error: ", e)
    finally:
        conn.close()

def TB_anal02_insert(df):
    try:
        conn=conn_utf8()
        for i, row in df.iterrows():
            cursor=conn.cursor()

            if row[4]=='0': #키워드
                sql="exec dbo.P_MNG_ANA002 @section='SA', @site_gubun=%s, @part_group_id=%s,@part_sub_id=%s, @part_id=%s, @keyword_gubun=%s, @keyword_positive=%s,@rlt_value_01=%s, @rlt_value_02=%s, @rlt_value_03=%s, @rlt_value_04=%s, @rlt_value_05=%s, @rlt_value_06=%s, @rlt_value_07=%s, @rlt_value_08=%s, @rlt_value_09=%s, @rlt_value_10=%s"
                cursor.execute(sql,tuple(row))
                print("anal02_recode inserted")
                conn.commit()

            elif row[4]=='1': #핵심문장
                sql="exec dbo.P_MNG_ANA002 @section='SA', @site_gubun=%s, @part_group_id=%s,@part_sub_id=%s, @part_id=%s, @keyword_gubun=%s, @keyword_positive=%s, @rlt_value_01=%s, @rlt_value_02=%s, @rlt_value_03=%s, @rlt_value_04=%s, @rlt_value_05=%s"
                cursor.execute(sql, tuple(row))
                print("anal02_recode inserted")
                conn.commit()
        print("anal02_insert_완료")
    except Exception as e:
        print("Error: ", e)
    finally:
        conn.close()

def TB_anal03_insert(df):
    try:
        conn=conn_utf8()
        for i, row in df.iterrows():
            cursor=conn.cursor()
            if row[4]=='0': # 키워드
                sql="exec dbo.P_MNG_ANA003 @section='SA',@site_gubun=%s,@part_group_id=%s,@part_sub_id=%s,@part_id=%s,@keyword_gubun=%s, @rlt_value_01=%s, @rlt_value_02=%s, @rlt_value_03=%s, @rlt_value_04=%s, @rlt_value_05=%s, @rlt_value_06=%s, @rlt_value_07=%s, @rlt_value_08=%s, @rlt_value_09=%s, @rlt_value_10=%s"
                cursor.execute(sql,tuple(row))
                print("anal03_record inserted")
                conn.commit()

            elif row[4]=='1': #핵심문장
                sql="exec dbo.P_MNG_ANA003 @section='SA',@site_gubun=%s,@part_group_id=%s,@part_sub_id=%s,@part_id=%s, @keyword_gubun=%s, @rlt_value_01=%s, @rlt_value_02=%s, @rlt_value_03=%s, @rlt_value_04=%s, @rlt_value_05=%s"
                cursor.execute(sql, tuple(row))
                print("anal03_record inserted")
                conn.commit()
        print("anal03_insert_완료")
    except Exception as e:
        print("Error: ",e)
    finally:
        conn.close()

### 프로시저 실행
def TB_anal01_count():
    '''ANAL01 테이블 insert&update (count 실행)'''
    try:
        conn=conn_utf8()
        cursor=conn.cursor()
        sql="exec dbo.P_MNG_ANA001 @section='SB'"
        cursor.execute(sql)
        conn.commit()
        print("anal01_count 완료")
    except Exception as e:
        print("Error: ", e)
    finally:
        conn.close()

def TB_anal04_count():
    '''ANAL01 테이블 insert&update (count 실행)'''
    try:
        conn=conn_utf8()
        cursor=conn.cursor()
        sql="exec dbo.P_MNG_ANA004 @section='SB'"
        cursor.execute(sql)
        conn.commit()
        print("anal04_count 완료")
    except Exception as e:
        print("Error: ", e)
    finally:
        conn.close()

def last_isrt_dttm():
    with open('./etc/last_isrt_dttm.txt','r',encoding='utf8') as f:
        lines=f.readlines()
        last_line=len(lines)-1
        isrt_date=lines[last_line].split('\t')[1]
    return isrt_date

def save_txt(content_list,file_path):
    file_name=f'{file_path}.txt'
    with open(file_name,'a',encoding='utf8') as f:
        for line in content_list:
            f.write(f'{line}\n')

def time_txt(content_list,file_path):
    file_name=f'{file_path}.txt'
    if not os.path.exists(file_name):
        with open(file_name,'a',encoding='utf8') as f:
            f.write('분석날짜\t분석모델\t분석제품수\t총 리뷰수\t분석시간\n')
            
    with open(file_name,'a',encoding='utf8') as f:
        for line in content_list:
            f.write(f'{line}\t')
        f.write("\n")

### send mail infomation
sendEmail="asclhg@naver.com"
recvEmail="seojeong@asc.kr"
mail_pw="llhhgg0119@"

smtpName="smtp.naver.com"
smtpPort=587
session=None


def success_sendEmail():
    try:
        path=today_path()
        # SMTP 세션 생성
        session=smtplib.SMTP(smtpName,smtpPort)
        session.set_debuglevel(False)
        
        # SMTP 계정 인증 설정
        session.ehlo()
        session.starttls()
        session.login(sendEmail,mail_pw)

        # 메일컨텐츠 설정
        message=MIMEMultipart("mixed")
        
        # 메일 송/수신 옵션 설정
        message.set_charset('utf-8')
        
        content_path=os.path.join(path,'분석시간체크.txt')
        if not os.path.exists(content_path):
            text=f'{today} 분석완료'
        else:
            with open(content_path,'r',encoding='utf8') as f:
                text=f.read()
        
        message['From']=sendEmail
        message['To']=recvEmail
        message['Subject']=f"[리뷰분석완료]{today} Lipaco 분석완료"
        message.attach(MIMEText(text))
        
        # 메일 첨부파일
        attachments=os.listdir(path) # file_list: 폴더 내 파일 리스트
        
        work_dir=os.getcwd()
        isrt_dttm_path=os.path.join(work_dir,'etc','last_isrt_dttm.txt')
        #isrt_attach=open(isrt_dttm_path,'rb')
        part=MIMEBase('application','octet-stream')
        part.set_payload(open(isrt_dttm_path,'rb').read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", 'attachment',filename=os.path.basename(isrt_dttm_path))
        message.attach(part)

        if len(attachments) > 0:
            for attachment in attachments:
                file_path=os.path.join(path,attachment)
                attach_binary=MIMEBase("application","octet-stream")
                try:
                    attach_file=open(file_path,"rb").read() #open the file
                    attach_binary.set_payload(attach_file)
                    encoders.encode_base64(attach_binary)
                    
                    # 파일이름 지정된 report header추가
                    attach_binary.add_header("Content-Disposition", 'attachment',filename=attachment)
                    message.attach(attach_binary)
                except Exception as e:
                    print(e)

        # 메일 발송
        session.sendmail(sendEmail,recvEmail,message.as_string())
        print("successfully sent the mail")

    except Exception as e:
        print(e)
    finally:
        if session is not None:
            session.quit()


def fail_sendEmail(err):
    msg=MIMEText(err)
    msg['Subject']=f"[리뷰분석오류]{today} 리파코 분석 오류"
    msg['From']=sendEmail
    msg['To']=recvEmail
    print(msg.as_string())

    s=smtplib.SMTP(smtpName,smtpPort)
    s.starttls()
    s.login(sendEmail,mail_pw)
    s.sendmail(sendEmail,recvEmail,msg.as_string())
    s.close()
    print("successfully sent the mail")


def today_path():
    '''backup folder create'''
    folder_path=os.getcwd()+'/etc/result'
    #folder_path=os.getcwd()+'\\etc\\result_data'
    today_path=os.path.join(folder_path,today)
    if not os.path.exists(today_path):
        os.mkdir(today_path)
    return today_path