# flask 모듈 임포트
from flask import Flask, render_template, request
# 세션 기능을 위한 모듈
from flask import session
import urllib.request
from urllib.parse import urlencode, quote_plus, unquote
import xml.etree.ElementTree as ET
import folium
import pprint
import requests
from tqdm import tqdm_notebook
import pandas
import numpy

decode_key = unquote('WF9v2HhErnR0ovu%2FVJJX8InWINAh4ZaZrMPvZLpcK%2FkXGR3V9%2F3kAQyfKuilCn7LqLPIZlnh97Ed3TxFoLkbrA%3D%3D')  # decode 해줍니다.

# flask 객체 생성
app = Flask(__name__)

# 세션을 위한 비밀키 설정
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
dog_imageUrl = ""

# # 라우터 등록 => 웹상 루트 주소 생성
@app.route('/', methods=['GET'])
def index():
    return render_template('layout.html')
#     # 세션이 있는지 없는지에 따라 html 분기
@app.route('/bbs', methods=['GET'])
def select_dog():
    return render_template('bbs.html')

@app.route('/choose_dog', methods=['GET'])
def choose_dog():
    dog_code = request.args.get('code')
    print(dog_code)
    return render_template('choose_dog.html',dog_code=dog_code)


#@app.route('/', methods=['GET','POST'])
def show_map():
    # 사용자가 선택한 조건에 따른 유기견 검색
    # location = request.form['location']
    # sort = request.form['sort']
    # age = request.form['age']
    # haircolor = request.form['haircolor']
    # neutral = request.form['neutral']
    # sex = request.form['sex']

    # 주소 담을 리스트
    address = []
    note = adopt_dog_api()

    for i in note.iter("careAddr"):
        place = i.text
        if '서울특별시' in place:
            print(place)
            address.append(place)
    map = folium.Map(location=[37.5103, 126.982], zoom_start=12)
    for i in address:
        geoData = getGeoData(i)
        folium.Marker(geoData, popup=i, icon=folium.Icon(color='red')).add_to(map)

    return map._repr_html_()
    # return render_template('choose_dog.html',address=address)

# api에서 유기견 정보 받아오는 함수
def adopt_dog_api():

    url = 'http://openapi.animal.go.kr/openapi/service/rest/abandonmentPublicSrvc/abandonmentPublic'
    # queryParams = '?' + urlencode({quote_plus('ServiceKey'): decode_key,
    #                                quote_plus('upkind'): 417000,
    #                                quote_plus('upr_cd'): 6110000,
    #                                quote_plus('pageNo'): 1})

    for n in range(1, 5):
        pagenum = str(n)

        queryParams = '?' + urlencode({quote_plus('ServiceKey'): decode_key,
                                       quote_plus('upkind'): 417000,
                                       # quote_plus('kindCd') : '000115',
                                       quote_plus('upr_cd'): '6110000',
                                       # quote_plus('org_cd') : '3220000',
                                       # 79쪽까지
                                       quote_plus('pageNo'): pagenum})
        req = urllib.request
        body = req.urlopen(url + queryParams)
        req.get_method = lambda: 'GET'
        response_body = body.read()
        result = response_body.decode('utf-8')
        print('pagenum: '+ pagenum)
        print(result)
        tree = ET.ElementTree(ET.fromstring(result))
        note = tree.getroot()
        return note

    # req = urllib.request
    # body = req.urlopen(url + queryParams)
    # req.get_method = lambda: 'GET'
    # response_body = body.read()
    # result = response_body.decode('utf-8')
    # print(result)
    # tree = ET.ElementTree(ET.fromstring(result))
    # return tree.getroot()

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
@app.route('/select_dog', methods=['GET', 'POST'])
def show_dog():
    # 사용자가 선택한 조건에 따른 유기견 검색
    #location = request.form['location']
    sort = request.form['sort']
    # haircolor = request.form['haircolor']
    neutral = request.form['neutral']
    sex = request.form['sex']
    print(sort, neutral,sex)

    # 주소 담을 리스트
    dog_data = {}
    care_location = []
    note = adopt_dog_api()

    for i in note.iter("item"):
        if ('보호중' in i.findtext('processState'))&(sort in i.findtext("kindCd")) & (neutral in i.findtext("neuterYn")) & (sex in i.findtext("sexCd")):
            print(i.findtext('careAddr'))
            dog_data[i.findtext('desertionNo')] = i.findtext('careAddr')
            care_location.append(i.findtext('careNm')) # 유기견 보호센터 이름

    map = folium.Map(location=[37.5103, 126.982], zoom_start=12,titles='Stamen Toner')

    num = 0
    for i in dog_data:
        geoData = getGeoData(dog_data.get(i))
        print(i)
        #folium.Marker(geoData, popup=i, icon=folium.Icon(color='red')).add_to(map)
        folium.Marker(geoData, popup=folium.Popup('<a href="http://127.0.0.1:5000/show_dog_list?code=' + i +'" target="_self">'+ care_location[num] +'</a>',show=True), icon=folium.Icon(color='red')).add_to(map)
        num +=1
    return map._repr_html_()

