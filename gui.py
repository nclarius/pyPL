#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Graphical interface.
CURRENTLY UNDER CONSTRUCTION.
"""


import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk

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
        self.logic = {"proppred": "pred", "classint": "class", "modal": "nonmodal", "constvar": "var", "frame": "K"}

        self.output = "tex"
        self.generation_mode = "mathematical"
        self.num_models = 1
        self.size_limit_factor = 1
        self.underline_open = True
        self.hide_nonopen = False
        self.verbose = False


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


class PyPLGUI(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()

        # general settings
        self.root.title("pyPL")
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.root.tk.call('wm', 'iconphoto', self.root._w, tk.PhotoImage(file=icon_path))
        self.root.geometry("1244x700")

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
                "TNotebook.Tab": {"configure": {"padding": [10, 7.5]}}})
        # todo visually distinguish action buttons, radio buttons and check buttons?
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

        frm_run = tk.Frame(self.root, bg=white, height=175)
        frm_run.pack(pady=10)

        # run button
        btn_run = tk.Button(frm_run,
                            text="Run!",
                            activebackground=lightgray, activeforeground=white,
                            state="disabled",
                            width=22, pady=10,
                            bg=white)
        btn_run.bind("<Button>", lambda e: self.run())
        btn_run.pack(in_=frm_run, pady=10)
        self.btn_run = btn_run
        # keyboard shortcut
        self.root.bind("<Control-Return>", lambda e: self.run())

        # info
        lbl_info = tk.Label(frm_run,
                            text="🛈 https://github.com/nclarius/pyPL", bg=white) \
            .pack(pady=10)

    def tab_0(self):  # 0. Start
        tab = self.tabs.nametowidget(self.tabs.tabs()[0])

        # welcome message
        lbl_greeting = ttk.Label(tab,
                                 bg=white,
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
        tab = self.tabs.nametowidget(self.tabs.tabs()[0])

        def update_summary():
            if self.inst.action == "tt":
                txt = "Test whether or not the conclusion is true in all structures [in which the premises are true]," \
                      "\nand generate a proof or counter model."
            elif self.inst.action == "tp":
                txt = "Generate a proof that the conclusion is true in all structures [in which the premises are true]."
            elif self.inst.action == "cmg":
                txt = "Generate a structure in which the conclusion is false [and the premises are true]."
            elif self.inst.action == "mg":
                txt = "Generate a structure in which the formula[s] is [/are] true."
            else:
                txt = "Check whether the formula is true in the structure."
            lbl_sum.config(text="(" + txt + ")")

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
        top = tk.Frame(tab, bg=white)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab, bg=white)
        mid.pack()

        # heading
        lbl_head = tk.Label(tab,
                            bg=white,
                            text="What would you like to do?",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # radio buttons
        action = tk.StringVar(None, self.inst.action)
        actions = [("Model checking", "mc"), ("Model generation", "mg"), ("Counter model generation", "cmg"),
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
        lbl_sum = tk.Label(bg=white)
        update_summary()
        lbl_sum.pack(in_=mid, ipady=15)

    def tab_2(self):  # 2. Input
        # todo make scrollable
        # todo dont delete all entries when switching input_modes
        # todo broaden on window resize

        tab = self.tabs.nametowidget(self.tabs.tabs()[1])

        def load():
            while len(input_raws) > 1:
                remove_formula(len(input_raws) - 1)
            initial_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
            if not os.path.exists(initial_dir):
                initial_dir = os.getcwd()
            file = tkinter.filedialog.askopenfile(initialdir=initial_dir)
            lines = [line.strip() for line in file]
            if self.inst.action != "mc":
                for i, line in enumerate(lines):
                    if not line:
                        continue
                    if i > 0:
                        add_formula()
                    input_ents[i].delete(0, tk.END)
                    input_ents[i].insert(0, line)
                    parse(i)
            else:
                empty_line = lines.index("") if "" in lines else len(lines)
                structure = lines[0:empty_line]
                formulas = lines[empty_line + 1:]
                ent_struct.delete("1.0", tk.END)
                ent_struct.insert(1.0, "\n".join(structure))
                parse_struct("\n".join(structure))
                for i, line in enumerate(formulas):
                    if not line:
                        continue
                    if i > 0:
                        add_formula()
                    formula = line
                    if "v:" in line:
                        v, formula = line[2:line.index(" ")], line[line.index(" ")+1:]
                        input_gs[i].delete(0, tk.END)
                        input_gs[i].insert(0, g)
                    if "w:" in line:
                        w, formula = line[2:line.index(" ")], line[line.index(" ")+1:]
                        input_ws[i].delete(0, tk.END)
                        input_ws[i].insert(0, w)
                    input_ents[i+1].delete(0, tk.END)
                    input_ents[i+1].insert(0, formula)
                    parse(i)

        def add_formula():
            # variable
            raw, v, w = tk.StringVar(), tk.StringVar(), tk.StringVar()
            input_raws.append(raw)
            input_fmls.append(None)
            input_modes.append(None)
            i = input_raws.index(raw)
            # frames
            if i > 0 or self.inst.action == "mc":
                new_mids = {j: tk.Frame(mid, bg=white) for j in range(len(mids), len(mids) + 1)}
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
            row = len(mids) - 1 if i > 0 else (1 if self.inst.action != "mc" else 3)
            # cap.pack(in_=mids[row], side=tk.LEFT)
            # caps.append(cap)
            # remove button
            rem = tk.Button(tab,
                            bg=white,
                            text="-",
                            # bg=darkgray, fg=white,
                            state="disabled",
                            activebackground=lightgray, activeforeground=white,
                            width=1, height=1)
            rem.pack(in_=mids[row], side=tk.LEFT, padx=5)
            rem["font"] = font_large
            rem.bind("<Button>", lambda e: remove_formula(i))
            rems.append(rem)
            if len(input_fmls) > 1:
                btn_swap.config(state="normal")
                rem.config(state="normal")
            # g and w fields
            if self.inst.action == "mc":
                ent_v = tk.Entry(tab, textvariable=v, width=2)
                ent_w = tk.Entry(tab, textvariable=w, width=3)
                ent_v.pack(in_=mids[row], side=tk.LEFT)
                ent_w.pack(in_=mids[row], side=tk.LEFT)
                input_gs.append(ent_v)
                input_ws.append(ent_w)
            # entry field
            ent = tk.Entry(tab,
                           textvariable=raw,
                           width=45 if self.inst.action != "mc" else 40)
            ent.pack(in_=mids[row], side=tk.LEFT)
            raw.trace("w", lambda *args: select_entry(i))
            input_ents.append(ent)
            ent.bind("<Return>", lambda e: parse(i))
            ent.bind("<Control-plus>", lambda e: add_formula())
            ent.bind("<Control-minus>", lambda e: remove_formula(i))
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
            # formula in plain text
            lbl = tk.Text(tab, height=1, width=45, borderwidth=0, bg=white, wrap=tk.CHAR)
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
            input_lbls.append(lbl)

        def remove_formula(i):
            # todo doesn't always work; indices not updated correctly?
            if not i < len(input_raws):
                return
            del input_raws[i]
            del input_fmls[i]
            # start = 3 if self.inst.action != "mg" else 2
            # for j in range(6 + start * (i - 1), 6 + start * (i - 1) + 3):
            #     mids[j].pack_forget()
            # for j in range(3):
            #     del mids[6 + start * (i - 1) + j]
            row = len(mids) - 1 if i > 0 else 1
            mids[row].pack_forget()
            del mids[row]
            # del caps[i]
            del input_lbls[i]
            del rems[i]
            del input_ents[i]
            del btns[i]
            if len(input_fmls) > 1:
                for j in range(1, len(input_fmls)):
                    pos = j if j <= i else j - 1
                    # caps[j].config(text="Premise " + str(pos) + ":")
                    rems[j].bind("<Button>", lambda e: remove_formula(pos))
                    input_raws[j].trace("w", lambda *args: select_entry(pos))
                    btns[j].bind("<Button>", lambda e: parse(pos))
            if len(input_fmls) == 1:
                btn_swap.config(state="disabled")
            set()

        def swap_formulas():
            c, p1 = input_raws[0].get(), input_raws[1].get()
            input_raws[0].set(p1)
            input_raws[1].set(c)
            parse(0)
            parse(1)

        def select_entry(i):
            raw = input_raws[i]
            if raw.get():
                if i >= 0:
                    btns[i].config(state="normal")
                else:
                    btn_parse_struct.config(state="normal")
            else:
                if i >= 0:
                    btns[i].config(state="disabled")
                else:
                    btn_parse_struct.config(state="disabled")

        def parse(i, arg=""):
            raw = input_raws[i].get() if not arg else arg
            lbl = input_lbls[i]
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
                    "vardomains":    ("constvar", "var", "const")
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

        def set():
            if not self.inst.action == "mc":
                self.inst.conclusion = input_fmls[0] if input_fmls else None
                self.inst.premises = input_fmls[1:] if len(input_fmls) > 1 else []
            else:
                self.inst.formulas = [tuple([input_fmls[i], input_gs[i].get(), input_ws[i].get()])
                                      for i in range(len(input_fmls))]
            # self.inst.structure = struct
            # update_summary()
            self.inst.completed.append(3)
            self.btn_run.config(state="normal", bg=darkgray, fg=white)

        for child in tab.winfo_children():
            child.destroy()

        # frames
        # canvas =ScrollableFrame(tab)
        # canvas.pack()
        # top
        top = tk.Frame(tab, bg=white)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # top mid
        topmid = tk.Frame(tab, bg=white)
        topmid.pack()  # todo make more compact?
        # mid
        mid = tk.Frame(tab, bg=white)
        mid.pack()
        mids = {i: tk.Frame(mid, bg=white) for i in range(3)}
        for i in mids:
            mids[i].pack(ipadx=5, ipady=5, padx=50)

        # reset button
        btn_reset = tk.Button(tab,
                              bg=white,
                              text="↶",
                              activebackground=lightgray, activeforeground=white)
        btn_reset.pack(in_=topmid, padx=15, side=tk.LEFT)
        btn_reset.bind("<Button>", lambda e: self.tab_2())

        # heading
        lbl_head = tk.Label(tab,
                            bg=white,
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
        btn_load.bind("<Button>", lambda e: load())

        # input fields
        input_fmls = []
        struct = None
        input_modes = []
        input_raws = []
        input_gs = []
        input_ws = []
        caps = []
        input_lbls = []
        rems = []
        input_ents = []
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
        lbl_sum = tk.Label(bg=white)
        # update_summary()
        # lbl_sum.pack(in_=mids[0])

        # captions
        cap_fml = tk.Label(tab, text="Formula:", bg=white)
        cap_fmls = tk.Label(tab, text="Formulas:", bg=white)
        cap_concl = tk.Label(tab, text="Conclusion:", bg=white)
        cap_prems = tk.Label(tab, text="Premises:", bg=white)
        cap_struct = tk.Label(tab, text="Structure:", bg=white)

        # buttons
        btn_swap = tk.Button(tab,
                             bg=white,
                             text="⇅",
                             state="disabled",
                             activebackground=lightgray, activeforeground=white,
                             width=1, height=1)
        btn_swap.bind("<Button>", lambda e: swap_formulas())
        btn_add_fml = tk.Button(tab,
                                bg=white,
                                text="+",
                                activebackground=lightgray, activeforeground=white,
                                width=1, height=1)
        btn_add_fml["font"] = font_large
        btn_add_fml.bind("<Button>", lambda e: add_formula())

        if self.inst.action == "mc":
            # todo add field for specification of g and w
            cap_struct.pack(in_=mids[0], padx=15, pady=15)
            # raw_struct = tk.StringVar()
            # ent_struct = tk.Entry(tab,
            #                textvariable=struct_raw)
            # ent_struct.pack(in_=mids[6], side=tk.LEFT, expand=True)
            # ent_struct.trace("w", lambda *args: select_entry(-1))
            ent_struct = tk.Text(tab, height=8, width=45)
            ent_struct.pack(in_=mids[1], side=tk.LEFT)
            input_ents.append(ent_struct)
            btn_parse_struct = tk.Button(tab,
                                         bg=white,
                                         text="↻",
                                         # bg=darkgray, fg=white,
                                         activebackground=lightgray, activeforeground=white)
            btn_parse_struct["font"] = font_large
            btn_parse_struct.pack(in_=mids[1], side=tk.LEFT, padx=5)
            btn_parse_struct.bind("<Button>", lambda e: parse_struct())
            btns.append(btn_parse_struct)
            lbl_struct = tk.Text(tab, height=6, width=40, borderwidth=0, bg=white)
            lbl_struct.configure(inactiveselectbackground=lbl_struct.cget("selectbackground"))
            lbl_struct.configure(state="disabled")
            lbl_struct.pack(in_=mids[1], side=tk.LEFT, padx=15, expand=True)
            mid2 = tk.Frame(mid, bg=white)
            mids[2] = mid2
            mids[2].pack(ipadx=5, ipady=5)
            cap_fmls.pack(in_=mids[2], side=tk.LEFT, padx=15, pady=15)
            btn_add_fml.pack(in_=mids[2], side=tk.LEFT)
            add_formula()
        elif self.inst.action == "mg":
            # cap_pseudo.pack(in_=mids[0], side=tk.LEFT, padx=15)
            cap_fmls.pack(in_=mids[0], side=tk.LEFT, pady=15)
            btn_add_fml.pack(in_=mids[0], side=tk.LEFT, padx=15)
            add_formula()
        else:
            cap_concl.pack(in_=mids[0], side=tk.LEFT, padx=15, pady=15)
            add_formula()
            btn_swap.pack(in_=mids[2], side=tk.LEFT, padx=15)
            cap_prems.pack(in_=mids[2], side=tk.LEFT, pady=15)
            btn_add_fml.pack(in_=mids[2], side=tk.LEFT, padx=15)
        input_ents[0].focus()

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

        def set():
            self.inst.logic = {var: val.get() for (var, val) in variables.items()}
            self.inst.completed.append(1)

        def next_step(i):
            set()
            self.switch_to_tab(i)

        # frames
        # top
        top = tk.Frame(tab, bg=white)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab, bg=white)
        mid.pack()
        mids = {i: tk.Frame(mid, bg=white) for i in range(5)}
        for i in mids:
            mids[i].pack(ipadx=0, ipady=5)

        # heading
        lbl_head = tk.Label(tab,
                            bg=white,
                            text="Which logic are you working in?",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # selection
        categories = ["proppred", "classint", "modal", "constvar", "frame"]
        labels = {
                "proppred": [("propositional logic", "prop"), ("predicate logic", "pred")],
                "classint": [("classical", "class"), ("intuitionistic", "int")],
                "modal":    [("non-modal", "nonmodal"), ("modal", "modal")],
                "constvar": [("with constant domains", "const"), ("with varying domains", "var")],
                "frame":    [("frame K", "K")]
        }
        variables = {
                "proppred": tk.StringVar(None, self.inst.logic["proppred"]),
                "classint": tk.StringVar(None, self.inst.logic["classint"]),
                "modal":    tk.StringVar(None, self.inst.logic["modal"]),
                "constvar": tk.StringVar(None, self.inst.logic["constvar"]),
                "frame":    tk.StringVar(None, self.inst.logic["frame"])
        }
        self.rbs_logic = {cat: dict() for cat in categories}
        for i, cat in enumerate(categories):
            for j, (txt, val) in enumerate(labels[cat]):
                enabled = False if cat in ["constvar", "frame"] else True
                rb = tk.Radiobutton(tab,
                                    bg=white,
                                    fg=black if enabled else white,
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
            if not underline.get():
                cbs[0].config(fg=black)
            if not hide.get():
                cbs[1].config(fg=black)
            set()

        def select_entry():
            set()

        def decrease_num_models():
            num_models.set(str(int(num_models.get()) - 1))

        def increase_num_models():
            num_models.set(str(int(num_models.get()) + 1))

        def decrease_size_limit():
            size_limit.set(str(int(size_limit.get()) - 1))

        def increase_size_limit():
            size_limit.set(str(int(size_limit.get()) + 1))

        def set():
            self.inst.output = output.get()
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
        top = tk.Frame(tab, bg=white)
        top.pack(side=tk.TOP, pady=25, anchor=tk.N)
        # mid
        mid = tk.Frame(tab, bg=white)
        mid.pack()
        mids = []
        for i in range(9):
            if i in [2, 5]:
                sep = tk.Frame(mid)
                sep.pack(pady=10)
            midi = tk.Frame(mid, bg=white)
            midi.pack()
            mids.append(midi)
        m = 0

        # heading
        lbl_head = tk.Label(tab,
                            bg=white,
                            text="How would you like pyPL to work?",
                            # font=("OpenSans", "12", "bold"),
                            anchor=tk.NW, justify=tk.LEFT) \
            .pack(in_=top)

        # denotation output format
        lbl_output = tk.Label(tab,
                              bg=white,
                              text="Denotation output format:")
        lbl_output.pack(in_=mids[m])
        m += 1
        
        cbs = []
        verbose = tk.BooleanVar(None, self.inst.verbose)
        enabled = True if self.inst.action == "mc" else False
        cb = tk.Checkbutton(tab,
                            bg=white,
                            fg=black,
                            text="verbose",
                            variable=verbose,
                            onvalue=True, offvalue=False,
                            state="disabled",  # not yet implemented
                            # state="normal" if enabled else "disabled",
                            selectcolor=darkgray, activebackground=lightgray, activeforeground=white,
                            indicatoron=0,
                            width=25, pady=7.5)
        cb.pack(in_=mids[m], side=tk.LEFT, pady=5)
        m += 1
        cb.config(command=lambda arg=cb: select_cb(arg))
        cbs.append(cb)
        
        # tableau output format
        lbl_output = tk.Label(tab,
                              bg=white,
                              text="Tableau output format:")
        lbl_output.pack(in_=mids[m])
        m += 1

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
        cb.config(command=lambda arg=cb: select_cb(arg))
        initial_select_cb(cb)
        cbs.append(cb)
        hide = tk.BooleanVar(None, self.inst.hide_nonopen)
        cb = tk.Checkbutton(tab,
                            bg=white,
                            text="hide non-open branches",
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
        lbl_output = tk.Label(tab,
                              bg=white,
                              text="Model generation mode:")
        lbl_output.pack(in_=mids[m])
        m += 1
        generations = [("mathematical", "mathematical"), ("linguistic", "linguistic")]
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
        lbl_num_models = tk.Label(tab,
                                  bg=white,
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
        lbl_size_limit = tk.Label(tab,
                                  bg=white,
                                  text="Tableau tree size limit factor:")
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

        tableau = __import__("tableau")
        concl = self.inst.conclusion
        premises = self.inst.premises
        formulas = self.inst.formulas
        axioms = self.inst.axioms
        structure = self.inst.structure

        # settings

        classical = True if self.inst.logic["classint"] == "class" else False
        propositional = True if self.inst.logic["proppred"] == "prop" else False
        modal = True if self.inst.logic["modal"] == "modal" else False
        vardomains = True if self.inst.logic["constvar"] == "var" else False
        frame = self.inst.logic["frame"]
        linguistic = True if self.inst.generation_mode == "linguistic" else False

        latex = True if self.inst.output == "tex" else False
        num_models = self.inst.num_models
        underline_open = True if self.inst.underline_open else False
        hide_nonopen = True if self.inst.hide_nonopen else False

        if self.inst.action == "mc":
            # model checking
            denot = ""
            for fml, v, w in formulas:
                denot += "[[" + str(fml) + "]]" + structure.s + ("," + v if v else "") + ("," + w if w else "") + "\n= "
                if not modal and classical:  # classical non-modal logic
                    if not v:
                        denot += str(fml.denotV(structure))
                    else:
                        denot += str(fml.denot(structure, structure.v[v]))
                else:  # classical modal logic or intuitionistic logic
                    if not v:
                        if not w:
                            denot += str(fml.denotVW(structure))
                        else:
                            denot += str(fml.denotV(structure, w))
                    else:
                        if not w:
                            denot += str(fml.denotW(structure, structure.v[v]))
                        else:
                            denot += str(fml.denot(structure, structure.v[v], w))
                denot += "\n\n"

            # todo make look nicer?
            # tk.messagebox.showinfo("", str(denot))
            win_output = tk.Toplevel(self.root, bg=white)
            # win_output.geometry("1000x605")  # todo geometry only applied on second opening
            win_output.destroy()
            win_output = tk.Toplevel(self.root, bg=white)
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
            win_output.tk.call('wm', 'iconphoto', win_output._w, tk.PhotoImage(file=icon_path))
            lbl_output = tk.Label(win_output, text=str(denot), font=font, bg=white)
            lbl_output.pack(pady=32)
            # frame_output = tk.Frame(win_output)
            # win_output.destroy()

        elif self.inst.action != "tt":
            validity = True if self.inst.action == "tp" else False
            satisfiability = True if self.inst.action == "mg" else False

            tableau.Tableau(concl, premises=premises, axioms=axioms,
                            validity=validity, satisfiability=satisfiability, linguistic=linguistic,
                            classical=classical, propositional=propositional,
                            modal=modal, vardomains=vardomains, frame=frame,
                            latex=latex, file=True, num_models=num_models,
                            underline_open=underline_open, hide_nonopen=hide_nonopen)

        else:
            # test if theorem
            tab1 = tableau.Tableau(concl, premises=premises, axioms=axioms,
                                   validity=True, satisfiability=False, linguistic=linguistic,
                                   classical=classical, propositional=propositional,
                                   modal=modal, vardomains=vardomains, frame=frame,
                                   latex=latex, file=True, silent=True, num_models=num_models,
                                   underline_open=underline_open, hide_nonopen=hide_nonopen)

            if tab1.closed():
                # win_wait.destroy()
                tab1.show()
            else:
                # test if non-theorem
                tab2 = tableau.Tableau(concl, premises=premises, axioms=axioms,
                                       validity=False, satisfiability=False, linguistic=linguistic,
                                       classical=classical, propositional=propositional,
                                       modal=modal, vardomains=vardomains, frame=frame,
                                       latex=latex, file=True, silent=True, num_models=num_models,
                                       underline_open=underline_open, hide_nonopen=hide_nonopen)
                if not tab2.infinite():
                    # win_wait.destroy()
                    tab2.show()

             # todo output sometimes shown twice?


if __name__ == "__main__":
    # redirect output to log file
    if not debug:
        import sys
        path_log = os.path.join(os.path.dirname(__file__), "pyPL.log")
        sys.stdout = open(path_log, 'w')
        sys.stderr = sys.stdout

    # run
    PyPLGUI()
