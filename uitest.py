
from tkinter import *
from tkinter import ttk
import cv2
from datetime import datetime, date, time
import imutils
import numpy as np
from centroidtracker import CentroidTracker
import pymysql
from PIL import ImageTk
import time
import os


elapsedTime = 0

protopath = "MobileNetSSD_deploy.prototxt"
modelpath = "MobileNetSSD_deploy.caffemodel"
detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)
# detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

tracker = CentroidTracker(maxDisappeared=80, maxDistance=90)


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


class Mainframe:
    def __init__(self, root):
        self.root = root
        self.root.title("Detection System")
        self.root.geometry("800x600+100+50")
        self.root.config(bg="#28282B")

        self.mainF = Frame(self.root)
        self.mainF.place(x=20, y=50, height=480, width=760)

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
            self.root, text="START", bg="yellow", command=lambda: showStream(self))
        self.startButton.place(x=50, y=550)
        self.stopLabel = Label(
            self.root, text="press 'q' to stop", bg="#28282B", fg="white")
        self.stopLabel.place(x=100, y=550)
        self.showdetails = Button(
            self.root, bg="yellow", text="SHOW ENTRIES", command=lambda: showEntry(self))
        self.showdetails.place(x=200, y=550)

        # Threads

        def showEntry(self):
            con = pymysql.connect(
                host="localhost", user="root", password="", database="countdetails")
            cur = con.cursor()
            cur.execute("select date,day,time,totalcount from countperhour")
            r_set = cur.fetchall()
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

            if (self.startButton['state'] == NORMAL):
                self.startButton['state'] = DISABLED

            else:
                self.startButton['state'] = NORMAL
            time1 = datetime.now()

            # cap = cv2.VideoCapture(
            #     'D:\\RAJ\\TE SEM6\\ml\\ML project\\FP\\videoplayback.mp4')
            cap = cv2.VideoCapture(
                'D:\\RAJ\\TE SEM6\\ml\\ML project\\FP\\myproject\\testvideo2.mp4')
            # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            # try:
            #     if not os.path.exists('captured'):
            #         os.makedirs('captured')
            # except OSError:
            #     print('wait, Creating Directory')

            fps_start_time = datetime.now()
            total_frames = 0
            object_id_list = []
            startTime = datetime.now()
            while True:

                time2 = datetime.now()  # waited a few minutes before pressing enter
                # print(time2)
                global elapsedTime
                elapsedTime = time2 - time1

                ret, frame = cap.read()
                assert not isinstance(frame, type(None)), 'video ended'
                # print(type(frame))
                frame = imutils.resize(frame, width=600)
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

                objects = tracker.update(rects)
                for (objectId, bbox) in objects.items():
                    x1, y1, x2, y2 = bbox
                    x1 = int(x1)
                    y1 = int(y1)
                    x2 = int(x2)
                    y2 = int(y2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    text = "ID: {}".format(objectId)
                    cv2.putText(frame, text, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

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
                # print(type(diff))
                print("diff", diff.total_seconds())
                print("count", opc_count)
                if diff.seconds > 0.0000000 and opc_count != 0 and diff.seconds % 5 == 0.0000000:
                    time.sleep(1)
                    date1 = date.today()

                    day1 = datetime.today().strftime("%A")
                    hour1 = datetime.now().strftime("%H:%M:%S")
                    # print(date1, day1, hour1)
                    # print("hour1", hour1)
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
                    break
            cap.release()
            cv2.destroyAllWindows()
            print(elapsedTime.total_seconds())


if __name__ == "__main__":
    root = Tk()
    obj = Mainframe(root)
    root.mainloop()
