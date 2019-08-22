# flask 모듈 임포트
from flask import Flask, render_template, request
# 세션 기능을 위한 모듈
from flask import session
import urllib.request
from urllib.parse import urlencode, quote_plus, unquote
import xml.etree.ElementTree as ET
import folium
import requests
from tqdm import tqdm_notebook
import googlemaps as gmaps
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import db

decode_key = unquote('WF9v2HhErnR0ovu%2FVJJX8InWINAh4ZaZrMPvZLpcK%2FkXGR3V9%2F3kAQyfKuilCn7LqLPIZlnh97Ed3TxFoLkbrA%3D%3D')  # decode 해줍니다.
gmaps_key="AIzaSyC2dDq-4r8MTzLsw_7Y2XCe5wwuq46Ve4k"
gmaps=gmaps.Client(key=gmaps_key)
# flask 객체 생성
app = Flask(__name__)

# 세션을 위한 비밀키 설정
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# # 라우터 등록 => 웹상 루트 주소 생성
@app.route('/', methods=['Get'])
def survey():
    return render_template('survey.html')
plt.rc('font', family='Malgun Gothic')

@app.route('/main_survey', methods=['POST'])
def main_survey():
    gu = request.form.get('hospital')
    count = request.form.get('time')
    hospital = request.form.get('hospital')
    money = request.form.get('money')
    money_rate = request.form.get('money')

    return render_template('survey.html', gu=gu, count=count, money=money, hospital=hospital, money_rate=money_rate, clicked='clicked')

@app.route('/home', methods=['Get'])
def home():
    return render_template('home.html')

@app.route('/bbs', methods=['POST','GET'])
def bbs():
    return render_template('bbs.html')

@app.route('/get',methods=['GET'])
def get():
    return render_template('get.html')

# 한글 주소를 위도,경도로 바꿔주는 함수
def getGeoData(address):
    # Local(테스트) 환경 - https 요청이 필요없고, API Key가 따로 필요하지 않지만 횟수에 제약이 있습니다.
    URL = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&language=ko&address={}' \
        .format(address)

    # Production(실제 서비스) 환경 - https 요청이 필수이고, API Key 발급(사용설정) 및 과금 설정이 반드시 필요합니다.
    URL = 'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyBTdPHS8frL94EdhFNBciIw6IcFj6MADDw' \
          '&sensor=false&language=ko&address={}'.format(address)

    # URL로 보낸 Requst의 Response를 response 변수에 할당
    response = requests.get(URL)

    # JSON 파싱
    data = response.json()

    # lat, lon 추출
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']

    return [lat, lng]

# 사용자가 선택한 강아지의 정보를 보여주는 함수
@app.route('/select_dog', methods=['GET'])
@app.route('/select_dog/<sort>/<neutral>/<sex>')
def select_dog(sort='', neutral='', sex=''):
    select = db.get_dog_location(sort,neutral,sex)

    location = [37.5103, 126.982]
    map = folium.Map(location=[37.5103, 126.982], zoom_start=10, titles='Stamen Toner')
    folium.Marker(location, icon=folium.Icon(color='blue')).add_to(map)

    check = {}
    for i in select:
        geoData = getGeoData(i['careAddr'])
        geo = str(geoData[0])+'/'+ str(geoData[1])
        print(geo)
        if geo in check.keys():
            check[geo] += i['desertionNo'] + '/'
        else:
            check[geo] = i['desertionNo'] + '/'

        folium.Marker(geoData, popup=folium.Popup(
            '<a href="http://127.0.0.1:5000/show_dog_list?code=' + check[geo] + '" target="_top">' + i[
                'careNm'] + '</a>',
            show=True), icon=folium.Icon(color='red')).add_to(map)

    return map._repr_html_()

# 사용자가 선택한 강아지 파일 추출
def make_dog_list(code):
    dog_list = []
    dog = db.get_dog_list(code)
    print(dog)
    for i in dog:
        temp = {}
        temp['사진파일'] = i['filename']
        temp['품종'] = i['kindCd']
        temp['성별'] = i['sexCd']
        temp['중성화여부'] = i['neuterYn']
        temp['나이'] = i['age']
        temp['특징'] = i['specialMark']
        temp['공고기한'] =i['noticeSdt']
        temp['접수일'] = i['happenDt']

        dog_list.append(temp)

    return dog_list

