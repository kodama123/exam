def check(logs):
    #pingが"-"の日時とアドレスを格納する配列
    checked_date_list = []
    checked_ip_list = []
    for log in logs:
        date = log[0]
        IP = log[1]
        ping = log[2]
        #print("日時 : {}, IP : {}, Ping : {}".format(date,IP,ping))
        #故障したかつ前回確認した時は正常だった
        if ping == "-" and not IP in checked_ip_list:
            checked_ip_list.append(IP)
            checked_date_list.append(date)
            #print(IP)
        #現在は故障していないかつ前回確認した時までは故障していた
        elif ping != "-" and IP in checked_ip_list:
            #現在確認しているサーバーが故障した日時
            checked_date = checked_date_list[checked_ip_list.index(IP)]
            print("サーバーアドレス:{}, 故障期間:{} - {}".format(IP,checked_date,date))
            #故障履歴の削除
            checked_date_list.pop(checked_ip_list.index(IP))
            checked_ip_list.remove(IP)
    #故障履歴が残っている = まだ故障しているため表示
    if len(checked_ip_list) != 0:
        for ip in checked_ip_list:
            print("サーバーアドレス:{}, 現在も故障中".format(ip))






#ログを格納する配列
logs = []
#ログの読み出し
with open("log.txt","r")as f:
    for i in f:
        logs.append(i.strip("\n").split(","))
check(logs)
