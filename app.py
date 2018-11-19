import re
from flask import request
from flask import Flask
import os
import time
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    #res = os.popen('ifconfig').read()
    #return render_template("index.html")
    return render_template("login1.html")

#@app.route('/login', methods=['POST'])
@app.route('/VerifyLogin', methods=['POST'])
def login():
    username = request.form['loginid']
    password = request.form['userpassword']
    if username == 'admin' and password=='admin':
        res = "登录成功"
    else:
        res = "密码错误"
    return render_template('welcome.html', name='巴音乔哥')

@app.route('/status',methods=['POST'])
def status():
    res = os.popen('ifconfig en0 | grep "inet"').read()
    res = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", res)
    if len(res) > 1:
        s = "本地IP为："+res[0]+"子网掩码为: "+res[1]
    else:
        s = "error，请检查网卡名是否为 eth0"
    return s


@app.route('/changepassword')
def changepassword():
    return render_template('changepassword.html',name="乔哥牛逼！！！！！！！！！！！！！")


@app.route('/applylocal', methods=['POST'])
def setIP():
    ip = request.form['ip']
    netmask = request.form['netmask']
    #gateway = request.form['gateway']

    lines = [
        'TYPE=Ethernet\n',
        'BOOTPROTO=static\n',
        'IPADDR='+ip+'\n',
        'NETMASK='+netmask+'\n',
        'NETWORK='+gateway+'\n',
        'DEFROUTE=yes'+'\n',
        'NAME=enp0s3'+'\n',
        'DEVICE=enp0s3'+'\n',
        'ONBOOT=yes'
        ]

    with open('/etc/sysconfig/network-scripts/ifcfg-enp0s3') as f:
        f.writelines(lines)

    os.popen('ifconfig eth0 down')
    time.sleep(1)
    os.popen('ifconfig eth0 up')
    return "设置成功"


@app.route('/applydhcp', methods=['POST'])
def dhcp():
    lines = ['TYPE=Ethernet\n',
        'BOOTPROTO=dhcp\n',
        'NM_CONTROLLED=yes\n',
        'DEFROUTE=yes\n',
        'NAME=eth0\n',
        'ONBOOT=yes\n'
        ]
    with open('/etc/sysconfig/network-scripts/ifcfg-enp0s3') as f:
        f.writelines(lines)
    os.popen('ifconfig eth0 down')
    time.sleep(1)
    os.popen('ifconfig eth0 up')
    return "DHCP 服务设置成功"


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=7777,
        debug=True
    )