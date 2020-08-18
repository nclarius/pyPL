#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Graphical interface.
CURRENTLY UNDER CONSTRUCTION.
"""

import tkinter as tk

blue = "#2493ff"
green = "#52c462"
red = "#bf5050"
yellow = "#ffb94f"


class PyPL:

    def __init__(self):
        self.action = None
        self.logic = None
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
        self.root.geometry("600x300")

        # application settings
        self.root.option_add("*Font", "LiberationSans 11")

        # main window contents
        lbl_greeting = tk.Label(
            text="Welcome to pyPL.") \
            .pack(pady=10)

        # Step 1
        btn_step1 = tk.Button(self.root,
                              text="1. Choose your task.",
                              width=20, pady=10)
        btn_step1.bind("<Button>", lambda e: self.step_1())
        btn_step1.pack(pady=5)
        self.btn_step1 = btn_step1

        # Step 2
        btn_step2 = tk.Button(
            text="2. Select your logic.",
            width=20, pady=10)
        btn_step2.bind("<Button>", lambda e: self.step_2())
        btn_step2.pack(pady=5)

        # Step 3
        btn_step3 = tk.Button(
            text="3. Specify your input.",
            width=20, pady=10)
        btn_step3.bind("<Button>", lambda e: self.step_3())
        btn_step3.pack(pady=5)

        # Go
        but_go = tk.Button(
            text="Go!",
            state="disabled",  # todo activate when all steps completed
            width=20, pady=10) \
            .pack(pady=15)

    def step_1(self):
        default_bg = self.root.cget("bg")

        step1 = tk.Toplevel(self.root)
        step1.title("1. Choose your task — pyPL")
        step1.tk.call('wm', 'iconphoto', step1._w, tk.PhotoImage(file='icon.png'))
        step1.geometry("600x300")

        def select_action():
            btn_ok.config(state="normal", bg=blue)
            btn_reset.config(state="normal")

        def reset_action():
            for radiobutton in radiobuttons:
                radiobutton.deselect()
            self.inst.action = None
            btn_ok.config(state="disabled", bg=default_bg)
            self.btn_step1.config(bg=default_bg)

        def cancel_action():
            step1.destroy()

        def save_action():
            self.inst.action = action.get()
            self.btn_step1.config(bg=green)
            step1.destroy()

        # frames
        top = tk.Frame(step1)
        bot = tk.Frame(step1)
        top.pack(side=tk.TOP)
        bot.pack(side=tk.BOTTOM, ipadx=25, expand=True)

        lbl = tk.Label(step1,
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
                                command=select_action,
                                indicatoron=0,
                                width=20, pady=7.5)
            rb.pack(in_=top, pady=5)
            radiobuttons.append(rb)

        # cancel button
        btn_cancel = tk.Button(step1,
                               text="Cancel")
        btn_cancel.bind("<Button>", lambda e: cancel_action())
        btn_cancel.pack(in_=bot, side=tk.LEFT)

        # reset button
        btn_reset = tk.Button(step1,
                              text="Reset",
                              bg=yellow if self.inst.action else default_bg,
                              state="normal" if self.inst.action else "disabled")
        btn_reset.bind("<Button>", lambda e: reset_action())
        btn_reset.pack(in_=bot, side=tk.RIGHT)

        # OK button
        btn_ok = tk.Button(step1,
                           text="OK",
                           state="normal" if self.inst.action else "disabled")
        btn_ok.bind("<Button>", lambda e: save_action())
        btn_ok.pack(in_=bot)

        pass

    def step_2(self):
        pass

    def step_3(self):
        pass


if __name__ == "__main__":
    app = Application(tk.Tk())
    app.mainloop()
