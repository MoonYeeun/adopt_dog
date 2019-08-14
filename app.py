# flask 모듈 임포트
from flask import Flask, render_template, request
# 세션 기능을 위한 모듈
from flask import session
# DB 파일 연결
import db
import urllib.request
from urllib.parse import urlencode, quote_plus, unquote
import xml.etree.ElementTree as ET
import folium
import pprint
import requests

decode_key = unquote('WF9v2HhErnR0ovu%2FVJJX8InWINAh4ZaZrMPvZLpcK%2FkXGR3V9%2F3kAQyfKuilCn7LqLPIZlnh97Ed3TxFoLkbrA%3D%3D')  # decode 해줍니다.

# flask 객체 생성
app = Flask(__name__)

# 세션을 위한 비밀키 설정
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
    queryParams = '?' + urlencode({quote_plus('ServiceKey'): decode_key,
                                   quote_plus('upkind'): 417000,
                                   quote_plus('upr_cd'): 6110000,
                                   quote_plus('pageNo'): 1})
    req = urllib.request
    body = req.urlopen(url + queryParams)
    req.get_method = lambda: 'GET'
    response_body = body.read()
    result = response_body.decode('utf-8')
    print(result)
    tree = ET.ElementTree(ET.fromstring(result))
    return tree.getroot()

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
    note = adopt_dog_api()

    for i in note.iter("item"):
        if (sort in i.findtext("kindCd")) & (neutral in i.findtext("neuterYn")) & (sex in i.findtext("sexCd")):
            print(i.findtext('careAddr'))
            dog_data[i.findtext('desertionNo')] = i.findtext('careAddr')

    map = folium.Map(location=[37.5103, 126.982], zoom_start=12,titles='Stamen Toner')


    for i in dog_data:
        geoData = getGeoData(dog_data.get(i))
        print(i)
        #folium.Marker(geoData, popup=i, icon=folium.Icon(color='red')).add_to(map)
        folium.Marker(geoData, popup=folium.Popup('<a href="http://127.0.0.1:5000/choose_dog?code={{i}}" target="_self">HOME</a>',show=True), icon=folium.Icon(color='red')).add_to(map)

    return map._repr_html_()



# # login.html 페이지에서 버튼을 눌렀을때 이동하는 라우터
# # @app.route('/', methods=['GET'])
# # @app.route('/index', methods=['GET'])
# # def index():
# #     # 세션이 있는지 없는지에 따라 html 분기
# #     if not session.get('logged_in'):
# #         return render_template('login.html')
# #     else:
# #         return render_template('logout.html')
#
# # login.html 페이지에서 버튼을 눌렀을때 이동하는 라우터
# @app.route('/login', methods=['POST'])
# def login():
#     # login.html의 폼필드의 데이값 확인
#     userId = request.form['userId']
#     password = request.form['password']
#     print(userId, password)
#     # DB의 레코드를 리스트로 저장
#     member_list = db.get_member_list()
#
#     # 레코드의 아이디와 패스워드의 아이디가 있으면 True
#     # 없으면 False 역할을 하는 변수
#     userIdCheck = userPwdCheck = False
#
#     # DB의 전체 레코드 값과 비교
#     # len(member_list) => DB의 전체 레코드수
#     # DB의 아이디값과 같으면 True
#     for i in range(0, len(member_list)):
#         if userId in member_list[i]['user_id']:
#             userIdCheck = True
#             print('userIdCheck = > ' , userIdCheck)
#             # 패스워드 비교를 위해서 idx 변수에 저장
#             idx = i
#             break
#         else:
#             continue
#
#     # 폼필드의 패스워드랑 DB의 패스워드랑 비교
#     if member_list[idx]['user_password'] == password:
#         userPwdCheck = True
#         print('userPwdCheck => ', userPwdCheck)
#
#     # 아이디랑 비밀번호가 모두 맞다면(True) 세션 설정
#     if userIdCheck and userPwdCheck:
#         session['logged_in'] = True
#
#     # 첫페이지로 이동해서 세션 판단
#     return index()
#
# # 로그인 상태에서 로그아웃 하이퍼링크 클릭시 적용되는 라우터
# @app.route('/logout')
# def logout():
#     session.clear()
#     return index()
#
# # 상단 Join 메뉴 클릭시 회원가입페이지로 이동하는 라우터
# @app.route('/join')
# def join():
#     return render_template('join.html')
#
# # 회원가입폼에서 텍스트필드를 입력받은 후
# # DB에 추가하는 라우터
# @app.route('/joinPro', methods=['post'])
# def joinPro():
#     userId = request.form['userId']
#     password = request.form['password']
#     print(userId, password)
#     db.addDb_member(userId, password)
#     # return 'success'
#     # 회원가입 완료 페이지로 이동
#     return render_template('joinResult.html')
#
#
# # 앱 실행  --> 마지막 위치 유지
# # 웹주소와 포트 지정
app.run(host='127.0.0.1', port=5000, debug=True)

