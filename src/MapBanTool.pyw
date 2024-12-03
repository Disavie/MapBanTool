import tkinter as tk
from tkinter import ttk
from tkinter.ttk import * 
import tkinter.messagebox
import megachungus
import re
import pprint
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  NavigationToolbar2Tk) 
import json
import threading
import sv_ttk as stk
import ctypes

class MyWindow:
    default_y_spacing = 0
    checkbuttons = {}
    pos_helper = [0,default_y_spacing]
    map_pool = []
    data = {}
    TEMPRESULTS = {'picks':[],'drops':[]}
    lock = threading.Lock()
    THE_JUICE = {}


    ALLMAPS = [
            'Antarctic Peninsula','Busan','Ilios','Lijiang Tower','Nepal','Oasis','Samoa',
            'Blizzard World','Eichenwalde','Hollywood','King\'s Row','Midtown','Numbani','Paraiso',
            'Colosseo','Esperanca','New Queen Street','Runasapi',
            'New Junk City','Suravasa',
            'Hanaoka','Throne of Anubis',
            'Circuit Royal','Dorado','Havana','Junkertown','Rialto','Route 66','Shambali Monastery','Watchpoint Gibraltar'
            ]
    presets = [[
            'Busan','Nepal','Oasis','Samoa',
            'Eichenwalde','Hollywood','Midtown','Paraiso',
            'Colosseo','Esperanca','New Queen Street',
            'New Junk City','Suravasa',
            'Junkertown','Rialto','Route 66','Shambali Monastery'
            ],[
            'Busan','Lijiang Tower','Nepal','Samoa',
            'Blizzard World','Eichenwalde','King\'s Row','Paraiso',
            'Colosseo','New Queen Street','Runasapi',
            'New Junk City','Suravasa',
            'Circuit Royal','Dorado','Junkertown','Shambali Monastery'
            ],[
            'Busan','Ilios','Oasis',
            'Hollywood','King\'s Row','Midtown',
            'Colosseo','Esperanca','Runasapi',
            'New Junk City','Suravasa',
            'Hanaoka','Throne of Anubis',
            'Circuit Royal','Shambali Monastery','Watchpoint Gibraltar'
            ],]      

    def __init__(self):
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        self.root =tk.Tk()
        self.root.geometry('800x900')
        self.root.title('MapBanTool')
        #self.root.config(bg='default')
        stk.set_theme('dark')

  


        self.presetlabel = ttk.Label(self.root,text='Presets:')
        self.main_frame =ttk.Frame(
                                    self.root,
                                    height=60,
                                    width = 770,
                                    #bg = 'blue'    
                                    )
        self.main_frame.pack(padx=15,pady=(15,0))
        self.main_frame.pack_propagate(False)
        self.input_frame =ttk.Frame(self.main_frame)
        self.input_frame.pack(side='left')
        self.button = ttk.Button(self.input_frame,text='Run',command=self.enter_text)
        self.entry = ttk.Entry(self.input_frame,textvariable=input,font=('Calibri 10'))
        #self.label = ttk.Label(self.input_frame,text='Enter team link:')
        #self.label.grid(sticky='w',row=0,column=0)
        self.entry.config(width=60)
        self.add_placeholder(self.entry,"Enter team url")
        self.entry.pack(side='left')
        self.button.pack(side='left')

        self.use_cache =tk.BooleanVar(self.root,True)
        self.radiobutton_frame =ttk.Frame(self.main_frame)
        self.radiobutton_frame.pack(side='right')
        self.radiobutton1 = ttk.Radiobutton(self.radiobutton_frame,text='Get new data',variable=self.use_cache,value=False)
        self.radiobutton2 = ttk.Radiobutton(self.radiobutton_frame,text='Use data from save',variable=self.use_cache,value=True)
        self.radiobutton2.pack(anchor='w',side='top')
        self.radiobutton1.pack(anchor='w',side='top')


        self.map_selection_frame =ttk.Frame(
                                    self.root,
                                    height=250,
                                    width=770,
                                    relief='sunken',
                                    #bg = 'white',
                                    borderwidth=3)
        self.map_selection_frame.pack(padx=15,pady=(25,0))
        self.presets_frame =ttk.Frame(
                                self.root,
                                height=20,
                                width=770,
                                relief='raised',
                                #bg='lightgray',
                                #fill = 'x',
                                borderwidth=3
                                )
        self.presets_frame.pack(padx=15,pady=0)
        self.chart_frame =ttk.Frame(self.root,
                               width=770,
                               height=500,
                               relief='sunken',
                               borderwidth=3
                               )
        #self.chart_frame.pack_propagate(False)
        self.chart_frame.pack(padx=15,pady=20)


    
        self.clear_button =ttk.Button(self.presets_frame,text='None',command=self.clear_maps)
        self.all_maps =ttk.Button(self.presets_frame,text='All',command=lambda : self.set_map_pool(self.ALLMAPS))
        self.preset_map_pool1 =ttk.Button(self.presets_frame,text='FACEIT League S1',command=lambda : self.set_map_pool(self.presets[0]))
        self.preset_map_pool2 =ttk.Button(self.presets_frame,text='FACEIT League S2',command=lambda : self.set_map_pool(self.presets[1]))
        self.preset_map_pool3 =ttk.Button(self.presets_frame,text='FACEIT League S3',command=lambda : self.set_map_pool(self.presets[2]))

        for item in self.ALLMAPS:
            self.create_cbox(item)

        self.presetlabel.pack(side='left')
        self.clear_button.pack(side='left')
        self.all_maps.pack(side='left')
        self.preset_map_pool1.pack(side='left')
        self.preset_map_pool2.pack(side='left')
        self.preset_map_pool3.pack(side='left')


        self.root.mainloop()

    def printthing(self):
        print(self.use_cache.get())


    def create_cbox(self,item):
        if item == 'Blizzard World' or item == 'Colosseo' or item == 'New Junk City' or item == 'Circuit Royal':
            self.pos_helper[0]+=150
            self.pos_helper = [self.pos_helper[0],self.default_y_spacing]
        cbox =ttk.Checkbutton(
                self.map_selection_frame,
                text=item,
                command=lambda: self.toggle_check(cbox),
                )
        cbox.invoke()

        cbox.place(x=self.pos_helper[0],y=self.pos_helper[1])
        self.checkbuttons[item] = cbox
        self.pos_helper[1]+=30

    def enter_text(self):
        input = self.entry.get()
        if input == '//clear':
            megachungus.delete_all_files('cache/')
            return
        try:
            match = re.search(r'/teams/([a-f0-9-]+)(?:/|$)', input)
            url = match.group(1)
        except:
            ttk.messagebox.showinfo('Error',"Enter a valid team url")
            return

        if megachungus.check_valid(url):
            if not self.use_cache.get():
                megachungus.delete_file(f'cache/{url}.cache')
            data = self.chungusmain(url)
            self.embed_chart()
        else:
           ttk.messagebox.showinfo('Error',"Enter a valid team url")
    
    def toggle_check(self,button):
        text = button.cget('text')
        if text in self.map_pool:
            button.state(['!selected'])
            self.map_pool.remove(text)
        else:
            button.state(['selected'])
            self.map_pool.append(text)

    def embed_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = megachungus.plot_data(self.THE_JUICE)
        canvas = FigureCanvasTkAgg(fig,master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both',expand='TRUE')
        canvas.draw()

    def set_map_pool(self,list):
        self.map_pool = list
        for cbutton in self.checkbuttons:
            if cbutton in list:
                self.checkbuttons[cbutton].state(['selected'])
            else:
                self.checkbuttons[cbutton].state(['!selected'])

    def clear_maps(self):
        self.map_pool = []
        for cbutton in self.checkbuttons:
            self.checkbuttons[cbutton].state(['!selected'])

    def get_data_helper(self,match_id,team_id):
        temp =megachungus.get_data(match_id,team_id)
        with self.lock:
            self.TEMPRESULTS['picks']+=temp['picks']
            self.TEMPRESULTS['drops']+=temp['drops']

    def add_placeholder(self, entry, placeholder, color="gray"):
        """Add placeholder text to an Entry widget."""
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground="white")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground=color)


        entry.insert(0,placeholder)
        entry.config(foreground=color)
        entry.bind("<FocusIn>",on_focus_in)
        entry.bind("<FocusOut>",on_focus_out)


    def chungusmain(self,team_id):
        if megachungus.check_data_cache(team_id):
            f = open(f'cache/{team_id}.cache')
            data = json.load(f)
            f.close()
            output_dict = {}
            for map in data:
                if map in self.map_pool:
                    output_dict[map]=data[map]

            self.THE_JUICE = output_dict
            return



        rooms = megachungus.get_rooms(team_id)

        dict = {
            'picks':[],
            'drops':[]
            }
        threads = []

        for match_id in rooms:
            thread = threading.Thread(target=self.get_data_helper,args=(match_id,team_id))
            threads.append(thread)
            thread.start()        

        for thread in threads:
            thread.join()

        map_winrates = megachungus.count_map_wins(rooms,self.map_pool,team_id)
        ALL_MAPWINRATES = megachungus.count_map_wins(rooms,self.ALLMAPS,team_id)
        #counting picks
        count = 0
        output_dict = {}
        output_dict_allmaps = {}

        for map in self.ALLMAPS:
            if map in self.map_pool:
                output_dict[map] = {}
                output_dict[map]['picks'] = self.TEMPRESULTS['picks'].count(map)
                output_dict[map]['drops'] = self.TEMPRESULTS['drops'].count(map)
            output_dict_allmaps[map] = {}
            output_dict_allmaps[map]['picks'] = self.TEMPRESULTS['picks'].count(map)
            output_dict_allmaps[map]['drops'] = self.TEMPRESULTS['drops'].count(map)


        for map in ALL_MAPWINRATES:
            if map in self.map_pool:
                output_dict[map]['winrate']=map_winrates[map][0]
            output_dict_allmaps[map]['winrate'] = ALL_MAPWINRATES[map][0]


        megachungus.cache_as_dictionary(team_id,output_dict_allmaps)
        self.THE_JUICE = output_dict
        #return output_dict

GUI = MyWindow()
