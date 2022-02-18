import pandas as pd
# #import emp_class
from keys.key import *
from db import *
# import pandas as pd
# def TB_join(df):
#     print('db_data_loading for keyword/sentence')
#     try:
#         review_col_name=["SITE_GUBUN","PART_GROUP_ID","PART_SUB_ID","PART_ID","REVIEW_DOC_NO","REVIEW"]
#         df_review_concat=pd.DataFrame(columns=review_col_name)
#         anal00_col_name=["REVIEW_DOC_NO","PART_ID","RLT_VALUE_03"]
#         anal00_concat=pd.DataFrame(columns=anal00_col_name)
#         conn=conn_cp949()
#         cursor = conn.cursor()


#         for i,part in df.iterrows():
#             print(i)
#             sql1="select SITE_GUBUN, PART_GROUP_ID, PART_SUB_ID, PART_ID, REVIEW_DOC_NO, REVIEW from TB_REVIEW (nolock) where PART_SUB_ID=%s and PART_ID=%s"
#             cursor.execute(sql1, tuple(part))
#             tb_review=cursor.fetchall()
#             df_review=pd.DataFrame(tb_review, columns=review_col_name)
#             df_review_concat=pd.concat([df_review_concat,df_review])
            
#             part_id=df.iloc[i,1]
#             print(part_id)
#             sql2="select REVIEW_DOC_NO, PART_ID, RLT_VALUE_03 from TB_REVIEW_ANAL_00 (nolock) where PART_ID=%s"
#             cursor.execute(sql2, (part_id))
#             row=cursor.fetchall()
#             df_anal00=pd.DataFrame(row, columns=anal00_col_name)
#             print(df_anal00)
#             anal00_concat=pd.concat([anal00_concat,df_anal00])
#     except Exception as e:
#         print("Error: ",e)
#     finally:
#         conn.close()
#     result=pd.merge(df_review_concat,anal00_concat,on=['REVIEW_DOC_NO','PART_ID'])
#     # df_columns=site_gubun, part_group_id, part_sub_id, part_id, review_doc_no, review, rlt_value_03
#     return result

anal00_df = anal00()
not_anal_df = TB_join(anal00_df)
print(not_anal_df)

#anal03=total(not_anal_df)
#print(anal03)
anal02=emo(not_anal_df)
# # 에러 테스트

# #import time
# #import os
# #import traceback
# #from datetime import datetimed
# from etc.log import error_time
# #err=''

# # class TestError(Exception):
# #     def __init__(self, e:str):
# #         now = datetime.now()
# #         current_time = time.strftime("%Y.%m.%d/%H:%M:%S", time.localtime(time.time()))
# #         now = now.strftime("%Y%m%d-%H-%M")
# #         self.value=e
# #         with open(f"./etc/log/{now} Log.txt", "a") as f: # 경로설정
# #             f.write(f"[{current_time}] - {self.value}\n")
# #         print("실행됨")
    
# #     def __str__(self):
# #         return self.value


# # def ErrorLog(error: str):
# #     now = datetime.now()
# #     current_time = time.strftime("%Y.%m.%d/%H:%M:%S", time.localtime(time.time()))
# #     now = now.strftime("%Y%m%d-%H-%M")

# #     with open(f"./etc/log/{now} Log.txt", "a") as f: # 경로설정
# #         f.write(f"[{current_time}] - {error}\n")

# # def test2():
# #     #global err
# #     #e = ''
# #     # error=TestError()
# #     try:
# #         df=pd.read_csv('1123_test_copy.csv')
# #         return df
# #     except Exception as e:
# #         error_content='error내용'
# #         error.TestError(error_content)
# #         print(e)
#     #err = err+e

# # df=test2()

# # def test():
# #     global err
# #     e = ''
# #     try:
# #         df=pd.read_csv('1123_test_copy.csv')
# #     except Exception as e:
# #         print(e)
# #     err = err+e
# #     return df


# # try:
# #     df=test2()
    
# #     if err!='':
# #         raise TestError(err)
# #     print(df)
# # except Exception:
# #         err = traceback.format_exc()
# #         ErrorLog(str(err))
# #         print("log 저장")



# # # 1. load data
# # #df=db.TB_REVIEW_qa(from_date,to_date)
# # df=pd.read_csv('1123_test_copy.csv')

# # # 2. sub_id:model_id
# # model_id_dic=db.TB_model_id()
# # # 3. property_id : property_name
# # property_id_dic=db.TB_property_id()

# # # 4. anal00(property+empathy result) insert
# # '''gpu 사용'''
# # anal00=emp_class.cos_model_pt(df,model_id_dic,property_id_dic)

# # '''api_url 사용'''
# # #anal00=emp_class.cos_model_url(df,model_id_dic,property_id_dic)
# # print(anal00)
# # db.TB_anal00_insert(anal00)

# # # 5. keyword/sentence
# # # 5-1. ['part_sub_id','part_id'] list
# # df_id=df[['part_sub_id','part_id']]
# # df_id=df_id.drop_duplicates(ignore_index=True)
# # id_list=[]
# # for index, row in df_id.iterrows():
# #     id_list.append(row.tolist())

# # 5-2. 

# # 5-3.
# #df1 = db.anal00_part_id()
# # print(df1)

# df2 =pd.read_csv('part_list.csv')
# df2 = df2.astype('string') 
# # print(df2)
# # id_list=[]
# # for index, row in df2.iterrows():
# #     id_list.append(row.tolist())

# # print(id_list)
#anal03=total(df)
# anal02=emo(df2_id)


######################################################################
