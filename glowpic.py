
from ntpath import join
from turtle import end_fill
import kss 
import os
import csv
from unicodedata import category, name
import pandas as pd
import time
from datetime import datetime
import pymssql

today=datetime.now().strftime('%Y%m%d')

def makeconn():

    host = 'ASC-AI.iptime.org'
    database = 'cosmeca'
    user = 'cosmeca '
    password = 'asc1234pw!'

    conn = pymssql.connect(
        host , user, password, database,charset='cp949'
    )
    return conn

# data = pd.read_csv('220214_glowpic_review.csv', header=None)
# data = data.iloc[:, 0:13]
def labeling(group):
    try:
        if group == 'P02':
            # P02	남성류(male_care)
            categorys = {'발림성' : ['발림','발려','발랐','발라','바르기','부드럽','발리'],
                        '지속력' : ['밀착','지속','오래','유지','무너짐','무너지','오랫'],
                        '보습력' : ['보습','촉촉','흡수','당기','당김','뽀송','보송','스며','매트','수분','유분'],
                        '커버력' : ['커버','표현','가려','잡티','밀착','보정','가리'],
                        '향' : ['향이','냄새','잔향','향도','향은','향기','청량','은은','무향'],
                        '효과' : ['트러블','피부','주름','산뜻','찐득','순하','기름','진정','끈적','밀림','번들','매끄','매끈','쿨링','시원'],
                        '기타' : ['편리','간편','편해','깔끔','편하']
                        }
            category_name = 'male_care'
        elif group == 'P04':
            # P04	마스크/팩(mask_care)
            categorys = {'발림성' : ['발림','발려','발랐','발라','바르기','부드럽','발리'],
                        '수분감' : ['촉촉','수분'],
                        '보습력' : ['보습','흡수','당기','당김','뽀송','보송','스며','매트','유분'],
                        '커버력' : ['커버','표현','가려','잡티','밀착','보정','가리'],
                        '향' : ['향이','냄새','잔향','향도','향은','향기','청량','은은','무향'],
                        '효과' : ['영양','물광','광도','꿀광','광채','진정','윤기','탄력','뽀루지','트러블','피부','주름','산뜻','찐득','순하','기름','진정','끈적','밀림','번들','매끄','매끈','쿨링','시원','탱탱','쫀쫀'],
                        '기타' : ['밀착','접착','얇게','얇았','두껍','부착','두꺼','얇고']
                        }
            category_name = 'mask_care'
        elif group == 'P05' or group=='P06':
            # P05/P06	메이크업(립)/메이크업(아이)(point_makeup)
            categorys = {'발림성' : ['발림','발려','발랐','발라','발리','바르기'],
                        '보습력' : ['촉촉','매트','흡수','보습','수분'],
                        '향' : ['향이','향기','냄새','향도'],
                        '지속력' : ['밀착','지속','오래','유지','무너짐','무너지','오랫'],
                        '발색력' : ['발색','색상','표현','선명','색깔'],
                        '효과' : ['번짐','워터푸르프','효과','성능','풍성','다크닝','번지는']
                        }
            category_name = 'point_makeup'
        elif group == 'P07':
            # P07	메이크업(페이스)(Base_makeup)
            categorys = {'발림성': ['발림','발려','발랐','발라','발리','바르기'],
                        '보습력' : ['보습','수분','촉촉','흡수'],
                        '커버력' : ['커버','표현','가려','잡티','밀착','보정','가리'],
                        '지속력' : ['지속','오래','유지','무너짐'],
                        '향' : ['향이','향도','향기','냄새'],
                        '효과' : ['꿀광','광이','광채','광도','물광','톤업','밝아','환해','자외선','차단','쫀존','다크닝','트러블','뾰루지']
                        }
            category_name = 'Base_makeup'
        elif group == 'P08' or group=='P12':
            # P08/P12	바디케어/헤어케어(hair_body)
            categorys = {'발림성' : ['발림','발려','발랐','발라','보송','바르기'],
                        '수분감' : ['촉촉','수분'],
                        '보습력' : ['보습','흡수','스며','당김'],
                        '거품세정력' : ['거품','버블','풍부','폼','세정','개운'],
                        '탈모' : ['숱','머리카락','탈모','빠짐','빠지'],
                        '효과' : ['영양','두피','비듬','윤기','찰랑','각질','환해','피부','밝아','진정','머릿결','자극','트러블'],
                        '향' : ['향이','향기','냄새','향도','잔향']
                        }
            category_name = 'hair_body'
        elif group == 'P09':
            # P09	선케어(sun_care)
            categorys = {'발림성': ['발림','발려','발랐','발라','발리','바르기'],
                        '효과' : ['톤업톤업','밝아','환해','주름','블루라이트','워터푸르프','시림','밀림','쿨링','시원','땀','물에','백탁','태닝','밝아','환해','주름','블루라이트','워터푸르프','시림','밀림','쿨링','시원','땀','물에'],
                        '보습력' : ['보습','수분','촉촉'],
                        '자외선' : ['자외선','차단','햇빛','타지','알러지','타는','기미','uv','UV'],
                        '향' : ['향이','향도','향기','냄새','무향'],
                        '끈적임' : ['끈적','산뜻','달라붙','보송']
                        }
            category_name = 'sun_care'
        elif group == 'P10':
            # P10	스킨케어(skin_care)
            categorys = {'발림성': ['발림','발려','발랐','발라','질감','발리','밝아','부드럽'],
                        '보습력' : ['보습','흡수','스며'],
                        '수분감' : ['수분','촉촉'],
                        '끈적임' : ['끈적','산뜻','달라붙'],
                        '향' : ['향이','향도','향기','냄새'],
                        '효과' : ['효과','물광','광도','광채','번들','광이','윤기','매끈','톤업','밝아','환해','영양','주름','탄력','리프팅','개선','영양','미백','자극','트러블','여드름','진정']
                        }
            category_name = 'skin_care'
        elif group == 'P11':
            # P11	클렌징(cleanser)
            categorys = {'거품력' : ['거품','버블','풍부','폼'], 
                    '보습력' : ['보습','수분','촉촉'],
                    '세정력' : ['세정','개운','깨끗','지워','세안'],
                    '향' : ['향이','향기','냄새','향도','무향'],
                    '효과' : ['뾰루지','각질','시림','당김','트러블','여드름','블랙헤드','진정','자극','효과']
                    }
            category_name = 'cleanser'
    except:
        pass
    return categorys,category_name
    
