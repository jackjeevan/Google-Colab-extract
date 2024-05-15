import os
import re
import time
import uuid
import urllib.request
import json
import psutil
import shutil
from zipfile import ZipFile
from io import BytesIO
from sys import exit as exx
from subprocess import Popen, PIPE
from IPython.display import clear_output, HTML, display

HOME = os.path.expanduser("~")
CWD = os.getcwd()
tokens = {}

class Ngrok:

    def __init__(self, TOKEN=None, USE_FREE_TOKEN=True, 
                 service=[['Service1', 80, 'tcp'], ['Service2', 8080, 'tcp']], 
                 region='us', 
                 dBug=[f"{HOME}/.ngrok2/ngrok.yml", 4040]):
        self.region = region
        self.configPath, self.dport = dBug
        self.TOKEN = TOKEN
        self.USE_FREE_TOKEN = USE_FREE_TOKEN
        self.service = service
        if USE_FREE_TOKEN:
            self.sdict = {}
            for i, sn in enumerate(service):
                tempcP = f'{HOME}/.ngrok2/{sn[0]}.yml'
                # Port, Protocol, config path
                self.sdict[sn[0]] = [self.dport + i, sn[2], tempcP]

    def nameport(self, TOKEN, AUTO):
        if AUTO:
            try:
                return tokens.popitem()[1]
            except KeyError:
                return "Invalid Token"
        elif not TOKEN:
            if 'your' not in tokens.keys():
                print(r"Copy authtoken from https://dashboard.ngrok.com/auth")
                __temp = input("Token: ")
                tokens['your'] = __temp.split(':')[1]
                USR_Api = "your"
            else:
                USR_Api = "your"
        else:
            USR_Api = "mind"
            tokens["mind"] = TOKEN
        return tokens[USR_Api]

    def ngrok_config(self, token, Gport, configPath, region, service):
        data = f"""
        region: {region}
        update: false
        update_channel: stable
        web_addr: localhost:{Gport}
        tunnels:
        """
        if not self.USE_FREE_TOKEN:
            data = f"authtoken: {token}\n" + data

        tunnels = ""
        for S in service:
            Sn, Sp, SpC = S
            tunnels += f"""
            {Sn}:
                addr: {Sp}
                proto: {SpC}
                inspect: false
            """
        data += tunnels
        os.makedirs(f'{HOME}/.ngrok2/', exist_ok=True)
        with open(configPath, "w+") as configFile:
            configFile.write(data)
        return True

    def startWebUi(self, token, dport, nServer, region, btc, configPath,
                   displayB, service, v):
        installNgrok()
        if v:
            clear_output()
            loadingAn(name="lds")
            textAn("Starting ngrok ...", ty='twg')
        if self.USE_FREE_TOKEN:
            for sn in service:
                self.ngrok_config(
                    token,
                    self.sdict[nServer][0],
                    self.sdict[nServer][2],
                    region,
                    service)
                if sn[0] == nServer:
                    runSh(f"ngrok {sn[2]} -config={self.sdict[nServer][2]} {sn[1]} &", shell=True)
        else:
            self.ngrok_config(token, dport, configPath, region, service)
            runSh(f"ngrok start --config {configPath} --all &", shell=True)
        time.sleep(3)
        try:
            if self.USE_FREE_TOKEN:
                dport = self.sdict[nServer][0]
                nServer = 'command_line'
            host = urllib.request.urlopen(f"http://localhost:{dport}/api/tunnels")
            host = json.loads(host.read())['tunnels']
            for h in host:
                if h['name'] == nServer:
                    host = h['public_url'][8:]
                    break
        except urllib.error.URLError:
            if v:
                clear_output()
                loadingAn(name="lds")
                textAn("Ngrok Token is in use! Trying token again ...", ty='twg')
            time.sleep(2)
            return True

        data = {"url": f"https://{host}"}
        if displayB:
            displayUrl(data, btc)
        return data

    def start(self, nServer, btc='b', displayB=True, v=True):
        try:
            nServerbk = nServer
            if self.USE_FREE_TOKEN:
                dport = self.sdict[nServer][0]
                nServer = 'command_line'
            else:
                dport = self.dport
            host = urllib.request.urlopen(f"http://localhost:{dport}/api/tunnels")
            host = json.loads(host.read())['tunnels']
            for h in host:
                if h['name'] == nServer:
                    host = h['public_url'][8:]
                    data = {"url": f"https://{host}"}
                    if displayB:
                        displayUrl(data, btc)
                    return data

            raise Exception('No tunnels found')
        except urllib.error.URLError:
            for _ in range(10):
                if v:
                    clear_output()
                    loadingAn(name='lds')
                dati = self.startWebUi(
                    self.nameport(self.TOKEN, self.USE_FREE_TOKEN) if not self.USE_FREE_TOKEN else {},
                    self.dport,
                    nServerbk,
                    self.region,
                    btc,
                    self.configPath,
                    displayB,
                    self.service,
                    v
                )
                if dati == True:
                    continue
                return dati

