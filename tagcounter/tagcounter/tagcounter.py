#region Imports
import os
import sys
import yaml
import time
import click
import logging
import datetime
import urllib.request
from tkinter import *
import tkinter as tknr
from tkinter import ttk
from tkinter import Entry
from datetime import datetime
from tkinter import messagebox
from tkinter import scrolledtext
from html.parser import HTMLParser
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
#endregion Imports

#region Common
logger = logging.getLogger("tagcounter")
logger.setLevel(logging.DEBUG)
fHandler = logging.FileHandler('tagcounter.log')
fHandler.setLevel(logging.DEBUG)
conHandler = logging.StreamHandler()
conHandler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fHandler.setFormatter(formatter)
conHandler.setFormatter(formatter)
logger.addHandler(fHandler)
logger.addHandler(conHandler)

tagCount = 0
tagsList = dict()
hlink = ''
Base = declarative_base()
#endregion Common

#region Classes
class Application(tknr.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('780x520')
        self.master.title("Specific site html tag counter")
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.run = tknr.Button(self, text="Run", command=self.run_clicked, font=('Helvetica', '11'), 
                                                                                 bg='#03ceeb', fg='#ffffff')
        self.run.grid(row=3, column=2, ipadx=10, ipady=3, sticky=W+E+N+S, pady=10, padx=10)

        self.quit = tknr.Button(self, text="Quit", command=self.master.destroy, font=('Helvetica', '11'), 
                                                                                 bg='#cef532')
        self.quit.grid(row=4, column=2, ipadx=10, ipady=3, sticky=W+E+N+S, pady=10, padx=10)
        
        self.info = tknr.Button(self, text="Info", command=self.info_clicked, font=('Helvetica', '11'))
        self.info.grid(row=4, column=1, ipadx=10, ipady=3, sticky=W+E+N+S, pady=10, padx=10)

        self.get_db = tknr.Button(self, text="DB query", command=self.get_result_from_db_clicked, font=('Helvetica', '11'))
        self.get_db.grid(row=3, column=0, ipadx=10, ipady=3, sticky=W+E+N+S, pady=10, padx=40)

        self.clear_db = tknr.Button(self, text="Clear DB", command=self.clear_db_clicked, font=('Helvetica', '11'), 
                                                                                           bg='#e82133', fg='#ffffff')
        self.clear_db.grid(row=4, column=0,  ipadx=10, ipady=3, sticky=W+E+N+S, pady=10, padx=40)

        self.copy = tknr.Button(self, text="Copy", command=self.copy_clicked, font=('Helvetica', '11'))
        self.copy.grid(row=3, column=1, ipadx=10, ipady=3, sticky=W+E+N+S, pady=10, padx=10)

        self.combo = ttk.Combobox(self, values=["", "google.com", "hub.docker.com", "learn.chef.io", "github.com"], state='readonly')
        #self.combo = ttk.Combobox(self, values=sites_aliases(), state='readonly')
        self.combo.set('Choose a site to get a list of tags:')
        self.combo.grid(row=0, column=1, sticky=W+E, ipadx=10, ipady=3, columnspan=2)

        self.entry_hlink = Entry(self, state=DISABLED)
        self.entry_hlink.grid(row=1, column=1, sticky=W+E, ipadx=10, ipady=3, columnspan=2)

        self.scr_txt_result = scrolledtext.ScrolledText(self, height=15)
        self.scr_txt_result.insert(INSERT, "Here will be shown results:")
        self.scr_txt_result.grid(row=2, column=0, columnspan=3, sticky=W+E+N+S, pady=10, padx=40)

        self.selected = IntVar()

        self.radio_button_combo = Radiobutton(self, text="Choose a site name from list", value=1, variable=self.selected, 
                                                    command=self.radio_button_combo_clicked, font=('Helvetica', '11'))
        self.radio_button_combo.select()
        self.radio_button_combo.grid(row=0, column=0, sticky=W, pady=20, padx=40)
        self.radio_button_combo.focus()
        self.radio_button_text = Radiobutton(self, text="Type manually a site name", value=2, variable=self.selected, 
                                                    command=self.radio_button_text_clicked, font=('Helvetica', '11'))
        self.radio_button_text.grid(row=1, column=0, sticky=W, pady=10, padx=40)

    def run_clicked(self):
        global tagCount
        global hlink
        global tagsList
        try:
            self.scr_txt_result.delete(1.0, END)
            self.scr_txt_result.insert(INSERT, "The results:\n")
            
            if self.selected.get() == 1:
                hlink = self.combo.get()
            elif self.selected.get() == 2:
                hlink = self.entry_hlink.get()
                hlink = sites_aliases(hlink)
            hlink = link_checker(hlink)
            GuiTagCounter = TagCounter()
            contents = GuiTagCounter.read_url_content(hlink)
            GuiTagCounter.feed(contents)
            totalTags = GuiTagCounter.print_tags(tagsList)
            self.scr_txt_result.insert(INSERT, f"{totalTags},\n{tagCount} tags have been encountered in total on {hlink}")
            logger.info(f"{hlink} : {tagCount} tags were encountered")
            push_tags_to_db(hlink, datetime_mark(), tagCount, totalTags)
            tagCount = 0
            tagsList = dict()
        except Exception as ex:
            exception_reporter(ex)

    def get_result_from_db_clicked(self):
        global hlink
        try:
            self.scr_txt_result.delete(1.0, END)       
            if self.selected.get() == 1:
                hlink = self.combo.get()
            elif self.selected.get() == 2:
                hlink = self.entry_hlink.get()
                hlink = sites_aliases(hlink)
            queried_result = pull_tags_from_db(hlink)
            self.scr_txt_result.insert(INSERT, queried_result)
            logger.info(f"{hlink} data was requested from database")
        except Exception as ex:
            exception_reporter(ex)
    
    def clear_db_clicked(self):
        self.scr_txt_result.delete(1.0, END)
        clear_tags_from_db()
        self.scr_txt_result.insert(INSERT, "Database has been truncated!")
        logger.info("Database has been truncated")

    def radio_button_combo_clicked(self):
        self.entry_hlink['state'] = DISABLED
        self.combo['state'] = 'readonly'

    def radio_button_text_clicked(self):
        self.entry_hlink['state'] = NORMAL
        self.combo['state'] = DISABLED
    
    def copy_clicked(self):
        try:
            to_copy = self.scr_txt_result.get(1.0, END)
            self.scr_txt_result.clipboard_clear()
            self.scr_txt_result.clipboard_append(to_copy)
        except Exception as co:
            exception_reporter(co)
    
    def info_clicked(self):
        try:
            alis = sites_aliases()
            messagebox.showinfo("Info", f"A valid format of a site address:\n[http(s)://]<site_name>.<domain>,\n\nacceptable aliases for sites:\n{alis}")
        except Exception as cp:
            exception_reporter(cp)

class TagCounter(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global tagCount
        global tagsList
        tagCount += 1
        if tag not in tagsList:
            tagsList.setdefault(tag, 1)
        else:
            tagsList[tag] += 1    

    def print_tags(self, tagsToPrint):
        rTags = str(tagsToPrint).replace("{", "").replace("}","").replace(":", " =").replace("'", "")
        return rTags

    def read_url_content(self, url):
        try:
            with urllib.request.urlopen(url, timeout=10) as urlRead: 
                urlContent = urlRead.read()
                return str(urlContent)
        except Exception as e:
            exception_reporter(e, url)

class TagsData(Base):
    __tablename__ = 'tagsdata'
    id = Column(Integer, primary_key=True)
    site_name = Column(String(50), nullable=False)
    check_date = Column(String(50), nullable=False)
    tags_count = Column(Integer, nullable=False)
    tags_data = Column(String(1000), nullable=False)
    
#endregion Classes

#region DB
engine = create_engine('sqlite:///tags_storage.db') # , echo=True
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def push_tags_to_db(site, date, tagsc, data):
    try:
        tag_to_add = TagsData(site_name=site, check_date=date, tags_count=tagsc, tags_data=data)
        session.add(tag_to_add)
        session.commit()
    except Exception as ep:
        exception_reporter(ep)

def pull_tags_from_db(site):
    try:
        site = link_checker(site)
        query_list = list()
        qry = session.query(TagsData).filter(site==TagsData.site_name)
        for i in qry: 
            query_list.append(f"{i.id} --- {i.site_name} --- {i.check_date} --- {i.tags_count} --- {i.tags_data}")
        if not query_list:
                out = f"There is no data for {site} in database!"
                return out
        query_text = str(query_list[-1]).replace("[", "").replace("]", "").replace("'", "") #.replace(",", "")
        query_result = f"Queried INFO:\n{query_text}"
        return query_result
    except Exception as exxx:
        exception_reporter(exxx)

def clear_tags_from_db():
    try:
        session.execute(f"DELETE FROM {TagsData.__tablename__}")
        session.commit()
    except Exception as exxx:
        exception_reporter(exxx)
#endregion DB

#region Functions
@click.command()
@click.option("-g", "--get", help="Collect html-tags data on the specified site")
@click.option("-v", "--view", help="View html-tags data from the specified site")
@click.option("-c", "--clear", is_flag=True, help="Clear/truncate all html-tags data from database (without deleting a table)")
def command_line (get, view, clear):
    try:
        if type(get) == str:
            ComTagCounter = TagCounter()
            get = sites_aliases(get)
            get = link_checker(get)
            contents = ComTagCounter.read_url_content(get)
            ComTagCounter.feed(contents)
            totalTags = ComTagCounter.print_tags(tagsList)
            click.echo(f"\n{totalTags},\n\n{tagCount} tags have been encountered in total on {get}\n")
            logger.info(f"{get} : {tagCount} tags were encountered")
            push_tags_to_db(get, datetime_mark(), tagCount, totalTags)
        elif type(view) == str:
            view = sites_aliases(view)
            pull = pull_tags_from_db(view)
            print(pull)
            logger.info(f"{view} data was requested from database")
        elif clear == True:
            clear_tags_from_db()
            logger.info("Database has been truncated")
            print("Database has been truncated!")
    except Exception as exx:
        exception_reporter(exx)

def exception_reporter(*args):
    if (len(sys.argv) - 1) == 0:
        messagebox.showerror("Exception info", f"Exception info: {args}")
        logger.error(f"Exception info: {args}")
    else:
        print(f"Exception info: {args}")
        logger.error(f"Exception info: {args}")

def datetime_mark():
    now = datetime.now()
    datemark = f'{now.strftime("%Y-%m-%d %H:%M:%S")}'
    return datemark

def link_checker(link):
    if link == '' or link == "Choose a site to get a list of tags:" or link == " " or link == None:
            link = "http://www.python.org/"
            if (len(sys.argv) - 1) == 0:
                messagebox.showinfo("Counting tags", "This time @www.python.org@ is used, "  
                    "next time, please, choose from combobox or type manually something different.")
            else: 
                print("This time @www.python.org@ is used, "  
                      "next time, please, choose from combobox or type manually something different.")
    if "http://" not in link: 
        if "https://" not in link:
            link = f"http://{link}"
    return link

def sites_aliases(*args):
    try:
        with open("sites_aliases.yaml") as yfile:
            data = yaml.full_load(yfile)
            if args:
                for key, value in data.items():
                    if args[0] == key:
                        return value
                return args[0]
            else:
                aliases = yaml.safe_dump(data)
                return aliases
    except Exception as f:
        exception_reporter(f)
#endregion Functions

def main():
    if (len(sys.argv) - 1) == 0:
        root = Tk()
        app = Application(master=root)
        app.mainloop()
    else:
        command_line()

if __name__ == "__main__": main()