from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import threading
import socket
import os

HEIGHT = 700
WIDTH = 800 
IP = ""
PORT = 0
FORMAT = "utf-8"
SIZE = 1024
HELP = False
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LIST = []
CLIENT_DATA_PATH = "client_data"
path = ""

root = Tk()
root.title("Client-Server File Transfer")

canvas = Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

frame = Frame(root, bg='grey')
frame.place(relx=0.05, rely=0.05, relheight = 0.07, relwidth=0.9)

def list_button():
    global client, BLIST, LIST, root
    BLIST = True
    cmd="LIST"
    client.send(cmd.encode(FORMAT))

llist = Label(root, text="If you want to see the files from server, click")
blist = Button(root, text="List", bg='#6488D2', fg='white',
                command=list_button)

def pop_up_delete():
    messagebox.showinfo("Deleted!","File deleted successfully!")

def pop_up_download():
    messagebox.showinfo("Downloaded","File downloaded successfully!")

def pop_up_upload(filename):
    messagebox.showinfo("Uploaded", filename+" uploaded successfully")

def show_list():
    global root, lblist, path
    lblist = Listbox(root,height=18, width = 45, bg = '#C0DCE0')
    for files in LIST:
        lblist.insert(END, files)
    lblist.place(relx=0.05, rely=0.22)

    def delete_button():
        file_name=lblist.get(ANCHOR)
        cmd="DELETE"
        client.send(f"{cmd}@{file_name}".encode(FORMAT))
        list_button()

    def download_button():
        file_name=lblist.get(ANCHOR)
        cmd="DOWNLOAD"
        print(file_name)
        client.send(f"{cmd}@{file_name}".encode(FORMAT))

    def select_button():
        global path
        path = filedialog.askopenfilename()
        print(path)

    def logout():
        global client
        cmd = "LOGOUT"
        client.send(cmd.encode(FORMAT))
        root.destroy()
        
    
    def upload_button():
        global path
        cmd="UPLOAD"
        filename = path.split("/")[-1]
        filesize = str(os.path.getsize(path))
        send_data = f"{cmd}@{filename}@{filesize}"
        client.send(send_data.encode(FORMAT))
        with open(f"{path}", "rb") as f:
            bytesToSend = f.read(1024)
            client.send(bytesToSend)
            while len(bytesToSend) !=0:
                bytesToSend = f.read(1024)
                client.send(bytesToSend)
        pop_up_upload(filename)
        list_button()
    
    # bupdate = Button(root, text="Update", bg='#6488D2', fg='white',
    #                 command=list_button)
    # bupdate.place(relwidth=0.1, relheight=0.05,relx=0.28, rely=0.73)

    lip = Label(root, text="To delete or Download selected items")
    lip.place(relx=.63, rely=0.35)
    
    bdelete = Button(root, text="Delete", bg='#FF583F', fg='white',
                    command=delete_button)
    bdelete.place(relwidth=0.12, relheight=0.05,relx=0.75, rely=0.40)
    
    bdownload = Button(root, text="Download", bg='#61FF44', fg='white',
                    command=download_button)
    bdownload.place(relwidth=0.12, relheight=0.05,relx=0.75, rely=0.45)

    lupload = Label(root, text="To upload a file: ")
    lupload.place(relx=0.05, rely=0.83)

    bselect = Button(root, text="Select File", bg='#7E8050', fg='white',
                    command=select_button)
    bselect.place(relwidth=0.50, relheight=0.05,relx=0.22, rely=0.82)

    bupload = Button(root, text="Upload", bg='#033806', fg='white',
                    command=upload_button)
    bupload.place(relwidth=0.12, relheight=0.05,relx=0.73, rely=0.82)

    blogout = Button(root, text="Logout", bg='red', fg='white',command=logout)
    blogout.place(relwidth=0.12, relheight=0.05, relx=0.45, rely=0.90)



def chat():
    global client, LIST

    while True:
        data = client.recv(SIZE).decode(FORMAT)
        mydata = data
        mydata = mydata.split("@")
        cmd = mydata[0]
        
       # print("upore",mydata)

        if cmd == "DISCONNECTED":
            msg = mydata[1]
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            msg = mydata[1]
            print(f"{msg}")
        elif cmd == "DELETE":
            pop_up_delete()
        elif cmd == "LIST":
            msg = mydata[1]
            LIST = msg.split('\n')
            show_list()
        elif cmd == "SAVE":
            name= mydata[2]
            filesize = int(mydata[1])
            filepath = os.path.join(CLIENT_DATA_PATH, name)
            f = open(filepath,'wb')
            data = client.recv(1024)
            totalRecv = len(data)
            f.write(data)
            while totalRecv < filesize:
                data = client.recv(1024)
                totalRecv+=len(data)
                f.write(data)
                # print("{0:.2f}".format((totalRecv/float(filesize))
                # *100)+"% DONE")
            f.close()
            pop_up_download()

    print("Disconnected")
    client.close()


def conn_button(ip, port):
    global IP, PORT, client
    IP = ip
    PORT = int(port)
    ADDR = (IP,PORT)
    client.connect(ADDR)
    thread = threading.Thread(target=chat)
    thread.start()
    llist.place(relx=0.05, rely=0.15)
    blist.place(relwidth=0.1, relheight=0.05,relx=0.48, rely=0.14)

lip = Label(frame, text="IP addr: ")
lip.place(relwidth=0.12, relheight=0.5, relx=0.01, rely=0.25)

ip_addr = Entry(frame)
ip_addr.place(relwidth=0.25, relheight=0.7, relx=0.15, rely=0.15)

lport = Label(frame, text="Port: ")
lport.place(relwidth=0.12, relheight=0.5, relx=0.42, rely=0.25)

port = Entry(frame)
port.place(relwidth=0.25, relheight=0.7, relx=0.56, rely=0.15)

bconn = Button(frame, text="Connect", bg='black', fg='white',
                    command=lambda: conn_button(ip_addr.get(), port.get()))
bconn.place(relwidth=0.15, relheight=0.7, relx=0.83, rely=0.15)
    
root.mainloop()

if __name__ == "__main__":
    chat()