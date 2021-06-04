from website.config import *
import requests
import json


headers = {
    "Authorization" : "Bearer "+api_key,
    "Content-Type": "application/json",
    "Accept" : "application/json"
}

class Dashboard:
    dash = {}

    def __init__(self, uid = None, dname="Dashboard"):
        #pesquisar dname da db de dashboards, obter uid 
        if uid == None: #if dnam not in db
            with open('./website/json_files/dashboard.json') as f:
                self.dash = json.load(f)
                self.dash['dashboard']['title'] = dname
        else: #get uid associa ao dname
            url = server + "/api/dashboards/uid/" + uid
            tmp = requests.get(url=url, headers=headers, verify=False)
            self.dash['dashboard'] = tmp.json()['dashboard']
            print("\n\n\n"+str(self.dash)+"\n\n\n")


    def get_panels(self):
        panels = []
        for p in self.dash['dashboard']['panels']:
            panels.append(p['title'])
        return panels


    def get_targets_selected(self, pname):
        targets = []
        for p in self.dash['dashboard']['panels']:
            if pname == p['title']:
                for t in p['targets']:
                    targets.append(t[''])#refid, atribuir ids aos targets
        return targets


    def del_dash(uid):
        #dada o dname obter o uid associado
        url = server + "/api/dashboards/uid/" + uid
        req = requests.delete(url=url, headers=headers, verify=False)
        if req.status_code == 200 : return 1
        return 0


    def dash_set_time(self, time_from, time_to):
        time = {}
        time['from'] = time_from
        time['to'] = time_to
        self.dash['dashboard']['time'] = time
        return 1


    def send_dash(self):
        url = server + "/api/dashboards/db"
        r = requests.post(url=url, headers=headers, data=json.dumps(self.dash), verify=False)
        if(r.status_code == 200):
            return r.json()['uid']
        return 0



    def add_panel(self, pname, ptype):
        with open('./website/json_files/'+ptype+'.json') as f:
            p = json.load(f)
        p['title'] = pname
        npnl = len(self.dash['dashboard']['panels'])
        p['gridPos']['y'] = 8*(npnl//2)
        #Resolução do erro
        p['id'] = len(self.get_panels())+1
        if npnl % 2 != 0:
            p['gridPos']['x'] = 12
        self.dash['dashboard']['panels'].append(p)
        return 1


    def del_panel(self, pname):
        self.dash['dashboard']['panels'].remove()

        return 1


    def add_query(self, pname, ptype, query_list):
        targets = []

        for q in query_list:
            with open('./website/json_files/target.json') as f:
                target = json.load(f)
            target['query'] = q
            targets.append(target)
        
        pexist = False
        for p in self.dash['dashboard']['panels']:
            if p['title'] == pname :
                pexist = True
                break
        if not pexist:
            self.add_panel(pname, ptype)

        for p in self.dash['dashboard']['panels']:
            if p['title'] == pname :
                p['targets'] = targets
                break

        return 1










'''
dashboard.id – id = None to create a new dashboard.
dashboard.uid – Optional unique identifier when creating a dashboard. uid = None will generate a new uid.
folderId – The id of the folder to save the dashboard in.
overwrite – Set to True if you want to overwrite existing dashboard with newer version, same dashboard title in folder or same dashboard uid.
refresh - Set the dashboard refresh interval.
'''

