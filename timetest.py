import datetime
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

            
            plt.plot(xlst, ylst)
            ax = plt.axes()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

            plt.xlabel('TIME')
            plt.ylabel('VISITERS', labelpad=10)

            plt.xticks(rotation=90)
            plt.subplots_adjust(bottom=0.2)

            plt.title('Graph of '+self.weekday.get())
            filename = str(self.weekday.get()))+".png"
            print(filename)
            plt.savefig('plt saved/'+filename)
            plt.show()