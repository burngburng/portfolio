import calendar, datetime
from quart import Quart, request, render_template, Response, url_for, redirect, jsonify
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# sqlalchemy.ext.asyncio : 비동기 데이터베이스 작업을 위한 SQLAlchemy 확장 모듈
from sqlalchemy.orm import sessionmaker, declarative_base
# sqlalchemy.orm : orm(object-relational mapping) 즉, 객체 관계 맵핑 기능 제공 
from sqlalchemy import Column, Integer, String, select
import asyncio, logging
# asyncio : 비동기 작업을 관리하기 위한 모듈
# logging : 로깅 기능 제공
from quart_cors import cors 
# quart_cors : cross-origin resource sharing(cors) 지원을 위한 모듈

# quart가 비동기 웹 프레임워크를 사용할 수 있기 때문임.
# 여기가 서버

# <로깅 설정> : 로깅 설정을 INFO 수준으로 설정하고 로거를 초기화함.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# <Quart 앱 초기화 및 cors 설정>
app = Quart(__name__, template_folder='templates')
app = cors(app, allow_origin = "*") #모든 도메인에서의 요청을 허용

# <데이터베이스 url 및 엔진 설정> 
DATABASE_URL = "sqlite+aiosqlite:///real_test.db"
# echo=True는 디버깅 목적으로 SQLAlchemy가 생성하는 모든 sql 구문을 콘솔(터미널)에 출력
engine = create_async_engine(DATABASE_URL, echo=True)
# SQLAlchemy에서 세션 만들기 : 2변수 - 원래는 동기적인 Session 클래스 사용하나, 비동기적인 작업을 수행하기 위한 AsyncSession 클래스를 사용함. 
# 비동기세션은 async with 문과 함께 사용할 수 있음.
# expire_on_commit = False : 커밋후에도 세션에 로드된 객체들이 만료되지 않음. 
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base 클래스 선언하여 모델 정의에 사용
Base = declarative_base()

# <데이터베이스 모델 정의>
class Me(Base) : # 데이터베이스 클래스 이름 : Me
  __tablename__ = "me" # 테이블 이름
  id = Column(Integer, primary_key=True, autoincrement=True)
  today = Column(String(12), index=True)
  today_dofw = Column(String(10), nullable= False) #선택한 날짜의 요일
  selected_date = Column(String(10), nullable= True) #이미지를 선택한 날짜
  emotion = Column(String(50), nullable =False)
  emotion_img = Column(String(50), nullable =False)
  title = Column(String(50), nullable=True)
  content = Column(String(500), nullable=True)

# <데이터베이스 초기화 함수>
async def init_db() :
  async with engine.begin() as conn: 
    # await conn.run_sync(Base.metadata.drop_all) 
    await conn.run_sync(Base.metadata.create_all)
# 기존 테이블 드랍하고, 새로 생성 - 다른 날짜면 드랍 x
    
# <데이터베이스 초기화 실행> 
asyncio.run(init_db())
    
now = datetime.datetime.now()
year = now.year
month = now.month
fixed_month = now.month #오늘 날짜의 해당 월
day = now.day 
fixed_day = now.day # 오늘 날짜의 해당 일

# 오늘 날짜, 요일 (한자리숫자일때는 자리수를 맞추기위해 0으로 채움.)
today_now = datetime.date(year, month, day)
today_now = str(today_now)

# 해당월 및 날짜 비교하기 위한 자릿수 맞추기
fixed_month = str(fixed_month)
if len(fixed_month) == 1 :
  fixed_month = '0'+str(fixed_month)
fixed_day = str(fixed_day)
if len(fixed_day) == 1 : 
  fixed_day = '0'+str(fixed_day)

def day_of_week(year, month, day) :  
  dates = datetime.date(year,month,day)
  dates = dates.weekday()
  date_list = ['(Mon)', '(Tue)', '(Wed)', '(Thu)', '(Fri)', '(Sat)', '(Sun)']

  return date_list[dates]

