import tkinter as tk
import tkinter.messagebox
import megachungus
import re
import pprint
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  NavigationToolbar2Tk) 

class MyWindow:

    checkbuttons = {}
    pos_helper = [0,25]
    map_pool = []
    data = {}
    ALLMAPS = [
            'Antarctic Peninsula','Busan','Ilios','Lijiang Tower','Nepal','Oasis','Samoa',
            'Blizzard World','Eichenwalde','Hollywood','King\'s Row','Midtown','Numbani','Paraiso',
            'Colosseo','Esperanca','New Queen Street','Runasapi',
            'New Junk City','Suravasa',
            'Hanaoka','Throne of Anubis',
            'Circuit Royal','Dorado','Havana','Junkertown','Rialto','Route 66','Shambali Monastery','Watchpoint Gibraltar'
            ]
    presets = [[
            'Busan','Ilios','Oasis',
            'Hollywood','King\'s Row','Midtown',
            'Colosseo','Esperanca','Runasapi',
            'New Junk City','Suravasa',
            'Hanaoka','Throne of Anubis',
            'Circuit Royal','Shambali Monastery','Watchpoint Gibraltar'
            ],]      

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('700x800')
        self.root.title('MapBanTool')

  


        self.label = tk.Label(self.root,text='Enter link to team:')
        self.label2 = tk.Label(self.root,text='unchecked')
        self.presetlabel = tk.Label(self.root,text='Presets:')
        self.entry = tk.Entry(self.root,textvariable=input)
        chart_frame = tk.Frame(self.root)
        chart_frame.place(x=0,y=280)
        self.button = tk.Button(self.root,text='go',command=lambda: self.enter_text(chart_frame))
        self.clear_button = tk.Button(self.root,text='None',command=self.clear_maps)
        self.all_maps = tk.Button(self.root,text='All',command=lambda : self.set_map_pool(self.ALLMAPS))
        self.preset_map_pool1 = tk.Button(self.root,text='FACEIT League S3',command=lambda : self.set_map_pool(self.presets[0]))

        for item in self.ALLMAPS:
            self.create_cbox(item)

        self.label2.place(x=0,y=240)
        self.label.place(x=0,y=0)
        self.entry.place(x=0,y=22)
        self.entry.config(width=75)
        self.button.place(x=450,y=22)

        self.presetlabel.place(x=0,y=200)
        self.clear_button.place(x=0,y=220)
        self.all_maps.place(x=40,y=220)
        self.preset_map_pool1.place(x=65,y=220)


        self.root.mainloop()


    def create_cbox(self,item):
        if item == 'Blizzard World' or item == 'Colosseo' or item == 'New Junk City' or item == 'Circuit Royal':
            self.pos_helper[0]+=130
            self.pos_helper = [self.pos_helper[0],25]
        self.pos_helper[1]+=20
        cbox = tk.Checkbutton(
                self.root,text=item,
                command=lambda: self.toggle_check(cbox),
                )
        cbox.place(x=self.pos_helper[0],y=self.pos_helper[1])
        self.checkbuttons[item] = cbox

    def enter_text(self,frame):
        input = self.entry.get()
        try:
            match = re.search(r'/teams/([a-f0-9-]+)(?:/|$)', input)
            url = match.group(1)
        except:
            tk.messagebox.showinfo('Error',"Enter a valid team url")
            return

        if megachungus.check_valid(url):
            data = megachungus.main(url,self.map_pool)
            self.embed_chart(data,frame)
        else:
            tk.messagebox.showinfo('Error',"Enter a valid team url")

    def toggle_check(self,button):
        text = button.cget('text')
        if text in self.map_pool:
            button.deselect()
            self.map_pool.remove(text)
        else:
            button.select()
            self.map_pool.append(text)
        print(self.map_pool)
        self.label2.config(text=self.map_pool)

    def embed_chart(self,data,frame):
        for widget in frame.winfo_children():
            widget.destroy()

        fig = megachungus.plot_data(data)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas.draw()

    def set_map_pool(self,list):
        self.map_pool = list
        for cbutton in self.checkbuttons:
            if cbutton in list:
                self.checkbuttons[cbutton].select()
            else:
                self.checkbuttons[cbutton].deselect()

    def clear_maps(self):
        self.map_pool = []
        for cbutton in self.checkbuttons:
            self.checkbuttons[cbutton].deselect()



GUI = MyWindow()
