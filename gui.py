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
gray = "#404040"
lightgray = "#737373"
font = "-family {Arial} -size 12 -weight normal -slant roman -underline 0 -overstrike 0"


class PyPLGUI(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()

        # general settings
        self.root.title("pyPL")
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file='icon.png'))
        self.root.geometry("713x480")

        # style
        self.style = ttk.Style()
        for widget in [".", "TFrame", "TNotebook", "TNotebook.Tab", "TLabel"]:
            self.style.configure(widget, background=white, foreground=black, font=font)
        self.style.map("TNotebook.Tab",
                       background=[("selected", gray), ("active", lightgray)],
                       foreground=[("selected", white), ("active", white)]
                       # font=[("selected", ("Arial", "12", "bold"))]
                       )
        self.root.configure(bg=white)
        self.root.option_add("*Font", "Arial 12")

        # invoke
        super().__init__(self.root)
        self.inst = PyPLInst()
        self.pack()
        self.win_main()
        self.mainloop()

    def win_main(self):
        self.main = ttk.Notebook(self.root)
        tabs = [
            "Start",
            "1. Pick your settings",
            "2. Choose your task",
            "3. Select your logic",
            "4. Specify your input",
            "5. Run"
        ]
        # add tabs
        for i, tab in enumerate(tabs):
            self.main.add(ttk.Frame(self.main, style="TFrame"), text=tab)
        # build tabs
        for i, tab in enumerate(tabs):
            getattr(self, "tab_" + str(i))()
        self.main.pack(expand=0, fill="both")

    def tab_0(self):  # 0. Start
        tab = self.main.nametowidget(self.main.tabs()[0])

        # welcome message
        lbl_greeting = ttk.Label(tab,
                                 text="Welcome to pyPL.",
                                 font=("Arial", "12", "bold")) \
            .pack(pady=10)

        # next tabs
        btn_next = tk.Button(tab,
                             text=">> 1. Pick your settings",
                             bg=gray, fg=white,
                             width=20, pady=10)
        btn_next.bind("<Button>", lambda e: self.switch_to_tab(1))
        btn_next.pack(pady=5)

        btn_step2 = tk.Button(tab, text="2. Choose your task", width=20, pady=10)
        btn_step2.bind("<Button>", lambda e: self.switch_to_tab(2))
        btn_step2.pack(pady=5)

        btn_step3 = tk.Button(tab, text="3. Select your logic", width=20, pady=10)
        btn_step3.bind("<Button>", lambda e: self.switch_to_tab(3))
        btn_step3.pack(pady=5)

        btn_step4 = tk.Button(tab, text="4. Specify your input", width=20, pady=10)
        btn_step4.bind("<Button>", lambda e: self.switch_to_tab(4))
        btn_step4.pack(pady=5)

        btn_step5 = tk.Button(tab, text="5. Run", width=20, pady=10)
        btn_step5.bind("<Button>", lambda e: self.switch_to_tab(5))
        btn_step5.pack(pady=5)

        # info
        lbl_info = tk.Label(tab,
                            text="🛈 https://github.com/nclarius/pyPL") \
            .pack(pady=20)

    def tab_1(self):  # 1. Settings
        tab = self.main.nametowidget(self.main.tabs()[1])

        def initial_select_rb(rb):
            rb.config(fg=white)

        def select_rb(rb):
            rb.config(fg=white)
            for rb_ in radiobuttons:
                if rb_ != rb:
                    rb_.config(fg=black)
            btn_set.config(state="normal", bg=gray, fg=white)
            btn_reset.config(state="normal")

        def select_entry():
            btn_set.config(state="normal", bg=gray, fg=white)
            btn_reset.config(state="normal")

        def reset():
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.completed.remove(1)
            self.inst.output = None
            btn_set.config(state="disabled", bg=white, fg=black)
            btn_next.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.output = output.get()
            self.inst.num_models = int(num_models.get())
            self.inst.completed.append(1)
            btn_next.config(state="normal", bg=gray, fg=white)

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
        bot = tk.Frame(tab)
        bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        bot1 = tk.Frame(bot)
        bot2 = tk.Frame(bot)
        bot1.pack(ipadx=20)
        bot2.pack(pady=5)

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
                                selectcolor=lightgray,  # todo foreground color white when selected
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
        num_models.trace("w", lambda args: select_entry())

        # reset button
        btn_reset = tk.Button(tab,
                              text="Reset",
                              state="normal" if self.inst.action else "disabled",
                              width=7, pady=10)
        btn_reset.bind("<Button>", lambda e: reset())
        btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            state="normal" if self.inst.action else "disabled",
                            width=7, pady=10)
        mid.pack()
        btn_set.bind("<Button>", lambda e: set())
        btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 2. Choose your task",
                             state="normal" if self.inst.action else "disabled",
                             bg=gray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step(2))
        btn_next.pack(in_=bot2)

    def tab_2(self):  # 2. Action
        tab = self.main.nametowidget(self.main.tabs()[2])

        def initial_select_rb(rb):
            rb.config(fg=white)

        def select_rb(rb):
            rb.config(fg=white)
            for rb_ in radiobuttons:
                if rb_ != rb:
                    rb_.config(fg=black)
            btn_set.config(state="normal", bg=gray, fg=white)
            btn_reset.config(state="normal")

        def reset():
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.completed.remove(1)
            self.inst.action = None
            btn_set.config(state="disabled", bg=white, fg=black)
            btn_next.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.action = action.get()
            self.inst.completed.append(1)
            btn_next.config(state="normal", bg=gray, fg=white)

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
        bot = tk.Frame(tab)
        bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        bot1 = tk.Frame(bot)
        bot2 = tk.Frame(bot)
        bot1.pack(ipadx=20)
        bot2.pack(pady=5)

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
                                selectcolor=lightgray,
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
        btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            state="normal" if self.inst.action else "disabled",
                            width=7, pady=10)
        btn_set.bind("<Button>", lambda e: set())
        btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 3. Select your logic",
                             state="normal" if self.inst.action else "disabled",
                             bg=gray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step(3))
        btn_next.pack(in_=bot2)

    def tab_3(self):  # 3. Logic
        tab = self.main.nametowidget(self.main.tabs()[3])

        def initial_select_rb(rb):
            rb.config(fg=white)

        def select_rb(rb):
            rb.config(fg=white)
            for rb_ in radiobuttons:
                if rb_ != rb:
                    rb_.config(fg=black)
            btn_set.config(state="normal", bg=gray, fg=white)
            btn_reset.config(state="normal")

        def reset():
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.completed.remove(1)
            self.inst.action = None
            btn_set.config(state="disabled", bg=white, fg=black)
            btn_next.config(state="disabled", bg=white, fg=black)

        def set():
            self.inst.logic = {var: val for (var, val) in variables.items()}
            self.inst.completed.append(1)
            btn_next.config(state="normal", bg=gray, fg=white)

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
        bot = tk.Frame(tab)
        bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        bot1 = tk.Frame(bot)
        bot2 = tk.Frame(bot)
        bot1.pack(ipadx=20)
        bot2.pack(pady=5)

        # heading
        lbl_head = tk.Label(tab,
                            text="Which logic are you working in?",
                            font=("Arial", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # selection
        # todo only display relevant categories
        radiobuttons = []
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
        for i, cat in enumerate(categories):
            for j, (txt, val) in enumerate(labels[cat]):
                rb = tk.Radiobutton(tab,
                                    text=txt,
                                    variable=variables[cat],
                                    value=val,
                                    selectcolor=lightgray,
                                    indicatoron=0,
                                    width=20, pady=7.5)
                rb.config(command=lambda arg=rb: select_rb(arg))
                if val == self.inst.logic:
                    initial_select_rb(rb)
                rb.pack(in_=mids[i], side=(tk.LEFT if j == 0 else tk.RIGHT))
                radiobuttons.append(rb)

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
        btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            bg=gray if self.inst.logic else white,
                            fg=white if self.inst.logic else black,
                            state="normal" if self.inst.logic else "disabled",
                            width=7, pady=10)
        btn_set.bind("<Button>", lambda e: set())
        btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 4. Specify your input",
                             state="normal" if self.inst.action else "disabled",
                             bg=gray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step(4))
        btn_next.pack(in_=bot2)

    def tab_4(self):  # 4. Input
        tab = self.main.nametowidget(self.main.tabs()[4])

        def select_entry():
            btn_set.config(state="normal", bg=gray, fg=white)
            btn_reset.config(state="normal")

        def parse(raw_fml, field):
            parser = __import__("parser")
            parsed_fml = parser.Parser().parse(raw_fml.get())
            field.configure(text=str(parsed_fml))

        def reset():
            fld_concl.configure(text="—")
            entry_concl.delete(first=0)
            self.inst.completed.remove(3)
            btn_set.config(state="disabled", bg=white, fg=black)

        def set():
            parser = __import__("parser")
            self.inst.conclusion = parser.Parser().parse(concl.get())
            self.inst.completed.append(3)

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
        mids = {i: tk.Frame(mid) for i in range(3)}
        for i in mids:
            mids[i].pack(ipadx=5, ipady=5)
        # bot
        bot = tk.Frame(tab)
        bot.pack(side=tk.BOTTOM, pady=10, ipady=5)
        bot1 = tk.Frame(bot)
        bot2 = tk.Frame(bot)
        bot1.pack(ipadx=20)
        bot2.pack(pady=5)

        # heading
        lbl_head = tk.Label(tab,
                            text="What would you like to analyze?",
                            font=("Arial", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)
            # .grid(row=0, columnspan=4, sticky="NESW")

        # input fields
        entries = []

        # conclusion
        concl = tk.StringVar()
        lbl_concl = tk.Label(tab, text="Conclusion:")
        lbl_concl.pack(in_=mids[0], side=tk.LEFT)
        # lbl_concl.grid(row=1, column=0, sticky=tk.W, padx=5)
        fld_concl = tk.Label(tab, text="—")
        fld_concl.pack(in_=mids[1], side=tk.LEFT)
        # fld_concl.grid(row=1, column=1, sticky=tk.W)
        entry_concl = tk.Entry(tab,
                               textvariable=concl,
                               width=50)
        entry_concl.pack(in_=mids[2], side=tk.LEFT)
        # entry_concl.grid(row=2, column=1, sticky=tk.W)
        btn_concl_set = tk.Label(tab, text="Parse", bg=gray, fg=white)
        btn_concl_set.pack(in_=mids[2], side=tk.LEFT, padx=5)
        # btn_concl_set.grid(row=2, column=2, padx=5, stick=tk.W)
        btn_concl_set.bind("<Button>", lambda e: parse(concl, fld_concl))
        entries.append(entry_concl)
        concl.trace("w", lambda args: select_entry())

        # reset button
        btn_reset = tk.Button(tab,
                              text="Reset",
                              width=7, pady=10)
        btn_reset.bind("<Button>", lambda e: reset())
        btn_reset.pack(in_=bot1, side=tk.LEFT)

        # set button
        btn_set = tk.Button(tab,
                            text="Set",
                            bg=gray if self.inst.conclusion else white,
                            fg=white if self.inst.conclusion else black,
                            state="normal" if self.inst.conclusion else "disabled",
                            width=7, pady=10)
        btn_set.bind("<Button>", lambda e: set())
        btn_set.pack(in_=bot1, side=tk.RIGHT)

        # next tab button
        btn_next = tk.Button(tab,
                             text=">> 5. Run",
                             bg=gray if self.inst.action else white,
                             fg=white if self.inst.action else black,
                             width=22, pady=10)
        btn_next.bind("<Button>", lambda e: next_step(5))
        btn_next.pack(in_=bot2)

    def tab_5(self):
        tab = self.main.nametowidget(self.main.tabs()[5])

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
                            bg=gray, fg=white,
                            width=22, pady=10)
        btn_run.bind("<Button>", lambda e: run())
        btn_run.pack(in_=mid)

    def switch_to_tab(self, i):
        tab_id = self.main.tabs()[i]
        self.main.select(tab_id)

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
