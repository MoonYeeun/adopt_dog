import pymysql
# flask 모듈 임포트

# 데이터 베이스에 접속하는 함수
def get_connection() :
    conn = pymysql.connect(host='database-1.cijzxjnptmnm.us-east-2.rds.amazonaws.com',
                           user='root',
                           password='12341234',
                           db='innodb',
                           charset='utf8')
    return conn
def get_dog_location(sort,neutral,sex):

    conn = get_connection()
    cursor = conn.cursor()
    sql = "SELECT sl.desertionNo as desertionNo, careAddr, careNm from shelter_list sl inner join dog_list dl on sl.desertionNo = dl.desertionNo where dl.kindCd like '%" + sort + "%'and dl.neuterYn = '" + neutral + "' and dl.sexCd = '" + sex + "'"
    print(sql)
    cursor.execute(sql)
    result = cursor.fetchall()

    dog_loc = []
    for i in result:
        location = {}
        location['desertionNo'] = i[0]
        location['careAddr'] = i[1]
        location['careNm'] = i[2]
        dog_loc.append(location)
    return dog_loc

# 강아지 정보를 가져오는 함수
def get_dog_list(code):
    # 데이터베이스 접속 함수 호출

    conn = get_connection()
    # 작업변수 생성
    cursor = conn.cursor()
    dog = []
    for i in code:
        sql = '''SELECT age, desertionNo, filename, happenDt, kindCd, 
                          neuterYn, noticeSdt, sexCd, specialMark
                    FROM dog_list where desertionNo = %s'''

        cursor.execute(sql, i)
        result = cursor.fetchall()
        for i in result:
            dog_list = {}
            dog_list['age'] = i[0]
            dog_list['desertionNo'] = i[1]
            dog_list['filename'] = i[2]
            dog_list['happenDt'] = i[3]
            dog_list['kindCd'] = i[4]
            dog_list['neuterYn'] = i[5]
            dog_list['noticeSdt'] = i[6]
            dog_list['sexCd'] = i[7]
            dog_list['specialMark'] = i[8]
            dog.append(dog_list)

    conn.close()
    return dog

# 보호소 정보를 가져오는 함수
def get_shelter_list(code):
    # 데이터베이스 접속 함수 호출
    conn = get_connection()
    # 작업변수 생성
    cursor = conn.cursor()
    shelter = []
    for i in code:
        sql = '''SELECT careNm, careAddr, careTel, chargeNm, officetel
                FROM shelter_list where desertionNo = %s'''

        cursor.execute(sql, i)
        result = cursor.fetchall()
        for i in result:
            shelter_list = {}
            shelter_list['careNm'] = i[0]
            shelter_list['careAddr'] = i[1]
            shelter_list['careTel'] = i[2]
            shelter_list['chargeNm'] = i[3]
            shelter_list['officetel'] = i[4]

            shelter.append(shelter_list)

    conn.close()
    return shelter