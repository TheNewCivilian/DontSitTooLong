import htmlPy
from tinydb import TinyDB, Query
import os
import json

if os.path.dirname(__file__) != '':
    os.chdir(os.path.dirname(__file__))
class BackEnd(htmlPy.Object):

    def __init__(self, app):
        super(BackEnd, self).__init__()
        self.app = app
        self.show_page("home","HOME")

    @htmlPy.Slot(str)
    def debug_to_console(self,mes):
        print str(mes)

    @htmlPy.Slot(result=str)
    def get_log_data(self):
        log = TinyDB('../database/log.json')
        db = TinyDB('../database/db.json')
        query = Query()
        log_entries = log.all()
        log_result = []
        for item in log_entries:
            task_data = db.search(query.tid == item["tid"])
            timestamp = {"year":item["year"],"month":item["month"],"day":item["day"],"hour":item["hour"],"minute":item["minute"]}
            for item in task_data:
                log_result.append({"time":timestamp,"arms":item['arms'],"legs":item['legs'],"stomach":item['stomach'],"chest":item['chest']}) #berarbeiten
        return json.dumps(log_result, separators=(',',':'))


    @htmlPy.Slot(int,result=str)
    def get_entries_by_tid(self,tid):
        db = TinyDB('../database/db.json')
        query = Query()
        db_entries = db.search(query.tid == tid)
        result = []
        for item in db_entries:
            result.append({"tid":item['tid'],"name":item['name'],"disc":item['disc'],"arms":item['arms'],"legs":item['legs'],"stomach":item['stomach'],"chest":item['chest']})
        return json.dumps(result, separators=(',',':'))

    @htmlPy.Slot(str,str)
    def show_page(self,pagename,headline):
        db = TinyDB('../database/db.json')
        query = Query()
        self.app.template = ("./index.html", {
        "page":"pages/"+pagename+".page",
        "active_tasks": db.search((query.tid >=0) & (query.active == 1)),
        "archive_tasks": db.search((query.tid >=0) & (query.active == 0)),
        "all_tasks": db.search((query.tid >=0)),
        "headline":headline
        })

    @htmlPy.Slot(str, result=int)
    def add_table_entry(self, json_data):
        db = TinyDB('../database/db.json')
        form_data = json.loads(json_data)
        if (int(form_data['tid']) == 0):
            db.insert({'tid': len(db.all())+1, 'name': form_data['name'],'disc':form_data['disc'], 'active': 1, 'arms':form_data['arms'], 'legs':form_data['legs'], 'stomach':form_data['stomach'], 'chest':form_data['chest']})
        else:
            tid = form_data['tid']
            query = Query()
            db.update({'name': form_data['name'],'disc':form_data['disc'], 'arms':form_data['arms'], 'legs':form_data['legs'], 'stomach':form_data['stomach'], 'chest':form_data['chest']}, query.tid == int(tid))
        return 0

    @htmlPy.Slot(str, result=int)
    def remove_table_entry(self, json_data):
        db = TinyDB('../database/db.json')
        update_query = Query()
        form_data = json.loads(json_data)
        entry_id = int(form_data['tid'])
        db.update({'active': 0}, update_query.tid == entry_id)
        self.show_page('tasks',"Active Tasks");
        return 0

    @htmlPy.Slot(str, result=int)
    def activate_table_entry(self, json_data):
        db = TinyDB('../database/db.json')
        update_query = Query()
        form_data = json.loads(json_data)
        entry_id = int(form_data['tid'])
        db.update({'active': 1}, update_query.tid == entry_id)
        self.show_page('archive',"Archive");
        return 0

    @htmlPy.Slot()
    def pause_training(self):
        db = TinyDB('../database/db.json')
        update_query = Query()
        db.update({'active': 1}, update_query.tid == -1)
        return 0

    @htmlPy.Slot(result=int)
    def get_pause_status(self):
        db = TinyDB('../database/db.json')
        query = Query()
        pauseelement = db.search(query.tid == -1)
        for item in pauseelement:
            return item["active"]


    @htmlPy.Slot()
    def resume_training(self):
        db = TinyDB('../database/db.json')
        update_query = Query()
        db.update({'active': 0}, update_query.tid == -1)
        return 0
