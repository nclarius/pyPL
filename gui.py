#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Graphical interface.
CURRENTLY UNDER CONSTRUCTION.
"""

import tkinter as tk
from tkinter import ttk
import os


class PyPLInst:

    def __init__(self):
        self.completed = []

        self.action = "tt"
        self.structure = None
        self.conclusion = None
        self.axioms = []
        self.premises = []
        self.logic = {"proppred": "pred", "classint": "class", "modal": "nonmodal", "constvar": "var", "frame": "K"}

        self.output = "tex"
        self.num_models = 1
        self.size_limit_factor = 1
        self.underline_open = True
        self.hide_nonopen = False


# style
white = "#ffffff"
black = "#000000"
green = "#52c462"
red = "#bf5050"
yellow = "#ffb94f"
# blue = "#2493ff"
# lightblue = "#80ccff"
darkgray = "#333333"
lightgray = "#666666"
font = "-family {OpenSans} -size 12 -weight normal -slant roman -underline 0 -overstrike 0"
font_large = "-family {OpenSans} -size 14 -weight normal -slant roman -underline 0 -overstrike 0"


# todo config file for default settings
# todo visually distinguish action buttons, radio buttons and check buttons?

class PyPLGUI(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()

        # general settings
        self.root.title("pyPL")
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file=icon_path))
        self.root.geometry("870x530")

        # style
        self.style = ttk.Style()
        for widget in [".", "TFrame", "TNotebook", "TNotebook.Tab", "TLabel"]:
            self.style.configure(widget, background=white, foreground=black, font=font)
        self.style.map("TNotebook.Tab",
                       background=[("selected", darkgray), ("active", lightgray)],
                       foreground=[("selected", white), ("active", white)]
                       # font=[("selected", ("OpenSans", "12", "bold"))]
                       )  # todo no rounded corners for tabs
        self.style.theme_settings("default", {"TNotebook.Tab": {"configure": {"padding": [10, 10]}}})
        self.root.configure(bg=white)
        self.root.option_add("*Font", "OpenSans 12")

        # invoke
        super().__init__(self.root)
        self.inst = PyPLInst()
        self.pack()
        self.win_main()
        self.mainloop()

    def win_main(self):
        self.tabs = ttk.Notebook(self.root)
        tabs = [
            "Start",
            "1. Choose your task",
            "2. Specify your input",
            "3. Select your logic",
            "4. Adjust your settings",
            # "5. Run"
        ]
        # add tabs
        for i, tab in enumerate(tabs):
            self.tabs.add(ttk.Frame(self.tabs, style="TFrame"), text=tab)
        # build tabs
        for i, tab in enumerate(tabs):
            getattr(self, "tab_" + str(i))()
        self.tabs.pack(fill="both")
        # self.tabs.grid(row=0, column=0)

        frm_run = tk.Frame(self.root)
        frm_run.pack(pady=10)

        # run button
        btn_run = tk.Button(frm_run,
                            text="Run!",
                            activebackground=lightgray, activeforeground=white,
                            state="disabled",
                            width=22, pady=10)
        btn_run.bind("<Button>", lambda e: self.run())
        btn_run.pack(in_=frm_run, pady=10)
        self.btn_run = btn_run
        # keyboard shortcut
        self.root.bind("<Control-Return>", lambda e: self.run())

        # info
        lbl_info = tk.Label(frm_run,
                            text="🛈 https://github.com/nclarius/pyPL") \
            .pack(pady=10)

    def tab_0(self):  # 0. Start
        tab = self.tabs.nametowidget(self.tabs.tabs()[0])

        # welcome message
        lbl_greeting = ttk.Label(tab,
                                 text="Welcome to pyPL.",
                                 font=("OpenSans", "12", "bold")) \
            .pack(pady=10)

        # next tabs
        btn_next = tk.Button(tab,
                             text=">> 1. Pick your settings",
                             bg=darkgray, fg=white,
                             width=20, pady=10)
        btn_next.bind("<Button>", lambda e: self.switch_to_tab(1))
        # btn_next.pack(pady=5)

        btn_step2 = tk.Button(tab,
                              text="1. Choose your task",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step2.bind("<Button>", lambda e: self.switch_to_tab(1))
        btn_step2.pack(pady=5)

        btn_step3 = tk.Button(tab,
                              text="2. Specify your input",
                              activebackground=lightgray, activeforeground=white,

                              width=20, pady=10)
        btn_step3.bind("<Button>", lambda e: self.switch_to_tab(2))
        btn_step3.pack(pady=5)

        btn_step4 = tk.Button(tab,
                              text="3. Select your logic",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step4.bind("<Button>", lambda e: self.switch_to_tab(3))
        btn_step4.pack(pady=5)

        btn_step1 = tk.Button(tab,
                              text="4. Adjust your settings",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step1.bind("<Button>", lambda e: self.switch_to_tab(4))
        btn_step1.pack(pady=5)

        btn_step5 = tk.Button(tab,
                              text="5. Run",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step5.bind("<Button>", lambda e: self.switch_to_tab(5))
        # btn_step5.pack(pady=5)

    def tab_1(self):  # 1. Action
        # todo theorem guessing
        tab = self.tabs.nametowidget(self.tabs.tabs()[1])

        def initial_select_rb(rb):
            rb.config(fg=white)

        def select_rb(rb):
            rb.config(fg=white)
            for rb_ in radiobuttons:
                if rb_ != rb:
                    rb_.config(fg=black)
            btn_set.config(state="normal", bg=darkgray, fg=white)
            btn_reset.config(state="normal")
            set()

        def reset():
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.completed.remove(1)
            self.inst.action = None
            btn_set.config(state="disabled", bg=white, fg=black)
            btn_next.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.action = action.get()
            self.update_summary()
            self.inst.completed.append(1)
            btn_next.config(state="normal", bg=darkgray, fg=white)

        def next_step(i):
            set()
            self.switch_to_tab(i)

        # frames
        # top
        top = tk.Frame(tab)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab)
        mid.pack()
        mid1 = tk.Frame(mid)
        mid2 = tk.Frame(mid)
        mid1.pack()
        mid2.pack(pady=20, ipadx=24)
        # bot
        # bot = tk.Frame(tab)
        # bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        # bot1 = tk.Frame(bot)
        # bot2 = tk.Frame(bot)
        # bot1.pack(ipadx=20)
        # bot2.pack(pady=5)

        # heading
        lbl_head = tk.Label(tab,
                            text="What would you like to do?",
                            font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # radio buttons
        action = tk.StringVar(None, self.inst.action)
        actions = [("Model checking", "mc"), ("Model generation", "mg"), ("Counter model generation", "cmg"),
                   ("Theorem proving", "tp"), ("Theorem testing", "tt")]  # todo implement MC
        radiobuttons = []
        for txt, val in actions:
            rb = tk.Radiobutton(tab,
                                text=txt,
                                variable=action,
                                value=val,
                                state="normal" if val != "mc" else "disabled",
                                selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                indicatoron=0,
                                width=25, pady=7.5)
            rb.config(command=lambda arg=rb: select_rb(arg))
            if val == self.inst.action:
                initial_select_rb(rb)
            rb.pack(in_=top, pady=5)
            radiobuttons.append(rb)
            # todo inexplicably thicker border around MG button

        # reset button
        btn_reset = tk.Button(tab,
                              text="Reset",
                              state="normal" if self.inst.action else "disabled",
                              width=7, pady=10)
        btn_reset.bind("<Button>", lambda e: reset())
        # btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            state="normal" if self.inst.action else "disabled",
                            width=7, pady=10)
        btn_set.bind("<Button>", lambda e: set())
        # btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 3. Select your logic",
                             state="normal" if self.inst.action else "disabled",
                             bg=darkgray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step(3))
        # btn_next.pack(in_=bot2)

    def tab_2(self):  # 2. Input
        # todo make scrollable

        tab = self.tabs.nametowidget(self.tabs.tabs()[2])

        def add_formula():
            # variable
            raw = tk.StringVar()
            raws.append(raw)
            fmls.append(raw)
            modes.append(raw)
            i = fmls.index(raw)
            # frames
            if i > 0:
                new_mids = {j: tk.Frame(mid) for j in range(len(mids), len(mids) + 3)}
                mids.update(new_mids)
                for j in new_mids:
                    mids[j].pack(ipadx=5, ipady=5)
            # caption
            cap = tk.Label(tab,
                           text=("Conclusion:" if i == 0 else "Premise " + str(i) + ":"))
            row = len(mids) - 3 if i > 0 else 1
            cap.pack(in_=mids[row], side=tk.LEFT)
            caps.append(cap)
            # remove button
            if i > 0:
                rem = tk.Button(tab,
                                text="-",
                                # bg=darkgray, fg=white,
                                activebackground=lightgray, activeforeground=white)
                rem.pack(in_=mids[row], side=tk.LEFT, padx=5)
                rem["font"] = font_large
                rem.bind("<Button>", lambda e: remove_formula(i))
            else:
                rem = None
            rems.append(rem)
            # formula in plain text  # todo make text selectable
            lbl = tk.Label(tab, text="...")
            lbl.pack(in_=mids[row + 1], side=tk.LEFT)
            # lbl = tk.Text(tab, height=1, borderwidth=0)
            # lbl.tag_configure("center", justify='center')
            # lbl.insert(1.0, "...", "center")
            # lbl.configure(state="disabled")
            # lbl.configure(inactiveselectbackground=lbl.cget("selectbackground"))
            # lbl.pack(in_=mids[row + 1], side=tk.LEFT)
            lbls.append(lbl)
            # entry field
            ent = tk.Entry(tab,
                           textvariable=raw,
                           width=50)
            ent.pack(in_=mids[row + 2], side=tk.LEFT)
            raw.trace("w", lambda *args: select_entry(i))
            ents.append(ent)
            # parse button
            btn_parse = tk.Button(tab,
                                  text="↻",
                                  # bg=darkgray, fg=white,
                                  activebackground=lightgray, activeforeground=white,
                                  state="disabled")
            btn_parse["font"] = font_large
            btn_parse.pack(in_=mids[row + 2], side=tk.LEFT, padx=5)
            btn_parse.bind("<Button>", lambda e: parse(i))
            btns.append(btn_parse)
            ent.bind("<Return>", lambda e: parse(i))
            # swap button
            if len(fmls) > 1:
                btn_swap.config(state="normal")

        def remove_formula(i):
            # todo doesn't always work; indices not updated correctly?
            del raws[i]
            del fmls[i]
            for j in range(6 + 3 * (i - 1), 6 + 3 * (i - 1) + 3):
                mids[j].pack_forget()
            for j in range(3):
                del mids[6 + 3 * (i - 1) + j]
            del caps[i]
            del lbls[i]
            del rems[i]
            del ents[i]
            del btns[i]
            if len(fmls) > 1:
                for j in range(1, len(fmls)):
                    pos = j if j <= i else j - 1
                    caps[j].config(text="Premise " + str(pos) + ":")
                    rems[j].bind("<Button>", lambda e: remove_formula(pos))
                    raws[j].trace("w", lambda *args: select_entry(pos))
                    btns[j].bind("<Button>", lambda e: parse(pos))
            if len(fmls) == 1:
                btn_swap.config(state="disabled")
            set()

        def swap_formulas():
            c, p1 = raws[0].get(), raws[1].get()
            raws[0].set(p1)
            raws[1].set(c)
            parse(0)
            parse(1)

        def select_entry(i):
            raw = raws[i]
            if raw.get():
                btns[i].config(state="normal")
                btn_set.config(state="normal", bg=darkgray, fg=white)
                btn_reset.config(state="normal")
            else:
                btns[i].config(state="disabled")
                btn_set.config(state="disabled", bg=white, fg=black)
                btn_reset.config(state="disabled")

        def parse(i):
            raw = raws[i]
            lbl = lbls[i]
            parser = __import__("parser")
            fml, mode = parser.Parser().parse_(raw.get())
            fmls[i] = fml
            modes[i] = mode
            lbl.configure(text=str(fml))
            set_mode(modes)
            set()

        def set_mode(modes):
            mode_map = {
                "classical": ("classint", "class", "int"),
                "propositional": ("proppred", "prop", "pred"),
                "modal": ("modal", "modal", "nonmodal"),
                "vardomains": ("constvar", "var", "const")
            }
            for md, (cat, val1, val2) in mode_map.items():
                if any([mode[md] for mode in modes]):
                    self.rbs_logic[cat][val1].invoke()
                    # self.rbs_logic[cat][val1].select()
                    # self.rbs_logic[cat][val2].deselect()
                    # select_rb((self.rbs_logic[cat][val1], cat))
                else:
                    self.rbs_logic[cat][val2].invoke()
                    # self.rbs_logic[cat][val2].select()
                    # self.rbs_logic[cat][val1].deselect()
                    # select_rb((self.rbs_logic[cat][val2], cat))
            if any([mode["modal"] for mode in modes]):
                self.rbs_logic["frame"]["K"].config(state="normal")
                if any([not mode["propositional"] for mode in modes]):
                    self.rbs_logic["constvar"]["const"].config(state="normal")
                    self.rbs_logic["constvar"]["var"].config(state="normal")
                else:
                    self.rbs_logic["constvar"]["const"].config(state="disabled")
                    self.rbs_logic["constvar"]["var"].config(state="disabled")
            else:
                self.rbs_logic["frame"]["K"].config(state="disabled")
                self.rbs_logic["constvar"]["const"].config(state="disabled")
                self.rbs_logic["constvar"]["var"].config(state="disabled")

        def reset():
            # lbl_concl.configure(text="—")
            # ent_concl.delete(first=0)
            self.inst.completed.remove(3)
            btn_set.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.conclusion = fmls[0] if fmls else None
            self.inst.premises = fmls[1:] if len(fmls) > 1 else []
            self.update_summary()
            self.inst.completed.append(3)
            self.btn_run.config(state="normal", bg=darkgray, fg=white)

        def next_step(i):
            set()
            self.switch_to_tab(i)

        # frames
        # top
        top = tk.Frame(tab)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab)
        mid.pack()
        mids = {i: tk.Frame(mid) for i in range(6)}
        for i in mids:
            mids[i].pack(ipadx=5, ipady=5)
        # bot
        # bot = tk.Frame(tab)
        # bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        # bot1 = tk.Frame(bot)
        # bot2 = tk.Frame(bot)
        # bot1.pack(ipadx=20)
        # bot2.pack(pady=5)

        # heading
        lbl_head = tk.Label(tab,
                            text="What would you like to analyze?",
                            font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)
        # .grid(row=0, columnspan=4, sticky="NESW")

        # summary
        self.lbl_sum = tk.Label()
        self.lbl_sum.pack(in_=mids[0])

        # input fields
        fmls = []
        modes = []
        raws = []
        caps = []
        lbls = []
        rems = []
        ents = []
        btns = []

        # conclusion
        add_formula()
        self.update_summary()

        # premise heading, swap and add premise buttons
        btn_swap = tk.Button(tab,
                             text="⇅",
                             state="disabled",
                             activebackground=lightgray, activeforeground=white)
        btn_swap.pack(in_=mids[4], side=tk.LEFT, padx=15)
        btn_swap.bind("<Button>", lambda e: swap_formulas())
        lbl_prem = tk.Label(tab, text="Premises:")
        lbl_prem.pack(in_=mids[4], side=tk.LEFT)
        btn_add_prem = tk.Button(tab,
                                 text="+",
                                 activebackground=lightgray, activeforeground=white)
        btn_add_prem["font"] = font_large
        btn_add_prem.pack(in_=mids[4], side=tk.LEFT, padx=15)
        btn_add_prem.bind("<Button>", lambda e: add_formula())
        ents[0].focus()

        # reset button
        btn_reset = tk.Button(tab,
                              text="Reset",
                              width=7, pady=10)
        btn_reset.bind("<Button>", lambda e: reset())
        # btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            bg=darkgray if self.inst.conclusion else white,
                            fg=white if self.inst.conclusion else black,
                            state="normal" if self.inst.conclusion else "disabled",
                            width=7, pady=10)
        btn_set.bind("<Button>", lambda e: set())
        # btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 5. Run",
                             bg=darkgray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step(5))
        # btn_next.pack(in_=bot2)

    def tab_3(self):  # 3. Logic
        tab = self.tabs.nametowidget(self.tabs.tabs()[3])

        def initial_select_rb(arg):
            rb, cat = arg
            rb.config(fg=white)

        def select_rb(arg):
            rb, cat = arg
            rb.config(fg=white)
            for val_ in self.rbs_logic[cat]:
                rb_ = self.rbs_logic[cat][val_]
                if rb_ != rb:
                    rb_.config(fg=black)
            btn_set.config(state="normal", bg=darkgray, fg=white)
            btn_reset.config(state="normal")
            set()
            update_availability()

        def update_availability():
            if self.inst.logic["modal"] == "modal":
                self.rbs_logic["frame"]["K"].config(state="normal")
                if self.inst.logic["proppred"] == "pred":
                    self.rbs_logic["constvar"]["const"].config(state="normal")
                    self.rbs_logic["constvar"]["var"].config(state="normal")
                else:
                    self.rbs_logic["constvar"]["const"].config(state="disabled")
                    self.rbs_logic["constvar"]["var"].config(state="disabled")
            else:
                self.rbs_logic["frame"]["K"].config(state="disabled")
                self.rbs_logic["constvar"]["const"].config(state="disabled")
                self.rbs_logic["constvar"]["var"].config(state="disabled")

        def reset():
            for cat_ in self.rbs_logic:
                for val_ in self.rbs_logic[cat_]:
                    rb_ = self.rbs_logic[cat][val_]
                    rb_.deselect()
            self.inst.completed.remove(1)
            self.inst.action = None
            btn_set.config(state="disabled", bg=white, fg=black)
            btn_next.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.logic = {var: val.get() for (var, val) in variables.items()}
            self.inst.completed.append(1)
            btn_next.config(state="normal", bg=darkgray, fg=white)

        def next_step(i):
            set()
            self.switch_to_tab(i)

        # frames
        # top
        top = tk.Frame(tab)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab)
        mid.pack()
        mids = {i: tk.Frame(mid) for i in range(5)}
        for i in mids:
            mids[i].pack(ipadx=5, ipady=5)
        # bot
        # bot = tk.Frame(tab)
        # bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        # bot1 = tk.Frame(bot)
        # bot2 = tk.Frame(bot)
        # bot1.pack(ipadx=20)
        # bot2.pack(pady=5)

        # heading
        lbl_head = tk.Label(tab,
                            text="Which logic are you working in?",
                            font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # selection
        # todo don't pre-select disabled buttons
        categories = ["proppred", "classint", "modal", "constvar", "frame"]
        labels = {
            "proppred": [("propositional logic", "prop"), ("predicate logic", "pred")],
            "classint": [("classical", "class"), ("intuitionistic", "int")],
            "modal": [("non-modal", "nonmodal"), ("modal", "modal")],
            "constvar": [("with constant domains", "const"), ("with varying domains", "var")],
            "frame": [("frame K", "K")]
        }
        variables = {
            "proppred": tk.StringVar(None, self.inst.logic["proppred"]),
            "classint": tk.StringVar(None, self.inst.logic["classint"]),
            "modal": tk.StringVar(None, self.inst.logic["modal"]),
            "constvar": tk.StringVar(None, self.inst.logic["constvar"]),
            "frame": tk.StringVar(None, self.inst.logic["frame"])
        }
        self.rbs_logic = {cat: dict() for cat in categories}
        for i, cat in enumerate(categories):
            for j, (txt, val) in enumerate(labels[cat]):
                rb = tk.Radiobutton(tab,
                                    text=txt,
                                    variable=variables[cat],
                                    value=val,
                                    state="disabled" if cat in ["constvar", "frame"] or val == "int" else "normal",
                                    selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                    indicatoron=0,
                                    width=20, pady=7.5)
                rb.config(command=lambda arg=(rb, cat): select_rb(arg))
                if val == self.inst.logic[cat]:
                    initial_select_rb((rb, cat))
                rb.pack(in_=mids[i], side=(tk.LEFT if j == 0 else tk.RIGHT))  # todo slightly off-center
                self.rbs_logic[cat][val] = rb

        # summary
        # lbl_summ = tk.Label(tab)
        # select()
        # lbl_summ.pack(in_=botmid)

        # reset button
        btn_reset = tk.Button(tab,
                              text="Reset",
                              state="normal" if self.inst.logic else "disabled",
                              width=7, pady=10)
        btn_reset.bind("<Button>", lambda e: reset())
        # btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            bg=darkgray if self.inst.logic else white,
                            fg=white if self.inst.logic else black,
                            state="normal" if self.inst.logic else "disabled",
                            width=7, pady=10)
        btn_set.bind("<Button>", lambda e: set())
        # btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 4. Specify your input",
                             state="normal" if self.inst.action else "disabled",
                             bg=darkgray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step())
        # btn_next.pack(in_=bot2)

    def tab_4(self):  # 4. Settings
        # todo implement size limit factor, underline open and hide nonopen
        tab = self.tabs.nametowidget(self.tabs.tabs()[4])

        def initial_select_rb(rb):
            rb.config(fg=white)

        def select_rb(rb):
            rb.config(fg=white)
            for rb_ in rbs:
                if rb_ != rb:
                    rb_.config(fg=black)
            btn_set.config(state="normal", bg=darkgray, fg=white)
            btn_reset.config(state="normal")
            set()

        def initial_select_cb(cb):
            cb.config(fg=white)

        def select_cb(cb):
            cb.config(fg=white)
            if not underline.get():
                cbs[0].config(fg=black)
            if not hide.get():
                cbs[1].config(fg=black)
            btn_set.config(state="normal", bg=darkgray, fg=white)
            btn_reset.config(state="normal")
            set()

        def select_entry():
            btn_set.config(state="normal", bg=darkgray, fg=white)
            btn_reset.config(state="normal")
            set()

        def decrease_num_models():
            num_models.set(str(int(num_models.get()) - 1))

        def increase_num_models():
            num_models.set(str(int(num_models.get()) + 1))

        def decrease_size_limit():
            size_limit.set(str(int(size_limit.get()) - 1))

        def increase_size_limit():
            size_limit.set(str(int(size_limit.get()) + 1))

        def reset():
            for radiobutton in rbs:
                radiobutton.deselect()
            self.inst.completed.remove(1)
            self.inst.output = None
            btn_set.config(state="disabled", bg=white, fg=black)
            btn_next.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.output = output.get()
            self.inst.underline_open = underline.get()
            self.inst.hide_nonopen = hide.get()
            if num_models.get():
                self.inst.num_models = int(num_models.get())
            if size_limit.get():
                self.inst.size_limit_factor = int(size_limit.get())
            self.inst.completed.append(1)
            btn_next.config(state="normal", bg=darkgray, fg=white)

        def next_step(i):
            set()
            self.switch_to_tab(i)

        # frames
        # top
        top = tk.Frame(tab)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab)
        mid.pack()
        mid1 = tk.Frame(mid)
        mid2 = tk.Frame(mid)
        mid3 = tk.Frame(mid)
        sep12 = tk.Frame(mid)
        mid4 = tk.Frame(mid)
        mid5 = tk.Frame(mid)
        mid1.pack()
        mid2.pack()
        mid3.pack()
        sep12.pack(pady=15)
        mid4.pack()
        mid5.pack(pady=15)
        # bot
        # bot = tk.Frame(tab)
        # bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        # bot1 = tk.Frame(bot)
        # bot2 = tk.Frame(bot)
        # bot1.pack(ipadx=20)
        # bot2.pack(pady=5)

        # heading
        lbl_head = tk.Label(tab,
                            text="How would you like pyPL to work?",
                            font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # output format
        output = tk.StringVar(None, self.inst.output)
        lbl_output = tk.Label(tab,
                              text="Output format:")
        lbl_output.pack(in_=mid1)

        outputs1 = [("LaTeX PDF", "tex"), ("plain text", "txt")]
        rbs = []
        for i, (txt, val) in enumerate(outputs1):
            rb = tk.Radiobutton(tab,
                                text=txt,
                                variable=output,
                                value=val,
                                selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                indicatoron=0,
                                width=25, pady=7.5)
            rb.pack(in_=mid2, side=(tk.LEFT if i == 0 else tk.RIGHT), pady=5)
            rb.config(command=lambda arg=rb: select_rb(arg))
            if val == self.inst.output:
                initial_select_rb(rb)
            rbs.append(rb)

        cbs = []
        underline = tk.BooleanVar(None, self.inst.underline_open)
        cb = tk.Checkbutton(tab,
                            text="mark open literals",
                            variable=underline,
                            onvalue=True, offvalue=False,
                            selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                            indicatoron=0,
                            width=25, pady=7.5)
        cb.pack(in_=mid3, side=tk.LEFT, pady=5)
        cb.config(command=lambda arg=cb: select_cb(arg))
        initial_select_cb(cb)
        cbs.append(cb)
        hide = tk.BooleanVar(None, self.inst.hide_nonopen)
        cb = tk.Checkbutton(tab,
                            text="hide non-open branches",
                            variable=hide,
                            onvalue=True, offvalue=False,
                            selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                            indicatoron=0,
                            width=25, pady=7.5)
        cb.config(command=lambda arg=cb: select_cb(arg))
        cb.pack(in_=mid3, side=tk.RIGHT, pady=5)
        cbs.append(cb)

        # number of models to generate
        num_models = tk.StringVar(None, self.inst.num_models)
        lbl_num_models = tk.Label(tab,
                                  text="Number of models to compute in model generation:")
        lbl_num_models.pack(in_=mid4, side=tk.LEFT, padx=15)
        btn_num_models_dn = tk.Button(tab,
                                      text="-",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_num_models_dn.bind("<Button>", lambda e: decrease_num_models())
        btn_num_models_dn.pack(in_=mid4, side=tk.LEFT, padx=5)
        ent_num_models = tk.Entry(tab,
                                  textvariable=num_models,
                                  justify=tk.RIGHT,
                                  width=2)
        ent_num_models.pack(in_=mid4, side=tk.LEFT, padx=5)
        num_models.trace("w", lambda *args: select_entry())
        btn_num_models_up = tk.Button(tab,
                                      text="+",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_num_models_up.bind("<Button>", lambda e: increase_num_models())
        btn_num_models_up.pack(in_=mid4, side=tk.LEFT, padx=5)

        # size limit factor
        size_limit = tk.StringVar(None, self.inst.size_limit_factor)
        lbl_size_limit = tk.Label(tab,
                                  text="Size limit factor for tableau trees:")
        lbl_size_limit.pack(in_=mid5, side=tk.LEFT, padx=15)
        btn_size_limit_dn = tk.Button(tab,
                                      text="-",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_size_limit_dn.bind("<Button>", lambda e: decrease_size_limit())
        btn_size_limit_dn.pack(in_=mid5, side=tk.LEFT, padx=5)
        ent_size_limit = tk.Entry(tab,
                                  textvariable=size_limit,
                                  justify=tk.RIGHT,
                                  width=2)
        ent_size_limit.pack(in_=mid5, side=tk.LEFT, padx=5)
        size_limit.trace("w", lambda *args: select_entry())
        btn_size_limit_up = tk.Button(tab,
                                      text="+",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_size_limit_up.bind("<Button>", lambda e: increase_size_limit())
        btn_size_limit_up.pack(in_=mid5, side=tk.LEFT, padx=5)

        # reset button
        btn_reset = tk.Button(tab,
                              text="Reset",
                              state="normal" if self.inst.action else "disabled",
                              width=7, pady=10)
        btn_reset.bind("<Button>", lambda e: reset())
        # btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            state="normal" if self.inst.action else "disabled",
                            width=7, pady=10)
        mid.pack()
        btn_set.bind("<Button>", lambda e: set())
        # btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 2. Choose your task",
                             state="normal" if self.inst.action else "disabled",
                             bg=darkgray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step(2))
        # btn_next.pack(in_=bot2)

    def tab_5(self):
        tab = self.tabs.nametowidget(self.tabs.tabs()[5])

        def run():
            self.run()

        # frames
        # top
        top = tk.Frame(tab)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab)
        mid.pack()

        # heading
        lbl_head = tk.Label(tab,
                            text="What are you waiting for?",
                            font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # run button
        btn_run = tk.Button(tab,
                            text="Run!",
                            activebackground=lightgray, activeforeground=white,
                            # bg=darkgray, fg=white,
                            width=22, pady=10)
        btn_run.bind("<Button>", lambda e: run())
        btn_run.pack(in_=mid)

    def switch_to_tab(self, i):
        tab_id = self.tabs.tabs()[i]
        self.tabs.select(tab_id)

    def update_summary(self):
        txt = "(You are searching for a " + ("proof that " if self.inst.action == "tp" else
                                             ("proof or refutation that " if self.inst.action == "tt" else
                                              "structure in which "))
        txt += (str(self.inst.conclusion) if self.inst.conclusion else "...") + " is "
        txt += ("true in all structures" if self.inst.action == "tp" or self.inst.action == "tt" else (
            "true" if self.inst.action == "mg" else "false"))
        if self.inst.premises:
            txt += ("\n in which " if self.inst.action == "tp" or self.inst.action == "tt" else " and ") + \
                   ", ".join([str(fml) for fml in self.inst.premises]) + " is true"
        txt += ".)"
        self.lbl_sum.config(text=txt)

    def run(self):
        tableau = __import__("tableau")
        concl = self.inst.conclusion
        premises = self.inst.premises
        axioms = self.inst.axioms

        # settings

        classical = True if self.inst.logic["classint"] == "class" else False
        propositional = True if self.inst.logic["proppred"] == "prop" else False
        modal = True if self.inst.logic["modal"] == "modal" else False
        vardomains = True if self.inst.logic["constvar"] == "var" else False
        frame = self.inst.logic["frame"]

        latex = True if self.inst.output == "tex" else False
        num_models = self.inst.num_models
        underline_open = True if self.inst.underline_open else False
        hide_nonopen = True if self.inst.hide_nonopen else False

        if self.inst.action != "tt":
            validity = True if self.inst.action == "tp" else False
            satisfiability = True if self.inst.action == "mg" else False

            tableau.Tableau(concl, premises=premises, axioms=axioms,
                            validity=validity, satisfiability=satisfiability,
                            classical=classical, propositional=propositional,
                            modal=modal, vardomains=vardomains, frame=frame,
                            latex=latex, file=True, num_models=num_models,
                            underline_open=underline_open, hide_nonopen=hide_nonopen)

        else:
            # test if theorem
            tab1 = tableau.Tableau(concl, premises=premises, axioms=axioms,
                                   validity=True, satisfiability=False,
                                   classical=classical, propositional=propositional,
                                   modal=modal, vardomains=vardomains, frame=frame,
                                   latex=latex, file=True, silent=True, num_models=num_models,
                                   underline_open=underline_open, hide_nonopen=hide_nonopen)

            if not tab1.infinite():
                tab1.show()
            else:
                tab2 = tableau.Tableau(concl, premises=premises, axioms=axioms,
                                       validity=False, satisfiability=False,
                                       classical=classical, propositional=propositional,
                                       modal=modal, vardomains=vardomains, frame=frame,
                                       latex=latex, file=True, silent=True, num_models=num_models,
                                       underline_open=underline_open, hide_nonopen=hide_nonopen)
                if not tab2.infinite():
                    tab2.show()


if __name__ == "__main__":
    PyPLGUI()
