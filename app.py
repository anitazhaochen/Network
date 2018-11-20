#coding:utf8
import re
from flask import request
from flask import Flask
import os
import time
from flask import render_template
from flask import redirect,url_for
from flask import session, abort
from functools import wraps
from flask import make_response
import uuid
from datetime import timedelta

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        uid = request.cookies.get('uid')
        if not uid in session:
            return redirect('/')
        return func(*args, **kwargs)
    return decorated_function

# python2 需要使用,否则页面会乱码报错
import sys
reload(sys)  # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.secret_key = '12345689'

@app.route('/')
def index():
    token = str(uuid.uuid1())
    if os.path.exists('password.txt'):
        resp = make_response(render_template('login.html', token=token))
    else:
        resp = make_response(render_template('index.html', token=token))
    cookie = request.cookies.get('uid')
    if cookie is None:
        resp.set_cookie('uid',token)
    return resp

@app.route('/VerifyLogin', methods=['POST'])
def verifyLogin():
    password = request.form['password']
    with open('password.txt') as f:
        oldpasword = f.read()
    if password == oldpasword:
        uid = request.cookies.get('uid')
        session[uid] = True
        res = "success"
    else:
        res = "failed"
    return res


@login_required
@app.route('/status',methods=['POST'])
def status():
    res = os.popen('ifconfig eth0 | grep "inet"').read()
    res = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", res)
    if len(res) > 1:
        s = "本地IP为："+res[0]+"子网掩码为: "+res[1]
    else:
        s = "error，请检查网卡名是否为 eth0"
    return s


@login_required
@app.route('/changepassword')
def changepassword():
    return render_template('changepassword.html',name="乔哥牛逼！！！！！！！！！！！！！")


@login_required
@app.route('/applylocal', methods=['POST'])
def setIP():
    ip = request.form['ip']
    netmask = request.form['netmask']
    gateway = request.form['gateway']

    lines = [
        'TYPE=Ethernet\n',
        'BOOTPROTO=static\n',
        'IPADDR='+ip+'\n',
        'NETMASK='+netmask+'\n',
        'NETWORK='+gateway+'\n',
        'DEFROUTE=yes'+'\n',
        'NAME=eth0'+'\n',
        'DEVICE=eth0'+'\n',
        'ONBOOT=yes'
        ]

    with open('/etc/sysconfig/network-scripts/ifcfg-eth0', 'w') as f:
        f.writelines(lines)
    time.sleep(1)
    os.popen('systemctl restart network')

    return "设置成功"


@login_required
@app.route('/applydhcp', methods=['POST'])
def dhcp():
    lines = ['TYPE=Ethernet\n',
        'BOOTPROTO=dhcp\n',
        'NM_CONTROLLED=yes\n',
        'DEFROUTE=yes\n',
        'NAME=eth0\n',
        'ONBOOT=yes\n'
        ]
    with open('/etc/sysconfig/network-scripts/ifcfg-eth0', 'w') as f:
        f.writelines(lines)
    time.sleep(1)
    os.popen('systemctl restart network')
    return "DHCP 服务设置成功"

@app.route('/createpassword', methods=['GET','POST'])
def createPassword():
    password1 = request.form['password1']
    password2 = request.form['password2']
    if password1 == password2 and not os.path.exists('password.txt'):
        with open('password.txt','w') as f:
            f.write(password1)
        #uuid = request.cookies.get('user')
        #u = user.User(uuid, True)
        session['login'] = True
        return 'success'
    else:
        return "Failed"


@app.route('/main')
@login_required
def setmain():
    return render_template('welcome.html')

if __name__ == "__main__":
    app.permanent_session_lifetime = timedelta(minutes=1)
    app.run(
        host='0.0.0.0',
        port=80,
        debug=True
    )


