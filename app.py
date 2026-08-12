#!/usr/bin/env python3
import http.server, socketserver, json, os, uuid, urllib.parse
from datetime import datetime
PORT=5000
DIR=os.path.dirname(os.path.abspath(__file__))
USERS_FILE=os.path.join(DIR,"users.json")
def load_users():
    if os.path.exists(USERS_FILE):
        try: return json.load(open(USERS_FILE,encoding="utf-8"))
        except: return {}
    return {}
def save_users(u):
    json.dump(u, open(USERS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=DIR,**k)
    def json(self,obj):
        b=json.dumps(obj,ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",len(b))
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        path=urllib.parse.urlparse(self.path).path
        routes={"/":"/index.html","/auth":"/auth.html","/register":"/register.html","/profile":"/profile.html"}
        if path in routes: self.path=routes[path]
        return super().do_GET()
    def do_POST(self):
        path=urllib.parse.urlparse(self.path).path
        length=int(self.headers.get("Content-Length",0))
        body=self.rfile.read(length).decode() if length else "{}"
        try: data=json.loads(body)
        except: data={}
        users=load_users()
        if path=="/api/register":
            u=(data.get("username") or "").strip(); p=(data.get("phone") or "").strip(); pw=(data.get("password") or "").strip()
            if not u or not pw: return self.json({"ok":False,"msg":"Thiếu thông tin"})
            if u in users: return self.json({"ok":False,"msg":"Tài khoản đã tồn tại"})
            token=str(uuid.uuid4())
            users[u]={"password":pw,"phone":p,"token":token,"created":datetime.now().isoformat()}
            save_users(users)
            return self.json({"ok":True,"token":token})
        if path=="/api/login":
            u=(data.get("username") or "").strip(); pw=(data.get("password") or "").strip()
            if u not in users or users[u].get("password")!=pw: return self.json({"ok":False,"msg":"Sai thông tin"})
            token=str(uuid.uuid4()); users[u]["token"]=token; save_users(users)
            return self.json({"ok":True,"token":token})
        return self.json({"ok":False,"msg":"Not found"})
if __name__=="__main__":
    with socketserver.TCPServer(("",PORT),Handler) as h:
        print("Shop running at http://localhost:5000")
        h.serve_forever()