def make_shelter_list(code):
    dog_shelter = []
    shelter = db.get_shelter_list(code)
    for i in shelter:
        temp = {}
        temp['보호소 이름'] = i['careNm']
        temp['보호 장소'] = i['careAddr']
        temp['보호소 전화번호'] = i['careTel']
        temp['담당자'] = i['chargeNm']
        temp['담당자 연락처'] = i['officetel']

        dog_shelter.append(temp)

    return dog_shelter

@app.route('/show_dog_list', methods=['GET'])
def show_dog_list():

    code = request.args.get('code')
    code = code.split('/')
    dog_code =[x for x in code if x != '']
    for i in dog_code:
        print(i)

    dog_list = make_dog_list(dog_code)
    dog_shelter= make_shelter_list(dog_code)
    print(dog_list)

    return render_template('show_dog_list.html', dog_list=dog_list, dog_shelter=dog_shelter )



# 편의시설 - 병원 위치 보여주기
@app.route('/hospital')
@app.route('/hospital/<gugu>')
def show_hospitals(gugu=None):
    if gugu==None:
        gugu='강남구'

    dog_hospital = pd.read_csv('static/csv/hospital/서울시 '+gugu+' 동물병원 현황.csv', encoding='utf-8')
    dog_hospital = dog_hospital[(dog_hospital['영업상태'] == '정상')]
    view_columns = ['업소명', '사업장소재지(지번)', '전화번호']
    dog_hospital = dog_hospital[view_columns]
    dog_hospital.rename(columns={dog_hospital.columns[1]: '위치'},
                        inplace=True)
    dog_hospital = dog_hospital.dropna(how='any')
    geo_dog = dog_hospital

    lat = []
    lng = []
    for n in tqdm_notebook(geo_dog.index):
        try:
            tmp_add = str(geo_dog['위치'][n]).split('(')[0]
            tmp_map = gmaps.geocode(tmp_add)

            tmp_loc = tmp_map[0].get('geometry')
            lat.append(tmp_loc['location']['lat'])
            lng.append(tmp_loc['location']['lng'])

        except:
            lat.append(np.nan)
            lng.append(np.nan)
            print('Here is nan!')

    geo_dog['lat'] = lat
    geo_dog['lng'] = lng

    map = folium.Map(location=[geo_dog['lat'].mean(),
                               geo_dog['lng'].mean()],
                     zoom_start=12)
    for n in geo_dog.index:
        hospital_name = geo_dog.loc[n, '업소명'] + '-' + geo_dog.loc[n, '위치']
        folium.Marker([geo_dog.loc[n, 'lat'],geo_dog.loc[n, 'lng']],popup=hospital_name).add_to(map)  # marker는 크기 지정이 안되어서 하려면 circle marker로 해야 함
    map

    return map._repr_html_()

# 편의시설 - 공원위치 보여주기
@app.route('/park')
@app.route('/park/<gugu>')
def park_html(gugu=None):
    if gugu == None:
        gugu = '강남구'

    park = pd.read_csv('static/csv/park/park' + gugu + '.csv', encoding='utf-8')
    view_columns = ['공원명', '지역', '위치', '전화번호']
    park = park[view_columns]
    geo_park = park
    lat = []
    lng = []

    for n in tqdm_notebook(geo_park.index):
        try:
            tmp_add = str(geo_park['위치'][n]).split('(')[0]
            tmp_map = gmaps.geocode(tmp_add)

            tmp_loc = tmp_map[0].get('geometry')
            lat.append(tmp_loc['location']['lat'])
            lng.append(tmp_loc['location']['lng'])

        except:
            lat.append(np.nan)
            lng.append(np.nan)
            print('Here is nan!')

    geo_park['lat'] = lat
    geo_park['lng'] = lng

    map = folium.Map(location=[geo_park['lat'].mean(), geo_park['lng'].mean()], zoom_start=12)

    for n in geo_park.index:
        park_name = geo_park.loc[n, '공원명'] + '-' + geo_park.loc[n, '위치']
        folium.Marker([geo_park.loc[n, 'lat'], geo_park.loc[n, 'lng']], popup=park_name).add_to(map)

    return map._repr_html_()

app.run(host='127.0.0.1', port=5000, debug=True)
#app.run(host='0.0.0.0', port=80, debug=True)