def split_before():
    '''리뷰data split하기 전 데이터 분할하여 저장'''
    # 폴더 생성
    if not os.path.isdir("C:/glowpic_sentences/glowpic_sentences_before_"+today):
        os.makedirs("C:/glowpic_sentences/glowpic_sentences_before_"+today)

    # db
    conn = makeconn()
    cs = conn.cursor()

    select_query = "SELECT * FROM TB_REVIEW WHERE SITE_GUBUN='G';"
    cs.execute(select_query)
    data_lis = cs.fetchall()
    conn.close()
    
    data = pd.DataFrame(data_lis)

    # csv 
    # data = pd.read_csv('220214_glowpic_review.csv', header=None)
    
    # 리뷰개수를 3천개로 분할하여 저장
    k = 3000  
    dfs = [data.loc[i:i+k-1, :] for i in range(0, len(data), k)]
    for i, df_before in enumerate(dfs):
        fname = 'data_split_before_'+str(i+1) + ".csv"
        df_before.to_csv('C:/glowpic_sentences/glowpic_sentences_before_'+today+'/'+fname, encoding='utf-8-sig')
    
    return df_before

def split_after():
    '''리뷰data split 후 데이터 저장'''
    # 폴더 생성
    if not os.path.isdir("C:/glowpic_sentences/glowpic_sentences_after_"+today):
        os.makedirs("C:/glowpic_sentences/glowpic_sentences_after_"+today)


    path='C:/glowpic_sentences/glowpic_sentences_before_'+today+'/' # 고치기
    file_list=os.listdir(path)  
    file_list_py=[file for file in file_list if file.endswith('.csv')]
    df=pd.DataFrame()

    for file_name in file_list_py:
        file_name_after = file_name.replace('before','after')
        data_list = split_after_in(file_name)
        print(f'file_name={file_name}')

        # df = pd.DataFrame(data_list, columns=['site', 'group', 'sub', 'part_id', 'doc_no', 'isrt_date', 'nicname', 'grade', 'age', 'gender', 'types', 'review', 'review_cnt','review_split', 'review_split_cnt'])
        # df.to_csv('C:/glowpic_sentences/glowpic_sentences_after_'+today+'/'+file_name_after, encoding='utf-8-sig')
        
        df_after=[]
        for k in data_list:
            site = k[0]
            group = k[1]
            sub = k[2]
            part_id = k[3]
            doc_no = k[4]
            isrt_date = k[5]
            nicname = k[6]
            grade = k[7]
            age = k[8]
            gender = k[9]
            types = k[10]
            review = k[11]
            cnt = k[12]
            review_split = k[13]
            review_split_cnt = k[14]
            
           
            t = labeling(group)

            kk=[]
            for key,ivalue in t[0].items():
                part_key = key 
                for i in ivalue:
                    if i in review_split:
                        a=(part_key, i)
                        kk.append(a)
            # categorys = ','.join(kk)
            kd = (site, group, sub, part_id, doc_no, isrt_date, nicname, grade, age, gender, types, review,cnt, review_split, review_split_cnt, kk)
            df_after.append(kd)
        df = pd.DataFrame(df_after, columns=['site', 'group', 'sub', 'part_id', 'doc_no', 'isrt_date', 'nicname', 'grade', 'age', 'gender', 'types', 'review', 'review_cnt','review_split', 'review_split_cnt','categorys'])
        df.to_csv('C:/glowpic_sentences/glowpic_sentences_after_'+today+'/'+file_name_after, encoding='utf-8-sig')

    return df_after

