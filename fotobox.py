import sys
import os
import subprocess
import cups
import pprint

from config import fotoboxText, fotoboxCfg

from datetime import datetime, date, time
from time import sleep

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTime, QTimer, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

from PIL import Image, ImageDraw

if not fotoboxCfg['nopi']:
  try:
    from picamera2 import Picamera2, Preview
  except ImportError:
    print("PiCamera not found - operating in simulation mode")
    fotoboxCfg['nopi']            = True
  
  try:
    import RPi.GPIO as GPIO
  except ImportError:
    print("RPi GPIO not found - operating in simulation mode")
    fotoboxCfg['nopi']            = True

from shutil import copyfile, move
from stat import S_ISREG, ST_MTIME, ST_MODE

class Ui_Form_mod(object):
  def setupUi(self, Form):
    Form.setObjectName("Form")
    Form.setWindowTitle("Fotobox")
    Form.resize(fotoboxCfg['window-width'], fotoboxCfg['window-height'])
    Form.setMinimumSize(QtCore.QSize(fotoboxCfg['window-width'], fotoboxCfg['window-height']))
    Form.setMaximumSize(QtCore.QSize(fotoboxCfg['window-width'], fotoboxCfg['window-height']))
    Form.setHtml("Initializing...")
    self.countdownTime = fotoboxCfg['countdown']
    self.entries = None
    self.tplFooterOrg = "Fotobox 0.4 · © Tobias Weber, Maria Weber, Florian Knodt"
    self.tplImage = "init.png"
    self.tplFooter = self.tplFooterOrg
    self.tplInstruct = "Instruction placeholder"
    self.tplBtn1 = "Button 1"
    self.tplBtn2 = "Button 2"
    self.tplBtn3 = "Button 3"
    self.tplInstructPreview = ""
    self.picturesTaken = 0
    self.composed = {}
    self.composed["first"] = ""
    self.composed["second"] = ""
    self.composed["third"] = ""
    self.composed["forth"] = ""
    self.composed["composed"] = '../'+fotoboxCfg["template"]
    self.timerCountdown = ""
    with open('design/template.html', 'r') as myfile:
      self.template=myfile.read().replace('\n', '')

    with open('design/templateBlack.html', 'r') as myfile2:
      self.templateBlack=myfile2.read().replace('\n', '')

    if fotoboxCfg['nopi']:
      self.tplFooterOrg = "Demo simulation mode"

  def initSystem(self, Form):
    #Camera
    if not fotoboxCfg['nopi']:
      self.cam2 = Picamera2()
      # self.camera.hflip = fotoboxCfg['cam-c-hflip']
      if(fotoboxCfg['cam-p-hflip'] == fotoboxCfg['cam-c-hflip']):
        fotoboxCfg['cam-p-hflip'] = False
    self.isLive = False
    
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)

    GPIO.output(19, GPIO.HIGH)
    GPIO.output(21, GPIO.HIGH)
    GPIO.output(16, GPIO.HIGH)

    #Countdown Updater
    self.timerCnt = QTimer(Form)
    self.timerCnt.timeout.connect(self.updateCountdown)
    self.timerCnt.setSingleShot(True)

    #Blank dummy image
    self.blankImage = QPixmap(1,1)

    self.lastPhoto = ""
    self.screen = ""
    self.temp = fotoboxCfg['temp']
    self.save = fotoboxCfg['save']

    if not self.temp.endswith('/'):
      self.temp += '/'
    if not self.save.endswith('/'):
      self.save += '/'

    if not os.path.exists(self.temp):
      try:
        os.makedirs(self.temp)
      except:
        print("Could not set up temp path")
        self.tplFooterOrg = "Could not set up temp path"
    if not os.path.exists(self.save):
      try:
        os.makedirs(self.save)
      except:
        print("Could not set up save path")
        self.tplFooterOrg = "Could not set up save path"

  def updateHtml(self, Form):
    data = self.template
    data = data.replace('${btn1}', self.tplBtn1, 1)
    data = data.replace('${btn2}', self.tplBtn2, 1)
    data = data.replace('${btn3}', self.tplBtn3, 1)
    data = data.replace('${info}', self.tplInstruct, 1)
    data = data.replace('${infoPreview}', self.tplInstructPreview, 1)
    data = data.replace('${status}', self.tplFooter, 1)
    data = data.replace('${image}', self.tplImage, 1)
    data = data.replace('${compose}', self.composed["composed"], 1)
    data = data.replace('${timer}', self.timerCountdown, 1)
    Form.setHtml(data, QUrl('file://'+os.path.dirname(os.path.realpath(__file__))+'/design/.'))

  def updateHtmlBlack(self, Form):
    data = self.templateBlack
    Form.setHtml(data, QUrl('file://'+os.path.dirname(os.path.realpath(__file__))+'/design/.'))

  def screenMain(self, Form):
    self.screen = 1

    self.tplInstruct = fotoboxText['info-home']
    self.tplBtn1 = fotoboxText['btn-capture']
    self.tplBtn2 = fotoboxText['btn-view']
    self.tplBtn3 = fotoboxText['btn-empty']

    GPIO.output(21, GPIO.HIGH) # grün
    GPIO.output(16, GPIO.LOW) # gelb
    GPIO.output(19, GPIO.LOW) # blau

    if not self.isLive:
      self.tplImage = "liveBack.png"
      if not fotoboxCfg['nopi']:
        #self.camera.resolution = (1640, 1232)
        #self.camera.preview_fullscreen=False
        #self.camera.preview_window=(fotoboxCfg['cam-p-x'], fotoboxCfg['cam-p-y'], fotoboxCfg['cam-p-width'], fotoboxCfg['cam-p-height'])
        #self.camera.start_preview(resolution=(1640, 1232), window = (fotoboxCfg['cam-p-x'], fotoboxCfg['cam-p-y'], fotoboxCfg['cam-p-width'], fotoboxCfg['cam-p-height']), hflip=fotoboxCfg['cam-p-hflip'])
      
        print("Enabling camera preview")
      self.isLive = True

    self.tplFooter = self.tplFooterOrg

    self.tplInstructPreview = self.tplInstruct

    self.updateHtml(Form)
    self.cam2.start_preview(Preview.DRM, x=100, y=200, width=800, height=600)

  def screenPrint(self, Form):
    self.screen = 5

    self.tplInstruct = fotoboxText['info-home']
    self.tplBtn1 = fotoboxText['btn-print']
    self.tplBtn2 = fotoboxText['btn-cancel']
    self.tplBtn3 = fotoboxText['btn-empty']
    self.tplInstructPreview = fotoboxText['info-print']

    GPIO.output(21, GPIO.HIGH) # grün
    GPIO.output(16, GPIO.HIGH) # gelb
    GPIO.output(19, GPIO.LOW) # blau

    self.tplImage = self.composed["composed"]

    self.tplFooter = self.tplFooterOrg

    self.updateHtml(Form)

  def screenCapture(self, Form):
    self.screen = 2
    self.tplBtn1 = fotoboxText['btn-empty']
    self.tplBtn2 = fotoboxText['btn-empty']
    self.tplBtn3 = fotoboxText['btn-empty']

    GPIO.output(21, GPIO.LOW) # grün aus

    if not self.isLive:
      self.tplImage = "liveBack.png"
      if not fotoboxCfg['nopi']:
        # self.camera.preview_window=(fotoboxCfg['cam-p-x'], fotoboxCfg['cam-p-y'], fotoboxCfg['cam-p-width'], fotoboxCfg['cam-p-height'])
        # self.camera.start_preview(resolution=(1640, 1232), fullscreen=False, window = (fotoboxCfg['cam-p-x'], fotoboxCfg['cam-p-y'], fotoboxCfg['cam-p-width'], fotoboxCfg['cam-p-height']), hflip=fotoboxCfg['cam-p-hflip'])
        print("Enabling camera preview")
      self.isLive = True

    self.tplFooter = self.tplFooterOrg

    self.updateHtml(Form)

    #start countdown
    self.countdownTime = fotoboxCfg['countdown']
    self.updateCountdown()

  def updateCountdown(self):
    Form = window
    self.tplInstructPreview = ""
    self.tplInstruct = fotoboxText['info-count']
    # self.tplInstruct = self.tplInstruct.replace('${countdown}', str(self.countdownTime), 1)
    if self.countdownTime > 0:
      self.timerCountdown = str(self.countdownTime)
    else:
      self.timerCountdown = ""
    self.updateHtml(Form)

    self.countdownTime-=1

    if(self.countdownTime > 0):
      self.timerCnt.start(1000)
    elif self.countdownTime == 0:
      self.timerCnt.start(750)
    elif self.countdownTime == -1:
      #We already switch it here because photoTake seems to freeze the GPU briefly
      #and the updated HTML will not be ready in time
      self.tplInstruct = fotoboxText['info-capture']
      self.tplImage = "capturing.png"
      self.tplFooter = "Capturing..."
      self.updateHtmlBlack(Form)
      self.timerCnt.start(250)
    else:
      self.photoTake(Form)

  def photoTake(self, Form):
    if(self.isLive):
      self.isLive=False
      if not fotoboxCfg['nopi']:
        # self.camera.stop_preview()
        print("Disabling camera preview")
    self.lastPhoto = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    if not fotoboxCfg['nopi']:
      if not fotoboxCfg['gphoto']:
        # self.camera.resolution = (fotoboxCfg['cam-c-width'], fotoboxCfg['cam-c-height'])
        # self.camera.capture(self.temp+self.lastPhoto)
        print("TODO")
      else:
        myCmd = 'gphoto2 --capture-image-and-download --filename '+self.temp+self.lastPhoto
        answer = os.popen(myCmd).read()
    else:
      copyfile(os.path.dirname(os.path.realpath(__file__)) + '/design/dummy.jpg', self.temp+self.lastPhoto)
    self.screenReview(Form)

  def send_print(self, filename):
    try:
      conn = cups.Connection()
      printers = conn.getPrinters ()
      default_printer = conn.getDefault()
      print ("Drucke" + filename)
      conn.printFile(default_printer, filename, "foto", {'fit-to-page':'True'})
    except:
      pass

  def createComposedImage(self):
    image1= Image.open(os.path.dirname(os.path.realpath(__file__)) + '/' + fotoboxCfg["template"])
    if self.picturesTaken != 0:
        image1 = Image.open(self.composed["composed"])
    image1cpy = image1.copy()
    image2 = Image.open(self.save+self.lastPhoto)
    image2cpy = image2.copy()
    # 4:3 744 558
    # 3:2 750 500
    faktor = 2
    image2cpy = image2cpy.resize((750 * faktor, 500 * faktor), Image.ANTIALIAS)
    if self.picturesTaken == 0:
        # image1cpy.paste(image2cpy, (61, 42))
        image1cpy.paste(image2cpy, (61 * faktor, 42 * faktor))
    elif self.picturesTaken == 1:
        # image1cpy.paste(image2cpy, (981, 42))
        image1cpy.paste(image2cpy, (981 * faktor, 42 * faktor))
    elif self.picturesTaken == 2:
        #image1cpy.paste(image2cpy, (61, 638))
        image1cpy.paste(image2cpy, (61 * faktor, 638 * faktor))
    elif self.picturesTaken == 3:
        #image1cpy.paste(image2cpy, (981, 638))
        image1cpy.paste(image2cpy, (981 * faktor, 638 * faktor))
    self.picturesTaken += 1
    self.composed["composed"] = self.temp+"composed_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    if image1cpy.mode in ("RGBA", "P"):
      image1cpy = image1cpy.convert("RGB")
    image1cpy.save(self.composed["composed"])
    if self.picturesTaken == 4:
        image2 = Image.open(os.path.dirname(os.path.realpath(__file__)) + '/' + fotoboxCfg["templateOverlay"])
        image2cpy = image2.copy()
        image2cpy = image2cpy.resize((image1cpy.width, image1cpy.height), Image.ANTIALIAS)
        image1cpy.paste(image2cpy, (0, 0), image2cpy)
        if image1cpy.mode in ("RGBA", "P"):
          image1cpy = image1cpy.convert("RGB")
        image1cpy.save(self.composed["composed"])
        self.picturesTaken = 0
        self.screenPrint(window)
    else:
      # self.screenMain(window)
      self.screenCapture(window)


  def screenReview(self, Form):
    self.screen = 3
    self.tplInstructPreview = fotoboxText['info-review']
    self.tplBtn1 = fotoboxText['btn-save']
    self.tplBtn2 = fotoboxText['btn-recapture']
    self.tplBtn3 = fotoboxText['btn-cancel']
    GPIO.output(21, GPIO.HIGH) # grün
    GPIO.output(16, GPIO.HIGH) # gelb
    GPIO.output(19, GPIO.HIGH) # blau
    self.tplImage = self.temp+self.lastPhoto
    self.tplFooter = "Foto: " + self.lastPhoto

    self.updateHtml(Form)

  def tempDel(self):
    if self.lastPhoto != "" and os.path.isfile(self.temp+self.lastPhoto):
      os.remove(self.temp+self.lastPhoto)
      self.lastPhoto = ""
    self.picturesTaken = 0
    self.composed["composed"] = '../'+fotoboxCfg["template"]

  def noConfirm(self, Form):
    self.tempDel()
    self.screenMain(window)

  def doConfirm(self, Form):
    move(self.temp+self.lastPhoto, self.save+self.lastPhoto)
    print("Saved " + self.save+self.lastPhoto)
    self.createComposedImage()

  def retry(self, Form):
    # self.tempDel()
    self.screenCapture(window)

  def startViewer(self, Form):
    self.screen = 4

    if(self.isLive):
      self.isLive=False
      self.tplImage = "init.png"
      if not fotoboxCfg['nopi']:
        # self.camera.stop_preview()
        print("TODO")

    self.entries = None
    self.entries = (os.path.join(self.save, fn) for fn in os.listdir(self.save))
    self.entries = ((os.stat(path), path) for path in self.entries)
    self.entries = ((stat[ST_MTIME], path)
      for stat, path in self.entries if S_ISREG(stat[ST_MODE]))
    self.entries = list(self.entries)

    if(len(self.entries) > 0):
      self.viewerIndex = 0
      self.screenViewer(Form)
    else:
      print("No images to show")
      self.screenMain(Form)

  def screenViewer(self, Form):
    self.tplInstruct = fotoboxText['info-view']

    if(self.viewerIndex < (len(self.entries)-1)):
      self.tplBtn1 = fotoboxText['btn-next']
    else:
      self.tplBtn1 = fotoboxText['btn-empty']
    
    if(self.viewerIndex > 0):
      self.tplBtn2 = fotoboxText['btn-previous']
    else:
      self.tplBtn2 = fotoboxText['btn-empty']

    self.tplBtn3 = fotoboxText['btn-back']
    self.tplImage = self.entries[self.viewerIndex][1]
    self.tplFooter = "Foto " + str(self.viewerIndex+1) + \
      ' von ' + str(len(self.entries)) + \
      " · " + str(os.path.basename(self.entries[self.viewerIndex][1]))
    
    self.updateHtml(Form)

  def viewPrev(self, Form):
    if(self.viewerIndex > 0):
      self.viewerIndex -= 1
    self.screenViewer(Form)

  def viewNext(self, Form):
    if(self.viewerIndex < (len(self.entries)-1)):
      self.viewerIndex += 1
    self.screenViewer(Form)
 
