from tkinter import *
from tkinter import messagebox
from PIL import ImageTk
import re
import pymysql
import login
from validate_email import validate_email


class Register:
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
        self.top = ImageTk.PhotoImage(file="images/user_registration.png")
        top = Label(root, image=self.top)
        top.place(x=90, y=20, width=500, height=50)
        self.root.config(bg="#7AD7F0")

        # first row
        f_name = Label(root, text="First Name", font=(
            "times new roman", 15), fg="orange", bg="gray")
        f_name.place(x=100, y=100)
        self.fname_enry = Entry(root, bg="lightgray", text="hi", font=(
            "times new roman", 12, "bold"))
        self.fname_enry.place(x=250, y=100, height=30, width=200)
        print(self.fname_enry.get())
        # second row
        l_name = Label(root, text="Last name", font=(
            "times new roman", 15), fg="orange", bg="gray")
        l_name.place(x=100, y=150)
        self.lname_enry = Entry(root, bg="lightgray",
                                font=("times new roman", 12, "bold"))
        self.lname_enry.place(x=250, y=150, height=30, width=200)
        # third row
        phone = Label(root, text="Contact", font=(
            "times new roman", 15), fg="orange", bg="gray")
        phone.place(x=100, y=200)
        self.phone_enry = Entry(root, bg="lightgray",
                                font=("times new roman", 12, "bold"))
        self.phone_enry.place(x=250, y=200, height=30, width=200)
        # fourth row
        email = Label(root, text="E-mail",
                      font=("times new roman", 15), fg="orange", bg="gray")
        email.place(x=100, y=250)
        self.email_enry = Entry(root, bg="lightgray",
                                font=("times new roman", 12, "bold"))
        self.email_enry.place(x=250, y=250, height=30, width=200)
        # fifth row
        username = Label(root, text="Create Username", font=(
            "times new roman", 15), fg="orange", bg="gray")
        username.place(x=100, y=300)
        self.username_enry = Entry(
            root, bg="lightgray", font=("times new roman", 12, "bold"))
        self.username_enry.place(x=250, y=300, height=30, width=200)
        # sixth row
        password = Label(root, text="Create Password", font=(
            "times new roman", 15), fg="orange", bg="gray")
        password.place(x=100, y=350)
        self.password_enry = Entry(
            root, bg="lightgray", font=("times new roman", 12, "bold"))
        self.password_enry.place(x=250, y=350, height=30, width=200)
        # seventh row
        passcode = Label(root, text="Passcode", font=(
            "times new roman", 15, "bold"), fg="orange", bg="gray")
        passcode.place(x=100, y=400)
        self.passcode_enry = Entry(
            root, bg="lightgray", font=("times new roman", 12, "bold"))
        self.passcode_enry.place(x=250, y=400, height=30, width=200)
        # eighth row
        self.Submit = Button(root, text="SUBMIT", font=(
            "times new roman", 15, "bold"), bg="green", fg="orange", command=self.register_data)
        self.Submit.place(x=200, y=440)

        signinlab = Label(root, text="Already Register?", font=(
            "", 8, "underline"), fg="white", bg="blue")
        signinlab.place(x=400, y=455)
        self.signin = Button(root, text="SIGN IN", font=("times new roman", 10, "bold"), bg="Light Blue",
                             fg="Green", command=self.gotologin)
        self.signin.place(x=500, y=450)

    def register_data(self):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        fname = self.fname_enry.get()
        lname = self.lname_enry.get()
        contact = self.phone_enry.get()
        email = self.email_enry.get()
        username = self.username_enry.get()
        password = self.password_enry.get()
        passcode = self.passcode_enry.get()
        print(fname+" "+lname)
        print(re.search(regex, email))
        is_valid = validate_email(email)
        if fname == "" or lname == "" or contact == "" or email == "" or username == "" or password == "" or passcode == "":
            messagebox.showerror("Error", "Fields cannot be empty")
        elif fname.isalpha() == False or lname.isalpha() == False:
            messagebox.showerror("Error", "Invalid first name or last name ")
            self.fname_enry.delete(0, END)
            self.lname_enry.delete(0, END)
        elif contact.isalnum == True or len(contact) != 10:
            messagebox.showerror("Error", "Invalid Phone Number")
        elif is_valid == False:
            messagebox.showerror("ERROR", "INVALID EMAIL")
        else:
            con = pymysql.connect(
                host="localhost", user="root", password="", database="countdetails")
            cur = con.cursor()
            cur.execute("select * from registration where email=%s", email)
            row_email = cur.fetchone()
            cur.execute("select * from registration where phone=%s", contact)
            row_contact = cur.fetchone()
            cur.execute(
                "select * from registration where username=%s", username)
            row_username = cur.fetchone()
            cur.execute(
                "select * from adminpasscodes where passcode=%s", passcode)
            row_passcode = cur.fetchone()

            if row_contact != None:
                messagebox.showerror(
                    "Error", " phone no already exists try another one")
                self.phone_enry.delete(0, END)
                con.commit()
                con.close()
            elif row_email != None:
                messagebox.showerror(
                    "Error", " e-mail already exists try another one")
                self.email_enry.delete(0, END)
                con.commit()
                con.close()
            elif row_username != None:
                messagebox.showerror(
                    "Error", " username already exists try another one")
                self.username_enry.delete(0, END)
                con.commit()
                con.close()
            elif row_passcode == None:
                messagebox.showerror(
                    "Wrong Passcode", " please entter correct passcode provided by administrator")
                self.passcode_enry.delete(0, END)
                con.commit()
                con.close()

            else:
                cur.execute("insert into registration (fname,lname,phone,email,username,password,passcode) values(%s, %s, %s, %s, %s, %s, %s)",
                            (str(self.fname_enry.get()),
                             str(self.lname_enry.get()),
                                str(self.phone_enry.get()),
                                str(self.email_enry.get()),
                                str(self.username_enry.get()),
                                str(self.password_enry.get()),
                                str(self.passcode_enry.get())
                             ))
                con.commit()
                con.close()
                messagebox.showinfo("Success", "Registered", parent=self.root)
                self.fname_enry.delete(0, END)
                self.lname_enry.delete(0, END)
                self.phone_enry.delete(0, END)
                self.email_enry.delete(0, END)
                self.username_enry.delete(0, END)
                self.password_enry.delete(0, END)
                self.passcode_enry.delete(0, END)
                self.gotologin()

    def gotologin(self):
        self.root.destroy()
        root1 = Tk()
        obj1 = login.Login(root1)
        root1.mainloop()


if __name__ == "__main__":
    root = Tk()
    obj = Register(root)
    root.mainloop()
