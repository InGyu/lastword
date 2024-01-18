import socket  # 소켓
import requests  # 오픈 api 사용하기 위해
import select  # select 모델
import random  # 랜덤함수

HOST = ''  # 아무것도 없으면 로컬호스트
PORT = 23525
apikey = "E5B6411F075C4F2D41D1C5B37575E1DB"  # https://krdict.korean.go.kr/에서 발급받은 api 키


def midReturn(val, s, e):  # 추출
    if s in val:
        val = val[val.find(s) + len(s):]
        if e in val: val = val[:val.find(e)]
    return val


def midReturn_all(val, s, e):  # xml 추출
    if s in val:
        tmp = val.split(s)
        val = []
        for i in range(0, len(tmp)):
            if e in tmp[i]: val.append(tmp[i][:tmp[i].find(e)])
    else:
        val = []
    return val


def findword(query, conn):  # 다음 단어 찾기
    url = 'https://krdict.korean.go.kr/api/search?key=' + apikey + '&part=word&pos=1&q=' + query
    response = requests.get(url)
    ans = []  # 단어리스트

    words = midReturn_all(response.text, '<item>', '</item>')
    for w in words:
        if not (w in client_dict[conn]['history']):
            word = midReturn(w, '<word>', '</word>')  # 단어
            pos = midReturn(w, '<pos>', '</pos>')  # 품사
            if len(word) > 1 and pos == '명사' and not word in client_dict[conn]['history']:
                ans.append(word)
    if len(ans) > 0:
        return random.choice(ans)
    else:
        return ''


def checkword(query, conn):  # 단어 체크
    url = 'https://krdict.korean.go.kr/api/search?key=' + apikey + '&part=word&pos=1&q=' + query
    response = requests.get(url)
    words = midReturn_all(response.text, '<item>', '</item>')
    for w in words:
        if not (w in client_dict[conn]['history']):
            word = midReturn(w, '<word>', '</word>')
            pos = midReturn(w, '<pos>', '</pos>')
            if len(word) > 1 and pos == '명사' and not word in client_dict[conn]['history']:
                return word
    return ''


client_dict = {}  # 클라이언트를 구분하기 위한 딕셔너리

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # 소켓 통신 시작
    s.bind((HOST, PORT))
    s.listen()
    print('서버가 시작되었습니다.')

    readsocks = [s]
    client_answer = ''
    server_word = '컴퓨터'
    while True:
        readables, writeables, excpetions = select.select(readsocks, [], [])
        for sock in readables:  # 읽기셋
            if sock == s:  # 신규 클라이언트
                newsock, addr = s.accept()
                print(f'클라이언트가 접속했습니다:{addr} 첫단어는 컴퓨터')
                client_dict[newsock] = {'addr': addr, 'server_word': server_word, 'history': []}
                readsocks.append(newsock)

            else:  # 이미 접속한 클라이언트의 요청
                conn = sock

                client_answer = conn.recv(1024).decode('utf-8')
                print(f'{client_dict[conn]['addr']}의 데이터:{client_answer}')

                if client_answer == "-1":  # 게임 동작
                    conn.sendall("-1".encode('utf-8'))
                    print(f"{addr} 클라이언트 종료")
                    conn.close()
                    readsocks.remove(conn)
                    del client_dict[conn]
                elif not checkword(client_answer, conn):
                    conn.sendall('단어가 아닙니다.'.encode('utf-8'))
                elif len(client_answer) == 1:
                    conn.sendall('적어도 두 글자가 되어야 합니다'.encode('utf-8'))
                elif client_answer in client_dict[conn]['history']:
                    conn.sendall('이미 입력한 단어입니다')
                elif client_answer.isspace():
                    conn.sendall("곰백이있음".encode('utf-8'))
                elif client_answer[0] != client_dict[conn]['server_word'][-1]:
                    conn.sendall("단어끝과 보내준 단어앞이 같지 않음".encode('utf-8'))
                else:
                    client_dict[conn]['server_word'] = midReturn(client_answer, '<word>', '</word>')
                    ansdef = midReturn(client_answer, '<definition>', '</definition>')
                    client_dict[conn]['history'].append(client_answer)
                    client_answer = client_answer[len(client_answer) - 1]
                    client_dict[conn]['server_word'] = findword(client_answer + '*', conn)
                    if client_dict[conn]['server_word'] == '':
                        conn.sendall('당신이 이겼습니다!'.encode('utf-8'))
                        print(f"{addr} 클라이언트 종료")
                        conn.close()
                        readsocks.remove(conn)
                    else:
                        print(f"{client_dict[conn]['addr']}다음 단어 > {client_dict[conn]['server_word']}")
                        conn.sendall(f'다음 단어는 > {client_dict[conn]['server_word']}'.encode('utf-8'))
