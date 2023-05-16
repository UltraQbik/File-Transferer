import logging
import os
import json
import base64
import socket
import threading
import threading as th
import customtkinter as ctk
from tkinter.filedialog import askopenfilename
from logging import log, DEBUG, INFO, WARNING, ERROR, CRITICAL

PORT = 13698
BUFFER_SIZE = 8192
TRANSFER_END = b'\x11packet_transfer_end\x11'


def message_box(title, message):
    log(INFO, f"Creating message box {title=}")

    pop = ctk.CTkToplevel()
    pop.wm_title(title)
    pop.attributes("-topmost", True)

    label = ctk.CTkLabel(pop, text=message)
    label.pack(padx=10, pady=10)

    button = ctk.CTkButton(pop, text="Ok", command=lambda: pop.destroy())
    button.pack(padx=10, pady=10)


def check_connection(sock: socket.socket | None) -> bool:
    if sock is None:
        return False

    try:
        sock.getsockname()
        return True

    except socket.error:
        return False


class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()

    def get_files_from_directory(self, external_file_location):
        ...

    def i_want_to_send_file_button(self, file_location, external_file_location, ip):
        ...


class Application:
    def __init__(self):
        self._win: ctk.CTk | None = None
        self._widgets: dict = {}
        self._opened_file: str = ""

        self._users: dict[str, dict[str, socket.socket | pgpy.PGPKey]] = {}
        self._socket: socket.socket | None = None
        self._ip: str = socket.gethostbyname(socket.gethostname())
        self._host: bool = False
        self._buffer: bytes = bytes()

        window = th.Thread(target=self._create_window)
        window.start()
        window.join()

    def _create_window(self):
        self._win = ctk.CTk()

        self._win.wm_title("File transfer")
        self._win.geometry("350x375")

        # Connection status
        connection_frame = ctk.CTkFrame(self._win, corner_radius=8)
        connection_frame.pack(padx=10, pady=10, fill="x")

        connection_label = ctk.CTkLabel(connection_frame, text="Connection status")
        connection_label.pack(padx=10, pady=10, side="left")

        connection_status_label = ctk.CTkLabel(connection_frame, text="not connected")
        connection_status_label.pack(padx=10, pady=10, side="left")

        self._widgets["connection_status_label"] = connection_status_label

        # Inner frame
        inner_frame = ctk.CTkFrame(self._win, corner_radius=8)
        inner_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # File frame
        file_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        file_frame.pack(padx=10, pady=10, anchor="nw")

        def choose_file_button():
            self._opened_file = askopenfilename()
            file_label.configure(text=os.path.basename(self._opened_file))

        file_button = ctk.CTkButton(file_frame, text="Choose file", width=290, command=choose_file_button)
        file_button.pack(padx=10, pady=10, side="left")

        file_label = ctk.CTkLabel(file_frame, text="", width=120, anchor="w")
        file_label.pack(padx=10, pady=10, side="left")

        # Sharing button frame
        sending_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        sending_frame.pack(padx=10, pady=10, anchor="nw")

        def share_file_button():
            if not check_connection(self._socket):
                message_box("Error", "You are not connected!")
                return

            with open(self._opened_file, "rb") as file:
                self.send(
                    "file",
                    file.read(),
                    filename=os.path.basename(self._opened_file))

        send_file_button = ctk.CTkButton(sending_frame, text="Send all", width=290, command=share_file_button)
        send_file_button.pack(padx=10, pady=10)

        # Server connection
        client_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        client_frame.pack(padx=10, pady=10, anchor="nw")

        client_label = ctk.CTkLabel(client_frame, text="Server IP", width=50)
        client_label.pack(padx=10, pady=10, side="left")

        client_entry = ctk.CTkEntry(client_frame, width=120)
        client_entry.pack(padx=10, pady=10, side="left")

        def connect_client_button():
            entry = client_entry.get()

            if check_connection(self._socket):
                message_box("Error", "You are already connected to a server!")
                return

            octets = [x.isdecimal() for x in entry.split(".")]
            if len(octets) == 4 and all(octets):
                th.Thread(target=self._connect_client, args=(entry,), daemon=True).start()
            else:
                message_box("Error", f"Incorrect ip address '{entry}'")

        client_button = ctk.CTkButton(client_frame, text="connect", width=80, command=connect_client_button)
        client_button.pack(padx=10, pady=10, side="left")

        # Host connection
        hosting_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        hosting_frame.pack(padx=10, pady=10, anchor="nw")

        hosting_label = ctk.CTkLabel(hosting_frame, text="User IP", width=50)
        hosting_label.pack(padx=10, pady=10, side="left")

        hosting_ip_label = ctk.CTkLabel(hosting_frame, text=self._ip, width=120)
        hosting_ip_label.pack(padx=10, pady=10, side="left")

        def connect_server_button():
            if check_connection(self._socket):
                message_box("Error", "You are already connected to a server!")
                return

            th.Thread(target=self._connect_server, daemon=True).start()

        hosting_button = ctk.CTkButton(hosting_frame, text="host", width=80, command=connect_server_button)
        hosting_button.pack(padx=10, pady=10, side="left")

        self._win.mainloop()

    # def _connect_client(self, ip):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #
    #     try:
    #         sock.connect((ip, PORT))
    #         self._widgets["connection_status_label"].configure(text="connection successful")
    #     except socket.error:
    #         self._widgets["connection_status_label"].configure(text="connection failed")
    #         return
    #
    #     self._socket = sock
    #
    #     while True:
    #         try:
    #             data = self._socket.recv(BUFFER_SIZE)
    #         except socket.error:
    #             self._socket.close()
    #             self._widgets["connection_status_label"].configure(text="connection shutdown")
    #             return
    #
    #         if data[-len(TRANSFER_END):] == TRANSFER_END:
    #             self._buffer += data[0:-len(TRANSFER_END)]
    #             self._decode_packet(self._buffer)
    #             self._buffer = bytes()
    #         else:
    #             self._buffer += data
    #
    # def _connect_server(self):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #
    #     try:
    #         sock.bind((self._ip, PORT))
    #         sock.listen(1)
    #         self._widgets["connection_status_label"].configure(text="connection successful")
    #
    #     except socket.socket:
    #         self._widgets["connection_status_label"].configure(text="connection failed")
    #         return
    #
    #     self._host = True
    #     self._socket = sock
    #
    #     while True:
    #         connection, _ = sock.accept()
    #         peer = {"socket": connection, "key": None}
    #         self._users[connection.getpeername().__repr__()] = peer
    #
    #         th.Thread(target=self._server_handler, args=(peer,), daemon=True).start()
    #
    # def _server_handler(self, peer: dict[str, socket.socket]):
    #     while True:
    #         try:
    #             data = peer["socket"].recv(BUFFER_SIZE)
    #             for _, user in self._users.items():
    #                 if user != peer:
    #                     user["socket"].send(data)
    #
    #         except socket.error:
    #             self._users.pop(peer["socket"].getpeername().__repr__())
    #             peer["socket"].close()
    #             break
    #
    #         if data[-len(TRANSFER_END):] == TRANSFER_END:
    #             self._buffer += data[0:-len(TRANSFER_END)]
    #             self._decode_packet(self._buffer)
    #             self._buffer = bytes()
    #
    #         else:
    #             self._buffer += data
    #
    # def _broadcast(self, data: bytes) -> None:
    #     if self._host:
    #         for _, user in self._users.items():
    #             user["socket"].send(data)
    #     else:
    #         self._socket.send(data)
    #
    # def _generate_payload(self, packet_type: str, data: bytes, **kwargs) -> bytes:
    #     packet = {
    #         "type": packet_type,
    #         "address": self._socket.getsockname().__repr__(),
    #         "data": base64.b64encode(data).decode('ascii')}
    #     packet.update(kwargs)
    #     payload = json.dumps(packet).encode("ascii")
    #
    #     return payload + TRANSFER_END
    #
    # def _decode_packet(self, packet: bytes) -> None:
    #     decoded = json.loads(packet.decode("ascii"))
    #     decoded["data"] = base64.b64decode(decoded['data'])
    #
    #     match decoded["type"]:
    #         case "file":
    #             self._decode_file(decoded)
    #         case _:
    #             log(WARNING, "Received request with unknown type,", decoded['type'])
    #
    # def _decode_file(self, decoded: dict) -> None:
    #     log(DEBUG, "Saving file,", decoded['filename'])
    #
    #     with open(decoded["filename"], "wb") as file:
    #         file.write(decoded["data"])
    #
    # def send(self, packet_type: str, data: bytes, **kwargs) -> None:
    #     log(DEBUG, f"Sending file, {packet_type=}")
    #     assert check_connection(self._socket)
    #     self._broadcast(
    #         self._generate_payload(
    #             packet_type,
    #             data,
    #             **kwargs
    #         )
    #     )


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    Application()


if __name__ == '__main__':
    logging.basicConfig(level=DEBUG, filename="FileTransfer.log")
    main()
