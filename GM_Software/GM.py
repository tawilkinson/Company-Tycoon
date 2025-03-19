import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import time
from threading import Thread
from collections import defaultdict
import os
import random
import json
import logging
import time
from utils import get_configs
from matplotlib.figure import Figure, Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class App:
    def __init__(self, master: tk.Tk):
        self.script_dir: str = os.path.dirname(os.path.abspath(__file__))
        log_name: str = os.path.join(self.script_dir, f"GM.log")
        logging.basicConfig(filename=log_name, level=logging.DEBUG)
        logging.info("Start Time: " + time.asctime(time.localtime()))

        # If there are multiple configs, offer a choice
        configs: list = get_configs("../Configs")
        if len(configs) > 0:
            chosen_config: str = configs[self.pick_config(configs)]
            self.load_json_cfg(chosen_config)
        else:
            self.load_json_cfg()

        self.fmaster: tk.Frame = tk.Frame(master)

        self.dyn_team: dict[list] = defaultdict(list)
        self.tab: ttk.Notebook = ttk.Notebook(self.fmaster)

        self.f1: tk.Frame = tk.Frame(self.tab)
        self.f2: tk.Frame = tk.Frame(self.tab)
        self.f3: tk.Frame = tk.Frame(self.tab)
        self.f1_top: tk.Frame = tk.Frame(self.f1)

        self.f1_bottom: tk.Frame = tk.Frame(self.f1)

        self.running: bool = False
        self.pause: bool = False
        self.reset_flg: bool = False
        self.points: int = 1
        self.initial_investment: int = -4000000
        self.tn: int = 8
        vcmd: str = (
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
        self.spdlbl: tk.Label = tk.Label(self.f1_top, text="Speed:")

        self.spd: tk.StringVar = tk.StringVar(master, value="1")
        self.spdbx: tk.Entry = tk.Entry(
            self.f1_top,
            width=3,
            validate="key",
            validatecommand=vcmd,
            textvariable=self.spd,
        )

        self.tmrlbl: tk.Label = tk.Label(self.f1_top, text="Game Length:")

        self.t: tk.StringVar = tk.StringVar(master, value="75:00")
        self.gt: int = int(self.t.get()[:-3]) * 60
        self.mins, _ = divmod(self.gt, 60)
        self.tmr: tk.Entry = tk.Entry(
            self.f1_top,
            width=6,
            validate="key",
            validatecommand=vcmd,
            textvariable=self.t,
        )

        self.start: tk.Button = tk.Button(
            self.f1_top, text="START", command=self.gamestart
        )

        self.pausebtn: tk.Button = tk.Button(
            self.f1_top, text="PAUSE", command=self.gamepause
        )

        self.reset: tk.Button = tk.Button(
            self.f1_top, text="RESET", command=self.gamereset
        )

        self.boon_one: tk.IntVar = tk.IntVar()
        self.boonone_btn: tk.Checkbutton = tk.Checkbutton(
            self.f1_top, text=self.boon_data[0]["name"], variable=self.boon_one
        )

        self.boon_two: tk.IntVar = tk.IntVar()
        self.boontwo_btn: tk.Checkbutton = tk.Checkbutton(
            self.f1_top, text=self.boon_data[1]["name"], variable=self.boon_two
        )

        self.boon_three: tk.IntVar = tk.IntVar()
        self.boonthree_btn: tk.Checkbutton = tk.Checkbutton(
            self.f1_top, text=self.boon_data[2]["name"], variable=self.boon_three
        )

        self.mes: tk.StringVar = tk.StringVar(master, value="")
        self.text_box: tk.Entry = tk.Entry(self.f1, textvariable=self.mes, width=80)

        self.teamer()

        self.colours: list[str] = [
            "red",
            "blue",
            "green",
            "purple",
            "orange",
            "black",
            "yellow",
            "grey",
            "brown",
        ]

        self.salefig: Figure = Figure(figsize=(20, 4), dpi=100)
        self.saleplot: Axes = self.salefig.add_subplot(111)
        self.revfig: Figure = Figure(figsize=(20, 4), dpi=100)
        self.revplot: Axes = self.revfig.add_subplot(111)
        self.tclear()

        self.salegraph: FigureCanvasTkAgg = FigureCanvasTkAgg(
            self.salefig, master=self.f2
        )
        self.revgraph: FigureCanvasTkAgg = FigureCanvasTkAgg(
            self.revfig, master=self.f3
        )
        self.draw_graphs()

        self.tab.add(self.f1, text="Game")
        self.tab.add(self.f2, text="Sales")
        self.tab.add(self.f3, text="Revenue")

        self.fmaster.pack(expand=1, fill="both")
        self.tab.pack(expand=1, fill="both")
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
        self.salegraph.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.revgraph.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def write(self, message: str) -> None:
        self.mes.set(message)

    def section_builder(
        self, section: dict[str], i: int, row_n: int, f: tk.Misc
    ) -> int:
        label_text: str = section["section"]
        col_n: int = 2 * i
        if section["required"] == "True":
            label_text += "*"
        label: tk.Label = tk.Label(f, text=label_text, font="Verdana 10 bold")
        label.grid(row=row_n, column=col_n, columnspan=2)
        row_n += 1
        counter: int = 1
        col_n -= 1
        for upgrade in section["upgrades"]:
            if counter > 2:
                row_n += 1
                counter = 1
            self.upgrade_bulider(upgrade, col_n + counter, row_n, i, f)
            counter += 1
        return row_n + 1

    def upgrade_bulider(
        self, upgrade: dict[str], col_n: int, row_n: int, i: int, f: tk.Misc
    ) -> None:
        var: tk.IntVar = tk.IntVar()
        self.dyn_team[i].append(var)
        check_btn = tk.Checkbutton(f, text=upgrade["name"], variable=var)
        check_btn.grid(sticky="W", row=row_n, column=col_n)

    def framer(self, i: int) -> None:
        f: tk.LabelFrame = tk.LabelFrame(self.f1_bottom, text=self.teams[i])
        row_n: int = 1

        for section in self.cfg_data:
            row_n = self.section_builder(section, i, row_n, f)
        f.grid(sticky="W", row=1, column=i, padx=2, pady=2)

    def research(self) -> None:
        for i in range(self.tn):
            cnt: int = 0
            for n in self.dyn_team[i]:
                if n.get():
                    key = self.teams[i] + str(cnt)
                    if int(self.cfg[key][0]) > 0:
                        self.cfg[key][0] = str(int(self.cfg[key][0]) - 1)
                cnt = cnt + 1

    def timer(self) -> None:
        self.t_old: tk.StringVar = self.t.get()
        self.pause = False
        self.gt = int(self.t.get()[:-3]) * 60
        self.points = int(self.t_old[:-3]) - int(self.gt / 60)
        while self.gt > 0:
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
        self.running = False
        self.write("Game Finished!")

    def gamestart(self) -> None:
        self.reset_flg = False
        self.running = True
        self.write("Starting Game")
        self.t1: Thread = Thread(target=self.timer)
        self.t1.daemon = True
        self.t1.start()
        self.t2: Thread = Thread(target=self.game)
        self.t2.daemon = True
        self.t2.start()

    def gamepause(self) -> None:
        if self.pause:
            self.pause = False
            self.running = True
            self.pausebtn.config(text="PAUSE")
            self.write("Game Resuming")
        else:
            self.pause = True
            self.running = False
            self.pausebtn.config(text="CONTINUE")
            self.write("Game Paused")

    def gamereset(self) -> None:
        self.reset_flg = True
        self.pause = False
        self.running = False
        self.pausebtn.config(text="PAUSE")
        self.write("Resetting Game")
        self.tclear()
        self.draw_graphs()

    def game(self) -> None:
        self.loadcfg()
        f = open("gamestate.txt", "w")
        f.close()
        f2 = open("sales.txt", "w")
        f2.close()
        f3 = open("revenue.txt", "w")
        f3.close()
        oldmins: int = self.mins
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

    def g_rand(self) -> int:
        random.seed()
        return random.randint(0, 100)

    def sale(self) -> tuple[str, str, str]:
        data: str = self.timeformat + ": "
        sales: str = ""
        revenue: str = ""
        for i in self.teams:
            if self.prod[i]:
                base: int = self.g_rand()
                mod, rev = self.mod(i)
                mod = self.multi(i, mod)
                result: float = base * mod

                if result > 66:
                    self.sales[i] = self.sales[i] + 1
                    self.rev[i] = self.rev[i] + rev

            self.update_plot(self.saleplot, self.s_line, i, self.sales[i])
            self.update_plot(self.revplot, self.r_line, i, self.rev[i])

            data = data + i + ", " + str(self.sales[i]) + ", "
            sales = sales + str(self.sales[i]) + ", "
            revenue = revenue + str(self.rev[i]) + ", "

        self.salegraph.draw()
        self.revgraph.draw()
        data = data[:-2] + "\n"
        sales = sales[:-2] + "\n"
        revenue = revenue[:-2] + "\n"

        return data, sales, revenue

    def load_json_cfg(self, config_dir="../Configs/Default") -> None:
        config: str = os.path.join(config_dir, "config.json")
        boons: str = os.path.join(config_dir, "boons.json")
        conf: str = os.path.join(self.script_dir, config)
        logging.info(conf)

        with open(conf) as json_file:
            self.cfg_data: dict[str] = json.load(json_file)
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

        boon_conf: str = os.path.join(self.script_dir, boons)
        logging.info(boon_conf)

        with open(boon_conf) as json_file:
            self.boon_data: dict[str] = json.load(json_file)
            if logging.getLogger().getEffectiveLevel() >= 10:
                for boon in self.boon_data:
                    logging.debug("Name: " + boon["name"])
                    logging.debug("Multiplier: " + boon["multiplier"])
                    logging.debug("Upgrade: " + boon["upgrade"])
                    logging.debug("_________________")

    def loadcfg(self) -> None:
        self.cfg: dict[str, str] = {}

        j: int = 0
        for section in self.cfg_data:
            for upgrade in section["upgrades"]:
                for k in self.teams:
                    self.cfg[k + str(j)] = [
                        upgrade["duration"],
                        upgrade["sales_multiplier"],
                        upgrade["price_modifier"],
                    ]
                j += 1

    def mod(self, i: int) -> tuple[float, int]:
        i2: int = int(i[-1:]) - 1
        rev: int = 400000
        mod: float = 1.0
        cnt: int = 0
        for j in self.dyn_team[i2]:
            key: str = i + str(cnt)
            if j.get():
                if int(self.cfg[key][0]) == 0:
                    mod = mod + float(self.cfg[key][1])
                    rev = rev + int(self.cfg[key][2])
            cnt = cnt + 1

        return mod, rev

    def multi(self, i: int, mod: float) -> float:
        i: int = int(i[-1:]) - 1
        nuclei: int = (
            self.dyn_team[i][15].get()
            + self.dyn_team[i][16].get()
            + self.dyn_team[i][17].get()
            + self.dyn_team[i][18].get()
        )
        if nuclei == 4:
            mod = mod + 0.4
            if self.dyn_team[i][12]:
                mod = mod + 0.2
        cryo: int = (
            self.dyn_team[i][19].get()
            + self.dyn_team[i][20].get()
            + self.dyn_team[i][22].get() * self.dyn_team[i][10].get()
        )
        if cryo > 0:
            mod = mod + 0.2
        return mod

    def go(self) -> None:
        for i in range(self.tn):
            mag: int = (
                self.dyn_team[i][0].get()
                + self.dyn_team[i][1].get()
                + self.dyn_team[i][2].get()
            )
            rack: int = self.dyn_team[i][3].get() + self.dyn_team[i][4].get()
            cover: int = self.dyn_team[i][5].get() + self.dyn_team[i][6].get()
            software: int = self.dyn_team[i][7].get() + self.dyn_team[i][8].get()
            tot: int = mag + rack + cover + software
            if tot > 3:
                self.prod[self.teams[i]] = True

    def boons(self) -> None:
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

    def update_plot(self, graph: Axes, line: list[list], team: int, val: int) -> None:
        team: int = int(team[-1:]) - 1
        self.add_point(graph, line, team, val)
        graph.set_xticks(range(self.points), minor=False)

    def add_point(self, graph: Axes, line: list[list], team: int, y: int) -> None:
        line[team].append(y)
        graph.plot(line[team], color=self.colours[team], label=f"Team {team + 1}")

    def teamer(self) -> None:
        self.teams: list[str] = []
        self.sales: dict[str, int] = {}
        self.rev: dict[str, int] = {}
        self.prod: dict[str, bool] = {}
        for i in range(self.tn):
            self.teams.append("Team " + str(i + 1))
            self.sales[self.teams[i]] = 0
            self.rev[self.teams[i]] = self.initial_investment
            self.framer(i)
            self.prod[self.teams[i]] = False

    def tclear(self) -> None:
        self.teams = []
        self.sales = {}
        self.rev = {}
        self.prod = {}
        self.s_line = []
        self.r_line = []
        self.saleplot.cla()
        self.saleplot.set_title("Total Sales")
        self.saleplot.set_xlabel("Time / months")
        self.saleplot.set_ylabel("Sales / unit")
        self.revplot.cla()
        self.revplot.set_title("Total Revenue")
        self.revplot.set_xlabel("Time / months")
        self.revplot.set_ylabel("Revenue / £")
        self.revplot.ticklabel_format(style="plain")
        for i in range(self.tn):
            self.teams.append("Team " + str(i + 1))
            self.sales[self.teams[i]] = 0
            self.rev[self.teams[i]] = self.initial_investment
            self.prod[self.teams[i]] = False
            self.s_line.append([])
            self.update_plot(self.saleplot, self.s_line, self.teams[i], 0)
            self.r_line.append([])
            self.update_plot(
                self.revplot, self.r_line, self.teams[i], self.initial_investment
            )
        self.saleplot.legend(loc="upper left")
        self.revplot.legend(loc="upper left")

    def draw_graphs(self) -> None:
        self.salegraph.draw()
        self.revgraph.draw()

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
    ) -> bool:
        if text in "0123456789:":
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

    def pick_config(self, config_dirs) -> str:
        suggestions: list[str] = []
        for i in range(len(config_dirs)):
            suggestions.append((i, os.path.basename(config_dirs[i])))
        popup: SuggestionPopup = SuggestionPopup(root, suggestions)
        result: (str) = popup.show()
        return result[0]


class SuggestionPopup(tk.Toplevel):
    def __init__(self, parent: tk.Misc, suggestions: list[int, str]):
        super().__init__(parent)

        self.parent: tk.Misc = parent
        self.title("Select suggestion")

        self.focus_set()
        self.attributes("-topmost", True)
        self.listbox: tk.Listbox = tk.Listbox(self, height=10, width=20)
        self.listbox.pack(pady=15)

        self.btn: tk.Button = tk.Button(
            self, text="Confirm selection", command=self.select
        )
        self.btn.pack(pady=10)

        for _, info in suggestions:
            self.listbox.insert(tk.END, info)

        self.selection: str | None = None

    def select(self) -> None:
        selection: str | None = self.listbox.curselection()
        if selection:
            self.selection = (selection[0], self.listbox.get(selection[0]))
        self.destroy()

    def show(self) -> str | None:
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

        return self.selection


if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    root.resizable(False, False)
    root.title("Company Tycoon")
    app: tk.Misc = App(root)
    root.mainloop()
