# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import ssl
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

ssl._create_default_https_context = ssl._create_unverified_context

slack_token = "xoxb-508622352290-508838010325-h8lamriulWb8h6Ud1JculrGP"
slack_client_id = "508622352290.508636234658"
slack_client_secret = "97d78569feaf6b4f67517723ccbf577f"
slack_verification = "4C9MtbGt84e2CaHHNXvng90M"
sc = SlackClient(slack_token)

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):

    global lib
    
    incheon_lib_list = { 
        '계양':'gyeyang',
        '북구':'bukgu',
        '중앙':'jungang',
        '부평':'bupyeong',
        '화도진':'hwadojin',
        '주안':'juan'
    }
    
    print(text)
    
    crt_txt = str(text).split()
    
    if len(crt_txt) == 1:
        url_incheon = "https://lib.ice.go.kr/gyeyang/html.do?menu_idx=32"
        response_incheon = urllib.request.urlopen(url_incheon).read()

        soup_incheon = BeautifulSoup(response_incheon, 'html.parser')
        soup_incheon = soup_incheon.find("div",class_="body")
        soup_incheon = soup_incheon.find_all("div",class_="auto-scroll")[1]
        soup_incheon = soup_incheon.find("table",class_="center")
        soup_incheon = soup_incheon.find_all("tr")[1:]
        del soup_incheon[3]
        del soup_incheon[5]
        del soup_incheon[6]
        
        cnt = 1
        ans = ''
        incheon_list = []

        for soup_incheon_list in soup_incheon:
            ans = ''
            soup_incheon_list = soup_incheon_list.find_all("td")
            ans = (str(soup_incheon_list[0]) + str(soup_incheon_list[2]) + str(soup_incheon_list[3]) + str(soup_incheon_list[4]))
            ans = ans.replace('</td><td>',', ').replace('<td>','').replace('</td>','')
            incheon_list.append(str(cnt)+'. '+ans)
            cnt += 1
        incheon_list.append('정보가 필요한 도서관을 키워드로 입력해주세요. 예)계양')
        return '\n'.join(incheon_list)
    else:
        print("here~~")
        crt_txt = crt_txt[1]
        if crt_txt in incheon_lib_list:
            #return incheon_lib_list[lib]
            lib = crt_txt
            print(lib)
            return '1. 신작 도서\n2. 도서 대출 배스트\n3. 찾아 오시는 길'
        elif crt_txt == '1':
            new = []
            url_new = "https://lib.ice.go.kr/" + incheon_lib_list[lib] + "/intro/search/newBook/index.do?menu_idx=7"
            req_new = urllib.request.Request(url_new)
            sourcecode_new = urllib.request.urlopen(url_new).read()
            soup_new = BeautifulSoup(sourcecode_new, "html.parser")

            for each in soup_new.find_all("a",class_="name goDetail"):
                new.append(each.get_text())
            
            return lib + ' 도서관 신작 도서\n' + '\n'.join(new)
    
        elif crt_txt == '2':
            print(lib, crt_txt)
            best = []
            url = "https://lib.ice.go.kr/" + incheon_lib_list[lib] + "/intro/search/bestBook/index.do?menu_idx=17"
            req = urllib.request.Request(url)
            sourcecode = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(sourcecode, "html.parser")

            for each in soup.find_all("a",class_="name goDetail"):
                best.append(each.get_text())

            return lib + ' 도서관 도서 대출 배스트\n' + '\n'.join(best)
                
        elif crt_txt == '3':
            if lib == '계양' or lib == '화도진' or lib == '부평' or lib == '북구':
                route_s = []
                route_l = []
                route = []
                url_route = "https://lib.ice.go.kr/" + incheon_lib_list[lib] + "/html.do?menu_idx=108"
                sourcecode_route = urllib.request.urlopen(url_route).read()
                soup1_route = BeautifulSoup(sourcecode_route, "html.parser")
                soup2_route = BeautifulSoup(sourcecode_route, "html.parser")


                soup1_route = soup1_route.find("ul",class_="con")
                soup1_route = soup1_route.find_all("strong")
                for each in soup1_route:
                    route_s.append(each.get_text().strip())

                soup2_route = soup2_route.find("ul",class_="con")
                soup2_route = soup2_route.find_all("ul")
                for each in soup2_route:
                    route_l.append(each.get_text().strip().replace("\n",", "))



                for i in range(0,len(route_s)):
                        route.append(str(route_s[i]+' : '+route_l[i]).strip())
                
                return lib + ' 도서관 찾아 오시는 길\n' + '\n'.join(route)
                
            elif lib == '주안':
                route_s_juan = []
                route_l_juan = []
                route_juan = []
                route_m_juan = []
                url_route_juan = "https://lib.ice.go.kr/juan/html.do?menu_idx=108"
                sourcecode_route_juan = urllib.request.urlopen(url_route_juan).read()
                soup1_route_juan = BeautifulSoup(sourcecode_route_juan, "html.parser")
                soup2_route_juan = BeautifulSoup(sourcecode_route_juan, "html.parser")


                soup1_route_juan = soup1_route_juan.find("ul",class_="con")
                soup1_route_juan = soup1_route_juan.find_all("strong")
                for each in soup1_route_juan:
                    route_s_juan.append(each.get_text().strip().replace("\n\n",", "))

                soup2_route_juan = soup2_route_juan.find("ul",class_="con")
                soup2_route_juan = soup2_route_juan.find_all("ul")
                for each in soup2_route_juan:
                    route_l_juan.append(each.get_text().strip().replace("\n\n",",").replace("\n",", "))



                for i in route_l_juan:
                    if i not in route_s_juan:
                        route_m_juan.append(i)
                #for i in range(0,len(route_m)):
                 #       route.append(str(route_s[i]+' : '+route_m[i]).strip())

                route_juan.append(route_s_juan[0]+" : "+route_l_juan[0])
                route_juan.append(route_s_juan[1]+" : 8, 33 (석바위 시장역 하차)")
                route_juan.append(route_s_juan[2]+" : 523-1(주안도서관 앞 하차), 540, 566(석바위 시장역 하차)")
                route_juan.append(route_s_juan[3]+" : "+route_l_juan[1])
                
                return lib + ' 도서관 찾아 오시는 길\n' + '\n'.join(route_juan)
                
            elif lib == '중앙':
                route_s_jungang = []
                route_l_jungang = []
                route_jungang = []

                url_route_jungang = "https://lib.ice.go.kr/jungang/html.do?menu_idx=108"
                sourcecode_route_jungang = urllib.request.urlopen(url_route_jungang).read()
                soup1_route_jungang = BeautifulSoup(sourcecode_route_jungang, "html.parser")
                soup2_route_jungang = BeautifulSoup(sourcecode_route_jungang, "html.parser")


                soup1_route_jungang = soup1_route_jungang.find("ul",class_="con")
                soup1_route_jungang = soup1_route_jungang.find_all("strong")
                for each in soup1_route_jungang:
                    route_s_jungang.append(each.get_text().strip().replace("\n\n",", "))

                soup2_route_jungang = soup2_route_jungang.find("ul",class_="con")
                soup2_route_jungang = soup2_route_jungang.find_all("ul")
                for each in soup2_route_jungang:
                    route_l_jungang.append(each.get_text().strip().replace("\n\n",",").replace("\n"," / ").replace("\r","").replace("           "," ").replace(":","-"))

                #for i in range(0,len(route_m)):
                 #       route.append(str(route_s[i]+' : '+route_m[i]).strip())
                route_jungang.append(route_s_jungang[0]+" : "+route_l_jungang[0])
                route_jungang.append(route_s_jungang[1]+" : "+route_l_jungang[1])
                
                return lib + ' 도서관 찾아 오시는 길\n' + '\n'.join(route_jungang)
    


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)
