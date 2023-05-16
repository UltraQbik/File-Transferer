import threading as th
import time

import customtkinter as ctk
from logging import log, DEBUG, INFO, WARNING, ERROR, CRITICAL


class UI:
    def __init__(self):
        self._win: ctk.CTk | None = None

        self._thread = th.Thread(target=self._create_window)
        self._thread.start()

    def _create_window(self):
        self._win = ctk.CTk()
        self._win.wm_title("Great!")
        self._win.geometry("1000x500")

        # create top frame
        top_frame = ctk.CTkFrame(self._win, height=30)
        top_frame.pack(padx=5, pady=5, fill="x", side="top")

        def _create_connection_window():
            # create top level window
            pop = ctk.CTkToplevel()
            pop.wm_title("Connection")
            pop.geometry("700x340")

            # doing that only because it launches the window behind the main one
            pop.attributes("-topmost", True)

            # create inner frame
            inner_frame = ctk.CTkFrame(pop)
            inner_frame.pack(padx=5, pady=5, fill="both", expand=True)

            # create server list frame
            server_frame = ctk.CTkFrame(inner_frame, width=300)
            server_frame.pack(padx=5, pady=5, side="left", fill="y", anchor="nw")

            # TODO: add server list

        open_connect_button = ctk.CTkButton(top_frame, text="connect", width=40, command=_create_connection_window)
        open_connect_button.pack(padx=5, pady=5, side="left")

        # create left frame
        left_frame = ctk.CTkFrame(self._win)
        left_frame.pack(padx=5, pady=5, fill="both", expand=True, side="left")

        # create right frame
        right_frame = ctk.CTkFrame(self._win)
        right_frame.pack(padx=5, pady=5, fill="both", expand=True, side="right")

        self._win.mainloop()

    def close(self):
        self._win.quit()


def main():
    test = UI()
    time.sleep(5)
    test.close()


if __name__ == '__main__':
    main()
