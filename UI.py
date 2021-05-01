
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as fd
import cv2, math
from cv2 import putText, rectangle, VideoCapture
from datetime import datetime, date, time
import imutils
from imutils.video import fps
import numpy as np
from centroidtracker import CentroidTracker
import pymysql
from PIL import ImageTk
import time
import os
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import login
from itertools import combinations

elapsedTime = 0

protopath = "D:\RAJ\TE SEM6\ml\ML project\FP\myproject\MobileNetSSD_deploy.prototxt"
modelpath = "D:\RAJ\TE SEM6\ml\ML project\FP\myproject\MobileNetSSD_deploy.caffemodel"
detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)
# detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
# detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

tracker = CentroidTracker(maxDisappeared=50, maxDistance=60)


def non_max_suppression_fast(boxes, overlapThresh):
    try:
        if len(boxes) == 0:
            return []

        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        pick = []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)

        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            overlap = (w * h) / area[idxs[:last]]

            idxs = np.delete(idxs, np.concatenate(([last],
                                                   np.where(overlap > overlapThresh)[0])))
        return boxes[pick].astype("int")
    except Exception as e:
        print("Exception occurred in non_max_suppression : {}".format(e))


mydata = []
class Mainframe:
    def __init__(self, root):
        self.root = root
        self.root.title("Detection System")
        self.root.geometry("800x600+100+50")
        p1 = PhotoImage(file="images\icon.png")
        self.root.iconphoto(False, p1)
        self.root.config(bg="gray")

        self.mainF = Frame(self.root, bg="silver")
        self.mainF.place(x=20, y=50, height=480, width=760)

        # style details table :Treeview
        ttk.Style(self.mainF).theme_use("classic")
        ttk.Style(self.mainF).configure("Treeview", background="silver",
                                        fieldbackground="silver", rowheight=25, font=("", 12, ""))
        ttk.Style(self.mainF).configure(
            "Treeview.Heading", font=('Calibri', 13, 'bold'))
        ttk.Style(self.mainF).map(
            "Treeview", background=[("selected", "green")])
        # :Treeview
        self.x_scroll = ttk.Scrollbar(self.mainF, orient=HORIZONTAL)
        self.y_scroll = ttk.Scrollbar(self.mainF, orient=VERTICAL)
        self.details_table = ttk.Treeview(self.mainF, columns=(
            'Srno', 'date', 'day', 'time', 'total_person'), yscrollcommand=self.y_scroll.set, xscrollcommand=self.x_scroll.set)
        self.x_scroll.pack(side=BOTTOM, fill=X)
        self.x_scroll.config(command=self.details_table.xview)
        self.y_scroll.pack(side=RIGHT, fill=Y)
        self.y_scroll.config(command=self.details_table.yview)
        self.details_table.heading("Srno", text="Srno")
        self.details_table.heading("date", text="date")
        self.details_table.heading("day", text="day")
        self.details_table.heading("time", text="time")
        self.details_table.heading("total_person", text="total persons")
        self.details_table['show'] = 'headings'
        self.details_table.column('Srno', width=150)
        self.details_table.column('date', width=150)
        self.details_table.column('day', width=150)
        self.details_table.column('time', width=150)
        self.details_table.column('total_person', width=150)
        self.details_table.pack(fill=BOTH, expand=1)

        self.startButton = Button(
            self.root, text="START", bg="yellow", font=("", 9, "bold"), command=lambda: showStream(self))
        self.startButton.place(x=50, y=550)
        self.stopLabel = Label(
            self.root, text="press 'q' to stop", bg="#28282B", fg="white")
        self.stopLabel.place(x=100, y=550)
        self.showdetails = Button(
            self.root, bg="yellow", text="SHOW DATA", font=("", 9, "bold"), command=lambda: showEntry(self))
        self.showdetails.place(x=200, y=550)
        self.path = Entry(self.root, width=70)
        self.path.place(x=300, y=550)
        self.pathlabel = Label(
            self.root, text="**enter video path here !!!", bg="#28282B", fg="red")
        self.pathlabel.place(x=310, y=570)
        self.showGraph = Button(self.root, text="Graph", bg='yellow', font=(
            "", 9, "bold"), command=lambda: searchbydate(self))
        self.showGraph.place(x=170, y=20)
        self.yearLabel = Label(self.root, width=5, text="year", height=1)
        self.yearLabel.place(x=50, y=1)
        self.enteryear = Entry(self.root, width=5)
        self.enteryear.place(x=50, y=20)
        self.monthLabel = Label(self.root, width=5, text="month", height=1)
        self.monthLabel.place(x=90, y=1)
        self.entermonth = Entry(self.root, width=5)
        self.entermonth.place(x=90, y=20)
        self.dayLabel = Label(self.root, width=5, text="day", height=1)
        self.dayLabel.place(x=130, y=1)
        self.enterday = Entry(self.root, width=5)
        self.enterday.place(x=130, y=20)
        self.showDayGraph = Button(self.root, text="Graph", bg='yellow', font=(
            "", 9, "bold"), command=lambda: searchbyday(self))
        self.showDayGraph.place(x=450, y=20)
        self.weekdayLabel = Label(self.root, width=9, text="weekday", height=1)
        self.weekdayLabel.place(x=350, y=1)
        self.weekday = Entry(self.root, width=15)
        self.weekday.place(x=350, y=20)
        self.export = Button(self.root, bg="yellow", text="DOWNLOAD DATA", font=(
            "", 6, "bold"), command=lambda: downloadData(self))
        self.export.place(x=700, y=5)
        self.signout = Button(self.root, text="SIGN OUT", bg="yellow", font=("", 7, "bold"), command=lambda: signOut(self))
        self.signout.place(x=700, y=25)

        def signOut(self):
            self.root.destroy()
            root1 = Tk()
            obj1 = login.Login(root1)
            root1.mainloop()

        def downloadData(self):
            if len(mydata) < 1:
                messagebox.showinfo("error", "nodata to export")
                return False
            fln = fd.asksaveasfilename(initialdir=os.getcwd(), title="Save CSV", filetypes=(
                ("CSV File", "*.csv"), ("All Files", "*.*")))
            with open(fln, mode="w") as myfile:
                exp_writer = csv.writer(myfile, delimiter=',')
                for i in mydata:
                    exp_writer.writerow(i)

                messagebox.showinfo(
                    "Data Exported", "File has been created"+os.path.basename(fln))

        def searchbyday(self):
            # print(self.enteryear.get()+"-" +
            #       self.entermonth.get()+"-"+self.enterday.get())
            con = pymysql.connect(
                host="localhost", user="root", password="", database="countdetails")
            cur = con.cursor()
            cur.execute("select time from countperhour where day = %s", self.weekday.get())
            x = cur.fetchall()
            xlst = []
            ylst = []
            if x != False:
                for entries in x:
                    xlst.append(entries[0])
            cur.execute("select totalcount from countperhour where day = %s", self.weekday.get())
            y = cur.fetchall()
            if y != False:
                for entries in y:
                    ylst.append(entries[0])
            cur.execute("select date,day,time,totalcount from countperhour where day = %s", self.weekday.get())
            r_set = cur.fetchall()
            global mydata
            mydata = r_set
            i = 1
            if r_set != False:
                self.details_table.delete(*self.details_table.get_children())
                for entries in r_set:
                    lst = list(entries)
                    lst.insert(0, i)
                    self.details_table.insert('', END, values=lst)
                    con.commit()
                    i += 1
                con.close()
            plt.plot(xlst, ylst)
            ax = plt.axes()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
            plt.xlabel('TIME')
            plt.ylabel('VISITERS', labelpad=10)
            plt.xticks(rotation=90)
            plt.subplots_adjust(bottom=0.2)
            plt.title('Graph of '+self.weekday.get())
            filename = str(self.weekday.get())+".png"
            print(filename)
            plt.savefig('plt saved/'+filename)
            plt.show()
    
        def searchbydate(self):
            print(self.enteryear.get()+"-" +
                  self.entermonth.get()+"-"+self.enterday.get())
            con = pymysql.connect(
                host="localhost", user="root", password="", database="countdetails")
            cur = con.cursor()
            cur.execute("select time from countperhour where date = %s", self.enteryear.get(
            )+"-"+self.entermonth.get()+"-"+self.enterday.get())
            x = cur.fetchall()
            cur.execute("select date,day,time,totalcount from countperhour where date = %s",self.enteryear.get(
            )+"-"+self.entermonth.get()+"-"+self.enterday.get())
            r_set = cur.fetchall()
            global mydata
            mydata = r_set
            i = 1
            if r_set != False:
                self.details_table.delete(*self.details_table.get_children())
                for entries in r_set:
                    lst = list(entries)
                    lst.insert(0, i)
                    self.details_table.insert('', END, values=lst)
                    con.commit()
                    i += 1
                con.close()
            xlst = []
            ylst = []

            if x != False:
                for entries in x:
                    xlst.append(entries[0])
            con = pymysql.connect(
                host="localhost", user="root", password="", database="countdetails")
            cur = con.cursor()
            cur.execute("select totalcount from countperhour where date = %s",
                        self.enteryear.get()+"-"+self.entermonth.get()+"-"+self.enterday.get())
            y = cur.fetchall()

            if Y != False:
                for entries in y:
                    ylst.append(entries[0])

            plt.plot(xlst, ylst)
            ax = plt.axes()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

            plt.xlabel('TIME')
            plt.ylabel('VISITERS', labelpad=10)

            plt.xticks(rotation=90)
            plt.subplots_adjust(bottom=0.2)

            plt.title('Graph of '+self.enteryear.get()+"-" +
                      self.entermonth.get()+"-"+self.enterday.get())
            filename = str(self.enteryear.get(
            ))+"-"+str(self.entermonth.get())+"-"+str(self.enterday.get())+".png"
            print(filename)
            plt.savefig('plt saved/'+filename)
            plt.show()

        def showEntry(self):
            con = pymysql.connect(
                host="localhost", user="root", password="", database="countdetails")
            cur = con.cursor()
            cur.execute("select date,day,time,totalcount from countperhour")
            r_set = cur.fetchall()
            global mydata
            mydata = r_set
            i = 1
            if r_set != False:
                self.details_table.delete(*self.details_table.get_children())
                for entries in r_set:
                    lst = list(entries)
                    lst.insert(0, i)
                    self.details_table.insert('', END, values=lst)
                    con.commit()
                    i += 1
                con.close()

        def showStream(self):
            print("start")

            if self.path.get() == "":
                cap = cv2.VideoCapture(0)

            else:
                cap = cv2.VideoCapture(self.path.get())

            if (self.startButton['state'] == NORMAL):
                self.startButton['state'] = DISABLED
            else:
                self.startButton['state'] = NORMAL

            time1 = datetime.now()
            fps_start_time = datetime.now()
            total_frames = 0
            object_id_list = []
            dtime = dict()
            dwell_time = dict()
            startTime = datetime.now()

            while True:
                time2 = datetime.now()  # waited a few minutes before pressing enter
                global elapsedTime
                elapsedTime = time2 - time1

                ret, frame = cap.read(cv2.IMREAD_REDUCED_COLOR_8)

                if ret == False:
                    self.startButton['state'] = NORMAL
                    print("No Frames to Record or wrong path")

                    break
                frame = imutils.resize(frame, width=800)

                total_frames = total_frames + 1

                (H, W) = frame.shape[:2]

                blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)

                detector.setInput(blob)
                person_detections = detector.forward()
                rects = []

                for i in np.arange(0, person_detections.shape[2]):
                    confidence = person_detections[0, 0, i, 2]
                    if confidence > 0.5:
                        idx = int(person_detections[0, 0, i, 1])

                        if CLASSES[idx] != "person":
                            continue

                        person_box = person_detections[0, 0,
                                                       i, 3:7] * np.array([W, H, W, H])
                        (startX, startY, endX, endY) = person_box.astype("int")
                        rects.append(person_box)

                boundingboxes = np.array(rects)
                boundingboxes = boundingboxes.astype(int)
                rects = non_max_suppression_fast(boundingboxes, 0.3)
                centroid_dict = dict()
                objects = tracker.update(rects)
                for (objectId, bbox) in objects.items():
                    x1, y1, x2, y2 = bbox
                    x1 = int(x1)
                    y1 = int(y1)
                    x2 = int(x2)
                    y2 = int(y2)
                    cX = int((x1 + x2) / 2.0)
                    cY = int((y1 + y2) / 2.0)


                    centroid_dict[objectId] = (cX, cY, x1, y1, x2, y2)
                    red_zone_list = []
                    for (id1, p1), (id2, p2) in combinations(centroid_dict.items(), 2):
                        dx, dy = p1[0] - p2[0], p1[1] - p2[1]
                        distance = math.sqrt(dx * dx + dy * dy)
                        if distance < 75.0:
                            if id1 not in red_zone_list:
                                red_zone_list.append(id1)
                            if id2 not in red_zone_list:
                                red_zone_list.append(id2)

                    if objectId not in object_id_list:
                        object_id_list.append(objectId)
                        dtime[objectId] = datetime.now()
                        dwell_time[objectId] = 0
                    else:
                        curr_time = datetime.now()
                        old_time = dtime[objectId]
                        time_diff = curr_time - old_time
                        dtime[objectId] = datetime.now()
                        sec = time_diff.total_seconds()
                        dwell_time[objectId] += sec

                    for id, box in centroid_dict.items():
                        if id in red_zone_list:
                            cv2.rectangle(frame, (box[2], box[3]), (box[4], box[5]), (0, 0, 255), 2)
                            text = "{}|{}".format(objectId, int(dwell_time[objectId]))
                            cv2.putText(frame, text, (x1, y1-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                        else:
                            cv2.rectangle(frame, (box[2], box[3]), (box[4], box[5]), (0, 255, 0), 2)
                            text = "{}|{}".format(objectId, int(dwell_time[objectId]))
                            cv2.putText(frame, text, (x1, y1-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

                    if objectId not in object_id_list:
                        object_id_list.append(objectId)

                fps_end_time = datetime.now()
                time_diff = fps_end_time - fps_start_time
                if time_diff.seconds == 0:
                    fps = 0.0
                else:
                    fps = (total_frames / time_diff.seconds)

                fps_text = "FPS: {:.2f}".format(fps)

                cv2.putText(frame, fps_text, (5, 30),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

                lpc_count = len(objects)
                opc_count = len(object_id_list)

                lpc_txt = "LPC: {}".format(lpc_count)
                opc_txt = "OPC: {}".format(opc_count)
                diff = datetime.now() - startTime
                print("diff", diff.total_seconds())
                print("count", opc_count)
                if diff.seconds > 0.0000000 and opc_count != 0 and diff.seconds % 20 == 0.0000000:
                    time.sleep(1)
                    date1 = date.today()

                    day1 = datetime.today().strftime("%A")
                    hour1 = datetime.now().strftime("%H:%M:%S")

                    con = pymysql.connect(
                        host="localhost", user="root", password="", database="countdetails")
                    cur = con.cursor()
                    sql = "INSERT INTO `countperhour` (`date`, `day`, `time`, `totalcount`) VALUES (%s, %s, %s, %s)"
                    cur.execute(sql, (str(date1), str(day1),
                                str(hour1), str(opc_count)))
                    con.commit()
                    showEntry(self)
                    con.close()

                cv2.putText(frame, lpc_txt, (5, 60),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                cv2.putText(frame, opc_txt, (5, 90),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                cv2.putText(frame, str(time2), (5, 120),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                cv2.imshow("Application", frame)

                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    self.startButton['state'] = NORMAL
                    objects.clear()
                    cap.release()
                    cv2.destroyAllWindows()
                    break
            cap.release()
            cv2.destroyAllWindows()
            print(elapsedTime.total_seconds())


if __name__ == "__main__":
    root = Tk()
    obj = Mainframe(root)
    root.mainloop()
