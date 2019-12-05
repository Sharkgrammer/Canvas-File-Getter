import os
import shutil
from tkinter import *
from tkinter.ttk import Progressbar
from selenium import webdriver
import threading

splitter = ":@:"
dir_path = os.path.dirname(os.path.realpath(__file__))
basedir = "canvasFiles\\"
tempPath = dir_path + "\\" + basedir + "\\temp"
driver = None
barvalue = 0.0


def courseScanner(innerUrl, name, amt):
    global driver
    print(name + ":  " + innerUrl)
    if not os.path.exists(name):
        os.makedirs(name)

    driver.get(innerUrl)

    items = driver.find_elements_by_class_name("item_link")
    itemsStrings = []
    for item in items:
        itemsStrings.append(item.get_attribute('href') + splitter + item.text)

    coursePercent = 1 / amt

    if len(itemsStrings) == 0:
        updateProgressBar(coursePercent)
        return

    linkPercent = coursePercent * (1 / len(itemsStrings))
    for string in itemsStrings:
        string = str(string)
        fileScanner(string.split(splitter)[0], linkCleanse(name + "\\" + string.split(splitter)[1]))
        updateProgressBar(linkPercent)

    tempMover(name)


def fileScanner(innerUrl, name):
    global driver
    driver.get(innerUrl)
    content = driver.find_element_by_class_name('ic-Layout-contentMain')

    links = content.find_elements_by_tag_name('a')

    for link in links:
        if "download" in str(link.get_attribute('href')):
            driver.implicitly_wait(1)
            link.click()


def tempMover(to):
    files = os.listdir(tempPath)

    for f in files:
        shutil.move(tempPath + "\\" + f, to)


def linkCleanse(link):
    return link.replace(" ", "_").replace(":", "_")


def updateProgressBar(value):
    global barvalue
    newvalue = 100 * value
    barvalue = barvalue + newvalue

    bar['value'] = round(barvalue, 0)


def mainMethod():
    global driver
    username = txtUsername.get()
    password = txtPassword.get()

    print("Starting...")

    if not os.path.exists(basedir):
        os.makedirs(basedir)

    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

    print(basedir)

    os.environ['MOZ_HEADLESS'] = '1'

    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "multipart/x-zip,application/zip,application/x-zip-compressed,application/x-compressed,application/msword,application/csv,text/csv,image/png ,image/jpeg, application/pdf, text/html,text/plain,  application/excel, application/vnd.ms-excel, application/x-excel, application/x-msexcel, application/octet-stream, application/vnd.ms-powerpoint, application/vnd.openxmlformats-officedocument.presentationml.presentation, application/x-rar-compressed, application/rtf,audio/mpeg")
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", tempPath)
    profile.set_preference("browser.download.useDownloadDir", True)

    driver = webdriver.Firefox(profile)

    loginUrl = "https://ucc.instructure.com/"

    print("Connecting...")

    driver.get(loginUrl)

    print("Connected, logging in...")

    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_name("_eventId_proceed").click()

    driver.implicitly_wait(5)

    test = driver.find_element_by_class_name("menu-item__text")
    if not test:
        print("Login error")
        exit()

    courseSpans = driver.find_elements_by_xpath('//a[@class="ic-DashboardCard__link"]')
    courseStrings = []

    for course in courseSpans:
        courseStrings.append(course.get_attribute('href') + splitter + str(course.text).split("\n")[0])

    for string in courseStrings:
        string = str(string)
        courseScanner(string.split(splitter)[0], linkCleanse(basedir + string.split(splitter)[1]), len(courseStrings))

    driver.quit()


class threadClass(object):

    def __init__(self, target):
        self.interval = 1

        thread = threading.Thread(target=target, args=())
        thread.daemon = True
        thread.start()


def runMethod():
    btn['state'] = 'disabled'
    txtPassword['state'] = 'disabled'
    txtUsername['state'] = 'disabled'

    run = threadClass(mainMethod)


UI = Tk()
UI.geometry('300x200')

UI.title('Canvas File Getter')

frmMain = Frame(UI)

lblUsername = Label(frmMain, text="Username:", padx=5, pady=5)
lblUsername.grid(column=0, row=2)

lblPassword = Label(frmMain, text="Password:", padx=5, pady=5)
lblPassword.grid(column=0, row=3)

txtUsername = Entry(frmMain, width=25)
txtUsername.grid(column=1, row=2)

txtPassword = Entry(frmMain, show="*", width=25)
txtPassword.grid(column=1, row=3)

btn = Button(frmMain, text="Download files", command=runMethod, padx=5, pady=5)
btn.grid(column=0, row=4, columnspan=2, padx=20, pady=20)

bar = Progressbar(frmMain, length=200)

bar.grid(column=0, row=6, columnspan=2)

frmMain.grid(row=0, column=0)
frmMain.grid_rowconfigure(0, weight=1)
frmMain.grid_columnconfigure(0, weight=1)
UI.grid_rowconfigure(0, weight=1)
UI.grid_columnconfigure(0, weight=1)

UI.mainloop()
