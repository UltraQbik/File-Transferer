import time
import threading as th
from abc import ABC

import customtkinter as ctk
from logging import log, DEBUG, INFO, WARNING, ERROR, CRITICAL


def create_two_panes(master) -> tuple:
    # create sides for the settings window
    left_side = ctk.CTkFrame(master)
    left_side.pack(padx=4, pady=4, fill="both", expand=True, side="left")

    right_side = ctk.CTkFrame(master)
    right_side.pack(padx=4, pady=4, fill="both", expand=True, side="right")

    return left_side, right_side


class ConnectTabView(ctk.CTkTabview, ABC):
    def __init__(self, master, server, **kwargs):
        super(ConnectTabView, self).__init__(master, **kwargs)

        self._server = server

        # create tabs
        self.add("Known servers")
        self.add("Trusted servers")

        # add widgets to "Known servers" tab
        self._known_servers_tab()

    def _known_servers_tab(self):
        tab = self.tab("Known servers")

        left, right = create_two_panes(tab)

        # dropdown server menu
        def dropdown_callback(var):
            # print(var, servers.index(var))
            pass
        # servers = [server.name for server in self._server.known_servers]
        servers = [f"192.168.{(i**3)%256}.{(i*3)%256}" for i in range(32)]
        server_dropdown = ctk.CTkComboBox(left, values=servers, command=dropdown_callback, width=300)
        server_dropdown.set("pick a known server")
        server_dropdown.pack(padx=4, pady=4, fill="x")


class OptionTabView(ctk.CTkTabview, ABC):
    def __init__(self, master, **kwargs):
        super(OptionTabView, self).__init__(master, **kwargs)

        # create tabs
        self.add("General settings")
        self.add("Connection settings")
        self.add("Maybe settings")

        # add widgets to the "General settings" tab
        self._general_settings_tab()

        # add widgets to the "Connection settings" tab
        self._connection_settings_tab()

        # add widgets to the "Maybe settings" tab
        self._maybe_settings_tab()

    def _general_settings_tab(self):
        tab = self.tab("General settings")

        left, right = create_two_panes(tab)

        # theme switch
        def _theme_switch():
            if theme_switch.get():
                ctk.set_appearance_mode("light")
            else:
                ctk.set_appearance_mode("dark")
        theme_switch = ctk.CTkSwitch(left, text="light theme", command=_theme_switch, width=180)
        theme_switch.pack(padx=4, pady=4, fill="x")
        # theme switch label
        theme_label = ctk.CTkLabel(right, text="Changes the theme of the UI (default: dark)")
        theme_label.pack(padx=4, pady=4, anchor="w")

        # default download folder
        download_entry = ctk.CTkEntry(left, width=180)
        download_entry.insert(0, "downloads")
        download_entry.pack(padx=4, pady=4, fill="x")
        # default download folder label
        download_label = ctk.CTkLabel(right, text="folder to which downloaded from server content will be put")
        download_label.pack(padx=4, pady=4, anchor="w")

    def _connection_settings_tab(self):
        tab = self.tab("Connection settings")

        left, right = create_two_panes(tab)

    def _maybe_settings_tab(self):
        tab = self.tab("Maybe settings")

        epik = ctk.CTkLabel(tab, text="Great UI bruv")
        epik.configure(font=ctk.CTkFont(size=72))
        epik.pack(padx=4, pady=4)


class UI:
    def __init__(self, server):
        self._server = server
        self._win: ctk.CTk | None = None

        self._picked_server: int = 0

        self._thread: th.Thread | None = None

    def start(self):
        self._thread = th.Thread(target=self._create_window)
        self._thread.start()

    def withdraw(self):
        self._win.withdraw()

    def deiconify(self):
        self._win.deiconify()

    def close(self):
        self._win.quit()

    @staticmethod
    def open_settings():
        # create top level window
        pop = ctk.CTkToplevel()
        pop.wm_title("Connection")
        pop.geometry("700x340")

        # Launches the window behind the main one, uncomment to make it always on top
        pop.attributes("-topmost", True)

        # create tabview
        tabview = OptionTabView(pop)
        tabview.pack(padx=8, pady=8, fill="both", expand=True)

    def open_connections_menu(self):
        # create top level window
        pop = ctk.CTkToplevel()
        pop.wm_title("Connection")
        pop.geometry("700x340")

        # Launches the window behind the main one, uncomment to make it always on top
        pop.attributes("-topmost", True)

        # create connection tabview
        tabview = ConnectTabView(pop, self._server)
        tabview.pack(padx=8, pady=8, fill="both", expand=True)

    def _create_window(self):
        # create the root window
        self._win = ctk.CTk()
        self._win.wm_title("Great!")
        self._win.geometry("1000x500")

        # create top frame
        top_frame = ctk.CTkFrame(self._win, height=30)
        top_frame.pack(padx=2, pady=2, fill="x", side="top")

        left_frame, right_frame = create_two_panes(self._win)

        open_connect_button = ctk.CTkButton(top_frame, text="connect", width=40, command=self.open_connections_menu)
        open_connect_button.pack(padx=4, pady=4, side="left")

        options_button = ctk.CTkButton(top_frame, text="options", width=40, command=self.open_settings)
        options_button.pack(padx=4, pady=4, side="right")

        self._win.wm_protocol("WM_DELETE_WINDOW", self.withdraw)
        self._win.mainloop()


def main():
    ui = UI(None)
    ui.start()


if __name__ == '__main__':
    main()
