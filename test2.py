#必要なモジュールのインポート
import sys
import collections


def check(logs,N):
    #pingが"-"の日時とアドレスを格納する配列
    #格納する値はkey=IP, value = [接続切れが始まった日時,接続切れの終わった日時,連続して接続切れした回数]
    disconnected_info = dict()
    #N回以上連続して接続切れしたアドレスと日時を格納する配列(print用)
    failure_info = dict()
    for log in logs:
        date = log[0]
        IP = log[1]
        ping = log[2]
        #print("日時 : {}, IP : {}, Ping : {}".format(date,IP,ping))

        #接続切れ
        if ping == "-":
            #初めて接続切れ
            if IP not in disconnected_info:
                disconnected_info.setdefault(IP, [date,0,1])
            #以前に接続切れを起こしている
            else :
                #前回は正常だったが、今回接続切れ(接続切れが始まった日時,接続切れの終わった日時の更新)
                if disconnected_info[IP][2] == 0:
                    disconnected_info[IP][0] = date
                    disconnected_info[IP][1] = 0
                #連続して接続切れしている(接続切れの終わった日時の更新)
                else:
                    disconnected_info[IP][1] = date
                #回数の更新
                disconnected_info[IP][2] += 1
            #print(IP)

        #現在は接続切れていないかつ前回確認した時までは接続切れしていた
        else:
            if IP in disconnected_info and disconnected_info[IP][2] != 0:
                disconnected_info[IP] = [0,0,0]

        #N回以上接続切れをおこした(故障した)サーバー情報の取得(IP,接続切れが始まった日時,接続切れの終わった日時)
        counter_list = {key:value for key,value in disconnected_info.items() if value[2] >= N }
        for IP, v in counter_list.items():
            #始めて故障と判定される
            if IP not in failure_info:
                failure_info.setdefault(IP, v)
            #すでに故障と判定されたことがある
            else:
                #3回以上故障(v[0]が配列)
                if isinstance(failure_info[IP][0],list):
                    #接続切れが始まった日時が同じ(現在も連続して接続切れしている)=接続切れの終わった日時のみ更新
                    if failure_info[IP][-1][0] == v[0]:
                        failure_info[IP][-1][1] = v[1]
                    #接続切れが始まった日時が異なる(新たに故障した)=故障した日時の追加
                    else:
                        value = failure_info.get(IP)+v
                        failure_info[IP] = value
                #接続切れが始まった日時が異なる(新たに故障した)=故障した日時の追加

                #故障2回目
                else:
                    #接続切れが始まった日時が同じ(現在も連続して接続切れしている)=接続切れの終わった日時のみ更新
                    if failure_info[IP][0] == v[0]:
                        failure_info[IP][1] = v[1]
                    #接続切れが始まった日時が異なる(新たに故障した)=故障した日時の追加
                    else:
                        value = [failure_info.get(IP),v]
                        failure_info[IP] = value


    for IP,values in failure_info.items():
        #複数回故障(values[0]が配列)
        if isinstance(values[0],list):
            for start_date,finish_date,count in values:
                print("サーバーアドレス:{}, 故障期間:{} - {}".format(IP,start_date,finish_date))
        #1回だけ故障
        else:
            start_date = values[0]
            finish_date = values[1]
            print("サーバーアドレス:{}, 故障期間:{} - {}".format(IP,start_date,finish_date))



#コマンドライン引数の格納(プログラム実行時に回数Nを指定)
args = sys.argv
N = int(args[1])

#ログを格納する配列
logs = []
#ログの読み出し
with open("log2.txt","r")as f:
    for i in f:
        logs.append(i.strip("\n").split(","))
check(logs,N)
