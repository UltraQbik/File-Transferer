import logging
import os
import json
import base64
import socket
import threading
import threading as th
import time

import customtkinter as ctk
from pgpy import PGPKey, PGPMessage, PGPUID
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm
from tkinter.filedialog import askopenfilename
from logging import log, DEBUG, INFO, WARNING, ERROR, CRITICAL
import logging
from dataclasses import dataclass
import urllib
from urllib import parse

PORT = 13698
BUFFER_SIZE = 8192
TRANSFER_END = b'\x11packet_transfer_end\x11'

KEY_SIZE = 4096


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


@dataclass
class TrustedServer:
    ip: str
    fingerprint: str
    name: str


class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()
        self._logger = logging.getLogger("Server")

        self._active_servers: list[ServerObject] = []
        self._trusted_servers: list[TrustedServer] = self._get_trusted_servers()
        self._key: PGPKey = self._load_key()
        self._running = True
        self._local_ip = "UNKNOWN"

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _get_trusted_servers(self):
        self._logger.log(INFO, "Loading servers")

        if not os.path.exists("TrustedServers"):
            self._logger.log(WARNING, "TrustedServers does not exist, creating it now")
            open("TrustedServers", "w").close()

        with open("TrustedServers", "r") as file:
            servers = file.readlines()

        servers = [TrustedServer(
            server.split(" ")[0],
            server.split(" ")[1],
            parse.unquote(server.split(" ")[2])
        ) for server in servers]

        self._logger.log(INFO, f"Loaded {len(servers)} servers")

        return servers

    def trust_server(self, server) -> None:
        self._logger.log(INFO, f"Trusting server with fingerprint {server.fingerprint}")

        self._trusted_servers.append(server)

        with open("TrustedServers", "w") as file:
            file.write(
                "\n".join(f"{server.ip} {server.fingerprint} {parse.quote(server.name)}" for server in self._trusted_servers)
            )

    def run(self) -> None:
        self._local_ip = socket.gethostbyname(socket.gethostname())
        self._logger.log(INFO, f"Starting server at {self._local_ip} on port {PORT}")

        self._socket.bind((self._local_ip, PORT))

        while self._running:
            time.sleep(5)

    @property
    def my_ip(self):
        return self._local_ip

    def close(self) -> None:
        self._running = False

    def _load_key(self):
        if os.path.exists("ServerKey"):
            self._logger.log(INFO, "Loading key from file")

            with open("ServerKey", "rb") as file:
                key = file.read()

            key, _ = PGPKey.from_blob(key)

            self._logger.log(INFO, "Key loaded with fingerprint " + key.fingerprint)

            return key

        else:
            self._logger.log(WARNING, "Key not found, generating one now")

            key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, KEY_SIZE)
            uid = PGPUID.new("FileTransferServer")
            key.add_uid(
                uid,
                usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed]
            )

            with open("ServerKey", "wb") as file:
                file.write(key.__bytes__())

            self._logger.log(INFO, "Key loaded with fingerprint " + key.fingerprint)

            return key

    @property
    def key_fingerprint(self):
        return self._key.pubkey.fingerprint

    @property
    def human_key(self):
        """
        more human friendly version of the key, can be used in rendering
        """
        return self._key.pubkey.fingerprint[-8:-4] + " " + self._key.pubkey.fingerprint[-4:]

    def discover_server_at(self, ip):
        # beep boop
        ...

    @property
    def known_servers(self):
        return self._active_servers


class ServerObject:
    def __init__(self):
        self._canonical_name = "Good Server"
        self._public_key: PGPKey = self._load_key()

    def _load_key(self):
        log(INFO, "Loading key from server")
        # do some stuff here
        # talk to server
        key_from_server = b"\xc6\x8d\x04dc\xc6\xcc\x01\x04\x00\xa0 }|\xaf\xeb\xb2\x19(\xa2B\x88z\x1b\x10Z\xf5!\xf8\xf6^\xf6\x88\x7f\x01\xe3\xaey\x90R\xe3\xe5\x19\x95\xf8\x95\xbf\n\x12\x822\xb0\x08i\xb6\xa9\xbb/\xda\x9c\xb3x\x9d\xb0J\x05\xfa>\xf3h\xe3\xa8\xd7,R\xd9X\x15\x82d\xe8.\xbc\x08\x90\x9b\x84d\x0fD_\x14\x8f7\xbc|'<T\x9b\xaa*z\x1b\xc0\x05\x97\xebd\xc3\xe6\xd0\xde=\xa8`\xcc\xdc\x9f\xf1\xf6\x03|xp\x05\xabl\xbd\xf5\x8dN\xe5\xd3_\xb6\x81\r\x00\x11\x01\x00\x01\xcd\x12FileTransferServer\xc2\xb9\x04\x13\x01\x08\x00#\x05\x02dc\xc6\xcc\x02\x1b\x06\x02\x1e\x01\x16!\x04')\xe0\xe4\x02g\x15\x1d\x9f\x8b\xe4\xd6\xb0I\xef\x98~O\xc8P\x00\n\t\x10\xb0I\xef\x98~O\xc8Pp\xd2\x04\x00\x81\x83\xa0\x07ri\t4\xfe\xb6=\\\xf2@6pD\x91\xa8\xba\xdeZ\xd1]C\xcdWN3d\x12K\x13\x82\x835\xde\x0c!Y\x8a\x89f`~\tTW1\xec7\xfcl\x04\x90\xc8\xfd\xf0\xcb\xc31LYk\x7f9\x98B#z\xe3\xb8Ehi\xc7\x9a/hO\x92\x17<\xdb\x81\xb8\xfaZ\x81\xa5\xea\xe3)\xfbm\x80\xee\xf5\xaa\x0b\x00nuP\xf4=\xe7\x12\x84\xd3\x87\xb2j\x85\x08\xf3\xb9\xf3\x16\xe2\xb3B\xa4.f\xc4\x08\x96"

        key, _ = PGPKey.from_blob(key_from_server)

        if not key.is_public:
            log(WARNING, "Server sent private key... what?")
            key = key.pubkey

        log(INFO, "Key loaded with fingerprint " + key.fingerprint)

        return key

    @property
    def name(self):
        return self._canonical_name

    @property
    def key_fingerprint(self):
        return self._public_key.fingerprint

    @property
    def human_key(self):
        """
        more human friendly version of the key, can be used in rendering
        """
        return self._public_key.fingerprint[-8:-4] + " " + self._public_key.fingerprint[-4:]

    def get_files_from_directory(self, external_file_location):
        ...

    def i_want_to_send_file_button(self, file_location, external_file_location):
        ...


class Application:
    def __init__(self, server):
        self._server: Server = server

        self._win: ctk.CTk | None = None
        self._widgets: dict = {}
        self._opened_file: str = ""

        self._users: dict[str, dict[str, socket.socket]] = {}
        self._socket: socket.socket | None = None
        self._ip: str = socket.gethostbyname(socket.gethostname())
        self._host: bool = False
        self._buffer: bytes = bytes()

        self._window = th.Thread(target=self._create_window)

    def launch(self):
        self._window.start()
        self._window.join()

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


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    server = Server()
    # app = Application(server=server)

    server.start()
    # app.launch()

    server.close()

if __name__ == '__main__':
    # logging.basicConfig(level=DEBUG, filename="FileTransfer.log")
    logging.basicConfig(level=DEBUG)
    main()
