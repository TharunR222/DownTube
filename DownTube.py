from PyQt5.QtWidgets import QComboBox, QApplication, QLineEdit, QLabel, QMessageBox, QPushButton, QListView, QWidget, QFileDialog
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QImage, QPixmap, QIcon
from pytube import YouTube, exceptions
import sys, requests, random, subprocess,os
from pathlib import Path
import requests.packages
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import resources_rc1, resources_rc2


#Main Window
class Widget1(QWidget):
    def __init__(self):
        super(Widget1, self).__init__()  
        
        #Load the UI file
        uic.loadUi("DownTubeWid1.ui", self)

        #Define Our Widgets that are going to be altered
        self.URL_Entry1 = self.findChild(QLineEdit, "lineEdit")
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle("Error")

        #Altering URL_Entry1 Box
        self.URL_Entry1.setPlaceholderText("Paste a URL")

        #Getting Input and Validating Input(URL) using functon:url_check()
        self.URL_Entry1.returnPressed.connect(self.url_check)
    #Function Usage: url_check() to validate input_text 
    def url_check(self):
        try:
            self.text = self.URL_Entry1.text().strip()
            self.yt = YouTube(self.text)
        except exceptions.RegexMatchError:
            self.msg.setText("Please Enter a Valid URL")
            self.msg.exec_()
            self.URL_Entry1.clear()
        else:
            self.go_on_common()

    #Function Usage: go_on_common() to setup the next page common elements
    def go_on_common(self):
        try:
            self.title1 = self.yt.title
            self.artist1 = self.yt.author
        except exceptions.VideoUnavailable:
            self.msg.setText("Sorry! This video is currently not available or It might not be a Youtube Video")
            self.msg.setWindowTitle("Error")
            self.msg.exec_()
            self.URL_Entry1.clear()
        else:                                                                                                        
            #Shifts to the Next Page
            widget.setCurrentIndex(widget.currentIndex() + 1)  
            W2.send_values(self.text)

