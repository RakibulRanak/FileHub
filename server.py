from tkinter import *
from tkinter import ttk
import os
import socket
import threading

HEIGHT = 700
WIDTH = 800 

IP = socket.gethostbyname(socket.gethostname())
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# PORT = 4467
# ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
STATUS = "" 
CLIENT = 0
FILES = ""

root = Tk()
root.title("Server")

canvas = Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

frame = Frame(root, bg='grey')
frame.place(relx=0.05, rely=0.05, relheight = 0.07, relwidth=0.9)

fclient = Frame(root, bg='grey')
status = Frame(root, bg='white')
text = Text(status, state=DISABLED)
lstatus = Label(status, text="Status Bar", bg='white') 
separator = ttk.Separator(status, orient='horizontal')

def show_files():
    files = os.listdir(SERVER_DATA_PATH)
    file_names=""
    if len(files) == 0:
        file_names += "The server directory is empty"
    else:
        file_names += "\n".join(f for f in files)

    list_files = file_names.split('\n')

    lblist = Listbox(root,height=15, width = 45, bg = '#C0DCE0')
    for fil in list_files:
        lblist.insert(END, fil)
    lblist.place(relx=0.1, rely=0.38)

def handle_client(conn, addr):
    global CLIENT, STATUS
    # print(f"[NEW CONNECTION] {addr} connected.")
    STATUS = " > [NEW CONNECTION] " + str(addr) + "connected" + "\n" + STATUS
    lstatus_msg = Label(status, text=STATUS, bg='white')
    lstatus_msg.place(relx=0.05,rely=0.25)

    conn.send("OK@Welcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        if cmd == "LIST":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "LIST@"

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            name=data[1]
            filepath = os.path.join(SERVER_DATA_PATH, name)
            filesize = int(data[2])
            f = open(filepath,'wb')
            data = conn.recv(1024)
            totalRecv = len(data)
            f.write(data)
            while totalRecv < filesize:
                data = conn.recv(1024)
                totalRecv+=len(data)
                f.write(data)
                # print("{0:.2f}".format((totalRecv/float(filesize))
                # *100)+"% DONE")
            f.close()
            print("UPLOAD Completed")
            send_data = "OK@File uploaded successfully."
            conn.send(send_data.encode(FORMAT))
            show_files()
        
        elif cmd == "DOWNLOAD":
            name = data[1]
            filepath = os.path.join(SERVER_DATA_PATH, name)
            msg = str(os.path.getsize(filepath))
            print("size",msg)
            cmd = "SAVE@"+msg+"@"+name
            send_data = cmd.encode(FORMAT)
            conn.send(send_data)
            with open(f"{filepath}", "rb") as f:
                bytesToSend = f.read(1024)
                conn.send(bytesToSend)
                while len(bytesToSend) !=0:
                    bytesToSend = f.read(1024)
                    conn.send(bytesToSend)
            show_files()

        elif cmd == "DELETE":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "DELETE@"
            filename = data[1]

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                if filename in files:
                    os.system(f"rm {SERVER_DATA_PATH}/{filename}")
                    send_data += "File deleted successfully."
                    show_files()
                else:
                    send_data += "File not found."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            CLIENT -= 1
            fclient.place(relx=0.05, rely=0.25, relheight = 0.07, relwidth=0.9)
            lcli = Label(fclient, text="Active Client Connection: "+str(CLIENT), bg='white')
            lcli.place(relx=0.32, rely=0.05, relheight=0.9,relwidth=0.3)
            break
            
        elif cmd == "HELP":
            data = "OK@"
            data += "LIST: List all the files from the server.\n"
            data += "UPLOAD <path>: Upload a file to the server.\n"
            data += "DOWNLOAD <filename>: Download a file from the server.\n"
            data += "DELETE <filename>: Delete a file from the server.\n"
            data += "LOGOUT: Disconnect from the server.\n"
            data += "HELP: List all the commands."

            conn.send(data.encode(FORMAT))

    # print(f"[DISCONNECTED] {addr} disconnected")
    STATUS = " > [DISCONNECTED] " + str(addr) + "disconnected" + "\n" + STATUS
    lstatus_msg = Label(status, text=STATUS, bg='white')
    lstatus_msg.place(relx=0.05,rely=0.25)
    conn.close()

def connection():
    global CLIENT
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        text.insert(INSERT, " > [Active Connections] " + str(threading.activeCount() - 1) + " \n")

        CLIENT += 1
        fclient.place(relx=0.05, rely=0.25, relheight = 0.07, relwidth=0.9)
        lcli = Label(fclient, text="Active Client Connection: "+str(CLIENT), bg='white')
        lcli.place(relx=0.32, rely=0.05, relheight=0.9,relwidth=0.3)


def conn_button(port, ip_addr):
    lcon1 = Label(root, text="Server is starting...")
    lcon1.place(relx=0.05, rely=0.15)
    PORT = int(port)
    IP=ip_addr
    ADDR = (ip_addr, PORT)
    server.bind(ADDR)
    server.listen()
    lcon2 = Label(root, text="Server is listening on "+str(IP)+":"+str(PORT))
    lcon2.place(relx=0.05, rely=0.20)

    lfname = Label(root, text="Files from Server ", font='Helvetica 10 bold')
    lfname.place(relx=0.40, rely=0.34)

    show_files()

    brefr = Button(root, text="Refresh", bg='#61FF44', fg='white',
                    command=show_files)
    brefr.place(relwidth=0.15, relheight=0.07, relx=0.75, rely=0.53)

    fclient.place(relx=0.05, rely=0.25, relheight = 0.07, relwidth=0.9)
    lcli = Label(fclient, text="Active Client Connection: "+str(CLIENT), bg='white')
    lcli.place(relx=0.32, rely=0.05, relheight=0.9,relwidth=0.3)

    status.place(relx=0.025, rely=0.8, relheight=0.18, relwidth=0.95)
    lstatus.place(relx=0.45, rely=0.05)
    separator.place(relx=0.025,rely=0.225,relwidth=0.95,relheight=0.001)

    thread_1 = threading.Thread(target=connection)
    thread_1.start()

lip = Label(frame, text="IP addr: ")
lip.place(relwidth=0.12, relheight=0.5, relx=0.01, rely=0.25)

lip_addr = Entry(frame, text=IP)
lip_addr.place(relwidth=0.25, relheight=0.7, relx=0.15, rely=0.15)
lip_addr.insert(END, IP)

lport = Label(frame, text="Port: ")
lport.place(relwidth=0.12, relheight=0.5, relx=0.42, rely=0.25)

port = Entry(frame)
port.place(relwidth=0.25, relheight=0.7, relx=0.56, rely=0.15)

bconn = Button(frame, text="Start", bg='black', fg='white',
                    command=lambda: conn_button(port.get(),lip_addr.get()))
bconn.place(relwidth=0.15, relheight=0.7, relx=0.83, rely=0.15)

root.mainloop()

# if __name__ == "__main__":
#     main()