# 사용자가 선택한 강아지 파일 추출
def make_dog_list(code):
    dog_list = {}
    note = adopt_dog_api()

    for i in note.iter("item"):
        if code in i.findtext('desertionNo'):
            if '보호중' in i.findtext('processState'):
                dog_list['사진파일'] = i.findtext('popfile')
                dog_list['품종'] = i.findtext('kindCd')
                dog_list['성별'] = i.findtext('sexCd')
                dog_list['중성화여부'] = i.findtext('neuterYn')
                dog_list['나이'] = i.findtext('age')
                dog_list['특징'] = i.findtext('specialMark')
                notice = i.findtext('noticeSdt') + " ~ " + i.findtext('noticeEdt')
                dog_list['공고기한'] = notice
                dog_list['접수일'] = i.findtext('happenDt')
                break
            elif '종료(반환)' in i.findtext('processState'):
                print("종료(반환)된 강아지 입니다. 다른 강아지를 선택해 주세요.")
            elif '종료(안락사)' in i.findtext('processState'):
                print("종료(안락사)된 강아지 입니다. 다른 강아지를 선택해 주세요.")
            elif '종료(입양)' in i.findtext('processState'):
                print("종료(입양)된 강아지 입니다. 다른 강아지를 선택해 주세요.")
            else:
                print("다른 강아지를 선택해 주세요.")
                # print("특이사항 : "+i.findtext('noticeComment'))
                # else:
                #     print('dog - 찾으시는 강아지가 없습니다.')
                break
    return dog_list

def make_shelter_list(code):
    dog_shelter = []
    note = adopt_dog_api()
    for i in note.iter("item"):
        if code in i.findtext('desertionNo'):
        # if '411320201901302' in i.findtext('desertionNo'):
            if '보호중' in i.findtext('processState'):
                dog_shelter.append(("보호소 이름 : " + i.findtext('careNm')))
                dog_shelter.append(("보호소 전화번호  : " + i.findtext('careTel')))
                dog_shelter.append(("보호 장소  : " + i.findtext('careAddr')))
                dog_shelter.append(("담당자  : " + i.findtext('chargeNm')))
                dog_shelter.append(("담당자 연락처 : " + i.findtext('officetel')))
                break
            elif '종료(반환)' in i.findtext('processState'):
                print("종료(반환)된 강아지 입니다. 다른 강아지를 선택해 주세요.")
            elif '종료(안락사)' in i.findtext('processState'):
                print("종료(안락사)된 강아지 입니다. 다른 강아지를 선택해 주세요.")
            elif '종료(입양)' in i.findtext('processState'):
                print("종료(입양)된 강아지 입니다. 다른 강아지를 선택해 주세요.")
            else:
                print("다른 강아지를 선택해 주세요.")
        else:
            print('shelter - 찾으시는 강아지가 없습니다.')
    return dog_shelter

@app.route('/show_dog_list', methods=['GET'])
def show_dog_list():

    dog_code = request.args.get('code')
    print(dog_code)

    dog_list = make_dog_list(dog_code)
    dog_shelter= make_shelter_list(dog_code)

    return render_template('show_dog_list.html', dog_image=dog_list['사진파일'], dog_list=dog_list, dog_shelter=dog_shelter )

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