class QWebView_mod(QWebView):
  def __init__(self):
    super(QWebView, self).__init__()
    self.ui = Ui_Form_mod()
    self.ui.setupUi(self)
    self.ui.initSystem(self)
    self.ui.screenMain(self)
    self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    if not fotoboxCfg['nopi']:
      self.btnC1 = GPIO.HIGH
      self.btnC2 = GPIO.HIGH
      self.btnC3 = GPIO.HIGH
    
    #Key Poller
    self.timerKey = QTimer(self)
    self.timerKey.timeout.connect(self.buttonCheck)
    self.timerKey.start(25)
    self.btnB  = 1

    self.showFullScreen()

  def buttonCheck(self):
    if not fotoboxCfg['nopi']:
      if self.btnB == 0:
        if GPIO.input(26) != self.btnC1:
          self.btnB =3
          if GPIO.input(26) == GPIO.LOW:
            self.buttonPress(1)
          self.btnC1 = GPIO.input(26)
        if GPIO.input(13) != self.btnC2:
          self.btnB = 3
          if GPIO.input(13) == GPIO.LOW:
            self.buttonPress(3)
          self.btnC2 = GPIO.input(13)
        if GPIO.input(20) != self.btnC3:
          self.btnB = 3
          if GPIO.input(20) == GPIO.LOW:
            self.buttonPress(2)
          self.btnC3 = GPIO.input(20)
      else:
        self.btnB -= 1

  #keyHandling
  def buttonPress(self, btn):
    print("Button Event: " + str(btn))
    if(self.ui.screen == 1):
      if(btn == 1):
        self.ui.screenCapture(self)
      #elif(btn == 2):
      #  self.ui.startViewer(self)
      elif(btn == 3): # reset printer
        GPIO.output(21, GPIO.LOW) # grün
        GPIO.output(16, GPIO.HIGH) # gelb
        os.system('cupsenable photoprinter')
        sleep(1)
        GPIO.output(21, GPIO.HIGH) # grün
        GPIO.output(16, GPIO.LOW) # gelb
    elif(self.ui.screen == 3):
      if(btn == 1):
        self.ui.doConfirm(self)
      elif(btn == 2):
        self.ui.retry(self)
      elif(btn == 3):
        self.ui.noConfirm(self)
    elif(self.ui.screen == 4):
      if(btn == 1):
        self.ui.viewNext(self)
      elif(btn == 2):
        self.ui.viewPrev(self)
      elif(btn == 3):
        self.ui.screenMain(self)
    elif(self.ui.screen == 5):
      if(btn == 1):
        print("Drucke " + self.ui.composed["composed"])
        self.ui.send_print(self.ui.composed["composed"])
        self.ui.noConfirm(self)
      elif(btn == 2):
        self.ui.screenMain(self)

  def keyPressEvent(self, e):
    if e.key() == QtCore.Qt.Key_Escape:
      self.close()
    elif e.key() == QtCore.Qt.Key_1:
      self.buttonPress(1)
    elif e.key() == QtCore.Qt.Key_2:
      self.buttonPress(2)
    elif e.key() == QtCore.Qt.Key_3:
      self.buttonPress(3)


app = QApplication(sys.argv)
window = QWebView_mod()

sys.exit(app.exec_())