@app.route('/', methods = ['GET','POST'])
async def index() :   
  global year, month, day
  cal = calendar.HTMLCalendar(firstweekday=6) # 일요일 시작
 
  # 자바스크립트에서 post 형식으로 보낸 데이터 테스트 ***
  if request.method == 'POST' : 
    try : 
      data = await request.get_json() # 비동기여서 await 추가함.
      posted_year = data.get('year')
      posted_month = data.get('month')
      print(f'html 자바스크립트로부터 전달받은 년, 월: {posted_year}, {posted_month}') #year: 문자형, month: 정수형
      posted_year = int(posted_year)
      posted_month = int(posted_month)
      month_days = cal.monthdayscalendar(posted_year, posted_month)
    except Exception as e :
      print(f'Error process json date : {e}')
      return jsonify({'error': 'Invalid data'}), 400
    
    #특정 년,월의 일수 아는법 (_: 앞의 값을 안받아오겠단 뜻)
    _, last_day = calendar.monthrange(posted_year, posted_month)
    years = str(posted_year)
    months = str(posted_month).rjust(2,'0')
    days = str(last_day).rjust(2,'0') 
    day_list = [years, months, days] # 전달받은 ["년", "월", "일"]
    print('day_list 출력 : ', day_list)
    
    days_with_images = [{'day': day, 'dayofweek': day_of_week(int(years),int(months), day), 'img_url': None} for week in month_days for day in week if day!= 0] # 선택된 월의 매일 받아오기
    
    async with SessionLocal() as session : 
      result = await session.execute(select(Me)) #데이터베이스 클래스 모두 가져오기 
      every_me = result.scalars().all()
      result_list = [{'오늘 날짜' : each_me.today, '감정' : each_me.emotion, '이미지 주소': each_me.emotion_img, '제목': each_me.title, '내용': each_me.content, '선택된 날짜': each_me.selected_date} for each_me in every_me]
  
      for result in result_list :
        for result2 in days_with_images : 
          if len(str(result2['day'])) == 1 : 
            result2['day'] = '0'+str(result2['day']) #문자열로 만들기
          else : 
            result2['day'] = str(result2['day'])
          if (result['오늘 날짜'].split('-')[-3] == years) and (result['오늘 날짜'].split('-')[-2] == months) and (result['오늘 날짜'].split('-')[-1] == result2['day']) :
            result2['img_url'] = result['이미지 주소'] #달력에 이미지 띄워야하니까
  
    return await render_template('index.html', days_with_images = days_with_images, day_list=day_list, result_list=result_list, fixed_month = fixed_month, fixed_day = fixed_day)
  
  else : 
    print('처음 기본 화면입니다.')
    month_days = cal.monthdayscalendar(year, month)
    
    years = str(year)
    months = str(month).rjust(2,'0')
    days = str(day).rjust(2,'0') #여기서는 days가 오늘 날짜임. 
    day_list = [years, months, days] # 현재의 ["년", "월", "일"]
    print(day_list)
    
    days_with_images = [{'day': day, 'dayofweek': day_of_week(int(years),int(months), day), 'img_url': None} for week in month_days for day in week if day!= 0] # 매일 받아오기
    
    async with SessionLocal() as session : 
      result = await session.execute(select(Me)) #데이터베이스에서 클래스 Me에 해당하는 데이터 모두 가져오기 
      every_me = result.scalars().all() # 테이블의 각 행
      result_list = [{'오늘 날짜' : each_me.today, '감정' : each_me.emotion, '이미지 주소': each_me.emotion_img, '제목': each_me.title, '내용': each_me.content, '선택된 날짜': each_me.selected_date} for each_me in every_me]
  
      for result in result_list :
        for result2 in days_with_images : 
          if len(str(result2['day'])) == 1 : 
            result2['day'] = '0'+str(result2['day']) #문자열로 만들기
          else : 
            result2['day'] = str(result2['day'])
          if (result['오늘 날짜'].split('-')[-3] == years) and (result['오늘 날짜'].split('-')[-2] == months) and (result['오늘 날짜'].split('-')[-1] == result2['day']) :
            result2['img_url'] = result['이미지 주소']
    
    return await render_template('index.html', days_with_images = days_with_images, day_list=day_list, result_list=result_list, fixed_month=fixed_month, fixed_day=fixed_day)

