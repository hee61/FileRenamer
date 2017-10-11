# ****** General Messageboard ******
# TODO: Update Messageboard

# ****** Imports ******
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askokcancel, askyesno
import configparser as cfp
from tkinter import font
from tkinter import ttk
from time import clock
import tkinter as tk
import random as rd
import re
import os

# ****** Special Imports ******
from xntypes import File, ListStack
from xntypes.tktypes import PageMaster, Output, ButtonFrame

# ****** Globals ******
FONT = "Source Code Pro"
FONT_SIZE = 12


class FileRenamerApp(PageMaster):
    VERSION = "3.5.5"
    ICON = "FileRenamer.ico"
    NAME = "FileRenamer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toggle(self)
        self.title("%s %s" % (self.NAME, self.VERSION))
        self.protocol("WM_DELETE_WINDOW", self.main_close)
        try: self.iconbitmap(self.ICON)
        except tk.TclError: pass

        self.container.bind_all("Control-k", self.main_close)

        # ****** Globals ******
        self.ini_file = "%s.ini" % self.NAME
        self.tk_style = ttk.Style()

        # ****** Imported Settings Definitions ******
        self.supported_extensions = tk.StringVar()
        self.os_operations = tk.BooleanVar()
        self.skip_named = tk.BooleanVar()
        self.nested_dirs = tk.BooleanVar()
        self.debug_var = tk.BooleanVar()

        # ****** Variable Initializations ******
        self.os_operations.set(True)
        self.non_export = ["os_ops"]
        self.defaults = {}
        self.default_extensions = "jpg, png, jpeg, gif, mp4, webm"
        self.variables = dict()

        # ****** Create Widgets ******
        self._import_settings()
        self.DEBUG = self.debug_var.get()

        if self.DEBUG:
            self.container.columnconfigure(0, weight=1)
            self.debug_window = Debug(self.container, self)
            self.debug_window.grid(
                row=0, column=1,
                sticky="nsew")

            self.display("Master Window Initialized")

        self._update_settings()
        self._make_copy_dict()

        frame = MainPage(self.container, self)
        self.frames[MainPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def main_close(self):
        for page in self.frames.values():
            if hasattr(page, "exit_steps"):
                page.exit_steps()
        self.suggest_export()
        self.destroy()

    def _import_settings(self):
        try:
            settings = cfp.ConfigParser()
            settings.read(self.ini_file)
            userset = settings["UserSettings"]
            self.supported_extensions.set(
                userset.get(
                    "supportedextensions",
                    self.default_extensions
                ))
            self.skip_named.set(
                userset.get(
                    "skipnamed",
                    True
                ))
            self.nested_dirs.set(
                userset.get(
                    "searchnested",
                    True
                ))
            self.debug_var.set(
                userset.getboolean(
                    "developer",
                    False
                ))
        except KeyError:
            self.supported_extensions.set(self.default_extensions)
            self.skip_named.set(True)
            self.nested_dirs.set(True)
            self.debug_var.set(False)

    def _export_settings(self):
        config = cfp.ConfigParser()
        config["UserSettings"] = {
            "supportedextensions":
                self.supported_extensions.get(),
            "skipnamed":
                self.skip_named.get(),
            "searchnested":
                self.nested_dirs.get()}

        if self.DEBUG:
            config["UserSettings"].update(
                developer=str(self.debug_var.get()))

        with open(self.ini_file, "w") as config_file:
            config.write(config_file)
        self._update_settings()

    def _make_copy_dict(self):
        self.vdc = dict()
        outdict = self.variables
        for key, value in zip(outdict, outdict.values()):
            if isinstance(value, tk.Variable):
                self.vdc[key] = type(value)()
                self.vdc[key].set(value.get())
            else:
                self.vdc[key] = list(value)

    def suggest_export(self):
        check = list()
        expdict = self.variables
        checkdict = self.vdc
        for key, item, copy in zip(
                expdict, expdict.values(),
                checkdict.values()):
            if key not in self.non_export:
                if isinstance(item, tk.Variable):
                    if not copy.get() == item.get():
                        check.append(False)
                else:
                    # this statement is not the same as the
                    # one above is for tk variables only.
                    # This is a check for non tk variables.
                    if not copy == item:
                        check.append(False)
        if all(check):
            self.display("\nExport suggested, not needed")
        else:
            self._export_settings()
            self.display("\nExported settings to ini file")
            self._make_copy_dict()

    def _update_settings(self):
        self.variables = dict()
        self.variables["skip_named"] = self.skip_named
        self.variables["supported_extensions"] = self.supported_extensions
        self.variables["os_operations"] = self.os_operations
        self.variables["nested_dirs"] = self.nested_dirs
        self.variables["debug_var"] = self.debug_var
        exts = self.supported_extensions.get().split(",")
        for i in range(len(exts)):
            exts[i] = exts[i].lstrip(" ")
        self.variables["converted_extensions"] = exts

        if self.DEBUG:
            self.display_vars()

    def display_vars(self):
        self.display("\nSettings Updated:")
        for key, value in zip(
                self.variables,
                self.variables.values()):
            self.display("".join(
                i[0].capitalize() for i in key.split("_")
                ) + ":", end=" ")
            if isinstance(value, tk.Variable):
                self.display(str(value.get()))
            else:
                self.display(", ".join(value))

    def display(self, *text, end="\n", sep=" "):
        if self.DEBUG:
            self.debug_window.display(*text, end=end, sep=sep)
        else:
            pass

    def __call__(self, *args, **kwargs):
        self.center(self)
        self.toggle(self)
        self.mainloop()


class Page(tk.Frame):
    @classmethod
    def class_name(cls):
        return cls.__name__

    def __init__(self, container, master, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.parent = master
        self.container = container
        self.variables = self.parent.variables
        self.tk_style = self.parent.tk_style

    def _pull_vars(self):
        self.variables = self.parent.variables

    def telldebug(self, *text):
        self.parent.display(*text)


class Debug(Page):
    def __init__(self, container, master, *args, **kwargs):
        super().__init__(container, master, *args, **kwargs)
        self._create_widgets()

    def _create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.output = Output(
            self, relief="sunken",
            width=40, height=1)

        if FONT in font.families():
            self.output["font"] = (FONT, FONT_SIZE)
        self.output["background"] = "#E6E6E6"
        self.output["foreground"] = "#293134"
        self.output["selectbackground"] = "#808080"
        self.output["selectforeground"] = "#293134"
        self.output.grid(
            row=0, column=0,
            sticky="nsew",
            padx=1, pady=1)
        self.display = self.output.display


class Options(Page):
    def __init__(self, container, master, *args, **kwargs):
        super().__init__(container, master, *args, **kwargs)
        self._pull_vars()
        self.local_vars = dict()
        for key in self.variables:
            if isinstance(self.variables[key], tk.Variable):
                self.local_vars[key] = type(self.variables[key])()
                self.local_vars[key].set(self.variables[key].get())

        self._create_widgets()

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # ****** Main Options Frame ******
        mainframe = ttk.Frame(self)
        mainframe.grid(
            row=0, column=0,
            sticky="nsew")
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=10)
        mainframe.rowconfigure(1, weight=90)

        # ****** Mainframe Bindings ******
        mainframe.bind_all("Control-s", self._config_apply)

        # ****** Widget Description Frame ******
        self.descbox = Output(
            mainframe,
            height=7,
            relief="flat")
        if "Source Code Pro" in font.families():
            self.descbox["font"] = ("Source Code Pro", "12")
        self.descbox["background"] = "#E6E6E6"
        self.descbox["foreground"] = "#293134"
        self.descbox["selectbackground"] = "#808080"
        self.descbox["selectforeground"] = "#293134"
        self.descbox["takefocus"] = False
        self.descbox.grid(
            row=0, column=0,
            sticky="nsew",
            padx=1, pady=1)
        self.display = self.descbox.display
        self.clear_desc = self.descbox.delete_all

        # ****** Description Notebook ******
        notebook_frame = ttk.Frame(mainframe)
        notebook_frame.grid(
            row=1, column=0,
            sticky="nsew",
            padx=5)
        notebook_frame.rowconfigure(0, weight=1)
        notebook_frame.columnconfigure(0, weight=1)

        notebook = ttk.Notebook(notebook_frame)
        notebook.grid(sticky="nsew")
        notebook.rowconfigure(0, weight=1)
        notebook.columnconfigure(0, weight=1)

        # ****** Rename Tab Frame ******
        renametab_pad = ttk.Frame(notebook)
        renametab_pad.grid(row=0, column=0, sticky="nsew")
        renametab_pad.columnconfigure(0, weight=1)
        renametab_pad.rowconfigure(0, weight=1)
        notebook.add(renametab_pad, text="Renaming".center(20))

        renametab = ttk.Frame(renametab_pad)
        renametab.grid(sticky="nsew", padx=5, pady=5)

        rename_widgets = 3
        for i in range(rename_widgets):
            renametab.rowconfigure(i, pad=1)
        renametab.columnconfigure(1, weight=1)

        default_desc = "EMPTY DESCRIPTION"
        # ****** Rename Tab Widgets ******
        se_desc = "" or default_desc
        se_row = rename_widgets - 3
        se_label = ttk.Label(
            renametab,
            text="Supported Extensions:",
            anchor="e")
        se_label.description = se_desc
        se_label.grid(
            row=se_row, column=0,
            sticky="ew")
        se_label.bind("<Enter>", self.description)
        se_label.bind("<Leave>", self.description)

        se_entry = ttk.Entry(
            renametab,
            textvariable=self.local_vars["supported_extensions"])
        se_entry.description = se_desc
        se_entry.grid(
            row=se_row,
            column=1,
            sticky="ew")

        sn_desc = "" or default_desc
        nd_row = rename_widgets - 2
        nd_label = ttk.Label(
            renametab,
            text="Skip Named:",
            anchor="e")
        nd_label.description = sn_desc
        nd_label.grid(
            row=nd_row, column=0,
            sticky="ew")
        nd_label.bind("<Enter>", self.description)
        nd_label.bind("<Leave>", self.description)

        nd_check = ttk.Checkbutton(
            renametab,
            variable=self.local_vars["skip_named"],
            onvalue=True, offvalue=False)
        nd_check.description = sn_desc
        nd_check.grid(
            row=nd_row, column=1,
            sticky="ew")

        nd_description = "" or default_desc
        nd_row = rename_widgets - 1
        nd_label = ttk.Label(
            renametab,
            text="Search Nested Dirs:",
            anchor="e")
        nd_label.grid(row=nd_row, column=0, sticky="ew")
        nd_label.description = nd_description
        nd_label.bind("<Enter>", self.description)
        nd_label.bind("<Leave>", self.description)

        nd_check = ttk.Checkbutton(
            renametab,
            variable=self.local_vars["nested_dirs"],
            onvalue=True, offvalue=False)
        nd_check.grid(row=nd_row, column=1, sticky="w")
        nd_check.description = nd_description

        if self.parent.DEBUG:
            # ****** Debug Tab Frame ******
            debugtab_pad = ttk.Frame(notebook)
            debugtab_pad.grid(row=0, column=0, sticky="nsew")
            debugtab_pad.columnconfigure(0, weight=1)
            debugtab_pad.rowconfigure(0, weight=1)
            notebook.add(debugtab_pad, text="Debug".center(20))

            debugtab = ttk.Frame(debugtab_pad)
            debugtab.grid(sticky="nsew", padx=5, pady=5)

            debug_widgets = 2
            for i in range(debug_widgets):
                debugtab.rowconfigure(i, pad=1)
            debugtab.columnconfigure(1, weight=1)

            # ****** Debug Tab Widgets ******
            oo_desc = ""
            oo_row = 0
            oo_label = ttk.Label(
                debugtab,
                text="Enable OS Operations:",
                anchor="e")
            oo_label.description = oo_desc
            oo_label.grid(
                row=oo_row, column=0,
                sticky="ew")
            oo_label.bind("<Enter>", self.description)
            oo_label.bind("<Leave>", self.description)

            oo_entry = ttk.Checkbutton(
                debugtab,
                variable=self.local_vars["os_operations"],
                onvalue=True, offvalue=False)
            oo_entry.description = oo_desc
            oo_entry.grid(
                row=oo_row, column=1,
                sticky="ew")

            dd_description = "" or default_desc
            dd_row = debug_widgets - 1
            dd_label = ttk.Label(
                debugtab, anchor="e",
                text="Disable Debug Widgets:")
            dd_label.grid(row=dd_row, column=0, sticky="ew")
            dd_label.description = dd_description
            dd_label.bind("<Enter>", self.description)
            dd_label.bind("<Leave>", self.description)

            dd_check = ttk.Checkbutton(
                debugtab, variable=self.local_vars["debug_var"],
                command=self.disable_debug,
                onvalue=False, offvalue=True)
            dd_check.grid(row=dd_row, column=1, sticky="w")
            dd_check.description = dd_description
            dd_check.bind("<Activate>", self.disable_debug)

        # ****** Option Buttons ******
        buttons_left = {}
        buttons_right = {
            "OK": self._config_ok,
            "Apply": self._config_apply,
            "Cancel": self._return
        }
        buttons = ButtonFrame(self)
        buttons.make_buttons(buttons_left, buttons_right)
        buttons.grid(row=1, sticky="sew", padx=5, pady=5)

    def disable_debug(self, event=None):
        check = askokcancel(
            title="Confirm",
            message=(
                "The program must be restarted\n"
                + "to remove debug widgets.\n"
                + "Restart?"
            ))
        self.local_vars["debug_var"].set(not check)
        if check:
            self.parent.debug_var.set(False)
            self.parent.main_close()
            run()

    def description(self, event):
        if event.type == "7":
            self.display(event.widget.description)
        elif event.type == "8":
            self.clear_desc()
        else:
            self.display(event.type)

    def _reset_vars(self):
        for key in self.local_vars:
            self.local_vars[key].set(self.variables[key].get())

    def _push_vars(self):
        for key in self.local_vars:
            self.variables[key].set(self.local_vars[key].get())

    def _return(self):
        self.parent.show_frame(MainPage)
        self._reset_vars()

    def _config_apply(self):
        self._push_vars()
        self.parent.suggest_export()

    def _config_ok(self):
        self._push_vars()
        self.parent.suggest_export()
        self._return()


class MainPage(Page):
    def __init__(self, container, master, *args, **kwargs):
        super().__init__(container, master, *args, **kwargs)

        # ****** Output Log Counting ******
        log_name = "FR_Output"
        self.num_of_logs = int()
        log_folder = r".\Logs"
        if not os.path.exists(log_folder):
            os.mkdir(log_folder)
        else:
            log_list = os.listdir(log_folder)
            if len(log_list):
                last_log = str()
                for log in log_list:
                    if log[:len(log_name)] == log_name:
                        last_log = log
                log_reg = re.compile(r"(%s)(\d+)(.txt)" % log_name).search(last_log)
                if log_reg is not None:
                    self.num_of_logs = int(log_reg[2])

        self.telldebug("Number of Logs:", self.num_of_logs)

        # ****** Page Variables ******
        self.folder = tk.StringVar()
        self.lead = tk.StringVar()
        self.name = tk.StringVar()
        self.lead_length = 3

        # ****** Initialization ******
        self._create_widgets()

    def _create_widgets(self):
        self.text_window = Output(
            self, width=70,
            height=12,
            relief="sunken")
        if "Source Code Pro" in font.families():
            self.text_window["font"] = ("Source Code Pro", "10")
        self.text_window.grid(
            row=0, column=0,
            sticky="nsew",
            padx=5, pady=5)

        self.rowconfigure(0, weight=90)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=1)
        self.display = self.text_window.display

        entry_frame = ttk.Frame(self)
        entry_frame.columnconfigure(3, weight=1)
        entry_frame.grid(
            row=1, column=0,
            sticky="nsew",
            padx=20, pady=5)
        for i in range(3):
            entry_frame.rowconfigure(i, pad=1)

        # ****** Folder Entry ******
        folder_label = ttk.Label(
            entry_frame,
            text="Folder:",
            anchor="e")
        folder_label.grid(
            row=0, column=0,
            sticky="ew")

        folder_entry = ttk.Entry(
            entry_frame,
            textvariable=self.folder)
        folder_entry.grid(
            row=0, column=1,
            sticky="ew",
            columnspan=3)
        folder_entry.bind("<Return>", self._browse_folders)

        # ****** Lead Entry ******
        lead_label = ttk.Label(
            entry_frame,
            text="Lead:",
            anchor="e")
        lead_label.grid(
            row=1, column=0,
            sticky="ew")

        lead_entry = ttk.Entry(
            entry_frame,
            textvariable=self.lead)
        lead_entry.grid(
            row=1, column=1,
            sticky="ew")
        lead_entry.bind("<Return>", self._lead_search)

        # ****** Name Entry ******
        name_label = ttk.Label(
            entry_frame,
            text="%10s" % "Name:",
            anchor="e")
        name_label.grid(
            row=1, column=2,
            sticky="ew")

        name_entry = ttk.Entry(
            entry_frame,
            textvariable=self.name)
        name_entry.grid(
            row=1, column=3,
            sticky="ew")
        # name_entry.bind("<Return>", self._name_gen)

        # ****** Program Buttons ******
        buttons_left = {
            "Options": self._settings
        }
        buttons_right = {
            "Browse": self._browse_folders,
            "Rename": self.rename,
            "Exit": self.parent.main_close
        }

        buttons = ButtonFrame(self)
        buttons.make_buttons(buttons_left, buttons_right)
        buttons.grid(
            row=2, column=0,
            sticky="sew",
            padx=5, pady=5)

        # ****** Status and Progress Frame ******
        statprog = ttk.Frame(self)
        statprog.grid(row=3, sticky="sew")
        statprog.columnconfigure(0, weight=1)

        # ****** Status Bar ******
        self.status = tk.StringVar()
        self.ready_status = "Ready"
        self.status.initialize(self.ready_status)
        self.status_bar = ttk.Label(
            statprog,
            textvariable=self.status,
            relief="sunken", border=1,
            anchor="w")
        self.status_bar.grid(row=1, sticky="sew")

        # ****** Progress Bar ******
        self.progress_bar = ttk.Progressbar(
            statprog, mode="determinate")
        self.progress_bar.grid(row=0, sticky="new")

    def exit_steps(self):
        self.export_output_logs()

    def _settings(self, event=None):
        self.parent.show_frame(Options)

    def export_output_logs(self):
        self.telldebug("\nExporting Output Logs")
        self.text_window.delete_all()

    def _lead_search(self, event=None):
        if not self.folder.get():
            return

        leadreg = re.compile("(\\d){%d,}" % self.lead_length).search(self.folder.get())
        if leadreg is not None:
            self.lead.set(leadreg.group())

    def _browse_folders(self, event=None):
        self.status.set("Browsing")
        self.folder.set(askdirectory(title="Select Folder"))
        self.status.set(self.ready_status)

    def _push_files(self, directories, stack, variables):
        # ****** Variable Shorthands ******
        folder = directories.pop()
        search_nested = variables[0]
        skip_named = variables[1]
        supp_exts = variables[2]
        lead = variables[3]

        # ****** Function Instructions ******
        for item in os.listdir(folder):
            ext_list = item.split(".")  # separating name and extension
            if len(ext_list) >= 2:
                ext = str(ext_list[-1])  # the last item is the extension

                # ****** Checking For Similar Leads ******
                same_lead = item[:len(lead)] == lead
                skip_check = (not same_lead) if skip_named else True

                # ****** Pushing to the Stack ******
                if ext.lower() in supp_exts and skip_check:
                    file = File(item, folder, ext)
                    stack.push(file)
            else:
                # ****** Adding Directories to Search List ******
                item = os.path.join(folder, item)
                if os.path.isdir(item) and search_nested:
                    directories.append(item)

        if len(directories) > 0:
            self._push_files(directories, stack, variables)
        else:
            self.telldebug("\n%d" % len(stack), "files pushed to stack")

    def rename(self, event=None):
        folder = self.folder.get()
        if not folder or not os.path.isdir(folder):
            self._browse_folders()
            return

        lead = self.lead.get()
        lead_check = "".join(
            ("The length of the lead entered",
             "is shorter than recommended, \n",
             "Do you wish to continue?"
             ))
        if len(lead) < self.lead_length:
            if not askyesno(message=lead_check):
                return

        self._pull_vars()

        os_ops = self.variables["os_operations"].get()
        os_ops_check = "".join(
            ("Are you sure you want",
             "to rename these files?\n",
             "This process cannot be reversed."
             ))
        if os_ops and not askyesno(message=os_ops_check):
            return

        self.status.set("Renaming Files")
        self.export_output_logs()

        # ****** Variable Definitions ******
        name = self.name.get()
        skip_named = self.variables["skip_named"].get()
        conv_exts = self.variables["converted_extensions"]
        search_nested = self.variables["nested_dirs"].get()
        names_generated = 0

        file_length = 30

        files = ListStack()
        check_list = list()
        renamed_list = list()
        failed_list = list()

        time_start = clock()
        dirs = [folder]
        self.status.set("Pushing Files")

        self.telldebug("\nPushing files to stack")
        push_variables = (search_nested, skip_named, conv_exts, lead)
        self._push_files(dirs, files, push_variables)
        len_of_files = len(files)
        self.status.set("Renaming Files")

        self.progress_bar["maximum"] = len(files)

        while not files.is_empty():
            # ****** Selecting a File From the Stack ******
            pop_file: File = files.pop()

            new_name: str
            name_taken = True
            while name_taken:

                # ****** Name Generation Calculations ******
                len_name_lead: int = len(lead) + len(name)
                digits: int = max(5, len(str(len(files))) + 1)
                name_max: int = max(file_length, (len_name_lead + 2 + digits))
                name_genrange: int = name_max - (len_name_lead + 2 if name else 0)

                # ****** Name Generation ******
                new_name = "".join(str(rd.randint(0, 9)) for iteration in range(name_genrange))

                # ****** Checking Whether the Name is Taken ******
                if all(new_name != other_name for other_name in check_list):
                    name_taken = False
                    
                # ****** Counter Increment ******
                names_generated += 1
            
            # ****** Name Concatenation ******
            name_check = (" " + name + " ") if name else ""
            full_name: str = "".join(
                (lead, name_check, new_name, ".", pop_file.extension)
            )

            # ****** OS Renaming Operations ******
            if os_ops:
                os.rename(
                    os.path.join(pop_file.folder, pop_file.name),
                    os.path.join(pop_file.folder, full_name))
                renamed_list.append(full_name)
            else:
                self.display(pop_file.name, ">", full_name)

            # ****** Appending Names to Lists ******
            check_list.append(new_name)

            # ****** Updating Master Widgets ******
            self.progress_bar.step()
            self.parent.update_idletasks()

        # ****** Displaying Information to User ******
        total_time = clock() - time_start
        out_tup = names_generated, len_of_files, total_time
        self.display(folder)
        self.display("%d names generated for %d items in %.3f seconds." % out_tup)
        self.display("%d files renamed" % len(renamed_list))
        if len(failed_list) > 0:
            self.display("These files failed to rename:")
            for item in failed_list:
                self.display(" "+chr(8594), item)
        self.status.set("Done")


def run():
    app = FileRenamerApp()
    app()

if __name__ == "__main__":
    run()
