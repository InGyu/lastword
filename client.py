import socket

HOST = 'localhost'
PORT = 23525

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(
        """
        SELECT 모델을 이용한 끝말잇기
        api : 국립국어원 한국어기초사전
        항복 또는 종료는 -1, 강제종료는 ctr+c
        첫단어는 컴퓨터입니다.
        """
    )
    while True:
        n = input("단어 : ")
        s.sendall(n.encode('utf-8'))
        data = s.recv(1024).decode('utf-8')
        print(f'서버응답 : {data}')
        if data == '당신이 이겼습니다!' or data == '-1':
            print('종료되었습니다.')
            break