def checkAvailable(path_="", userPath=False):
    from os import path as _p

    if path_ == "":
        return False
    else:
        return (
            _p.exists(path_)
            if not userPath
            else _p.exists(f"/usr/local/sessionSettings/{path_}")
        )

def accessSettingFile(file="", setting={}, v=True):
    fullPath = f"/usr/local/sessionSettings/{file}"
    try:
        if not len(setting):
            if not checkAvailable(fullPath):
                if v:
                    print(f"File unavailable: {fullPath}.")
                exx()
            with open(fullPath) as jsonObj:
                return json.load(jsonObj)
        else:
            with open(fullPath, "w+") as outfile:
                json.dump(setting, outfile)
    except Exception as e:
        if v:
            print(f"Error accessing the file: {fullPath}. {e}")

def displayUrl(data, btc='b', pNamU='Public URL: ', EcUrl=None, ExUrl=None, cls=True):
    if cls:
        clear_output()
    showTxT = f'{pNamU}{data["url"]}'
    showUrL = data["url"] + EcUrl if EcUrl else ExUrl if ExUrl else data["url"]
    button_colors = {
        'b': ('hsla(210, 50%, 85%, 1)', 'hsl(210, 80%, 42%)', 'hsla(210, 40%, 52%, .4)'),
        'g': ('hsla(110, 50%, 85%, 1)', 'hsla(110, 86%, 56%, 1)', 'hsla(110, 40%, 52%, .4)'),
        'r': ('hsla(10, 50%, 85%, 1)', 'hsla(10, 86%, 56%, 1)', 'hsla(10, 40%, 52%, .4)')
    }
    bttxt, btcolor, btshado = button_colors[btc]

    display(HTML(f'''
    <style>
        @import url('https://fonts.googleapis.com/css?family=Source+Code+Pro:200,900');
        :root {{
            --text-color: {bttxt};
            --shadow-color: {btshado};
            --btn-color: {btcolor};
            --bg-color: #141218;
        }}
        * {{
            box-sizing: border-box;
        }}
        button {{
            position: relative;
            padding: 10px 20px;
            border: none;
            background: none;
            cursor: pointer;
            font-family: "Source Code Pro";
            font-weight: 900;
            font-size: 100%;
            color: var(--text-color);
            background-color: var(--btn-color);
            box-shadow: var(--shadow-color) 2px 2px 22px;
            border-radius: 4px;
            z-index: 0;
            overflow: hidden;
        }}
        button:focus {{
            outline-color: transparent;
            box-shadow: var(--btn-color) 2px 2px 22px;
        }}
        .right::after, button::after {{
            content: var(--content);
            display: block;
            position: absolute;
            white-space: nowrap;
            padding: 40px 40px;
            pointer-events: none;
        }}
        button::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 300%;
            height: 300%;
            transition: all 0.3s;
            background-repeat: no-repeat;
            background-size: 25% 25%, 25% 25%;
            background-position: top left, bottom right;
            z-index: -1;
            transition: all 0.5s;
        }}
        button:hover::before {{
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 4px;
        }}
        button {{
            --content: "{showTxT}";
        }}
    </style>
    <div>
        <a href="{showUrL}" target="_blank" style="text-decoration:none;">
            <button>{showTxT}</button>
        </a>
    </div>
    '''))

def runSh(*args, shell=True):
    cmds = [i for i in args]
    try:
        runProcess = Popen(cmds, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=shell)
        output, error = runProcess.communicate()
        return output, error
    except Exception as e:
        return False, e

def terminateOldNgrok(v=True):
    while True:
        for proc in psutil.process_iter():
            if 'ngrok' in proc.name():
                try:
                    proc.terminate()
                except Exception as e:
                    if v:
                        print(e)
                    continue
        if not any('ngrok' in p.name() for p in psutil.process_iter()):
            break

def installNgrok(v=True):
    ngrokPath = f"{HOME}/.ngrok2/ngrok"
    if not os.path.exists(ngrokPath):
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
        if v:
            print("Downloading ngrok...")
        response = urllib.request.urlopen(url)
        with ZipFile(BytesIO(response.read())) as zfile:
            zfile.extractall(f"{HOME}/.ngrok2/")
        os.system(f"chmod +x {HOME}/.ngrok2/ngrok")
