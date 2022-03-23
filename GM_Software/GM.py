import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import time
from threading import Thread
from collections import defaultdict
import sys
import os
import random
import json
import logging
import threading
import time
from utils import get_configs


class App:
    def __init__(self, master):

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        log_name = os.path.join(self.script_dir, f"GM.log")
        logging.basicConfig(filename=log_name, level=logging.DEBUG)
        logging.info("Start Time: " + time.asctime(time.localtime()))

        # If there are multiple configs, offer a choice
        configs = get_configs("../Configs")
        if len(configs) > 0:
            chosen_config = configs[self.pick_config(configs)]
            self.load_json_cfg(chosen_config)
        else:
            self.load_json_cfg()

        self.fmaster = tk.Frame(master)

        self.dyn_team = defaultdict(list)
        self.tab = ttk.Notebook(self.fmaster)

        self.f1 = tk.Frame(self.tab)
        self.f2 = tk.Frame(self.tab)
        self.f3 = tk.Frame(self.tab)
        self.f1_top = tk.Frame(self.f1)

        self.f1_bottom = tk.Frame(self.f1)

        self.running = 0
        self.tn = 5
        vcmd = (
            master.register(self.validate),
            "%d",
            "%i",
            "%P",
            "%s",
            "%S",
            "%v",
            "%V",
            "%W",
        )
        self.spdlbl = tk.Label(self.f1_top, text="Speed:")

        self.spd = tk.StringVar(master, value="1")
        self.spdbx = tk.Entry(
            self.f1_top,
            width=3,
            validate="key",
            validatecommand=vcmd,
            textvariable=self.spd,
        )

        self.tmrlbl = tk.Label(self.f1_top, text="Game Length:")

        self.t = tk.StringVar(master, value="75:00")
        self.gt = int(self.t.get()[:-3]) * 60
        self.mins, secs = divmod(self.gt, 60)
        self.tmr = tk.Entry(
            self.f1_top,
            width=6,
            validate="key",
            validatecommand=vcmd,
            textvariable=self.t,
        )

        self.start = tk.Button(self.f1_top, text="START", command=self.gamestart)

        self.pausebtn = tk.Button(self.f1_top, text="PAUSE", command=self.gamepause)

        self.reset = tk.Button(self.f1_top, text="RESET", command=self.gamereset)

        self.boon_one = tk.IntVar()
        self.boonone_btn = tk.Checkbutton(
            self.f1_top, text=self.boon_data[0]["name"], variable=self.boon_one
        )

        self.boon_two = tk.IntVar()
        self.boontwo_btn = tk.Checkbutton(
            self.f1_top, text=self.boon_data[1]["name"], variable=self.boon_two
        )

        self.boon_three = tk.IntVar()
        self.boonthree_btn = tk.Checkbutton(
            self.f1_top, text=self.boon_data[2]["name"], variable=self.boon_three
        )

        self.mes = tk.StringVar(master, value="")
        self.text_box = tk.Entry(self.f1, textvariable=self.mes, width=80)

        self.teamer()

        self.salegraph = tk.Canvas(self.f2)

        self.revgraph = tk.Canvas(self.f3)

        colours = ["red", "blue", "green", "purple", "orange", "black"]

        self.s_line = []
        for i in range(self.tn):
            self.s_line.append(self.salegraph.create_line(0, 0, 0, 0, fill=colours[i]))

        self.r_line = []
        for i in range(self.tn):
            self.r_line.append(self.revgraph.create_line(0, 0, 0, 0, fill=colours[i]))

        self.tab.add(self.f1, text="Game")
        self.tab.add(self.f2, text="Sales")
        self.tab.add(self.f3, text="Revenue")

        self.fmaster.grid()
        self.tab.grid()
        self.f1_top.grid()
        self.f1_bottom.grid()
        self.spdlbl.grid(sticky="W", row=0, column=0)
        self.spdbx.grid(sticky="W", row=0, column=1)
        self.tmrlbl.grid(sticky="W", row=0, column=2)
        self.tmr.grid(sticky="W", row=0, column=3)
        self.start.grid(sticky="W", row=0, column=4)
        self.pausebtn.grid(sticky="W", row=0, column=5)
        self.reset.grid(sticky="W", row=0, column=6)
        self.boonone_btn.grid(sticky="W", row=0, column=7)
        self.boontwo_btn.grid(sticky="W", row=0, column=8)
        self.boonthree_btn.grid(sticky="W", row=0, column=9)
        self.text_box.grid()
        self.salegraph.grid(sticky="N")
        self.revgraph.grid(sticky="N")

    def write(self, message):
        self.mes.set(message)

    def section_builder(self, section, i, row_n, f):
        label_text = section["section"]
        col_n = 2 * i
        if section["required"] == "True":
            label_text += "*"
        label = tk.Label(f, text=label_text, font="Verdana 10 bold")
        label.grid(row=row_n, column=col_n, columnspan=2)
        row_n += 1
        counter = 1
        col_n -= 1
        for upgrade in section["upgrades"]:
            if counter > 2:
                row_n += 1
                counter = 1
            self.upgrade_bulider(upgrade, col_n + counter, row_n, i, f)
            counter += 1
        return row_n + 1

    def upgrade_bulider(self, upgrade, col_n, row_n, i, f):

        var = tk.IntVar()
        self.dyn_team[i].append(var)
        check_btn = tk.Checkbutton(f, text=upgrade["name"], variable=var)
        check_btn.grid(sticky="W", row=row_n, column=col_n)

    def framer(self, i):
        f = tk.LabelFrame(self.f1_bottom, text=self.teams[i])
        row_n = 1

        for section in self.cfg_data:
            row_n = self.section_builder(section, i, row_n, f)
        f.grid(sticky="W", row=1, column=i, padx=2, pady=2)

    def research(self):
        for i in range(self.tn):
            cnt = 0
            for n in self.dyn_team[i]:
                if n.get():
                    key = self.teams[i] + str(cnt)
                    if int(self.cfg[key][0]) > 0:
                        self.cfg[key][0] = str(int(self.cfg[key][0]) - 1)
                cnt = cnt + 1

    def timer(self):
        self.t_old = self.t.get()
        self.pause = 0
        self.gt = int(self.t.get()[:-3]) * 60
        self.points = int(self.t_old[:-3]) - int(self.gt / 60)
        while self.gt:
            if self.reset_flg == 1:
                self.t.set(self.t_old)
                break
            while self.pause == 1:
                time.sleep(1)
            self.mins, secs = divmod(self.gt, 60)
            self.timeformat = "{:02d}:{:02d}".format(self.mins, secs)
            self.write("Game time remaining: " + self.timeformat)
            time.sleep(1)
            self.gt -= int(self.spd.get())
            self.points = int(self.t_old[:-3]) - int(self.gt / 60)
            self.t.set(self.timeformat)
        self.write("Game Finished!")

    def gamestart(self):
        self.reset_flg = 0
        self.running = 1
        self.write("Starting Game")
        self.t1 = Thread(target=self.timer)
        self.t1.daemon = True
        self.t1.start()
        self.t2 = Thread(target=self.game)
        self.t2.daemon = True
        self.t2.start()

    def gamepause(self):
        if self.pause == 0:
            self.pause = 1
            self.running = 0
            self.pausebtn.config(text="CONTINUE")
            self.write("Game Paused")
        else:
            self.pause = 0
            self.running = 1
            self.pausebtn.config(text="PAUSE")
            self.write("Game Resuming")

    def gamereset(self):
        self.reset_flg = 1
        self.pause = 0
        self.running = 0
        self.pausebtn.config(text="PAUSE")
        self.write("Resetting Game")
        self.tclear()

    def game(self):
        self.loadcfg()
        f = open("gamestate.txt", "w")
        f.close()
        f2 = open("sales.txt", "w")
        f2.close()
        f3 = open("revenue.txt", "w")
        f3.close()
        oldmins = self.mins
        while self.gt:
            if self.mins < oldmins:
                f = open("gamestate.txt", "a")
                f2 = open("sales.txt", "a")
                f3 = open("revenue.txt", "a")
                self.research()
                self.boons()
                self.go()

                data, sales, revenue = self.sale()

                f.write(data)
                f2.write(sales)
                f3.write(revenue)
                f.close()
                f2.close()
                f3.close()

                oldmins = self.mins

    def g_rand(self):
        random.seed()
        return random.randint(0, 100)

    def sale(self):
        data = self.timeformat + ": "
        sales = ""
        revenue = ""
        for i in self.teams:
            if self.prod[i]:
                base = self.g_rand()
                mod, rev = self.mod(i)
                mod = self.multi(i, mod)
                result = base * mod

                if result > 66:
                    self.sales[i] = self.sales[i] + 1
                    self.rev[i] = self.rev[i] + rev

            self.update_plot(self.salegraph, self.s_line, i, self.sales[i])
            self.update_plot(self.revgraph, self.r_line, i, self.rev[i])

            data = data + i + ", " + str(self.sales[i]) + ", "
            sales = sales + str(self.sales[i]) + ", "
            revenue = revenue + str(self.rev[i]) + ", "

        data = data[:-2] + "\n"
        sales = sales[:-2] + "\n"
        revenue = revenue[:-2] + "\n"

        return data, sales, revenue

    def load_json_cfg(self, config_dir="../Configs/Default"):
        config = os.path.join(config_dir, "config.json")
        boons = os.path.join(config_dir, "boons.json")
        conf = os.path.join(self.script_dir, config)
        logging.info(conf)

        with open(conf) as json_file:
            self.cfg_data = json.load(json_file)
            if logging.getLogger().getEffectiveLevel() >= 10:
                for s in self.cfg_data:
                    logging.debug("Name: " + s["section"])
                    logging.debug("Required: " + s["required"])
                    logging.debug("Upgrades: ")
                    for u in s["upgrades"]:
                        logging.debug("    Name: " + u["name"])
                        logging.debug("    Required: " + u["duration"])
                        logging.debug("    Sales Multiplier: " + u["sales_multiplier"])
                        logging.debug("    Price Modifier: " + u["price_modifier"])
                        logging.debug("    _________________")
                    logging.debug("_________________")

        boon_conf = os.path.join(self.script_dir, boons)
        logging.info(boon_conf)

        with open(boon_conf) as json_file:
            self.boon_data = json.load(json_file)
            if logging.getLogger().getEffectiveLevel() >= 10:
                for boon in self.boon_data:
                    logging.debug("Name: " + boon["name"])
                    logging.debug("Multiplier: " + boon["multiplier"])
                    logging.debug("Upgrade: " + boon["upgrade"])
                    logging.debug("_________________")

    def loadcfg(self):
        self.cfg = {}

        j = 0
        for section in self.cfg_data:
            for upgrade in section["upgrades"]:
                for k in self.teams:
                    self.cfg[k + str(j)] = [
                        upgrade["duration"],
                        upgrade["sales_multiplier"],
                        upgrade["price_modifier"],
                    ]
                j += 1

    def mod(self, i):
        i2 = int(i[-1:]) - 1
        rev = 400000
        mod = 1.0
        cnt = 0
        for j in self.dyn_team[i2]:
            key = i + str(cnt)
            if j.get():
                if int(self.cfg[key][0]) == 0:
                    mod = mod + float(self.cfg[key][1])
                    rev = rev + int(self.cfg[key][2])
            cnt = cnt + 1

        return mod, rev

    def multi(self, i, mod):
        i = int(i[-1:]) - 1
        nuclei = (
            self.dyn_team[i][15].get()
            + self.dyn_team[i][16].get()
            + self.dyn_team[i][17].get()
            + self.dyn_team[i][18].get()
        )
        if nuclei == 4:
            mod = mod + 0.4
            if self.dyn_team[i][12]:
                mod = mod + 0.2
        cryo = (
            self.dyn_team[i][19].get()
            + self.dyn_team[i][20].get()
            + self.dyn_team[i][22].get() * self.dyn_team[i][10].get()
        )
        if cryo > 0:
            mod = mod + 0.2
        return mod

    def go(self):
        for i in range(self.tn):
            mag = (
                self.dyn_team[i][0].get()
                + self.dyn_team[i][1].get()
                + self.dyn_team[i][2].get()
            )
            rack = self.dyn_team[i][3].get() + self.dyn_team[i][4].get()
            cover = self.dyn_team[i][5].get() + self.dyn_team[i][6].get()
            software = self.dyn_team[i][7].get() + self.dyn_team[i][8].get()
            tot = mag + rack + cover + software
            if tot > 3:
                self.prod[self.teams[i]] = True

    def boons(self):
        if self.boon_one:
            for i in self.teams:
                key = i + self.boon_data[0]["upgrade"]
                self.cfg[key][1] = self.boon_data[0]["multiplier"]
        else:
            for i in self.teams:
                key = i + self.boon_data[0]["upgrade"]
                self.cfg[key][1] = "0"
        if self.boon_two:
            for i in self.teams:
                key = i + self.boon_data[1]["upgrade"]
                self.cfg[key][1] = self.boon_data[1]["multiplier"]
        else:
            for i in self.teams:
                key = i + self.boon_data[1]["upgrade"]
                self.cfg[key][1] = "0"
        if self.boon_three:
            for i in self.teams:
                key = i + self.boon_data[2]["upgrade"]
                self.cfg[key][1] = self.boon_data[1]["multiplier"]
        else:
            for i in self.teams:
                key = i + self.boon_data[2]["upgrade"]
                self.cfg[key][1] = "0"

    def update_plot(self, graph, line, team, val):
        team = int(team[-1:]) - 1
        self.add_point(graph, line[team], val)
        graph.xview_moveto(1.0)

    def add_point(self, graph, line, y):
        coords = graph.coords(line)
        w = graph.winfo_width()
        h = graph.winfo_height()
        for n in range(0, self.points):
            x = (w * n) / self.points
            coords.append(x)
            coords.append(h - (y / h))
        # coords = coords[-200:]  # keep # of points to a manageable size
        graph.coords(line, *coords)
        graph.configure(scrollregion=graph.bbox("all"))

    def teamer(self):
        self.teams = []
        self.sales = {}
        self.rev = {}
        self.prod = {}
        for i in range(self.tn):
            self.teams.append("Team " + str(i + 1))
            self.sales[self.teams[i]] = 0
            self.rev[self.teams[i]] = -4000000
            self.framer(i)
            self.prod[self.teams[i]] = False

    def tclear(self):
        self.teams = []
        self.sales = {}
        self.rev = {}
        self.prod = {}
        for i in range(self.tn):
            self.teams.append("Team " + str(i + 1))
            self.sales[self.teams[i]] = 0
            self.rev[self.teams[i]] = -4000000
            self.prod[self.teams[i]] = False

    def validate(
        self,
        action,
        index,
        value_if_allowed,
        prior_value,
        text,
        validation_type,
        trigger_type,
        widget_name,
    ):
        if text in "0123456789:":
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

    def pick_config(self, config_dirs):
        suggestions = []
        for i in range(len(config_dirs)):
            suggestions.append((i, os.path.basename(config_dirs[i])))
        popup = SuggestionPopup(root, suggestions)
        result = popup.show()
        return result[0]


class SuggestionPopup(tk.Toplevel):
    def __init__(self, parent, suggestions):
        super().__init__(parent)

        self.parent = parent
        self.title("Select suggestion")

        self.focus_set()
        self.attributes('-topmost', True)
        self.listbox = tk.Listbox(self, height=10, width=20)
        self.listbox.pack(pady=15)

        self.btn = tk.Button(self, text="Confirm selection", command=self.select)
        self.btn.pack(pady=10)

        for (idd, info) in suggestions:
            self.listbox.insert(tk.END, info)

        self.selection = None

    def select(self):
        selection = self.listbox.curselection()
        if selection:
            self.selection = (selection[0], self.listbox.get(selection[0]))
        self.destroy()

    def show(self):
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

        return self.selection


if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    root.resizable(False, False)
    root.title("Company Tycoon")
    app = App(root)
    root.mainloop()
