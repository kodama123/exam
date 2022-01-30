#必要なモジュールのインポート
import sys
import collections
import ipaddress
import numpy as np

################################test2からの追加項目################################
def create_network(IP):
    Segment = ipaddress.IPv4Network(IP, strict=False)
    #ネットワーク範囲に入るIPアドレスを取得
    Hosts = Segment.hosts()
    #IPアドレスのサブネットマスクを取得
    subnetMask = Segment.netmask
    IPs = dict()
    #初期状態は全てのIPアドレスで接続成功(True)
    for IP in Hosts:
        IPs.setdefault(IP,True)
    network.setdefault(subnetMask,IPs)
    #print("network : ",network)
    counter = 0
    #for key,vs in network.items():
        #for v_key,v in vs.items():
            #print("key : {}, v_key : {}, value : {}".format(key,v_key,v))
        #print(counter)
    #print(a)


def check_subnet(failure_info):
    #故障したIPアドレスの取得
    failure_IPs = failure_info.keys()
    check_IP_connected = []
    #network内の故障したIPアドレスの接続状態をFalseにする
    for failure_IP in failure_IPs:
        Segment = ipaddress.IPv4Network(failure_IP, strict=False)
        #IPアドレスのサブネットマスクを取得
        subnetMask = Segment.netmask
        #print("network[subnet] : ",network[subnet])
        network[subnetMask][failure_IP.split("/")[0]] = False

    #スイッチが壊れているネットマスクの格納
    failure_netMask = []
    #ネットワーク内にTrue(接続成功)があるか確認
    for key, values in network.items():
        subnet_value = values.values()
        #Trueがある = 接続成功したIPアドレスが存在するためスキップ
        if True in subnet_value:
            continue
        failure_netMask.append(key)
    return failure_netMask

#スイッチの故障時期の表示
def check_time(failure_network):
    #各ネットワークで確かめ
    for netMask,values in failure_network.items():
        #開始時間と終了時間の取得
        IP,v = values.items()
        v = np.array(v, dtype=float)
        #故障開始日時を取得してソートしたときの1番速い日時の取得
        start_date = np.sort(v[:,0])[0]
        #故障開始日時を取得してソートしたときの1番遅い日時の取得
        finish_date = np.sort(v[:,1])[-1]
        print("ネットマスク : {}, 故障期間:{} - {}".format(netMask,start_date,finish_date))

#################################################################################



def check(logs,N):
    global network
    #各IPアドレスのサブネットマスクをkeyとするIPアドレスと故障状況を格納する配列
    #ネットワーク({subnetMask1:{IPアドレス:故障状況(True or False)},...,subnetMaskM:{IPアドレス:故障状況(True or False)}})
    network = dict()
    #pingが"-"の日時とアドレスを格納する配列
    #格納する値はkey=IP, value = [接続切れが始まった日時,接続切れの終わった日時,連続して接続切れした回数]
    disconnected_info = dict()
    #N回以上連続して接続切れしたアドレスと日時を格納する配列(print用)
    failure_info = dict()

    for log in logs:
        date = log[0]
        IP = log[1]
        ping = log[2]
        netmusk = ipaddress.IPv4Network(IP, strict=False).netmask
        if netmusk not in network:
            create_network(IP)
        #Create_segment(IP)
        #print(a)

        #print("IP:{}, subnet:{}".format(IP,subnet))
        #print(a)
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

    ################################test2からの追加項目################################
    #壊れたスイッチがあるかどうか確認
    failure_netMask = check_subnet(failure_info)
    #壊れたスイッチがあるとき
    if len(failure_netMask) >0:
        #各ネットワーク範囲での故障開始時間と終了時間を格納
        failure_network = dict()
        for netMask in failure_netMask:
            failure_IPs_info = dict()
            for IP,values in failure_info.items():
                IP_netmusk = ipaddress.IPv4Network(IP, strict=False).netmask
                #同一ネットワーク内のIPアドレス,故障開始時間と終了時間を格納
                if IP_netmusk == netMask:
                    failure_IPs_info.setdefault(IP,values)

            failure_network(netMask,failure_IPs_info)
        check_time(failure_network)
    else:
        print("故障したスイッチは無し")
    #################################################################################



#コマンドライン引数の格納(プログラム実行時に回数Nを指定)
args = sys.argv
N = int(args[1])

#ログを格納する配列
logs = []
#ログの読み出し
with open("log.txt","r")as f:
    for i in f:
        logs.append(i.strip("\n").split(","))
check(logs,N)