def split_after_in(file_name):
    start_time = time.time()
    path='C:/glowpic_sentences/glowpic_sentences_before_'+today+'/' # 고치기

    data=pd.read_csv(path+file_name)
    file_name_after = file_name.replace('before','after')
    data = data.values.tolist()

    data_list=[]

    for data_low in data:
        site = data_low[1]
        group = data_low[2]
        sub = data_low[3]
        part_id = data_low[4]
        doc_no = data_low[5]
        isrt_date = data_low[6]
        nicname = data_low[7]
        grade = data_low[9]
        age = data_low[10]
        gender = data_low[11]
        types = data_low[12]
        review = data_low[13]
        review_cnt = len(review)
        

        
        review_split_total = kss.split_sentences(review)
        for review_split_low in review_split_total:
            review_split = review_split_low.replace("'","")
            review_split_cnt = len(review_split)
            kd = (site, group, sub, part_id, doc_no, isrt_date, nicname, grade, age, gender, types, review, review_cnt,review_split, review_split_cnt)
            data_list.append(kd)
    end_time = (time.time() - start_time)/60    
    print('split 완료시간 --- {0:0.2f} 분 소요'.format(end_time))

    return data_list


# if __name__ == '__main__':
#     try : 
#         # 폴더생성
#         if not os.path.isdir("C:/glowpic_sentences"):
#             os.makedirs("C:/glowpic_sentences")

#         start_time = time.time()
        
#         # 데이터 3000개씩 나눔
#         # split_before()

#         split_after()

#         end_time = (time.time() - start_time)/60
#         print('split 완료시간 --- {0:0.2f} 분 소요'.format(end_time))
#     except Exception as e:
#         print(e)

