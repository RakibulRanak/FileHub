from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
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
runn = False
if os.path.exists(CLIENT_DATA_PATH)==False:
    os.mkdir(CLIENT_DATA_PATH)

root = Tk()
root.title("Client-Server File Transfer")

canvas = Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

frame = Frame(root, bg='grey')
frame.place(relx=0.05, rely=0.05, relheight = 0.07, relwidth=0.9)

progress = ttk.Progressbar(root, orient = HORIZONTAL,
                       length = 300, mode = 'determinate')
ldownloading = Label(root, text="Downloading... ")
ldownper = Label(root, text=str(0.0)+"%")

progressup = ttk.Progressbar(root, orient = HORIZONTAL,
                       length = 300, mode = 'determinate')
luploading = Label(root, text="Uploading... ")
lupper = Label(root, text=str(0.0)+"%")
lsize = Label(root, text="")

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
    ldownloading.place_forget()
    progress.place_forget()
    ldownper.place_forget()
    lsize.place_forget()

def pop_up_upload(filename):
    messagebox.showinfo("Uploaded", filename+" uploaded successfully")
    luploading.place_forget()
    progressup.place_forget()
    lupper.place_forget()
    lsize.place_forget()


def upload():
    luploading.place(relx=0.2, rely=0.92)
    progressup.place(relx=0.3, rely=0.92)
    lupper.place(relx=0.7, rely=0.92)
    lsize.place(relx=0.8, rely=0.92)
    global path
    cmd="UPLOAD"
    filename = path.split("/")[-1]
    filesize = str(os.path.getsize(path))
    size = os.path.getsize(path)
    lsize.config(text = "Size: " +str(round(size/(1000*1000))) + " MB")
    send_data = f"{cmd}@{filename}@{filesize}"
    client.send(send_data.encode(FORMAT))
    totalSend = 0
    with open(f"{path}", "rb") as f:
        bytesToSend = f.read(1024)
        while len(bytesToSend) !=0:
            totalSend += 1024
            prg = (totalSend/size)*100
            progressup['value'] = prg
            lupper.config(text = str(round(prg,2))+"%")
            client.send(bytesToSend)
            bytesToSend = f.read(1024)
    pop_up_upload(filename)
    list_button()

def upload_button():
    thread2 = threading.Thread(target=upload)
    thread2.start()

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
        lfileupload = Label(root, text=path.split("/")[-1])
        lfileupload.place(relx=0.35, rely=0.83)
        print(path)

    def logout():
        global client
        cmd = "LOGOUT"
        client.send(cmd.encode(FORMAT))
        root.destroy()
        
    
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
    bselect.place(relwidth=0.12, relheight=0.05,relx=0.22, rely=0.82)

    bupload = Button(root, text="Upload", bg='#033806', fg='white',
                    command=upload_button)
    bupload.place(relwidth=0.12, relheight=0.05,relx=0.73, rely=0.82)

    blogout = Button(frame, text="Logout", bg='red', fg='white',command=logout)
    blogout.place(relwidth=0.12, relheight=0.7, relx=0.87, rely=0.15)



def chat():
    global client, LIST, progress, runn

    while True:
        data = client.recv(SIZE).decode(FORMAT)
        mydata = data
        mydata = mydata.split("@")
        cmd = mydata[0]
        
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
            ldownloading.place(relx=0.2, rely=0.92)
            progress.place(relx=0.3, rely=0.92)
            ldownper.place(relx=0.7, rely=0.92)
            lsize.place(relx=0.8, rely=0.92)
            runn = True
            progress['value'] = 0
            name= mydata[2]
            filesize = int(mydata[1])
            lsize.config(text = "Size: " +str(round(filesize/(1000*1000),2)) + " MB")
            filepath = os.path.join(CLIENT_DATA_PATH, name)
            f = open(filepath,'wb')
  
            totalRecv=0
            while totalRecv < filesize:
                data = client.recv(1024)
                totalRecv+=len(data)
                f.write(data)
                prg = totalRecv/float(filesize)*100
                print(prg)
                progress['value'] = prg

                ldownper.config(text = str(round(prg,2)) + "%")
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
ip_addr.place(relwidth=0.20, relheight=0.7, relx=0.15, rely=0.15)

lport = Label(frame, text="Port: ")
lport.place(relwidth=0.12, relheight=0.5, relx=0.37, rely=0.25)

port = Entry(frame)
port.place(relwidth=0.20, relheight=0.7, relx=0.51, rely=0.15)

bconn = Button(frame, text="Connect", bg='black', fg='white',
                    command=lambda: conn_button(ip_addr.get(), port.get()))
bconn.place(relwidth=0.12, relheight=0.7, relx=0.74, rely=0.15)
    
root.mainloop()

if __name__ == "__main__":
    chat()