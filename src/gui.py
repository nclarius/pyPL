#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Graphical interface.
"""

import os
from subprocess import DEVNULL, STDOUT, check_call
from datetime import datetime

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk

debug = False
if os.name == "posix" and os.uname()[1] == "montague" and os.getlogin() == "natalie":
    debug = True

class PyPLInst:

    def __init__(self):
        self.completed = []

        self.action = "tt"
        self.structure = None
        self.conclusion = None
        self.axioms = []
        self.premises = []
        self.formulas = []
        self.structure = None
        self.logic = {"proppred": "pred",
                      "classint": "class",
                      "modal": "nonmodal",
                      "valued": "twovalued",
                      "constvar": "var",
                      "locglob": "local",
                      "frame": "K",
                      "threeval": "weak"
                      }
        self.output = "tex"
        self.generation_mode = "mathematical"
        self.num_models = 1
        self.size_limit_factor = 2
        self.underline_open = True
        self.hide_nonopen = False
        self.stepwise = False


# style
white = "#ffffff"
black = "#000000"
# green = "#52c462"
# red = "#bf5050"
# yellow = "#ffb94f"
# blue = "#2493ff"
# lightblue = "#80ccff"
darkgray = "#404040"
lightgray = "#666666"
darkwhite = "#F5F5F5"
font = "-family {OpenSans} -size 12 -weight normal -slant roman -underline 0 -overstrike 0"
font_large = "-family {OpenSans} -size 14 -weight normal -slant roman -underline 0 -overstrike 0"


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                        scrollregion=canvas.bbox("all")
                )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=1000, height=500)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class Tooltip(object):
    # todo add info for keyboard shortcuts

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        widget.bind("<Enter>", lambda e: self.showtip())
        widget.bind("<Leave>", lambda e: self.hidetip())

    def showtip(self):
        if self.tipwindow or not self.text or not self.widget.bbox("insert"):
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = ttk.Label(tw, text=self.text, justify=tk.LEFT,
                      font=("OpenSans", "10", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class PyPLGUI(ttk.Frame):

    def __init__(self):
        self.root = tk.Tk()

        # general settings
        self.root.title("pyPL")
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file=icon_path))
        self.root.geometry("1333x750")

        # style
        self.style = ttk.Style()
        for widget in [".", "TFrame", "TNotebook", "TNotebook.Tab", "TLabel", "TButton"]:
            self.style.configure(widget, background=white, foreground=black, font=font)
        self.style.map("TNotebook.Tab",
                       background=[("selected", darkgray), ("active", lightgray)],
                       foreground=[("selected", white), ("active", white)]
                       # font=[("selected", ("OpenSans", "12", "bold"))]
                       )  # todo no rounded corners for tabs
        self.style.theme_settings("default", {
                "TNotebook":     {"configure": {"tabposition": "n", "borderwidth": 0}},
                "TNotebook.Tab": {"configure": {"padding": [10, 6.25]}}})
        # todo visually distinguish action buttons, radio buttons and check buttons?
        self.style.configure("Frame.TFrame", background=white)
        self.style.configure("Label.TLabel", background=white)
        self.style.configure("TabButton.TButton", activebackground=lightgray, activeforeground=white)
        self.style.configure("URLButton.TButton", backgroundg=white, borderwidth=0, highlightthickness=1)
        self.style.configure("ActionButton.TButton", background=darkgray, foreground=white, activebackground=lightgray, activeforeground=white)
        self.style.configure("ToolButton.TButton", background=darkgray, foreground=white, activebackground=lightgray, activeforeground=white)
        self.style.configure("RadioButton.TButton", background=darkgray, foreground=white, activebackground=lightgray, activeforeground=white)
        self.style.configure("CheckButton.TButton", background=darkgray, foreground=white, activebackground=lightgray, activeforeground=white)
        self.root.configure(bg=white)
        self.root.option_add("*Font", "NotoSans 12")

        # invoke
        super().__init__(self.root)
        self.inst = PyPLInst()
        self.pack()
        self.win_main()
        self.mainloop()

    def win_main(self):
        self.tabs = ttk.Notebook(self.root)
        tabs = [
                # "Start",
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
            getattr(self, "tab_" + str(i + 1))()
        self.tabs.pack(fill="both", expand=True)
        # self.tabs.grid(row=0, column=0)

        frm_run = ttk.Frame(self.root, style="Frame.TFrame", height=175)
        frm_run.pack(pady=10)

        # run button
        btn_run = ttk.Button(frm_run,
                            text="Run!",
                            style="ActionButton.TButton",
                            state="disabled",
                            width=22)
        btn_run.grid(ipady=10)
        btn_run.bind("<Button>", lambda e: self.run())
        btn_run.pack(in_=frm_run, pady=10)
        self.btn_run = btn_run
        # keyboard shortcut
        self.root.bind("<Control-Return>", lambda e: self.run())

        # info
        url = "https://github.com/nclarius/pyPL"
        lbl_info = ttk.Button(frm_run, text="🛈 " + url, style="URLButton.TButton")
        lbl_info.bind("<Button>", lambda e: check_call(["xdg-open", url], stdout=DEVNULL, stderr=STDOUT))
        lbl_info.pack(pady=10)

    def tab_0(self):  # 0. Start
        tab = self.tabs.nametowidget(self.tabs.tabs()[0])

        # welcome message
        lbl_greeting = ttk.Label(tab,
                                 text="Welcome to pyPL.",
                                 font=("OpenSans", "12", "bold")) \
            .pack(pady=10)

        # # next tabs
        # btn_next = ttk.Button(tab,
        #                      text=">> 1. Pick your settings",
        #                      style="TabButton",
        #                      width=20, pady=10)
        # btn_next.bind("<Button>", lambda e: self.switch_to_tab(1))
        # # btn_next.pack(pady=5)

        btn_step2 = ttk.Button(tab,
                              text="1. Choose your task",
                              style="TabButton",
                              width=20, pady=10)
        btn_step2.bind("<Button>", lambda e: self.switch_to_tab(1))
        btn_step2.pack(pady=5)

        btn_step3 = ttk.Button(tab,
                              text="2. Specify your input",
                              style="TabButton",
                              width=20, pady=10)
        btn_step3.bind("<Button>", lambda e: self.switch_to_tab(2))
        btn_step3.pack(pady=5)

        btn_step4 = ttk.Button(tab,
                              text="3. Select your logic",
                              style="TabButton",
                              width=20, pady=10)
        btn_step4.bind("<Button>", lambda e: self.switch_to_tab(3))
        btn_step4.pack(pady=5)

        btn_step1 = ttk.Button(tab,
                              text="4. Adjust your settings",
                              style="TabButton",
                              width=20, pady=10)
        btn_step1.bind("<Button>", lambda e: self.switch_to_tab(4))
        btn_step1.pack(pady=5)

        btn_step5 = ttk.Button(tab,
                              text="5. Run",
                              style="TabButton",
                              width=20, pady=10)
        btn_step5.bind("<Button>", lambda e: self.switch_to_tab(5))
        # btn_step5.pack(pady=5)

    def tab_1(self):  # 1. Action
        tab = self.tabs.nametowidget(self.tabs.tabs()[0])

        def update_summary():
            summary = {
                    "tt": "Test whether or not the conclusion is true in all structures "
                          "[in which the premises are true], \nand generate a proof or counter model.",
                    "tp": "Generate a proof that the conclusion is true in all structures "
                          "[in which the premises are true].",
                    "cmg": "Generate a structure in which the conclusion is false [and the premises are true].",
                    "mg": "Generate a structure in which the sentence[s] is [/are] true.",
                    "mc": "Check the denotation of the expression in the structure.",
                    "tc": "Compute the truth table for the formula."
            }
            lbl_sum.config(text="(" + summary[self.inst.action] + ")")

        def initial_select_rb(rb):
            rb.config(fg=white)

        def select_rb(rb):
            rb.config(fg=white)
            for rb_ in radiobuttons:
                if rb_ != rb:
                    rb_.config(fg=black)
            set()

        def set():
            self.inst.action = action.get()
            update_summary()
            self.tab_2()
            # self.tab_4()
            self.inst.completed.append(1)

        # frames
        # top
        top = ttk.Frame(tab,style="Frame.TFrame")
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = ttk.Frame(tab, style="Frame.TFrame")
        mid.pack()

        # heading
        lbl_head = ttk.Label(tab,
                            style="Label.TLabel",
                            text="What would you like to do?",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # radio buttons
        action = tk.StringVar(None, self.inst.action)
        actions = [("Truth table computation", "tc"), ("Model checking", "mc"),
                   ("Model generation", "mg"), ("Counter model generation", "cmg"),
                   ("Theorem proving", "tp"), ("Theorem testing", "tt")]
        radiobuttons = []
        for txt, val in actions[::-1]:
            rb = tk.Radiobutton(tab,
                                bg=white,
                                text=txt,
                                variable=action,
                                value=val,
                                state="normal",
                                selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                indicatoron=0,
                                width=25, pady=7.5)
            rb.config(command=lambda arg=rb: select_rb(arg))
            if val == self.inst.action:
                initial_select_rb(rb)
            rb.pack(in_=mid, pady=5)
            radiobuttons.append(rb)

        # summary
        lbl_sum = ttk.Label(style="Label.TLabel")
        update_summary()
        lbl_sum.pack(in_=mid, ipady=15)

    def tab_2(self):  # 2. Input
        # todo make scrollable
        # todo dont delete all entries when switching input_modes
        # todo broaden on window resize

        tab = self.tabs.nametowidget(self.tabs.tabs()[1])

        def doc():
            path_doc = os.path.join(os.path.dirname(os.path.dirname(__file__)), "doc", "parser.md")
            check_call(["xdg-open", path_doc], stdout=DEVNULL, stderr=STDOUT)

        def load():
            while len(raws_fml) > 1:
                remove_formula(len(raws_fml) - 1)
                ent_struct.delete("1.0", tk.END)
                lbl_struct.delete("1.0", tk.END)
                lbl_struct.configure(state="disabled")
                self.inst.structure = None
            initial_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "input")
            if not os.path.exists(initial_dir):
                initial_dir = os.getcwd()
            file = tkinter.filedialog.askopenfile(initialdir=initial_dir)
            if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            lines = [line.rstrip() for line in file if line]
            if self.inst.action not in ["mc"]:
                for i, line in enumerate(lines):
                    if not line:
                        continue
                    if i > 0:
                        add_formula()
                    ents_fml[i].delete(0, tk.END)
                    ents_fml[i].insert(0, line)
                    parse(i)
            else:
                if self.inst.action == "mc":
                    blankline = lines.index("") if "" in lines else len(lines) if " = " in "".join(lines) else 0
                    structure = lines[0:blankline]
                    formulas = lines[blankline + 1:]
                    ent_struct.delete("1.0", tk.END)
                    ent_struct.insert(1.0, "\n".join(structure))
                    parse_struct("\n".join(structure))
                else:
                    formulas = lines
                for i, line in enumerate(formulas):
                    if not line:
                        continue
                    if i > 0:
                        add_formula()
                    # todo v and w not always recognized
                    if "v:" in line:
                        v = line[2:line.index(" ")]
                        ents_v[i].delete(0, tk.END)
                        ents_v[i].insert(0, v)
                        line = line[line.index(" ")+1:]
                    if "w:" in line:
                        w = line[2:line.index(" ")]
                        ents_w[i].delete(0, tk.END)
                        ents_w[i].insert(0, w)
                        line = line[line.index(" ")+1:]
                    formula = line
                    ents_fml[i].delete(0, tk.END)
                    ents_fml[i].insert(0, formula)
                    parse(i)

        def save():
            # generate text string
            res = ""
            if self.inst.action == "mc":
                res = ent_struct.get(1.0, "end-1c") + "\n\n"
            for i, fml in enumerate(raws_fml):
                if not fml.get():
                    continue
                if self.inst.action == "mc":
                    if raws_v[i].get():
                        res += "v:" + raws_v[i].get() + " "
                    if raws_w[i].get():
                        res += "w:" + raws_w[i].get() + " "
                res += raws_fml[i].get() + "\n"
            # ask for file
            initial_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "input")
            if not os.path.exists(initial_dir):
                initial_dir = os.getcwd()
            file = tk.filedialog.asksaveasfile(initialdir=initial_dir)
            if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            file.write(res)
            file.close()

        def add_formula():
            # variable
            raw, v, w = tk.StringVar(), tk.StringVar(), tk.StringVar()
            raws_fml.append(raw)
            raws_v.append(v)
            raws_w.append(w)
            input_fmls.append(None)
            input_modes.append(None)
            i = len(raws_fml)-1
            # frames
            new_mids = {j: ttk.Frame(mid, style="Frame.TFrame") for j in range(len(mids), len(mids)+1)}
            mids.update(new_mids)
            for j in new_mids:
                mids[j].pack(ipadx=5, ipady=5, padx=50)
            # row = len(mids) - 3 if i > 0 else 1 if self.inst.action != "mg" else len(mids) - 2 if i > 0 else 2
            # # caption
            # cap = tk.Label(tab,
            #                bg=white,
            #                text=(("Conclusion:" if i == 0 else "Premise " + str(i) + ":")
            #                      if self.inst.action in ["tt", "tp", "cmg"]
            #                       else "Formula " + str(i+1) + ":" if self.inst.action in ["mg"] else "Formula:"))
            offset = 1 if self.inst.action in ["mg", "tc"] else (3 if self.inst.action in ["tt", "tp", "cmg"] else 3)
            row = len(mids)-1
            # cap.pack(in_=mids[row], side=tk.LEFT)
            # caps.append(cap)
            if not self.inst.action == "tc":
                # remove button
                rem = tk.Button(tab,
                                bg=white,
                                text="-",
                                # bg=darkgray, fg=white,
                                state="disabled" if i == 0 and self.inst.action in ["tt", "tp", "cmg"] else "normal",
                                activebackground=lightgray, activeforeground=white,
                                width=1, height=1)
                rem.pack(in_=mids[row], side=tk.LEFT, padx=5)
                rem["font"] = font_large
                Tooltip(rem, "remove this formula")
                rem.bind("<Button>", lambda e: remove_formula(i))
                rems.append(rem)
                # swap buttons
                swap_up = tk.Button(tab,
                                     bg=white,
                                     text="⇅",
                                     # text="⇡",
                                     state="disabled" if i == 0 else "normal",
                                     activebackground=lightgray, activeforeground=white,
                                     width=1, height=1)
                swap_up["font"] = font_large
                Tooltip(swap_up, "move this formula one position up")
                swap_up.bind("<Button>", lambda e: swap_up_formula(i))
                swap_up.pack(in_=mids[row], side=tk.LEFT, padx=5)
                swap_ups.append(swap_up)
                swap_dn = tk.Button(tab,
                                     bg=white,
                                     text="⇣",
                                     state="disabled" if i == len(raws_fml)-1 else "normal",
                                     activebackground=lightgray, activeforeground=white,
                                     width=1, height=1)
                swap_dn["font"] = font_large
                Tooltip(swap_dn, "move this formula one position down")
                swap_dn.bind("<Button>", lambda e: swap_dn_formula(i))
                # swap_dn.pack(in_=mids[row], side=tk.LEFT, padx=5)
                swap_dns.append(swap_dn)
                for j in range(len(input_fmls)):
                    if j < i:
                        swap_dns[j].configure(state="normal")
            # v and w fields
            if self.inst.action in ["mc"]:
                ent_v = tk.Entry(tab, textvariable=v, width=2, disabledbackground=darkwhite, font=("Consolas", 12)
                                 #state="disabled" if self.inst.logic["proppred"] == "prop" else "normal",
                                 )
                Tooltip(ent_v, "the variable assignment to evaluate the expression against (e.g. 'v1')\n"
                               "if left empty, the expression will be evaluated relative to all assignments")
                ent_w = tk.Entry(tab, textvariable=w, width=3, disabledbackground=darkwhite, font=("Consolas", 12)
                                 # state="disabled" if self.inst.logic["modal"] == "nonmodal" else "normal")
                                 )
                Tooltip(ent_w, "the possible world to evaluate the expression against (e.g. 'w1')\n"
                               "if left empty, the expression will be evaluated relative to all worlds")
                ent_v.pack(in_=mids[row], side=tk.LEFT)
                ent_w.pack(in_=mids[row], side=tk.LEFT)
                ents_v.append(ent_v)
                ents_w.append(ent_w)
            # entry field
            ent = tk.Entry(tab,
                           textvariable=raw,
                           font=("Consolas", 12),
                           width=50 if self.inst.action not in ["mc"] else 45)
            tt = {
                    True: {
                        "tt": "enter the conclusion to be proven or refuted",
                        "tp": "enter the conclusion to be proven",
                        "cmg": "enter the conclusion to be refuted",
                        "mg": "enter a formula to be satisfied",
                        "mc": "enter an expression (formula or term) to be evaluated in the structure",
                        "tc": "enter the formula to compute the truth table for"
                    },
                    False: {
                        "tt": "enter a premise to be assumed",
                        "tp": "enter a premise to be assumed",
                        "cmg": "enter a premise to be assumed",
                        "mg": "enter a formula to be satisfied",
                        "mc": "enter an expression (formula or term) to be evaluated in the structure",
                        "tc": "enter the formula to compute the truth table for"
                    }
                }
            Tooltip(ent, tt[i == 0][self.inst.action])
            ent.pack(in_=mids[row], side=tk.LEFT)
            raw.trace("w", lambda *args: select_entry(i))
            ents_fml.append(ent)
            ent.bind("<Up>", lambda e: ents_fml[(i-1 if i-1 in range(len(ents_fml)) else i)].focus_set())
            ent.bind("<Down>", lambda e: ents_fml[(i+1 if i+1 in range(len(ents_fml)) else i)].focus_set())
            ent.bind("<Return>", lambda e: parse(i))
            ent.bind("<Control-plus>", lambda e: add_formula())
            ent.bind("<Control-minus>", lambda e: remove_formula(i))
            ent.bind("<Control-Up>", lambda e: swap_up_formula(i))
            ent.bind("<Control-Down>", lambda e: swap_dn_formula(i))
            ent.bind("<Control-R>", lambda e: self.tab_2())
            ent.bind("<Control-L>", lambda e: load())
            ent.bind("<Control-S>", lambda e: save())  # todo not working
            ent.focus_set()
            # parse button
            btn_parse = tk.Button(tab,
                                  bg=white,
                                  text="↻",
                                  # bg=darkgray, fg=white,
                                  activebackground=lightgray, activeforeground=white)
            btn_parse["font"] = font_large
            btn_parse.pack(in_=mids[row], side=tk.LEFT, padx=5)
            btn_parse.bind("<Button>", lambda e: parse(i))
            btns.append(btn_parse)
            Tooltip(btn_parse, "parse this formula")
            # formula in plain text
            lbl = tk.Text(tab, height=1, width=55, borderwidth=0, bg=white, wrap=tk.CHAR)
            lbl.configure(inactiveselectbackground=lbl.cget("selectbackground"))
            lbl.configure(state="disabled")
            # lbl.pack(in_=mids[row + 1], side=tk.LEFT)
            lbl.pack(in_=mids[row], side=tk.LEFT, padx=15, expand=True)
            # lbl = tk.Text(tab, height=1, borderwidth=0)
            # lbl.tag_configure("center", justify='center')
            # lbl.insert(1.0, "...", "center")
            # lbl.configure(state="disabled")
            # lbl.configure(inactiveselectbackground=lbl.cget("selectbackground"))
            # lbl.pack(in_=mids[row + 1], side=tk.LEFT)
            lbls_fml.append(lbl)

        def remove_formula(i):
            # todo sometimes not working properly
            if not i < len(raws_fml):
                return
            del raws_fml[i]
            del input_fmls[i]
            # start = 3 if self.inst.action != "mg" else 2
            # for j in range(6 + start * (i - 1), 6 + start * (i - 1) + 3):
            #     mids[j].pack_forget()
            # for j in range(3):
            #     del mids[6 + start * (i - 1) + j]
            offset = 1 if self.inst.action in ["mg", "tc"] else (2 if self.inst.action in ["tt", "tp", "cmg"] else 3)
            row = i + offset
            mids[row].pack_forget()
            del mids[row]
            del lbls_fml[i]
            del rems[i]
            del ents_fml[i]
            del btns[i]
            for j in range(len(input_fmls)):
                if j >= i:
                    mids[j+offset] = mids[j+offset+1]
                rems[j].bind("<Button>", lambda e: remove_formula(j))
                raws_fml[j].trace("w", lambda *args: select_entry(j))
                btns[j].bind("<Button>", lambda e: parse(j))
            swap_ups[0].configure(state="disabled")
            if self.inst.action in ["tt", "tp", "cmg"]:
                rems[0].configure(state="disabled")
            swap_dns[len(swap_dns)-1].configure(state="disabled")
            set()

        def swap_up_formula(i):
            f1, f2 = raws_fml[i-1].get(), raws_fml[i].get()
            raws_fml[i-1].set(f2)
            raws_fml[i].set(f1)
            parse(i-1)
            parse(i)
            if i == 1:
                swap_ups[i-1].configure(state="disabled")
                swap_dns[i].configure(state="normal")
                if self.inst.action in ["tt", "tp", "cmg"]:
                    rems[i-1].configure(state="disabled")
                    rems[i].configure(state="normal")

        def swap_dn_formula(i):
            f1, f2 = raws_fml[i].get(), raws_fml[i+1].get()
            raws_fml[i].set(f2)
            raws_fml[i+1].set(f1)
            parse(i)
            parse(i+1)
            if i == len(input_fmls)-2:
                swap_ups[i].configure(state="normal")
                swap_dns[i+1].configure(state="disabled")

        def select_entry(i):
            raw = raws_fml[i]
            if raw.get():
                btns[i].config(state="normal")
            else:
                btns[i].config(state="disabled")

        def parse(i, arg=""):
            raw = raws_fml[i].get() if not arg else arg
            lbl = lbls_fml[i]
            parser = __import__("parser")
            fml, mode = parser.FmlParser().parse_(raw)
            input_fmls[i] = fml
            input_modes[i] = mode
            # lbl.configure(text=str(fml))
            lbl.configure(state="normal")
            lbl.delete("1.0", tk.END)
            lbl.insert(1.0, str(fml))
            lbl.configure(state="disabled")
            set_mode(input_modes)
            set()

        def parse_struct(arg=""):
            parser = __import__("parser")
            struct_raw = ent_struct.get(1.0, "end-1c") if not arg else arg
            struct = parser.StructParser().parse(struct_raw)
            # lbl_struct.configure(text=str(struct))
            lbl_struct.configure(state="normal")
            lbl_struct.delete("1.0", tk.END)
            lbl_struct.insert(1.0, str(struct))
            lbl_struct.configure(state="disabled")
            self.inst.structure = struct
            # set()

        def set_mode(modes):  # todo extend for structure
            mode_map = {
                    "classical":     ("classint", "class", "int"),
                    "propositional": ("proppred", "prop", "pred"),
                    "modal":         ("modal", "modal", "nonmodal"),
                    "vardomains":    ("constvar", "var", "const"),
                    "threeval":      ("threeval", "weak", "strong")
            }
            for md, (cat, val1, val2) in mode_map.items():
                if any([mode[md] for mode in modes if mode]):
                    self.rbs_logic[cat][val1].invoke()
                    # self.rbs_logic[cat][val1].select()
                    # self.rbs_logic[cat][val2].deselect()
                    # select_rb((self.rbs_logic[cat][val1], cat))
                else:
                    self.rbs_logic[cat][val2].invoke()
                    # self.rbs_logic[cat][val2].select()
                    # self.rbs_logic[cat][val1].deselect()
                    # select_rb((self.rbs_logic[cat][val2], cat))
            if any([mode["modal"] for mode in modes if mode]):
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
            if any([mode["threeval"] for mode in modes if mode]):
                self.rbs_logic["threeval"]["weak"].config(state="normal")
                self.rbs_logic["threeval"]["strong"].config(state="normal")
            else:
                self.rbs_logic["threeval"]["weak"].config(state="disabled")
                self.rbs_logic["threeval"]["strong"].config(state="disabled")
            if self.inst.action == "mc":
                for i in range(len(input_fmls)):
                    pass
                    # ents_v[i].config(state="disabled" if self.inst.logic["proppred"] == "prop" else "normal")
                    # ents_w[i].config(state="disabled" if self.inst.logic["modal"] == "nonmodal" else "normal")

        def set():
            if self.inst.action not in ["mc"]:
                self.inst.conclusion = input_fmls[0] if input_fmls else None
                self.inst.premises = input_fmls[1:] if len(input_fmls) > 1 else []
            # elif self.inst.action in ["mg"]:
            #     self.inst.conclusion = tuple([input_fmls[0], raws_v[0].get(), raws_w[0].get()]) if input_fmls else None
            #     self.inst.premises = [tuple([input_fmls[i], raws_v[i].get(), raws_w[i].get()])
            #                           for i in range(1, len(input_fmls))] if len(input_fmls) > 1 else []
            elif self.inst.action == "mc":
                self.inst.formulas = [tuple([input_fmls[i], raws_v[i].get(), raws_w[i].get()])
                                      for i in range(len(input_fmls))]
            # self.inst.structure = struct
            # update_summary()
            self.inst.completed.append(3)
            self.btn_run.config(state="normal")

        for child in tab.winfo_children():
            child.destroy()

        # frames
        # canvas =ScrollableFrame(tab)
        # canvas.pack()
        # top
        top = ttk.Frame(tab, style="Frame.TFrame")
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # top mid
        topmid = ttk.Frame(tab, style="Frame.TFrame")
        topmid.pack()  # todo make more compact?
        # mid
        mid = ttk.Frame(tab, style="Frame.TFrame")
        mid.pack()
        mids = {}

        # reset button
        btn_reset = tk.Button(tab,
                              bg=white,
                              text="↶",
                              activebackground=lightgray, activeforeground=white)
        btn_reset.pack(in_=topmid, padx=15, side=tk.LEFT)
        Tooltip(btn_reset, "reset")
        btn_reset.bind("<Button>", lambda e: self.tab_2())

        # heading
        lbl_head = ttk.Label(tab,
                             style="Label.TLabel",
                             text="What would you like to analyze?",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top, side=tk.LEFT)
        # .grid(row=0, columnspan=4, sticky="NESW")

        # load from file button
        btn_load = tk.Button(tab,
                             bg=white,
                             text="↥",
                             # bg=darkgray, fg=white,
                             activebackground=lightgray, activeforeground=white)
        btn_load.pack(in_=topmid, padx=15, side=tk.LEFT)
        Tooltip(btn_load, "load input from file")
        btn_load.bind("<Button>", lambda e: load())
        # .grid(row=0, columnspan=4, sticky="NESW")

        # save to file button
        btn_save = tk.Button(tab,
                             bg=white,
                             text="⤓",
                             # bg=darkgray, fg=white,
                             activebackground=lightgray, activeforeground=white)
        btn_save.pack(in_=topmid, padx=15, side=tk.LEFT)
        Tooltip(btn_save, "save input to file")
        btn_save.bind("<Button>", lambda e: save())

        # doc button
        btn_doc = tk.Button(tab,
                             bg=white,
                             text="?",
                             # bg=darkgray, fg=white,
                             activebackground=lightgray, activeforeground=white)
        btn_doc.pack(in_=topmid, padx=15, side=tk.LEFT)
        Tooltip(btn_doc, "show documentation on entering input")
        btn_doc.bind("<Button>", lambda e: doc())

        # input fields
        input_fmls = []
        struct = None
        input_modes = []
        raws_fml = []
        raws_v = []
        raws_w = []
        caps = []
        lbls_fml = []
        rems = []
        swap_ups = []
        swap_dns = []
        ents_fml = []
        ents_v = []
        ents_w = []
        btns = []

        def update_summary():
            concl = self.inst.conclusion
            if self.inst.action == "tt":
                txt = "You are searching for a proof or refutation that " + \
                      (str(concl) if concl else "...") + " is true in all structures" + \
                      (" in which " + ", ".join([fml if fml else "..." for fml in input_fmls[1:]]) + " is true"
                       if len(input_fmls) > 1 else "") + "."
            elif self.inst.action == "tp":
                txt = "You are searching for a proof that " + \
                      (str(concl) if concl else "...") + " is true in all structures" + \
                      (" in which " + ", ".join([fml if fml else "..." for fml in input_fmls[1:]]) + " is true"
                       if len(input_fmls) > 1 else "") + "."
            elif self.inst.action == "cmg":
                txt = "You are searching for a structure in which " + \
                      (str(concl) if concl else "...") + " is false" + \
                      (" and " + ", ".join([fml if fml else "..." for fml in input_fmls[1:]]) + " is true"
                       if len(input_fmls) > 1 else "") + "."
            elif self.inst.action == "mg":
                txt = "You are searching for a structure in which " + \
                      ", ".join([str(fml) if fml else "..." for fml in input_fmls]) + \
                      (" is " if len(input_fmls) == 1 else " are ") + "true."
            else:
                txt = "You are searching for the denotation of " + \
                      (str(concl) if concl else "...") + " in  " + "S."
            lbl_sum.config(text="(" + txt + ")")

        # summary
        lbl_sum = ttk.Label(style="Label.TLabel")
        # update_summary()
        # lbl_sum.pack(in_=mids[0])

        # captions
        cap_exprs = ttk.Label(tab, text="Expressions:", style="Label.TLabel")
        cap_fml = ttk.Label(tab, text="Formula:", style="Label.TLabel")
        cap_fmls = ttk.Label(tab, text="Formulas:", style="Label.TLabel")
        cap_concl = ttk.Label(tab, text="Conclusion:", style="Label.TLabel")
        cap_prems = ttk.Label(tab, text="Premises:", style="Label.TLabel")
        cap_struct = ttk.Label(tab, text="Structure:", style="Label.TLabel")

        # buttons
        btn_add_fml = tk.Button(tab,
                                bg=white,
                                text="+",
                                activebackground=lightgray, activeforeground=white,
                                width=1, height=1)
        btn_add_fml["font"] = font_large
        Tooltip(btn_add_fml, "add a formula")
        btn_add_fml.bind("<Button>", lambda e: add_formula())

        if self.inst.action == "tc":
            new_mids = {i: ttk.Frame(mid, style="Frame.TFrame") for i in range(len(mids)+1)}
            for i in new_mids:
                new_mids[i].pack(ipadx=5, ipady=5, padx=50)
            mids.update(new_mids)
            cap_fml.pack(in_=mids[0], side=tk.LEFT, padx=15, pady=15)
            add_formula()

        elif self.inst.action == "mc":
            new_mids = {i: ttk.Frame(mid, style="Frame.TFrame") for i in range(len(mids), len(mids)+2)}
            for i in new_mids:
                new_mids[i].pack(ipadx=5, ipady=5, padx=50)
            mids.update(new_mids)
            # todo add field for specification of g and w
            cap_struct.pack(in_=mids[0], padx=15, pady=15)
            phantom_struct = ttk.Label(text="", width=5)
            phantom_struct.pack(in_=mids[1], side=tk.LEFT)
            # raw_struct = tk.StringVar()
            # ent_struct = tk.Entry(tab,
            #                textvariable=struct_raw)
            # ent_struct.pack(in_=mids[6], side=tk.LEFT, expand=True)
            # ent_struct.trace("w", lambda *args: select_entry(-1))
            ent_struct = tk.Text(tab, height=8, width=60, font=("Consolas", 12))
            Tooltip(ent_struct, "enter the structure to evaluate the expressions against")
            ent_struct.pack(in_=mids[1], side=tk.LEFT)
            # input_ents.append(ent_struct)
            btn_parse_struct = tk.Button(tab,
                                         bg=white,
                                         text="↻",
                                         # bg=darkgray, fg=white,
                                         activebackground=lightgray, activeforeground=white)
            btn_parse_struct["font"] = font_large
            Tooltip(btn_parse_struct, "parse this structure")
            btn_parse_struct.pack(in_=mids[1], side=tk.LEFT, padx=5)
            btn_parse_struct.bind("<Button>", lambda e: parse_struct())
            # btns.append(btn_parse_struct)
            lbl_struct = tk.Text(tab, height=8, width=60, borderwidth=0, bg=white)
            lbl_struct.configure(inactiveselectbackground=lbl_struct.cget("selectbackground"))
            lbl_struct.configure(state="disabled")
            lbl_struct.pack(in_=mids[1], side=tk.LEFT, padx=15, expand=True)
            new_mids = {i: ttk.Frame(mid, style="Frame.TFrame") for i in range(len(mids), len(mids)+1)}
            for i in new_mids:
                new_mids[i].pack(ipadx=5, ipady=5, padx=50)
            mids.update(new_mids)
            mid2 = ttk.Frame(mid, style="Frame.TFrame")
            mids[2] = mid2
            mids[2].pack(ipadx=5, ipady=5)
            cap_exprs.pack(in_=mids[2], side=tk.LEFT, padx=15, pady=15)
            btn_add_fml.pack(in_=mids[2], side=tk.LEFT)
            add_formula()
            ent_struct.focus()

        elif self.inst.action == "mg":
            new_mids = {i: ttk.Frame(mid, style="Frame.TFrame") for i in range(len(mids), len(mids)+1)}
            for i in new_mids:
                new_mids[i].pack(ipadx=5, ipady=5, padx=50)
            mids.update(new_mids)
            for i in mids:
                mids[i].pack(ipadx=5, ipady=5, padx=50)
            # cap_pseudo.pack(in_=mids[0], side=tk.LEFT, padx=15)
            cap_fmls.pack(in_=mids[0], side=tk.LEFT, pady=15)
            btn_add_fml.pack(in_=mids[0], side=tk.LEFT, padx=15)
            add_formula()
            ents_fml[0].focus()
        else:
            new_mids = {i: ttk.Frame(mid, style="Frame.TFrame") for i in range(len(mids)+1)}
            for i in new_mids:
                new_mids[i].pack(ipadx=5, ipady=5, padx=50)
            mids.update(new_mids)
            cap_concl.pack(in_=mids[0], side=tk.LEFT, padx=15, pady=15)
            add_formula()
            new_mids = {i: ttk.Frame(mid, style="Frame.TFrame") for i in range(len(mids)+1)}
            for i in new_mids:
                new_mids[i].pack(ipadx=5, ipady=5, padx=50)
            mids.update(new_mids)
            cap_prems.pack(in_=mids[2], side=tk.LEFT, pady=15)
            btn_add_fml.pack(in_=mids[2], side=tk.LEFT, padx=15)
            ents_fml[0].focus()

    def tab_3(self):  # 3. Logic
        tab = self.tabs.nametowidget(self.tabs.tabs()[2])

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
            set()
            update_availability()

        def update_availability():
            if self.inst.logic["modal"] == "modal":
                if self.inst.logic["proppred"] == "pred":
                    self.rbs_logic["constvar"]["const"].config(state="normal")
                    self.rbs_logic["constvar"]["var"].config(state="normal")
                else:
                    self.rbs_logic["constvar"]["const"].config(state="disabled")
                    self.rbs_logic["constvar"]["var"].config(state="disabled")
                self.rbs_logic["locglob"]["local"].config(state="normal")
                self.rbs_logic["locglob"]["global"].config(state="normal")
                self.rbs_logic["frame"]["K"].config(state="normal")
            else:
                self.rbs_logic["constvar"]["const"].config(state="disabled")
                self.rbs_logic["constvar"]["var"].config(state="disabled")
                self.rbs_logic["locglob"]["local"].config(state="disabled")
                self.rbs_logic["locglob"]["global"].config(state="disabled")
                self.rbs_logic["locglob"]["global"].config(fg=black)
                self.rbs_logic["frame"]["K"].config(state="disabled")
            if self.inst.logic["valued"] == "threevalued":
                self.rbs_logic["threeval"]["weak"].config(state="normal")
                self.rbs_logic["threeval"]["strong"].config(state="normal")
            else:
                self.rbs_logic["threeval"]["weak"].config(state="disabled")
                self.rbs_logic["threeval"]["strong"].config(state="disabled")

        def reset():
            for cat_ in self.rbs_logic:
                for val_ in self.rbs_logic[cat_]:
                    rb_ = self.rbs_logic[cat][val_]
                    rb_.deselect()
            self.inst.completed.remove(1)
            self.inst.action = None

        def set():
            self.inst.logic = {var: val.get() for (var, val) in variables.items()}
            self.inst.completed.append(1)

        def next_step(i):
            set()
            self.switch_to_tab(i)

        # frames
        # top
        top = ttk.Frame(tab, style="Frame.TFrame")
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = ttk.Frame(tab, style="Frame.TFrame")
        mid.pack()
        mids = {i: ttk.Frame(mid, style="Frame.TFrame") for i in range(13)}
        for i in mids:
            mids[i].pack(ipadx=0, ipady=5)

        # heading
        lbl_head = ttk.Label(tab,
                            style="Label.TLabel",
                            text="Which logic are you working in?",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)
        lbl_headmodal = ttk.Label(tab,
                            style="Label.TLabel",
                            text="For modal logic:",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=mids[5])
        lbl_threeval = ttk.Label(tab,
                                style="Label.TLabel",
                                text="For three-valued logic:",
                                # font=("OpenSans", "12", "bold"),
                                anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=mids[10])

        # selection
        categories = ["proppred", "classint", "modal", "valued", "constvar", "locglob", "frame", "threeval"]
        labels = {
                "proppred": [("propositional logic", "prop"), ("predicate logic", "pred")],
                "classint": [("classical", "class"), ("intuitionistic", "int")],
                "modal":    [("non-modal", "nonmodal"), ("modal", "modal")],
                "valued":   [("two-valued", "twovalued"), ("three-valued", "threevalued")],
                "constvar": [("constant domains", "const"), ("varying domains", "var")],
                "locglob":  [("local validity/satisfiability", "local"), ("global validity/satisfiability", "global")],
                "frame":    [("frame K", "K")],
                "threeval": [("weak Kleene", "weak"), ("strong Kleene", "strong")]
        }
        variables = {
                "proppred": tk.StringVar(None, self.inst.logic["proppred"]),
                "classint": tk.StringVar(None, self.inst.logic["classint"]),
                "modal":    tk.StringVar(None, self.inst.logic["modal"]),
                "valued":   tk.StringVar(None, self.inst.logic["valued"]),
                "constvar": tk.StringVar(None, self.inst.logic["constvar"]),
                "locglob":  tk.StringVar(None, self.inst.logic["locglob"]),
                "frame":    tk.StringVar(None, self.inst.logic["frame"]),
                "threeval": tk.StringVar(None, self.inst.logic["threeval"])
        }
        self.rbs_logic = {cat: dict() for cat in categories}
        for i, cat in enumerate(categories):
            i += 2 if cat in ["constvar", "locglob", "frame"] else 0
            i += 4 if cat in ["threeval"] else 0
            for j, (txt, val) in enumerate(labels[cat]):
                enabled = False if cat in ["constvar", "locglob", "frame", "threeval"] else True
                rb = tk.Radiobutton(tab,
                                    bg=white,
                                    fg=black,
                                    text=txt,
                                    variable=variables[cat],
                                    value=val,
                                    state="normal" if enabled else "disabled",
                                    selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                    indicatoron=0,
                                    width=25, pady=7.5)
                rb.config(command=lambda arg=(rb, cat): select_rb(arg))
                if val == self.inst.logic[cat] and enabled:
                    initial_select_rb((rb, cat))
                rb.pack(in_=mids[i], side=(tk.LEFT if j == 0 else tk.RIGHT))  # todo slightly off-center
                self.rbs_logic[cat][val] = rb

        Tooltip(self.rbs_logic["constvar"]["const"], "all worlds share the same domain of discourse")
        Tooltip(self.rbs_logic["constvar"]["var"], "each world has its own domain of discourse")
        Tooltip(self.rbs_logic["locglob"]["local"], "check truth perservance/satisfaction on world level")
        Tooltip(self.rbs_logic["locglob"]["global"], "check truth preservance/satisfaction on structure level")
        Tooltip(self.rbs_logic["frame"]["K"], "no additional frame properties")
        Tooltip(self.rbs_logic["threeval"]["weak"], "weak Kleene three-valued logic")
        Tooltip(self.rbs_logic["threeval"]["strong"], "strong Kleene three-valued logic")

    def tab_4(self):  # 4. Settings
        # todo config file for default settings

        tab = self.tabs.nametowidget(self.tabs.tabs()[3])

        def initial_select_rb(rb):
            rb.config(fg=white, bg=darkgray)

        def select_rb(rb, rbs):
            rb.config(fg=white)
            for rb_ in rbs:
                if rb_ != rb:
                    rb_.config(fg=black, bg=white)
            set()

        def initial_select_cb(cb):
            cb.config(fg=white, bg=darkgray)

        def select_cb(cb):
            cb.config(fg=white)
            if not stepwise.get():
                cbs[0].config(fg=black)
            if not underline.get():
                cbs[1].config(fg=black)
            if not hide.get():
                cbs[2].config(fg=black)
            set()

        def select_entry():
            set()

        def decrease_num_models():
            num_models.set(str(int(num_models.get()) - 1))
            set()

        def increase_num_models():
            num_models.set(str(int(num_models.get()) + 1))
            set()

        def decrease_size_limit():
            size_limit.set(str(int(size_limit.get()) - 1))
            set()

        def increase_size_limit():
            size_limit.set(str(int(size_limit.get()) + 1))
            set()

        def set():
            self.inst.output = output.get()
            self.inst.stepwise = stepwise.get()
            self.inst.underline_open = underline.get()
            self.inst.hide_nonopen = hide.get()
            self.inst.generation_mode = generation.get()
            if num_models.get():
                self.inst.num_models = int(num_models.get())
            if size_limit.get():
                self.inst.size_limit_factor = int(size_limit.get())
            self.inst.completed.append(1)

        def next_step(i):
            set()
            self.switch_to_tab(i)

        # frames
        # top
        top = ttk.Frame(tab, style="Frame.TFrame")
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = ttk.Frame(tab, style="Frame.TFrame")
        mid.pack()
        mids = []
        for i in range(9):
            if i in [5]:
                sep = ttk.Frame(mid, style="Frame.TFrame")
                sep.pack(pady=10)
            midi = ttk.Frame(mid, style="Frame.TFrame")
            midi.pack()
            mids.append(midi)
        m = 0

        # heading
        lbl_head = ttk.Label(tab,
                            style="Label.TLabel",
                            text="How would you like pyPL to work?",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # derivation output format
        lbl_output = ttk.Label(tab,
                              style="Label.TLabel",
                              text="Derivation output format:")
        # lbl_output.pack(in_=mids[m])
        # m += 1

        # output format
        lbl_output = ttk.Label(tab,
                              style="Label.TLabel",
                              text="Output format:")
        lbl_output.pack(in_=mids[m])
        m += 1

        cbs = []

        enabled = True if self.inst.action != "mc" else False
        output = tk.StringVar(None, self.inst.output)
        outputs1 = [("LaTeX PDF", "tex"), ("plain text", "txt")]
        rbs = []
        rbs1 = []
        for i, (txt, val) in enumerate(outputs1):
            rb = tk.Radiobutton(tab,
                                bg=white,
                                text=txt,
                                variable=output,
                                value=val,
                                # state="normal" if enabled else "disabled",
                                selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                indicatoron=0,
                                width=25, pady=7.5)
            rb.pack(in_=mids[m], side=(tk.LEFT if i == 0 else tk.RIGHT), pady=5)
            rbs1.append(rb)
            rb.config(command=lambda arg=rb: select_rb(arg, rbs1))
            if val == self.inst.output:
                initial_select_rb(rb)
            rbs.append(rb)
        m += 1

        stepwise = tk.BooleanVar(None, self.inst.stepwise)
        # enabled = True if self.inst.action == "mc" else False
        cb = tk.Checkbutton(tab,
                            bg=white,
                            fg=black,
                            text="show stepwise derivation",
                            variable=stepwise,
                            onvalue=True, offvalue=False,
                            # state="disabled",  # not yet implemented
                            # state="normal" if enabled else "disabled",
                            selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                            indicatoron=0,
                            width=25, pady=7.5)
        cb.pack(in_=mids[m], side=tk.LEFT, pady=5)
        m += 1
        cb.config(command=lambda arg=cb: select_cb(arg))
        cbs.append(cb)

        underline = tk.BooleanVar(None, self.inst.underline_open)
        cb = tk.Checkbutton(tab,
                            bg=white,
                            text="mark open literals",
                            variable=underline,
                            onvalue=True, offvalue=False,
                            # state="normal" if enabled else "disabled",
                            selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                            indicatoron=0,
                            width=25, pady=7.5)
        cb.pack(in_=mids[m], side=tk.LEFT, pady=5)
        m += 1
        cb.config(command=lambda arg=cb: select_cb(arg))
        initial_select_cb(cb)
        cbs.append(cb)

        hide = tk.BooleanVar(None, self.inst.hide_nonopen)
        cb = tk.Checkbutton(tab,
                            bg=white,
                            text="show only open branches",
                            variable=hide,
                            onvalue=True, offvalue=False,
                            # state="normal" if enabled else "disabled",
                            selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                            indicatoron=0,
                            width=25, pady=7.5)
        cb.config(command=lambda arg=cb: select_cb(arg))
        cb.pack(in_=mids[m], side=tk.RIGHT, pady=5)
        cbs.append(cb)
        m += 1

        # mathematical vs linguistic mode
        enabled = True if self.inst.action in ["tt", "mg", "cmg"] else False
        generation = tk.StringVar(None, self.inst.generation_mode)
        lbl_output = ttk.Label(tab,
                              style="Label.TLabel",
                              text="Model generation mode:")
        lbl_output.pack(in_=mids[m])
        m += 1
        generations = [("minimal domain", "mathematical"), ("non-minimal domain", "linguistic")]
        rbs = []
        rbs2 = []
        for i, (txt, val) in enumerate(generations):
            rb = tk.Radiobutton(tab,
                                bg=white,
                                text=txt,
                                variable=generation,
                                value=val,
                                # state="normal" if enabled else "disabled",
                                selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                                indicatoron=0,
                                width=25, pady=7.5)
            rb.pack(in_=mids[m], side=(tk.LEFT if i == 0 else tk.RIGHT), pady=5)
            rbs2.append(rb)
            rb.config(command=lambda arg=rb: select_rb(arg, rbs2))
            if val == self.inst.generation_mode:
                initial_select_rb(rb)
            rbs.append(rb)
        m += 1

        # number of models to generate
        num_models = tk.StringVar(None, self.inst.num_models)
        lbl_num_models = ttk.Label(tab,
                                  style="Label.TLabel",
                                  text="Number of models to compute:")
        lbl_num_models.pack(in_=mids[m], side=tk.LEFT, padx=15)
        btn_num_models_dn = tk.Button(tab,
                                      bg=white,
                                      text="-",
                                      # state="normal" if enabled else "disabled",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_num_models_dn.bind("<Button>", lambda e: decrease_num_models())
        btn_num_models_dn.pack(in_=mids[m], side=tk.LEFT, padx=5)
        ent_num_models = tk.Entry(tab,
                                  textvariable=num_models,
                                  justify=tk.RIGHT,
                                  width=2)
        ent_num_models.pack(in_=mids[m], side=tk.LEFT, padx=5)
        num_models.trace("w", lambda *args: select_entry())
        btn_num_models_up = tk.Button(tab,
                                      bg=white,
                                      text="+",
                                      # state="normal" if enabled else "disabled",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_num_models_up.bind("<Button>", lambda e: increase_num_models())
        btn_num_models_up.pack(in_=mids[m], side=tk.LEFT, padx=5)
        m += 1

        # size limit factor
        enabled = True if self.inst.action != "mc" else False
        size_limit = tk.StringVar(None, self.inst.size_limit_factor)
        lbl_size_limit = ttk.Label(tab,
                                  style="Label.TLabel",
                                  text="Tableau tree size limit factor:")
        Tooltip(lbl_size_limit, "stop the search when the tree gets deeper or wider than "
                                "factor * length of assumptions")
        lbl_size_limit.pack(in_=mids[m], side=tk.LEFT, padx=15)
        btn_size_limit_dn = tk.Button(tab,
                                      bg=white,
                                      text="-",
                                      # state="normal" if enabled else "disabled",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_size_limit_dn.bind("<Button>", lambda e: decrease_size_limit())
        btn_size_limit_dn.pack(in_=mids[m], side=tk.LEFT, padx=5)
        ent_size_limit = tk.Entry(tab,
                                  textvariable=size_limit,
                                  justify=tk.RIGHT,
                                  # state="normal" if enabled else "disabled",
                                  width=2)
        ent_size_limit.pack(in_=mids[m], side=tk.LEFT, padx=5)
        size_limit.trace("w", lambda *args: select_entry())
        btn_size_limit_up = tk.Button(tab,
                                      bg=white,
                                      text="+",
                                      # state="normal" if enabled else "disabled",
                                      activebackground=lightgray, activeforeground=white,
                                      width=1)
        btn_size_limit_up.bind("<Button>", lambda e: increase_size_limit())
        btn_size_limit_up.pack(in_=mids[m], side=tk.LEFT, padx=5)
        m += 1

    def switch_to_tab(self, i):
        tab_id = self.tabs.tabs()[i]
        self.tabs.select(tab_id)

    def run(self):
        # # wait window  # todo doesn't work/only with large delay
        # win_wait = tk.Toplevel(self.root, bg=white)
        # icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        # win_wait.tk.call('wm', 'iconphoto', win_wait._w, tk.PhotoImage(file=icon_path))
        # win_wait.geometry("300x100")
        # lbl_wait = tk.Label(win_wait, text="...", font=font, bg=white)
        # lbl_wait.pack(pady=32)

        truthtable = __import__("truthtable")
        denotation = __import__("denotation")
        tableau = __import__("tableau")
        concl = self.inst.conclusion
        premises = self.inst.premises
        formulas = self.inst.formulas
        axioms = self.inst.axioms
        structure = self.inst.structure

        # settings
        classical = self.inst.logic["classint"] == "class"
        propositional = self.inst.logic["proppred"] == "prop"
        modal = self.inst.logic["modal"] == "modal"
        vardomains = self.inst.logic["constvar"] == "var"
        local = self.inst.logic["locglob"] == "local"
        frame = self.inst.logic["frame"]
        linguistic = self.inst.generation_mode == "linguistic"

        latex = self.inst.output == "tex"
        stepwise = self.inst.stepwise
        underline_open = self.inst.underline_open
        hide_nonopen = self.inst.hide_nonopen
        num_models = self.inst.num_models
        size_limit = self.inst.size_limit_factor

        if self.inst.action == "tc":
            tt = truthtable.Truthtable(concl, latex)
            tt.show()

        elif self.inst.action == "mc":
            print("starting denotation computation", [(fml, structure, v, w) for fml, v, w in formulas])
            denot = denotation.Denotation([(fml, structure, v, w) for fml, v, w in formulas])
            denot.show(latex)

            # # todo make look nicer?
            # # tk.messagebox.showinfo("", str(denot))
            # win_output = tk.Toplevel(self.root, bg=white)
            # # win_output.geometry("1000x605")  # todo geometry only applied on second opening
            # win_output.destroy()
            # win_output = tk.Toplevel(self.root, bg=white)
            # icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
            # win_output.tk.call('wm', 'iconphoto', win_output._w, tk.PhotoImage(file=icon_path))
            # lbl_output = tk.Label(win_output, text=str(denot), font=font, bg=white)
            # lbl_output.pack(pady=32)
            # # frame_output = ttk.Frame(win_output)
            # # win_output.destroy()

        elif self.inst.action != "tt":
            validity = True if self.inst.action == "tp" else False
            satisfiability = True if self.inst.action == "mg" else False

            tableau.Tableau(concl, premises=premises, axioms=axioms,
                            validity=validity, satisfiability=satisfiability, linguistic=linguistic,
                            classical=classical, propositional=propositional,
                            modal=modal, vardomains=vardomains, local=local, frame=frame,
                            silent=True, file=True, latex=latex, stepwise=stepwise,
                            num_models=num_models, size_limit_factor=size_limit,
                            underline_open=underline_open, hide_nonopen=hide_nonopen).show()

        else:
            # test if theorem
            tab1 = tableau.Tableau(concl, premises=premises, axioms=axioms,
                                   validity=True, satisfiability=False, linguistic=linguistic,
                                   classical=classical, propositional=propositional,
                                   modal=modal, vardomains=vardomains, local=local, frame=frame,
                                   silent=True, file=True, latex=latex, stepwise=stepwise,
                                   num_models=num_models, size_limit_factor=size_limit,
                                   underline_open=underline_open, hide_nonopen=hide_nonopen)
            if tab1.closed():
                # win_wait.destroy()
                tab1.show()
            else:
                # test if non-theorem
                tab2 = tableau.Tableau(concl, premises=premises, axioms=axioms,
                                       validity=False, satisfiability=False, linguistic=linguistic,
                                       classical=classical, propositional=propositional,
                                       modal=modal, vardomains=vardomains, local=local, frame=frame,
                                       silent=True, file=True, latex=latex, stepwise=stepwise,
                                       num_models=num_models, size_limit_factor=size_limit,
                                       underline_open=underline_open, hide_nonopen=hide_nonopen)
                if tab2.open() or tab2.infinite():
                    # win_wait.destroy()
                    tab2.show()


def write_output(res, latex=True):
    # generate and open output file
    path_output = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    if not os.path.exists(path_output):
        os.mkdir(path_output)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M_%S%f')
    os.chdir(path_output)
    if not latex:
        # generate and open txt file
        file_txt = "output_" + timestamp + ".txt"
        path_txt = os.path.join(path_output, file_txt)
        with open(path_txt, "w", encoding="utf-8") as f:
            f.write(res)
        # open file
        check_call(["xdg-open", path_txt], stdout=DEVNULL, stderr=STDOUT)
        os.chdir(os.path.dirname(__file__))
    else:
        # generate and open latex and pdf file
        # prepare output files
        file_tex = "output_" + timestamp + ".tex"
        file_pdf = "output_" + timestamp + ".pdf"
        path_tex = os.path.join(path_output, file_tex)
        path_pdf = os.path.join(path_output, file_pdf)
        # write LaTeX code
        with open(path_tex, "w") as texfile:
            texfile.write(res)
        # compile LaTeX to PDF
        check_call(["pdflatex", file_tex], stdout=DEVNULL, stderr=STDOUT)
        # open file
        check_call(["xdg-open", path_pdf], stdout=DEVNULL, stderr=STDOUT)
        # cleanup
        for file in os.listdir(path_output):
            path_file = os.path.join(path_output, file)
            if os.path.exists(path_file) and file.endswith(".log") or file.endswith(".aux") or file.endswith(".gz"):
                os.remove(path_file)
        os.chdir(os.path.dirname(__file__))

def main():
    # redirect output to log file
    if not debug:
        import sys
        path_log = os.path.join(os.path.dirname(__file__), "pyPL.log")
        sys.stdout = open(path_log, 'w')
        sys.stderr = sys.stdout

    # run
    PyPLGUI()

if __name__ == "__main__":
    main()
