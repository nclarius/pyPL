#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Graphical interface.
CURRENTLY UNDER CONSTRUCTION.
"""

import tkinter as tk

white = "#ffffff"
black = "#000000"
blue = "#2493ff"
green = "#52c462"
red = "#bf5050"
yellow = "#ffb94f"
lightgray = "#f5f5f5"
lightblue = "#6bb5ff"


class PyPL:

    def __init__(self):
        self.completed = []

        # todo implement settings
        self.action = "mg"
        self.logic = {"proppred": "pred", "classint": "class", "modal": "nonmodal", "constvar": "var", "frame": "K"}
        self.structure = None
        self.axioms = None
        self.premises = None
        self.conclusion = None


class Application(tk.Frame):

    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.inst = PyPL()
        self.pack()
        self.main_window()

    def main_window(self):
        # main window
        self.root.title("pyPL")
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file='icon.png'))
        self.root.geometry("600x350")

        # application settings
        self.root.option_add("*Font", "LiberationSans 11")
        self.root.configure(bg=white)

        # main window contents
        lbl_greeting = tk.Label(
            text="Welcome to pyPL.") \
            .pack(pady=10)

        # Step 1
        btn_step1 = tk.Button(self.root,
                              text="1. Choose your task",
                              width=20, pady=10)
        btn_step1.bind("<Button>", lambda e: self.step_1())
        btn_step1.pack(pady=5)
        self.btn_step1 = btn_step1

        # Step 2
        btn_step2 = tk.Button(
            text="2. Select your logic",
            width=20, pady=10)
        btn_step2.bind("<Button>", lambda e: self.step_2())
        btn_step2.pack(pady=5)
        self.btn_step2 = btn_step2

        # Step 3
        btn_step3 = tk.Button(
            text="3. Specify your input",
            width=20, pady=10)
        btn_step3.bind("<Button>", lambda e: self.step_3())
        btn_step3.pack(pady=5)
        self.btn_step3 = btn_step3

        # Go
        state = "disabled",  # todo only enable when all steps completed
        btn_go = tk.Button(
            text="Go!",
            bg=blue,
            fg=white,
            width=20, pady=10)
        btn_go.bind("<Button>", lambda e: self.go())
        btn_go.pack(pady=15)
        self.btn_go = btn_go

        # Info
        lbl_info = tk.Label(
            text="🛈 https://github.com/nclarius/pyPL") \
            .pack(pady=20)
        self.lbl_info = lbl_info

    def step_1(self):

        def select():
            btn_ok.config(state="normal", bg=blue, fg=white)
            btn_reset.config(state="normal")

        def reset():
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.completed.remove(1)
            self.inst.action = None
            btn_ok.config(state="disabled", bg=white, fg=black)
            self.btn_step1.config(bg=white, fg=black)

        def cancel():
            step1.destroy()

        def save():
            self.inst.action = action.get()
            self.inst.completed.append(1)
            self.update_buttons()
            self.btn_step1.config(bg=green, fg=white)
            step1.destroy()

        # window
        step1 = tk.Toplevel()
        step1.title("1. Choose your task — pyPL")
        step1.tk.call('wm', 'iconphoto', step1._w, tk.PhotoImage(file='icon.png'))
        step1.geometry("600x300")

        # frames
        top = tk.Frame(step1)
        bot = tk.Frame(step1)
        top.pack(side=tk.TOP)
        bot.pack(side=tk.BOTTOM, ipadx=25, expand=True)

        # heading
        lbl_step1 = tk.Label(step1,
                             text="What would you like to do?",
                             pady=7.5,
                             justify=tk.LEFT) \
            .pack(in_=top)

        # radio buttons
        action = tk.StringVar(None, self.inst.action)
        actions = [("Model checking", "mc"), ("Model generation", "mg"), ("Theorem proving", "tp")]
        radiobuttons = []
        for txt, val in actions:
            rb = tk.Radiobutton(step1,
                                text=txt,
                                variable=action,
                                value=val,
                                command=select,
                                bg=lightgray,
                                selectcolor=lightblue,
                                indicatoron=0,
                                width=20, pady=7.5)
            rb.pack(in_=top, pady=5)
            radiobuttons.append(rb)

        # cancel button
        btn_cancel = tk.Button(step1,
                               text="Cancel")
        btn_cancel.bind("<Button>", lambda e: cancel())
        btn_cancel.pack(in_=bot, side=tk.LEFT)

        # reset button
        btn_reset = tk.Button(step1,
                              text="Reset",
                              state="normal" if self.inst.action else "disabled")
        btn_reset.bind("<Button>", lambda e: reset())
        btn_reset.pack(in_=bot, side=tk.RIGHT)

        # OK button
        btn_ok = tk.Button(step1,
                           text="OK",
                           state="normal" if self.inst.action else "disabled")
        btn_ok.bind("<Button>", lambda e: save())
        btn_ok.pack(in_=bot)

    def step_2(self):

        def select():
            lbl_summ.config(text=(
                    ("classical" if variables["classint"].get() == "class" else "intuitionistic") + " " +
                    ("non-modal" if variables["modal"].get() == "nonmodal" else "modal") + " " +
                    ("predicate" if variables["proppred"].get() == "pred" else "propositional") + " " +
                    "logic" +
                    ((" with " + ("varying" if variables["constvar"].get() == "var" else "constant") +
                      " domains" if variables["proppred"].get() == "pred" else "") +
                     " in a " + variables["frame"].get() + " frame"
                     if variables["modal"].get() == "modal" else "")
            ))

        def reset():
            # todo reset to default instead of empty selection?
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.logic = None
            self.inst.completed.remove(2)
            btn_ok.config(state="disabled", bg=white, fg=black)
            self.btn_step2.config(bg=white, fg=black)

        def cancel():
            step2.destroy()

        def save():
            self.inst.logic = {cat: variables[cat].get() for cat in categories}
            self.inst.completed.append(2)
            self.update_buttons()
            self.btn_step2.config(bg=green, fg=white)
            step2.destroy()

        # window
        step2 = tk.Toplevel()
        step2.title("2. Select your logic — pyPL")
        step2.tk.call('wm', 'iconphoto', step2._w, tk.PhotoImage(file='icon.png'))
        step2.geometry("600x400")

        # frames
        top = tk.Frame(step2)
        mid = tk.Frame(step2)
        mids = {i: tk.Frame(mid) for i in range(5)}
        bot = tk.Frame(step2)
        top.pack(side=tk.TOP, ipady=5)
        mid.pack(pady=5)
        for i in mids:
            mids[i].pack(ipadx=5, ipady=5)
        bot.pack(side=tk.BOTTOM, pady=10, ipadx=25, expand=True)

        # heading
        lbl_step2 = tk.Label(step2,
                             text="Which logic are you working in?",
                             pady=7.5,
                             justify=tk.LEFT) \
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
                rb = tk.Radiobutton(step2,
                                    text=txt,
                                    variable=variables[cat],
                                    value=val,
                                    command=select,
                                    bg=lightgray,
                                    selectcolor=lightblue,
                                    indicatoron=0,
                                    width=20, pady=7.5)
                rb.pack(in_=mids[i], side=(tk.LEFT if j == 0 else tk.RIGHT))
                radiobuttons.append(rb)

        # summary
        lbl_summ = tk.Label(step2)
        select()
        # lbl_summ.pack(in_=botmid)

        # cancel button
        btn_cancel = tk.Button(step2,
                               text="Cancel")
        btn_cancel.bind("<Button>", lambda e: cancel())
        btn_cancel.pack(in_=bot, side=tk.LEFT)

        # reset button
        btn_reset = tk.Button(step2,
                              text="Reset",
                              state="normal" if self.inst.logic else "disabled")
        btn_reset.bind("<Button>", lambda e: reset())
        btn_reset.pack(in_=bot, side=tk.RIGHT)

        # OK button
        btn_ok = tk.Button(step2,
                           text="OK",
                           bg=blue if self.inst.logic else white,
                           fg=white if self.inst.logic else black,
                           state="normal" if self.inst.logic else "disabled")
        btn_ok.bind("<Button>", lambda e: save())
        btn_ok.pack(in_=bot)

    def step_3(self):

        def reset():
            for entry in entries:
                entry.delete()
            self.inst.completed.remove(3)
            btn_ok.config(state="disabled", bg=white, fg=black)
            self.btn_step2.config(bg=white, fg=black)

        def cancel():
            step3.destroy()

        def save():
            self.inst.conclusion = concl.get()
            self.inst.completed.append(3)
            self.update_buttons()
            self.btn_step3.config(bg=green, fg=white)
            step3.destroy()

        # window
        step3 = tk.Toplevel()
        step3.title("3. Specify your input — pyPL")
        step3.tk.call('wm', 'iconphoto', step3._w, tk.PhotoImage(file='icon.png'))
        step3.geometry("600x300")

        # frames
        top = tk.Frame(step3)
        bot = tk.Frame(step3)
        top.pack(side=tk.TOP)
        bot.pack(side=tk.BOTTOM, ipadx=25, expand=True)

        # heading
        lbl_step3 = tk.Label(step3,
                             text="What would you like to analyze?",
                             pady=7.5,
                             justify=tk.LEFT) \
            .pack(in_=top)

        # input fields
        entries = []

        # conclusion
        concl = tk.StringVar()
        lbl_concl = tk.Label(step3,
                             text="Conclusion")
        lbl_concl.pack(side=tk.LEFT)
        entry_concl = tk.Entry(step3,
                               textvariable=concl,
                               width=50)
        entry_concl.pack(side=tk.RIGHT)
        entries.append(entry_concl)

        # cancel button
        btn_cancel = tk.Button(step3,
                               text="Cancel")
        btn_cancel.bind("<Button>", lambda e: cancel())
        btn_cancel.pack(in_=bot, side=tk.LEFT)

        # reset button
        btn_reset = tk.Button(step3,
                              text="Reset")
        btn_reset.bind("<Button>", lambda e: reset())
        btn_reset.pack(in_=bot, side=tk.RIGHT)

        # OK button
        btn_ok = tk.Button(step3,
                           text="OK",
                           bg=blue,
                           fg=white,
                           state="normal" if self.inst.logic else "disabled")
        btn_ok.bind("<Button>", lambda e: save())
        btn_ok.pack(in_=bot)

    def update_buttons(self):
        pass
        # if len(self.inst.completed) == 3:
        #     self.btn_go.config(bg=blue, fg=white)
        # else:
        #     self.btn_go.config(bg=white, fg=black)

    def go(self):
        tableau = __import__("tableau")
        parser = __import__("parser")
        concl = parser.Parser().parse(self.inst.conclusion)
        tab = tableau.Tableau(concl, validity=False)

if __name__ == "__main__":
    app = Application(tk.Tk())
    app.mainloop()
