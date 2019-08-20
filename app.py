
# flask 모듈 임포트
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from ipywidgets import IntProgress
import foliumTest
import pandas as pd
import seaborn as sns
import folium
import googlemaps
from tqdm import tqdm_notebook

# from io import BytesIO
# import base64

# 세션 기능을 위한 모듈
from flask import session
# DB 파일 연결
# import db

# 11
# flask 객체 생성
app = Flask(__name__)

# 세션을 위한 비밀키(안써도 되지만, 해킹을 방지하기위해)
app.secret_key = b'_5#y2L"F4Q8z/n/xec]/'
gmaps_key="AIzaSyC2dDq-4r8MTzLsw_7Y2XCe5wwuq46Ve4k"
gmaps=googlemaps.Client(key=gmaps_key)

# 라우터 등록 => 웹상 루트 주소 생성
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



@app.route('/park')
@app.route('/park/<gugu>')
def park_html(gugu=None):
    if gugu == None:
        gugu ="강남구"

    park = pd.read_csv('static/gupark/park' + gugu + '.csv', encoding='utf-8')
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





# 앱 실행
# 웹주소와 포트 지정
app.run(host='127.0.0.1', port=8079, debug=True)

# 결과 확인은?
# 터미널창에서 python app.py
# 주소가 표시되면 [Ctrl]누른 상태에서 클릭
# 터미널창에서 [Ctrl]+[C]

















