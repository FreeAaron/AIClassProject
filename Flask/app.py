import random
import unicodedata
from flask import Flask
from flask import request
from flask import redirect #直接定向，目前用不到
from flask import session
from flask import render_template
from matplotlib.pyplot import text
import mongomember as mon
import json

#靜態路由設定
app = Flask(__name__,
static_folder="homepage", #資料夾名稱 在裡面的都會對應至路徑
static_url_path="/",      #對應的網址路徑 "/"
template_folder= 'templates',
)
#key設定
app.secret_key = "the key"

#狀態設定
__islogin__ = False
#資料庫連線
mon.init()
#動態路由設定#
#內部網頁導向區#
#首頁
@app.route("/", methods=["GET"]) #GET方法 函式裝飾 設定路由 /對應的處理 
def index():
    # print("請求方法", request.method)
    # print("通訊協定",request.scheme)
    # print("主機名稱",request.host)
    # print("路徑",request.path)
    # print("網址",request.url)
    # print("瀏覽器與os",request.headers.get("user-agent"))
    # print("語言偏好",request.headers.get("accept-language"))
    # print("引薦網址",request.headers.get("referrer")) #從哪連過來
    if(__islogin__):
        nickname_ = session["nickname"]
        username_ = session["username","123456"]
        return render_template("index.html",name=nickname_,user=username_)

    lang = request.headers.get("accept-language") #瀏覽器的偏好語言
    if(lang.startswith("zh-TW")):
        print("語言偏好:繁中")
        return render_template("index.html",name="陌生人")
    else:
        print("語言偏好:英文or其他")
        return render_template("hello.html")
        #return redirect("hello")

#搜尋
@app.route("/search")
def search():
    searchinfo = request.args.get("searchinfo","")
    return render_template("search.html",searchinfo=searchinfo)
#填寫聯絡表單
@app.route("/contact", methods=["POST"])
def contact():
    nickname = request.form.get("nickname")
    useremail = request.form.get("email")
    usermessage = request.form.get("message")

    return render_template("contactok.html",name=nickname,email=useremail,msg=usermessage)

#註冊
@app.route("/register") 
def register():
    return render_template("register.html")
@app.route("/registerok", methods = ["POST"]) 
def registerok():
    username = request.form.get("username")
    nickname = request.form.get("nickname")
    useremail = request.form.get("email")
    password = request.form.get("password")
    likecategory = request.form.get("category")  #喜愛的類別 <= 這個之後再做
    sex = request.form["gender"]
    if sex==1:
        sex=0
    else:
        sex=1
    copy = request.form.get("copy") or""
    human= request.form.get("human") or""
    if human=="":
        return render_template("error.html",errormsg=errordict[4]) #不是人

    if mon.newamember(username,password,nickname,useremail,0,sex,1):
        return render_template("registerok.html")
    else:
        return render_template("error.html",errormsg=errordict[3]) #被註冊了
#登入
@app.route("/login") 
def login():
    return render_template("login.html")
@app.route("/loginok", methods = ["POST"]) 
def loginok():
    username = request.form.get("username")
    password = request.form.get("password")
    human= request.form.get("human") or""
    if human=="":
        return render_template("error.html",errormsg=errordict[4]) #不是人
#登入成功
    if mon.login(username,password):
        result = mon.getadatabyusername(username)
        session["nickname"]=result["nickname"]
        session["useremail"] = result["useremail"]
        session["username"] = result["username"]
        #r="/personal"
        #?username="+username
        return redirect("/personal")
    else:
        print("登入失敗")
        return render_template("error.html",errormsg=errordict[0]) #沒帳號
#個人頁
@app.route("/personal")
def personal():
    usermessage_ ="歡迎~"
    if "nickname" in session:
        nickname_=session["nickname"]
        username_=session["username"]
        useremail_=session["useremail"]
        return render_template("personal.html",name=nickname_,username=username_,email=useremail_,msg=usermessage_)
    else:
        #非法請求，直接導回首頁
        return redirect("/")
#錯誤頁面
errordict = {0:"沒這個帳號",1:"密碼錯了",2:"未知錯誤發生",3:"已經有此帳號存在，請勿重複註冊",4:"未勾選您不是機器人"}
@app.route("/error")
def error():
    print("產生錯誤")
    if errnum == None:
        errnum = request.args.get("errornumber",2)
    errmsg = errordict.get(errnum)
    if(errmsg==None): errmsg="這是一個還沒有被定義的錯誤"
    return render_template("error.html",errormsg = errmsg)
#登出
@app.route("/signout")
def signout():
    #移除session，安全措施
    if(session.__getitem__) != None:
        del session["nickname"]
        del session["username"]
        del session["useremail"]
    return redirect("/")

#暫時放置區
class TempArea:
    @app.route("/getid")
    def getid():
        id = request.args.get("id",1)
        numberid = int(id)
        print("使用者代號是: ",id)
        # temp =  random.randint(1,100)
        # return "隨機產生num: " + str(temp)

    userlist = ('chloe','aaron','simo','meistu','better')

    @app.route("/user/<name>") #名字參數
    def getUser(name):
        if name not in __name__.userlist:
            return render_template("register.html")
        return name



    

#啟動
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0") #啟動server

