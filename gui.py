#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Graphical interface.
CURRENTLY UNDER CONSTRUCTION.
"""

import tkinter as tk
from tkinter import ttk


class PyPLInst:

    def __init__(self):
        self.completed = []

        self.action = "mg"
        self.structure = None
        self.conclusion = None
        self.axioms = []
        self.premises = []
        self.logic = {"proppred": "pred", "classint": "class", "modal": "nonmodal", "constvar": "var", "frame": "K"}
        self.output = "tex"
        self.num_models = 1


# style
white = "#ffffff"
black = "#000000"
green = "#52c462"
red = "#bf5050"
yellow = "#ffb94f"
# blue = "#2493ff"
# lightblue = "#80ccff"
darkgray = "#333333"  # todo distinguish clickable buttons from selected radiobuttons?
lightgray = "#666666"
font = "-family {Arial} -size 12 -weight normal -slant roman -underline 0 -overstrike 0"


# todo config file for default settings

class PyPLGUI(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()

        # general settings
        self.root.title("pyPL")
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file='icon.png'))
        self.root.geometry("715x485")

        # style
        self.style = ttk.Style()
        for widget in [".", "TFrame", "TNotebook", "TNotebook.Tab", "TLabel"]:
            self.style.configure(widget, background=white, foreground=black, font=font)
        self.style.map("TNotebook.Tab",
                       background=[("selected", darkgray), ("active", lightgray)],
                       foreground=[("selected", white), ("active", white)]
                       # font=[("selected", ("Arial", "12", "bold"))]
                       )  # todo no rounded corners for tabs
        self.style.theme_settings("default", {"TNotebook.Tab": {"configure": {"padding": [10, 10]}}})
        self.root.configure(bg=white)
        self.root.option_add("*Font", "Arial 12")

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
            "1. Pick your settings",
            "2. Choose your task",
            "3. Select your logic",
            "4. Specify your input"
            # "5. Run"
        ]
        # add tabs
        for i, tab in enumerate(tabs):
            self.tabs.add(ttk.Frame(self.tabs, style="TFrame"), text=tab)
        # build tabs
        for i, tab in enumerate(tabs):
            getattr(self, "tab_" + str(i))()
        self.tabs.pack(expand=0, fill="both")

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
                                 font=("Arial", "12", "bold")) \
            .pack(pady=10)

        # next tabs
        btn_next = tk.Button(tab,
                             text=">> 1. Pick your settings",
                             bg=darkgray, fg=white,
                             width=20, pady=10)
        btn_next.bind("<Button>", lambda e: self.switch_to_tab(1))
        # btn_next.pack(pady=5)

        btn_step1 = tk.Button(tab,
                              text="1. Pick your settings",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step1.bind("<Button>", lambda e: self.switch_to_tab(1))
        btn_step1.pack(pady=5)

        btn_step2 = tk.Button(tab,
                              text="2. Choose your task",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step2.bind("<Button>", lambda e: self.switch_to_tab(2))
        btn_step2.pack(pady=5)

        btn_step3 = tk.Button(tab,
                              text="3. Select your logic",
                              activebackground=lightgray, activeforeground=white,

                              width=20, pady=10)
        btn_step3.bind("<Button>", lambda e: self.switch_to_tab(3))
        btn_step3.pack(pady=5)

        btn_step4 = tk.Button(tab,
                              text="4. Specify your input",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step4.bind("<Button>", lambda e: self.switch_to_tab(4))
        btn_step4.pack(pady=5)

        btn_step5 = tk.Button(tab,
                              text="5. Run",
                              activebackground=lightgray, activeforeground=white,
                              width=20, pady=10)
        btn_step5.bind("<Button>", lambda e: self.switch_to_tab(5))
        # btn_step5.pack(pady=5)

    def tab_1(self):  # 1. Settings
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

        def select_entry():
            btn_set.config(state="normal", bg=darkgray, fg=white)
            btn_reset.config(state="normal")
            set()

        def reset():
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.completed.remove(1)
            self.inst.output = None
            btn_set.config(state="disabled", bg=white, fg=black)
            btn_next.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.output = output.get()
            if num_models.get():
                self.inst.num_models = int(num_models.get())
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
                            text="How would you like pyPL to work?",
                            font=("Arial", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # output format
        output = tk.StringVar(None, self.inst.output)
        lbl_output = tk.Label(tab,
                              text="Output format:")
        lbl_output.pack(in_=mid1)
        outputs = [("LaTeX PDF", "tex"), ("plain text", "txt")]
        radiobuttons = []
        for i, (txt, val) in enumerate(outputs):
            rb = tk.Radiobutton(tab,
                                text=txt,
                                variable=output,
                                value=val,
                                selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                indicatoron=0,
                                width=25, pady=7.5)
            rb.pack(in_=mid1, side=(tk.LEFT if i == 0 else tk.RIGHT), pady=5)
            rb.config(command=lambda arg=rb: select_rb(arg))
            if val == self.inst.output:
                initial_select_rb(rb)
            radiobuttons.append(rb)

        # number of models to generate
        num_models = tk.StringVar(None, self.inst.num_models)
        lbl_num_models = tk.Label(tab,
                                  text="Number of models to generate in model generation:")
        lbl_num_models.pack(in_=mid2)
        ent_num_models = tk.Entry(tab,
                                  textvariable=num_models,
                                  justify=tk.RIGHT,
                                  width=2)
        ent_num_models.pack(in_=mid2)
        num_models.trace("w", lambda *args: select_entry())

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

    def tab_2(self):  # 2. Action
        tab = self.tabs.nametowidget(self.tabs.tabs()[2])

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
                            font=("Arial", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # radio buttons
        action = tk.StringVar(None, self.inst.action)
        actions = [("Model checking", "mc"), ("Model generation", "mg"), ("Counter model generation", "cmg"),
                   ("Theorem proving", "tp")]  # todo implement MC
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
                            font=("Arial", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # selection
        # todo only display relevant categories
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
        btn_next.bind("<Button>", lambda e: next_step(4))
        # btn_next.pack(in_=bot2)

    def tab_4(self):  # 4. Input
        # todo make scrollable

        tab = self.tabs.nametowidget(self.tabs.tabs()[4])

        def add_formula():
            # variable
            raw = tk.StringVar()
            raws.append(raw)
            fmls.append(raw)
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
                rem.bind("<Button>", lambda e: remove_formula(i))
            else:
                rem = None
            rems.append(rem)
            # formula in plain text
            lbl = tk.Label(tab, text="...")
            lbl.pack(in_=mids[row + 1], side=tk.LEFT)
            lbls.append(lbl)
            # entry field
            ent = tk.Entry(tab,
                           textvariable=raw,
                           width=50)
            ent.pack(in_=mids[row + 2], side=tk.LEFT)
            raw.trace("w", lambda *args: select_entry(i))
            ents.append(ent)
            # parse button
            btn = tk.Button(tab,
                            text="Parse",
                            # bg=darkgray, fg=white,
                            activebackground=lightgray, activeforeground=white,
                            state="disabled")
            btn.pack(in_=mids[row + 2], side=tk.LEFT, padx=5)
            btn.bind("<Button>", lambda e: parse(i))
            btns.append(btn)

        def remove_formula(i):
            # todo doesn't always work; indexes not updated correctly?
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
            field = lbls[i]
            parser = __import__("parser")
            fml, mode = parser.Parser().parse_(raw.get())
            fmls[i] = fml
            field.configure(text=str(fml))
            if i == 0:
                set_mode(mode)
            set()

        def set_mode(mode):
            mode_map = {
                "classical": ("classint", "class", "int"),
                "propositional": ("proppred", "prop", "pred"),
                "modal": ("modal", "modal", "nonmodal"),
                "vardomains": ("constvar", "var", "const")
            }
            for md in mode_map:
                cat, val1, val2 = mode_map[md]
                if mode[md]:
                    self.rbs_logic[cat][val1].invoke()
                    # self.rbs_logic[cat][val1].select()
                    # self.rbs_logic[cat][val2].deselect()
                    # select_rb((self.rbs_logic[cat][val1], cat))
                else:
                    self.rbs_logic[cat][val2].invoke()
                    # self.rbs_logic[cat][val2].select()
                    # self.rbs_logic[cat][val1].deselect()
                    # select_rb((self.rbs_logic[cat][val2], cat))

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
                            font=("Arial", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)
        # .grid(row=0, columnspan=4, sticky="NESW")

        # summary
        self.lbl_sum = tk.Label()
        self.lbl_sum.pack(in_=mids[0])

        # input fields
        fmls = []
        raws = []
        caps = []
        lbls = []
        rems = []
        ents = []
        btns = []

        # conclusion
        add_formula()
        self.update_summary()

        # premise heading and add premise button
        lbl_prem = tk.Label(tab, text="Premises:")
        lbl_prem.pack(in_=mids[4], side=tk.LEFT)
        btn_add_prem = tk.Button(tab,
                                 text="+",
                                 activebackground=lightgray, activeforeground=white)
        btn_add_prem.pack(in_=mids[4], side=tk.RIGHT)
        btn_add_prem.bind("<Button>", lambda e: add_formula())

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
                            font=("Arial", "12", "bold"),
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
        txt = "You are searching for a " + ("proof that " if self.inst.action == "tp" else "model in which ")
        txt += (str(self.inst.conclusion) if self.inst.conclusion else "...") + " is "
        txt += ("true in all structures" if self.inst.action == "tp" else (
               "true" if self.inst.action == "mg" else "false"))
        if self.inst.premises:
            txt += (" in which " if self.inst.action == "tp" else " and ") + \
                   ", ".join([str(fml) for fml in self.inst.premises]) + " is true"
        txt += "."
        self.lbl_sum.config(text=txt)

    def run(self):
        tableau = __import__("tableau")
        concl = self.inst.conclusion
        premises = self.inst.premises
        axioms = self.inst.axioms

        # settings
        validity = True if self.inst.action == "tp" else False
        satisfiability = True if self.inst.action == "mg" else False
        classical = True if self.inst.logic["classint"] == "class" else False
        propositional = True if self.inst.logic["proppred"] == "prop" else False
        modal = True if self.inst.logic["modal"] == "modal" else False
        vardomains = True if self.inst.logic["constvar"] == "var" else False
        frame = self.inst.logic["frame"]
        latex = True if self.inst.output == "tex" else False
        num_models = self.inst.num_models

        tableau.Tableau(concl, premises=premises, axioms=axioms,
                        validity=validity, satisfiability=satisfiability,
                        classical=classical, propositional=propositional,
                        modal=modal, vardomains=vardomains, frame=frame,
                        latex=latex, file=True, num_models=num_models)


if __name__ == "__main__":
    PyPLGUI()