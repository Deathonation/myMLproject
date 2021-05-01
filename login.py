from tkinter import *
from PIL import ImageTk
import pymysql
from tkinter import messagebox
import project
from datetime import datetime
import UI


class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Registration window")
        self.root.geometry("640x480+0+0")
        # root background
        self.bg = ImageTk.PhotoImage(
            file="images/frank-busch-ChDWtI3N9w4-unsplash.jpg")
        self.root.config(bg="#7AD7F0")
        bg = Label(root, image=self.bg)
        bg.place(x=0, y=0, relwidth=1, relheight=1)

        # user registration image
        self.top = ImageTk.PhotoImage(file="images/user_login.jpg")
        top = Label(root, image=self.top)
        top.place(x=80, y=20, width=500, height=50)
        self.root.config(bg="#7AD7F0")

        # first row
        username = Label(root, text="Username", font=(
            "times new roman", 15), fg="orange", bg="gray")
        username.place(x=100, y=200)
        self.username_enry = Entry(
            root, bg="lightgray", font=("times new roman", 12, "bold"))
        self.username_enry.place(x=250, y=200, height=30, width=200)
        # second row
        password = Label(root, text="Password", font=(
            "times new roman", 15), fg="orange", bg="gray")
        password.place(x=100, y=250)
        self.password_enry = Entry(
            root, bg="lightgray", show="*", font=("times new roman", 12, "bold"))
        self.password_enry.place(x=250, y=250, height=30, width=200)
        
        passcode = Label(root, text="Passcode", font=(
            "times new roman", 15, "bold"), fg="orange", bg="gray")
        passcode.place(x=100, y=300)
        self.passcode_enry = Entry(
            root, bg="lightgray", show="*", font=("times new roman", 12, "bold"))
        self.passcode_enry.place(x=250, y=300, height=30, width=200)
        
        self.login = Button(root, text="LOGIN", font=(
            "times new roman", 12, "bold"), bg="green", fg="orange", command=self.confirm_login)
        self.login.place(x=250, y=360)

        self.backreg = Button(root, text= "Go to Registration", font=(
            "times new roman", 10, "bold"), bg="blue", fg="orange", command=self.gotoreg)
        self.backreg.place(x=225, y=400)

    def confirm_login(self):
        username = self.username_enry.get()
        password = self.password_enry.get()
        passcode = self.passcode_enry.get()
        con = pymysql.connect(host="localhost", user="root",
                              password="", database="countdetails")
        cur = con.cursor()
        cur.execute("select * from registration where username=%s", username)
        row_username = cur.fetchone()
        cur.execute("select * from registration where passcode=%s", passcode)
        row_passcode = cur.fetchone()

        if row_username == None:
            messagebox.showerror("Error", "wrong username")
        elif row_passcode == None:
            messagebox.showerror("Error", "wrong passcode")
        else:
            cur.execute("insert into login (username,date_time) values(%s, %s)",
            (str(self.username_enry.get()),
            str(datetime.now())
            ))
            con.commit()
            con.close()
            self.root.destroy()
            root = Tk()
            obj = UI.Mainframe(root)
            root.mainloop()

    def gotoreg(self):
        self.root.destroy()
        root1 = Tk()
        obj = project.Register(root1)
        root1.mainloop()

if __name__== "__main__":
    root1 = Tk()
    obj = Login(root1)
    root1.mainloop()


