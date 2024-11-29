# 매일 감정 체크기 
# 제목 : 나의 감정 다이어리 
# 행복 지수 감정을 좀 더 세분화해서 달력 불러와서 스티커 자동으로 붙이기

import tkinter as tk
from tkinter import messagebox
import requests, webbrowser

win = tk.Tk()

url = 'http://127.0.0.1:5000'

label1 = tk.Label(win, text='label1', width=60)
label1['text'] = '오늘 나만의 감정을 돌아보아요.'
label1.grid(row=0,column=0, padx=5, pady=5, columnspan=4)

label2 = tk.Label(win, text='')
label2.grid(row=1,column=0, padx=5, pady=5, columnspan=4)

def input_emotion(emotion) : 
  label2['text'] = emotion
  
  try: 
    # 직접 포스트하여 데이터베이스로 넘겨주기
    # 형식 : requests.post(url, json데이터)
    response = requests.post(url + '/add_emotion', json={'감정': emotion})
    response.raise_for_status() # 요청이 성공했는지 확인 
    
    if response.status_code == 201:
      if emotion in {text1, text2, text3, text4} :
        response = messagebox.askokcancel('알림', f'오늘 {emotion} 감정을 느끼셨군요.\n\
당신의 감정을 솔직하게 얘기해주어서 정말 좋아요!\n\
MyCalendar&Diary로 와서 같이 감정 일기를 작성해보아요!')

      elif emotion in {text5, text6, text7, text8} :
        response = messagebox.askokcancel('알림', f'오늘 {emotion} 감정을 느끼셨군요.\n\
정말 힘드셨겠어요..\n\
듣는 제가 다 서운하네요..\n\
오늘의 일은 저 멀리 넘겨버려요!\n\
또 하나의 계단과 발판이 될거에요.\n\
MyCalendar&Diary로 와서 같이 감정 일기를 작성해보아요!')
        
      # 127.0.0.1:5000 홈페이지로 이동
      if response : webbrowser.open(url)
       
    else :
      messagebox.showerror('오류', '서버에서 오류가 발생했습니다.')
  
  except Exception as e : 
    messagebox.showerror('오류', f'서버와의 통신중 오류가 발생했습니다. : {e}')    

text1 = '기쁨, 즐거움'      
button1 = tk.Button(win, width=15, text=text1,\
                    command = lambda : input_emotion(text1))
button1.grid(row=2,column=0, padx=5, pady=5)

text2 = '행복함'
button2 = tk.Button(win, width=15, text=text2,\
                    command = lambda : input_emotion(text2))
button2.grid(row=2,column=1, padx=5, pady=5)

text3 = '뿌듯함'
button3 = tk.Button(win, width=15, text=text3,\
                    command = lambda : input_emotion(text3))
button3.grid(row=2,column=2, padx=5, pady=5)

text4 = '안정적임'
button4 = tk.Button(win, width=15, text=text4,\
                    command = lambda : input_emotion(text4))
button4.grid(row=2,column=3, padx=5, pady=5)

text5 = '불안함'
button5 = tk.Button(win, width=15, text=text5,\
                    command = lambda : input_emotion(text5))
button5.grid(row=3,column=0, padx=5, pady=5)

text6 = '슬픔, 우울함'
button6 = tk.Button(win, width=15, text=text6,\
                    command = lambda : input_emotion(text6))
button6.grid(row=3,column=1, padx=5, pady=5)

text7 = '화남'
button7 = tk.Button(win, width=15, text=text7,\
                    command = lambda : input_emotion(text7))
button7.grid(row=3,column=2, padx=5, pady=5)

text8 = '억울함'
button8 = tk.Button(win, width=15, text=text8,\
                    command = lambda : input_emotion(text8))
button8.grid(row=3,column=3, padx=5, pady=5)

win.mainloop()