#Second Window
class Widget2(QWidget):
    def __init__(self):
        super(Widget2, self).__init__()

        #Load the UI file
        uic.loadUi("DownTubeWid2.ui", self)
    
        #Define Our Widgets that are going to be altered 
        self.just_show_url = self.findChild(QLabel, "url_label")
        self.thumbnail = self.findChild(QLabel, "thumbnail_label")
        self.back_button = self.findChild(QPushButton, "backbutton")
        self.msg_down = QMessageBox()
        self.image = QImage() 

        #Tab for MP3
        self.title_text1 = self.findChild(QLabel, "title_hold_label1")
        self.size_text1 = self.findChild(QLabel, "size_hold_label1")
        self.artist_text1 = self.findChild(QLabel, "artist_hold_label1")
        self.mp3_shift_button = self.findChild(QPushButton, "download_mp3_button")
        self.mp3_combo = self.findChild(QComboBox, "quality_combo_box1")
        self.mp3_combo.wheelEvent = lambda event1: None

        #Tab for MP4
        self.title_text2 = self.findChild(QLabel, "title_hold_label2")
        self.size_text2 = self.findChild(QLabel, "size_hold_label2")
        self.artist_text2 = self.findChild(QLabel, "artist_hold_label2")
        self.mp4_shift_button = self.findChild(QPushButton, "mp4_button")
        self.mp4_combo = self.findChild(QComboBox, "quality_combo_box2")  
        self.mp4_combo.wheelEvent = lambda event2: None

        
        #Calling the function to go to previous page
        self.back_button.clicked.connect(self.backpage)

        self.mp4_combo.activated.connect(self.set_goingsize)
        self.mp3_combo.activated.connect(self.set_goingsize_mp3)
        self.mp4_shift_button.clicked.connect(self.goingdownload)
        self.mp3_shift_button.clicked.connect(self.goingdownloadmp3)

    def event1(self):
        pass

    def event2(self):
        pass

    def send_values(self, val):
        self.rec_val = val

        self.strm_resolution = []
        self.yt1 = YouTube(self.rec_val)

        for self.strm in self.yt1.streams.order_by('resolution'):
                self.strm_resolution.append(self.strm.resolution)
       
        self.res_result = []
        [self.res_result.append(x) for x in self.strm_resolution if x not in self.res_result]

        #Setting up mp4 combo box for the entered url of mp4
        self.mp4_combo.setView(QListView())
        for i in range(len(self.res_result), 10):
            self.mp4_combo.view().setRowHidden(i,True)

        #Setting initialy the mp4 combo box to first index(first value)
        self.mp4_combo.setCurrentIndex(0)
        self.mp3_combo.setCurrentIndex(0)

        self.title_text1.setText(self.yt1.title)   
        self.title_text2.setText(self.yt1.title)
        self.artist_text1.setText(self.yt1.author)
        self.artist_text2.setText(self.yt1.author)
        self.thumbnail1 = self.yt1.thumbnail_url
        self.image.loadFromData(requests.get(self.thumbnail1, verify = False).content)                                                                    
        self.thumbnail.setPixmap(QPixmap(self.image))
        self.just_show_url.setText(self.rec_val)

        self.set_size = self.yt1.streams.filter(res = self.mp4_combo.currentText()).first().filesize
        self.set_length = self.yt1.length
        self.size_text2.setText(str(self.set_size/10**6) + "MB")

        self.size_text1.setText(str(int(self.mp3_combo.currentText().partition('k')[0]) * (self.set_length/60) * 0.0075) + "MB")


    def set_goingsize(self):
        self.set_size = self.yt1.streams.filter(res = self.mp4_combo.currentText()).first().filesize
        self.size_text2.setText(str(self.set_size/10**6) + "MB")

    def set_goingsize_mp3(self):
        self.size_text1.setText(str(int(self.mp3_combo.currentText().partition('k')[0]) * (self.set_length/60) * 0.0075) + "MB")

    def goingdownloadmp3(self):
        self.msg_down.show()
        self.msg_down.setWindowTitle("Downloading...")
        self.msg_down.setText("Your Audio is Being Downloaded...")
        self.filenamemp3formp3 = "".join(x for x in self.yt1.title if x.isalnum()) + str(random.randrange(1,2000)) + ".mp3"
        self.finalfilenamemp3 = "".join(x for x in self.yt1.title if x.isalnum()) + str(random.randrange(1,2000)) + ".mp3"
        self.audio = self.yt1.streams.filter(only_audio = True).first()
        self.file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.audio.download(self.file+"/", filename = self.filenamemp3formp3)

        self.all_dir = os.getcwd()
        os.chdir("./ffmpeg/bin/")
        #Added -loglevel quiet
        subprocess.run("ffmpeg -loglevel quiet -i "+self.file+"/"+ self.filenamemp3formp3 + " -ab " + self.mp3_combo.currentText().partition('b')[0].replace(" ", "") + " "+self.file+"/"+ self.finalfilenamemp3)

        Path(self.file+"/" + self.filenamemp3formp3).unlink()

        self.msg_down.setWindowTitle("Download Successful")
        self.msg_down.setText("Your Audio has Been Downloaded Successfully")
        os.chdir(self.all_dir)
        self.msg_down.exec_()

        

    def goingdownload(self):
        self.msg_down.show()
        self.msg_down.setWindowTitle("Downloading...")
        self.msg_down.setText("Your Video is Being Downloaded...")
        self.filenamemp4 = "".join(x for x in self.yt1.title if x.isalnum()) + str(random.randrange(1,2000)) + ".mp4"
        self.filenamemp3 = "".join(x for x in self.yt1.title if x.isalnum()) + str(random.randrange(1,2000)) + ".mp3"
        self.finalfilename = "".join(x for x in self.yt1.title if x.isalnum()) + str(random.randrange(1,2000)) + ".mp4"
        self.audio = self.yt1.streams.filter(only_audio = True).first()
        self.video = self.yt1.streams.filter(only_video = True, res = self.mp4_combo.currentText()).first()
        self.file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.video.download(self.file+"/", filename = self.filenamemp4)
        self.audio.download(self.file+"/", filename = self.filenamemp3)
        self.combine_aud_vid(self.file)

    def combine_aud_vid(self, file):
        self.file = file
        self.all_dir = os.getcwd()
        os.chdir("./ffmpeg/bin/")
        #Added -loglevel quiet
        subprocess.run("ffmpeg -loglevel quiet -i "+self.file+"/"+ self.filenamemp4 + " -i "+self.file+"/"+ self.filenamemp3 + " -c copy "+self.file+"/" + self.finalfilename)

        Path(self.file+"/" + self.filenamemp4).unlink()
        Path(self.file+"/" + self.filenamemp3).unlink()


        self.msg_down.setWindowTitle("Download Successful")
        self.msg_down.setText("Your Video has Been Downloaded Successfully")
        os.chdir(self.all_dir)
        self.msg_down.exec_()
    
    #Shifting to the Previous Window
    def backpage(self):
        W1.URL_Entry1.setText("")   
        self.thumbnail.clear()
        self.title_text1.setText("")
        self.title_text2.setText("")
        self.size_text1.setText("")
        self.size_text2.setText("")
        self.artist_text1.setText("")
        self.artist_text2.setText("")
        widget.setCurrentIndex(widget.currentIndex() - 1)   

if __name__ == "__main__":
    #Initialize the App
    app = QApplication(sys.argv)

    #Creating and stacking widgets
    widget = QtWidgets.QStackedWidget()
    W1 = Widget1()
    W2 = Widget2()
    widget.addWidget(W1)
    widget.addWidget(W2)

    #Show the App
    widget.showMaximized()
    widget.setWindowTitle("DownTube")
    widget.setWindowIcon(QIcon(".\Final_File\logo_alone.png"))
    widget.show()

    #Exit the App
    app.exec_()