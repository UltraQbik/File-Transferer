import time
import threading as th
import customtkinter as ctk
from logging import log, DEBUG, INFO, WARNING, ERROR, CRITICAL


class UI:
    def __init__(self, server):
        self._server = server
        self._win: ctk.CTk | None = None

        self._picked_server: int = 0

        self._thread: th.Thread | None = None

    def run(self):
        self._thread = th.Thread(target=self._create_window)
        self._thread.start()

    def close(self):
        self._win.quit()

    def _create_window(self):
        # some magic numbers
        frp = 6         # padding

        # create the root window
        self._win = ctk.CTk()
        self._win.wm_title("Great!")
        self._win.geometry("1000x500")

        # create top frame
        top_frame = ctk.CTkFrame(self._win, height=30)
        top_frame.pack(padx=frp, pady=frp, fill="x", side="top")

        def create_connection_window():
            # create top level window
            pop = ctk.CTkToplevel()
            pop.wm_title("Connection")
            pop.geometry("700x340")

            # Launches the window behind the main one, uncomment to make it always on top
            pop.attributes("-topmost", True)

            # create inner frame
            inner_frame = ctk.CTkFrame(pop)
            inner_frame.pack(padx=frp, pady=frp, fill="both", expand=True)

            # create a server frame
            server_frame = ctk.CTkFrame(inner_frame)
            server_frame.pack(padx=frp, pady=frp, fill="both", side="left")

            # servers = [server.name for server in self._server.known_servers]
            servers = [f"server_192.168.{i**2%255}.{i}" for i in range(16)]
            server_dropdown = ctk.CTkOptionMenu(server_frame, values=servers, dynamic_resizing=False, width=200)
            server_dropdown.set("pick a known server")
            server_dropdown.pack(padx=frp, pady=frp, fill="x")

            # create a connection frame
            connect_frame = ctk.CTkFrame(inner_frame)
            connect_frame.pack(padx=frp, pady=frp, fill="both", expand=True, side="right")

            connect_button = ctk.CTkButton(connect_frame, text="connect!")
            connect_button.pack(padx=frp, pady=frp, side="left", anchor="nw")

            # NOTE: Radio buttons cause the window to bug out and not close properly
            # def radiobutton_callback():
            #     self._picked_server = server_var.get()
            #
            # NOTE: text=server must be changed to text=server.name when uncommenting this line
            # servers = self._server.known_servers
            # servers = [f"server_192.168.{i**2%255}.{i}" for i in range(32)]
            # server_var = ctk.StringVar()
            # for idx, server in enumerate(servers):
            #     radiobutton = ctk.CTkRadioButton(
            #         server_frame,
            #         text=server, value=server, variable=server_var,
            #         command=radiobutton_callback)
            #     radiobutton.pack(padx=5, pady=5, fill="x")

        def open_options():
            # create top level window
            pop = ctk.CTkToplevel()
            pop.wm_title("Connection")
            pop.geometry("700x340")

            # Launches the window behind the main one, uncomment to make it always on top
            pop.attributes("-topmost", True)

            # create inner frame
            inner_frame = ctk.CTkFrame(pop)
            inner_frame.pack(padx=frp, pady=frp, fill="both", expand=True)

            # create top frame
            top_opt_frame = ctk.CTkFrame(inner_frame, height=30)
            top_opt_frame.pack(padx=frp, pady=frp, fill="x", side="top")

            def change_mode(val):
                if not val:
                    ctk.set_appearance_mode("dark")
                else:
                    ctk.set_appearance_mode("light")

            change_theme_button = ctk.CTkCheckBox(top_opt_frame, text="theme", width=50,
                                                  command=lambda: change_mode(change_theme_button.get()))
            change_theme_button.pack(padx=frp, pady=frp, side="left")

            # create folder entry
            entry_frame = ctk.CTkFrame(inner_frame)
            entry_frame.pack(padx=frp, pady=frp, fill="both", side="left")

            download_folder = ctk.CTkEntry(entry_frame)
            download_folder.delete(0, "end")
            download_folder.insert(0, "downloads")
            download_folder.pack(padx=frp, pady=frp, side="left", anchor="nw")

            # create label frame
            label_frame = ctk.CTkFrame(inner_frame)
            label_frame.pack(padx=frp, pady=frp, fill="both", expand=True, side="right")

            download_folder_label = ctk.CTkLabel(label_frame, text="Default download folder")
            download_folder_label.pack(padx=frp, pady=frp, side="left", anchor="nw")

        open_connect_button = ctk.CTkButton(top_frame, text="connect", width=40, command=create_connection_window)
        open_connect_button.pack(padx=frp, pady=frp, side="left")

        options_button = ctk.CTkButton(top_frame, text="options", width=40, command=open_options)
        options_button.pack(padx=frp, pady=frp, side="right")

        # create left frame
        left_frame = ctk.CTkFrame(self._win)
        left_frame.pack(padx=frp, pady=frp, fill="both", expand=True, side="left")

        # create right frame
        right_frame = ctk.CTkFrame(self._win)
        right_frame.pack(padx=frp, pady=frp, fill="both", expand=True, side="right")

        self._win.wm_protocol("WM_DELETE_WINDOW", self.close)
        self._win.mainloop()


def main():
    ui = UI(None)
    ui.run()


if __name__ == '__main__':
    main()