@app.route('/add_emotion', methods=['GET', 'POST'])
# post 요청 받을 때 작동 
async def get_data() : 
  try : 
    data = await request.get_json()
    if data is None : 
      raise ValueError('No data provided') # raise 예외 발생 - 콘솔(터미너)창에 뜸
     
    logger.info(f"Recieved data : {data}")
    # 로그에 받은 데이터 기록. 디버깅이나 모니터링에 유용. 
    emotion = data.get('감정')
    # json 데이터에서 '감정'이라는 키 값을 가져옴! 
    logger.info(f"Recieved emotion: {emotion}")
    
    emotion_img = None 
    if emotion in {'기쁨, 즐거움'} :
      emotion_img = 'enjoy.png'
    elif emotion in {'행복함'} : 
      emotion_img = 'happiness.png'
    elif emotion in {'뿌듯함'} : 
      emotion_img = 'proud.png'
    elif emotion in {'안정적임'} : 
      emotion_img = 'feel_safe.png'
    elif emotion in {'불안함'} : 
      emotion_img = 'anxious.png'
    elif emotion in {'슬픔, 우울함'} : 
      emotion_img = 'blue.png'
    elif emotion in {'화남'} : 
      emotion_img = 'angry.png'
    elif emotion in {'억울함'} : 
      emotion_img = 'chagrin.png'
    
    if emotion_img is None : 
      logger.error(f'Invalid emotion : {emotion}')
      return Response('Invalid emotion', status=400)
    
    async with SessionLocal() as session :
      # SessionLocal로 부터 비동기 세션 생성.
      # 세션은 데이터베이스와의 작업 관리 
        stmt = select(Me).filter(Me.today==today_now)
        # Me 테이블에서 today 열이 현재 날짜 today_now 와 일치하는 레코드를 선택하는 쿼리 작성
        result = await session.execute(stmt)
        # 작성한 쿼리를 비동기적으로 실행하고 결과 기다림.
        existing_me = result.scalars().first()
        # 실행결과에서 첫번째 값 가져옴.
       
        dayofweek = day_of_week(year, month, day)
      
        if existing_me : 
          # 이미 존재하는 레코드가 있다면, 새로운 값 업데이트
            existing_me.today = today_now
            existing_me.today_dofw = dayofweek
            existing_me.emotion = emotion
            existing_me.emotion_img = 'emotion/'+emotion_img
        else : 
          # 존재하는 레코드가 없다면 정보 새로 추가하기
            me = Me(today=today_now, today_dofw=dayofweek, emotion=emotion, emotion_img='emotion/'+emotion_img)
            session.add(me)
            # 생성한 객체를 세션에 추가해서 데이터베이스에 저장할 준비. 
        await session.commit()
        # 세션의 변경 사항을 데이터베이스에 커밋하여 저장함.  
            
    logger.info('Emotion added successfully.')
    return Response("Emotion added", status=201)
  
  except Exception as e:
        logger.error(f'Error: {e}', exc_info = True)
        return Response(f"Error: {e}", status=500)
    
@app.route('/wr_diary', methods=['GET', 'POST']) 
async def wr_diary() : 
# 데이터받아서 디비에 넣어야 함.  
# 비동기데이터는 form = await request.form 이렇게 받아야함.(얘도 동기적으로 사용되서)
# 데이터 받아왔을 때, 비교 작업을 여기서하고 html에서는 그대로 띄우기 

  if request.method == 'POST' :
    form = await request.form 
    title = form['title']
    content = form['content']
    nowday = form['selectedDate'] # 선택된 날짜를 클릭하면 해당 다이어리를 읽어와야 하기 때문

    # 디비에 넣기
    async with SessionLocal() as session :
      stmt = select(Me).filter(Me.today==nowday)
      result = await session.execute(stmt)
      existing_me = result.scalars().first()
      
      if existing_me : 
          # 이미 존재하는 레코드가 있다면, 새로운 값 업데이트
          # 이미지를 이미 넣었기 때문에, 이미존재하는 레코드가 있다고 당연히 뜸
          existing_me.selected_date = nowday
          existing_me.title = title
          existing_me.content = content
          logger.info(f'recieved data : {existing_me.today} {existing_me.today_dofw} {existing_me.emotion}\
            {existing_me.emotion_img} {existing_me.title} {existing_me.content}')  
        
      await session.commit()
        # 세션의 변경 사항을 데이터베이스에 커밋하여 저장함.

    return redirect(url_for('index')) 
  

if __name__ == "__main__" : 
  app.run(debug=True)