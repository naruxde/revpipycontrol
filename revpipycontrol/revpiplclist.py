# -*- coding: utf-8 -*-
u"""Fenster um RevPi-Verbindungen einzurichten."""

__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2018 Sven Sager"
__license__ = "GPLv3"

import os.path
import pickle
import tkinter
import tkinter.messagebox as tkmsg
from mytools import gettrans
from mytools import savefile_connections as savefile
from revpidevelop import _loaddefaults as developloaddefaults
from revpidevelop import _savedefaults as developsavedefaults
from revpiprogram import _loaddefaults as programloaddefaults
from revpiprogram import _savedefaults as programsavedefaults
from os import makedirs


# Übersetzungen laden
_ = gettrans()


def get_connections():
    u"""Verbindungen aus Datei laden.
    @return dict() mit Verbindungen"""
    if os.path.exists(savefile):
        with open(savefile, "rb") as fh:
            connections = pickle.load(fh)
        return connections
    else:
        return {}


class RevPiPlcList(tkinter.Frame):

    u"""TK Fenster."""

    def __init__(self, master):
        u"""Init RevPiPlcList-class.
        @param master tkinter master"""
        super().__init__(master)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.pack()

        self.changes = False

        # Daten laden
        self._connections = get_connections()

        # Fenster bauen
        self._createwidgets()
        self.build_listconn()

    def _checkclose(self, event=None):
        u"""Prüft ob Fenster beendet werden soll.
        @param event tkinter-Event"""
        ask = True
        if self.changes:
            ask = tkmsg.askyesno(
                _("Question"),
                _("Do you really want to quit? \nUnsaved changes will "
                    "be lost"),
                parent=self.master
            )

        if ask:
            self.master.destroy()

    def _createwidgets(self):
        u"""Erstellt alle Widgets."""
        self.master.wm_title(_("RevPi Python PLC connections"))
        self.master.wm_resizable(width=False, height=False)
        self.master.protocol("WM_DELETE_WINDOW", self._checkclose)

        # Listbox mit vorhandenen Verbindungen
        self.scr_conn = tkinter.Scrollbar(self)
        self.scr_conn.grid(column=1, row=0, rowspan=10, sticky="ns")
        self.list_conn = tkinter.Listbox(self, width=20, heigh=15)
        self.list_conn.bind("<<ListboxSelect>>", self.evt_listconn)
        self.list_conn.grid(column=0, row=0, rowspan=10)
        self.list_conn["yscrollcommand"] = self.scr_conn.set
        self.scr_conn["command"] = self.list_conn.yview

        # Variablen und Defaultwerte
        self.var_address = tkinter.StringVar(self)
        self.var_port = tkinter.StringVar(self)
        self.var_name = tkinter.StringVar(self)
        self.var_port.set("55123")

        # Eingabefelder für Adresse und Namen
        tkinter.Label(self, text=_("Name")).grid(
            column=2, row=0, sticky="wn", padx=5, pady=5
        )
        self.txt_name = tkinter.Entry(self, textvariable=self.var_name)
        self.txt_name.bind("<KeyRelease>", self.evt_keypress)
        self.txt_name.grid(
            column=3, row=0, columnspan=3, sticky="n", padx=5, pady=5
        )

        tkinter.Label(self, text=_("IP address")).grid(
            column=2, row=1, sticky="wn", padx=5, pady=5
        )
        self.txt_address = tkinter.Entry(self, textvariable=self.var_address)
        self.txt_address.bind("<KeyRelease>", self.evt_keypress)
        self.txt_address.grid(
            column=3,  row=1, columnspan=3, sticky="n", padx=5, pady=5
        )

        tkinter.Label(self, text=_("Port")).grid(
            column=2, row=2, sticky="wn", padx=5, pady=5
        )
        self.txt_port = tkinter.Entry(self, textvariable=self.var_port)
        self.txt_port.bind("<KeyRelease>", self.evt_keypress)
        self.txt_port.grid(
            column=3, row=2, columnspan=3, sticky="n", padx=5, pady=5
        )

        # Listenbutton
        self.btn_new = tkinter.Button(
            self, text=_("New"), command=self.evt_btnnew
        )
        self.btn_new.grid(column=2, row=3, sticky="s")
        self.btn_add = tkinter.Button(
            self, text=_("Apply"),
            command=self.evt_btnadd, state="disabled"
        )
        self.btn_add.grid(column=3, row=3, sticky="s")
        self.btn_remove = tkinter.Button(
            self, text=_("Remove"),
            command=self.evt_btnremove, state="disabled"
        )
        self.btn_remove.grid(column=4, row=3, sticky="s")

        # Fensterbuttons
        self.btn_save = tkinter.Button(
            self, text=_("Save"), command=self.evt_btnsave
        )
        self.btn_save.grid(column=3, row=9, sticky="se")
        self.btn_close = tkinter.Button(
            self, text=_("Close"), command=self._checkclose
        )
        self.btn_close.grid(column=4, row=9, sticky="se")

    def _saveappdata(self):
        u"""Speichert Verbindungen im home Dir.
        @return True, bei erfolgreicher Verarbeitung"""
        try:
            makedirs(os.path.dirname(savefile), exist_ok=True)
            with open(savefile, "wb") as fh:
                pickle.dump(self._connections, fh)
            self.changes = False
        except Exception:
            return False

        # Andere Einstellungen aufräumen
        dict_o = developloaddefaults()
        for revpi in tuple(dict_o.keys()):
            if revpi not in self._connections:
                del dict_o[revpi]
        developsavedefaults(None, dict_o)
        dict_o = programloaddefaults()
        for revpi in tuple(dict_o.keys()):
            if revpi not in self._connections:
                del dict_o[revpi]
        programsavedefaults(None, dict_o)

        return True

    def build_listconn(self):
        u"""Füllt Verbindungsliste."""
        self.list_conn.delete(0, "end")
        lst_conns = sorted(self._connections.keys(), key=lambda x: x.lower())
        self.list_conn.insert("end", *lst_conns)

    def evt_btnadd(self):
        u"""Verbindungseinstellungen übernehmen."""
        # TODO: Daten prüfen
        self._connections[self.var_name.get()] = \
            (self.var_address.get(), self.var_port.get())

        self.build_listconn()
        self.evt_btnnew()
        self.changes = True

    def evt_btnnew(self):
        u"""Neue Verbindung erstellen."""
        self.list_conn.select_clear(0, "end")
        self.evt_listconn()

        self.btn_add["state"] = "disabled"
        self.var_address.set("")
        self.var_name.set("")
        self.var_port.set("55123")

    def evt_btnremove(self):
        u"""Verbindung löschen."""
        item_index = self.list_conn.curselection()
        if len(item_index) == 1:
            item = self.list_conn.get(item_index[0])
            ask = tkmsg.askyesno(
                _("Question"),
                _("Do you really want to delete the selected connection '{0}'?"
                    "").format(item),
                parent=self.master
            )
            if ask:
                # Daten löschen
                del self._connections[item]
                self.build_listconn()
                self.evt_btnnew()
                self.changes = True

    def evt_btnsave(self):
        u"""Alle Verbindungen speichern."""
        if self._saveappdata():
            ask = tkmsg.askyesno(
                _("Information"),
                _("Successfully saved. \nDo you want to close this window?"),
                parent=self.master
            )
            if ask:
                self.master.destroy()
        else:
            tkmsg.showerror(
                _("Error"),
                _("Failed to save connections"),
                parent=self.master
            )

    def evt_listconn(self, evt=None):
        u"""Übernimmt Einstellungen in Eingabefelder."""

        item_index = self.list_conn.curselection()
        if len(item_index) == 1:

            # Daten lesen
            item = self.list_conn.get(item_index[0])
            self.var_name.set(item)
            self.var_address.set(self._connections[item][0])
            self.var_port.set(self._connections[item][1])

            self.btn_add["state"] == "normal"
            self.btn_remove["state"] = "normal"
        else:
            self.btn_remove["state"] = "disabled"

    def evt_keypress(self, evt=None):
        u"""Passt bei Tastendruck den Status der Buttons an."""
        okvalue = "normal" if (
            self.var_address.get() != "" and
            self.var_name.get() != "" and
            self.var_port.get() != ""
        ) else "disabled"
        self.btn_add["state"] = okvalue


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiPlcList(root)
    myapp.mainloop()
