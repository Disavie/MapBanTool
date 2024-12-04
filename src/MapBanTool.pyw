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
import time

class MyWindow:
    default_y_spacing = 0
    checkbuttons = {}
    pos_helper = [0,default_y_spacing]
    map_pool = []
    lock = threading.Lock()
    toolbars = []


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
    options = [
                'All Time',
                '1 Week Ago',
                '1 Month Ago',
                '3 Months Ago',
                '6 Months Ago',
                ]    

    def __init__(self):
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
        self.root =tk.Tk()
        self.root.geometry('800x1000')
        self.root.title('MapBanTool')
        self.root.iconbitmap('dumbdog.ico')
        #self.root.config(bg='default')
        stk.set_theme('dark')

  



        self.main_frame =ttk.Frame(
                                    self.root,
                                    height=100,
                                    width = 770,
                                    #bg = 'blue'    
                                    )
        self.main_frame.pack(padx=15,pady=(15,0))
        self.main_frame.pack_propagate(False)
        self.input_frame =ttk.Frame(self.main_frame)
        self.input_frame.pack(anchor='n',side='left')
        self.button = ttk.Button(self.input_frame,text='Run',command=self.enter_text)
        self.entry = ttk.Entry(self.input_frame,textvariable=input,font=('Calibri 10'))
        
        self.entry.config(width=60)
        self.add_placeholder(self.entry,"Enter team url")
        self.entry.pack(side='left')
        self.button.pack(side='left')

        self.use_cache =tk.BooleanVar(self.root,True)
        self.radiobutton_frame =ttk.Frame(self.main_frame)
        self.radiobutton_frame.pack(side='right')
        self.radiobutton1 = ttk.Radiobutton(self.radiobutton_frame,text='Collect new data',variable=self.use_cache,value=False,
                                            command = lambda : self.selectRange.configure(state='enabled'))
        self.radiobutton2 = ttk.Radiobutton(self.radiobutton_frame,text='Use data from save',variable=self.use_cache,value=True,
                                            command = lambda : self.selectRange.configure(state='disabled'))
        self.strv = tk.StringVar()
        #self.strv.set(self.options[0])
        self.selectRange = ttk.OptionMenu(self.radiobutton_frame,self.strv,self.options[0],*self.options)
        self.selectRange.configure(state='disabled')
        self.radiobutton2.pack(anchor='w',side='top')
        self.radiobutton1.pack(anchor='w',side='top')
        self.selectRange.pack(anchor='e',side='top',pady=5,fill='x')
        self.presets_frame =ttk.Frame(
                                self.root,
                                height=40,
                                width=770,
                                )
        self.presets_frame.pack(padx=15,pady=0)
        self.presets_frame.pack_propagate(False)

        self.map_selection_frame =ttk.Frame(
                                    self.root,
                                    height=250,
                                    width=770,
                                    relief='sunken',
                                    #bg = 'white',
                                    borderwidth=3)
        self.map_selection_frame.pack(padx=15,pady=(0,5))
        self.chart_frame =ttk.Frame(self.root,
                               width=770,
                               height=500,
                               relief='sunken',
                               borderwidth=3
                               )
        #self.chart_frame.pack_propagate(False)
        self.chart_frame.pack(padx=15,pady=(5,0))


    
        self.clear_button =ttk.Button(self.presets_frame,text='None',command=self.clear_maps)
        self.all_maps =ttk.Button(self.presets_frame,text='All',command=lambda : self.set_map_pool(self.ALLMAPS))
        self.preset_map_pool1 =ttk.Button(self.presets_frame,text='FACEIT League S1',command=lambda : self.set_map_pool(self.presets[0]))
        self.preset_map_pool2 =ttk.Button(self.presets_frame,text='FACEIT League S2',command=lambda : self.set_map_pool(self.presets[1]))
        self.preset_map_pool3 =ttk.Button(self.presets_frame,text='FACEIT League S3',command=lambda : self.set_map_pool(self.presets[2]))

        for item in self.ALLMAPS:
            self.create_cbox(item)
        self.clear_button.pack(side='left')
        self.all_maps.pack(side='left')
        self.preset_map_pool1.pack(side='left')
        self.preset_map_pool2.pack(side='left')
        self.preset_map_pool3.pack(side='left')


        self.root.mainloop()




    def determine_time_requirement(self):
        now = time.time()
        option = self.strv.get()
        if option == self.options[0]:
            return 0
        elif option == self.options[1]:
            return now-604800 #needs to have have a time greater than this value
        elif option == self.options[2]:
            return now-2629743
        elif option == self.options[3]:
            return now-(3*2629743)
        elif option == self.options[4]:
            return now-(6*2629743)
        

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
            tk.messagebox.showinfo('Error',"Enter a valid team url")
            return

        if megachungus.check_valid(url):
            time = 0
            if not self.use_cache.get():
                megachungus.delete_file(f'cache/{url}.cache')
                time = self.determine_time_requirement()
            data = megachungus.main(url,self.map_pool,time)
            self.embed_chart(data)
        else:
           tk.messagebox.showinfo('Error',"Enter a valid team url")
    
    def toggle_check(self,button):
        text = button.cget('text')
        if text in self.map_pool:
            button.state(['!selected'])
            self.map_pool.remove(text)
        else:
            button.state(['selected'])
            self.map_pool.append(text)

    def embed_chart(self,data):
        for t in self.toolbars:
            t.destroy()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        fig = megachungus.plot_data(data)
        axes = fig.axes


        canvas = FigureCanvasTkAgg(fig,master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both')

        toolbar = NavigationToolbar2Tk(canvas,self.root,pack_toolbar=False)
        canvas.draw()
        toolbar.update()
        toolbar.pack(pady=5,fill='x',anchor='w',padx=15)
        self.toolbars.append(toolbar)



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



GUI = MyWindow()
