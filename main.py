from platform import platform
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Ui_ui_main import *
import sqlite3
import login
import os

import logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

allProfileDataPath = r'D:\DATA-GOLOGIN\Data'

list_profile = os.listdir(allProfileDataPath)
list_profile.sort()

def sort_list():
    global list_profile
    len_list = len(list_profile)
    number_list = []
    char_list = []
    for i in range(0, len(list_profile)):
        if list_profile[i].isdigit():
            number_list.append(int(list_profile[i]))
        else:
            char_list.append(list_profile[i])
    number_list.sort()
    list_profile.clear()
    for i in range(0, len(number_list)):
        list_profile.append(str(number_list[i]))
    list_profile += char_list

class ItemDelegate(QtWidgets.QStyledItemDelegate):
    cellEditingStarted = QtCore.pyqtSignal(int, int)

    def createEditor(self, parent, option, index):
        result = super(ItemDelegate, self).createEditor(parent, option, index)
        if result:
            self.cellEditingStarted.emit(index.row(), index.column())
        return result

class MyForm(QMainWindow):

    SIGN_CHROME = False
    SIGN_SYNC = pyqtSignal()
    tag1 = False
    tag2 = False
    title1 = False
    title2 = False

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.createData()
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.ui.tableWidget.customContextMenuRequested.connect(self.contextMenu)
        self.ui.pushButton.clicked.connect(self.createProfile)
        
        self.ui.pushButton_5.clicked.connect(self.deleteEvent)
        self.delegate = ItemDelegate(self)
        self.delegate.cellEditingStarted.connect(self.test2)
        self.ui.tableWidget.setItemDelegate(self.delegate)
        self.delegate.closeEditor.connect(self.test1)
        self.point = [0,0]
        # self.addDataProfile()
        self.showData()
        self._threads = []


    def test1(self):
        if self.point[1] == 2:
            note = self.ui.tableWidget.item(self.point[0], self.point[1]).text()
            uid = self.ui.tableWidget.item(self.point[0], 0).text()
            conn = sqlite3.connect('db_app.db')
            cur = conn.cursor()
            cur.execute(
                'UPDATE Profiles SET status=? WHERE profile_id=?',(note, uid))
            conn.commit()
            conn.close()
            self.ui.statusbar.showMessage(self.tr("Cập nhật ghi chú"))
            self.showData()

    def test2(self, row, column):
        self.point = [row, column]
    

    def addDataProfile(self):
        sort_list()
        conn = sqlite3.connect('db_app.db')
        cur = conn.cursor()
        for profile_id in list_profile:
            profile_path = os.path.join(allProfileDataPath, profile_id)
            try:
                cur.execute('INSERT INTO Profiles( \
                    profile_id, \
                    profile_path \
                ) VALUES (?,?)',
                    (profile_id, profile_path))
                conn.commit()
            except Exception:
                import traceback 
                print(traceback.format_exc())  
            # self.Show_all()
            # self.statusBar().showMessage('New user Added')
        conn.close()


        # self.getData(1)
    def createData(self):
        try:
            conn = sqlite3.connect('db_app.db')
            cur = conn.cursor()

            cur.execute('CREATE TABLE IF NOT EXISTS Profiles ( \
                    id INTERGER PRIMARY KEY, \
                    profile_id varchar(255) UNIQUE, \
                    profile_path text, \
                    status text)')

            conn.commit()
            conn.close()
        except Exception:
            import traceback
            print(traceback.format_exc())

    def showData(self):
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)
        conn = sqlite3.connect('db_app.db')
        cur = conn.cursor()
        cur.execute('SELECT `profile_id`, `profile_path`, `status` FROM Profiles')
        
        data = cur.fetchall()
        if data:
            self.ui.tableWidget.insertRow(0)
            for row, form in enumerate(data):
                for column, item in enumerate(form):
                    if column == 0:
                        chkBoxItem = QTableWidgetItem(str(item))
                        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable |
                            QtCore.Qt.ItemIsEnabled)
                        chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                        self.ui.tableWidget.setItem(row, column, chkBoxItem)
                    else:
                        self.ui.tableWidget.setItem(row, column, QTableWidgetItem(str(item)))
                    column += 1

                row_positon = self.ui.tableWidget.rowCount()
                if row < len(data)-1:
                    self.ui.tableWidget.insertRow(row_positon)
        
        conn.close()

    def addProfile(self, profile_id, profile_path):
        try:
            conn = sqlite3.connect('db_app.db')
            cur = conn.cursor()
            try:
                cur.execute('INSERT INTO Profiles( \
                    profile_id, \
                    profile_path \
                ) VALUES (?,?)',
                    (profile_id, profile_path))
            except Exception:
                import traceback 
                print(traceback.format_exc())
            conn.commit()
            conn.close()
            return True
            # self.Show_all()
            # self.statusBar().showMessage('New user Added')
        except Exception:
            import traceback 
            print(traceback.format_exc())
            return False

    def createProfile(self):
        profile_path = QFileDialog.getExistingDirectory(self, "Select profile", '', QFileDialog.ShowDirsOnly)
        if profile_path:
            profile_id = profile_path.split('/')[-1]
            self.addProfile(profile_id, profile_path)
            self.showData()

    
    def deleteAccount(self, uid):
        conn = sqlite3.connect('db_app.db')
        cur = conn.cursor()
        try:
            cur.execute('DELETE FROM Profiles WHERE profile_id=?', (uid,))
        except:
            import traceback
            print(traceback.format_exc())
            pass
        conn.commit()   
        conn.close()

    def deleteEvent(self):
        rowPosition = self.ui.tableWidget.rowCount()
        for x in range(0, rowPosition):
            item = self.ui.tableWidget.item(x, 0)
            tt = item.checkState()
            if(tt == 2):
                accountID = self.ui.tableWidget.item(x, 0).text()
                self.deleteAccount(accountID)
        self.showData()

    def contextMenu(self, event):
        if int(self.ui.tableWidget.rowCount()) > 0:
            widget = self.sender()
            a = self.ui.tableWidget.indexAt(event)
            menu = QtWidgets.QMenu(self) 
            view_action = menu.addAction('Mở Profile')
            # close_action = menu.addAction('Close Browser')
            # dataProfile = self.ui.tableWidget.item(a.row(), 1).text() if self.ui.tableWidget.item(a.row(), 1).text() != '' else ''
            # if dataProfile == '':
            #     view_action.setEnabled(False)
            action = menu.exec_(widget.mapToGlobal(event)) 
            if action == view_action:
                uid = self.ui.tableWidget.item(a.row(), 0).text()
                obj = login.Login(uid)
                self._threads.append(obj)
                obj.finished.connect(obj.deleteLater)
                obj.start()





# "C:\Users\DELL\.gologin\browser\orbita-browser-120\chrome.exe" --lang=vi-VN --disable-encryption --donut-pie=undefined --webrtc-ip-handling-policy=default_public_interface_only --font-masking-mode=2 --load-extension="C:\Users\DELL\.gologin\extensions\cookies-ext\65dda30a2e65dc84c8ad52dc," --restore-last-session --user-data-dir="C:\Users\DELL\AppData\Local\Temp\GoLogin\profiles\65dda30a2e65dc84c8ad52dc" --flag-switches-begin --flag-switches-end






    # def createProfile(self):
    #     new_profile_folder = QFileDialog.getExistingDirectory(self, "Select profile", '', QFileDialog.ShowDirsOnly)
    #     if new_profile_folder:
    #         self._threads = []
    #         obj = login.Login(new_profile_folder)
    #         thread = QThread()
    #         obj.moveToThread(thread)
    #         self._threads.append((thread, obj))
    #         # signal from object
    #         obj.sign_chrome.connect(self.signChrome)
    #         obj.sign_data.connect(self.addAccount)
    #         obj.sign_exit.connect(thread.quit)
    #         # send signal from gui
    #         self.SIGN_SYNC.connect(obj.getCookie)
    #         # run thread
    #         thread.started.connect(obj.loginAccount)
    #         thread.finished.connect(obj.deleteLater)
    #         thread.start()
    
    
        
    @pyqtSlot(dict)
    def addAccount(self, data):
        cookie = data['cookie']
        token = data['token']
        username = data['name']
        profile_path = data['profile_path']
        userId = data['userId']
        name = profile_path.split('/')[-1]
        userAgent = data['userAgent']
        platform = data['platform']
        result = self.createOrUpdateAccount(
            profile=profile_path,
            name = name,
            cookie=cookie,
            token=token,
            userId=userId,
            username=username,
            userAgent=userAgent,
            platform=platform,
            fanpageOfUser=''
            )
        if result:
            self.addProfile(userId=userId, username=username, folder_upload='')
        
        self.showData()
        self.showDataProfile()

    def createOrUpdateAccount(self, profile, name, cookie, userAgent, token, platform, userId,  username, fanpageOfUser):
        result = self.addAccountToDatabase(
            profile=profile,
            name = name,
            cookie=cookie,
            token=token,
            userId=userId,
            username=username,
            userAgent=userAgent,
            platform=platform,
            fanpageOfUser=fanpageOfUser
            )
        if result:
            return True    
        else:
            self.updateAccount(
            profile=profile,
            name = name,
            cookie=cookie,
            token=token,
            userId=userId,
            username=username,
            userAgent=userAgent,
            platform=platform,
            fanpageOfUser=fanpageOfUser)
            return False


    def updateAccount(
        self, 
        profile,
        name, 
        cookie, 
        userAgent, 
        token, 
        platform, 
        userId, 
        username, 
        fanpageOfUser
    ):
        flag = True
        try:
            conn = sqlite3.connect('db_app.db')
            cur = conn.cursor()
            try:
                cur.execute('UPDATE Accounts SET \
                    profile=?,\
                    name=?, \
                    cookie=?, \
                    userAgent=?, \
                    token=?, \
                    platform=?, \
                    username=?, \
                    fanpageOfUser=? \
                    WHERE userId=?',
                    (profile,
                    name, 
                    cookie, 
                    userAgent,
                    token, 
                    platform, 
                    username, 
                    fanpageOfUser,
                    userId))
            except Exception:
                flag = False
                import traceback 
                print(traceback.format_exc())
            conn.commit()
            conn.close()
            # self.Show_all()
            # self.statusBar().showMessage('New user Added')
            print('update')
        except Exception:
            flag = False
            import traceback 
            print(traceback.format_exc())
        return flag

    def btnState(self, b):
        if b.objectName() == 'checkBox':
            if b.isChecked() == True:
                self.tag1 = True
            else:
                self.tag1 = False
        if b.objectName() == 'checkBox_2':
            if b.isChecked() == True:
                self.title1 = True
            else:
                self.title1 = False
        if b.objectName() == 'checkBox_3':
            if b.isChecked() == True:
                self.tag2 = True
            else:
                self.tag2 = False
        if b.objectName() == 'checkBox_4':
            if b.isChecked() == True:
                self.title2 = True
            else:
                self.title2 = False


    def runUpload(self):
        list_profile = []
        rowPosition = self.ui.tableWidget_2.rowCount()
        start = int(self.ui.spinBox_2.text())
        end = int(self.ui.spinBox_3.text())
        limit = int(self.ui.spinBox_4.text())
        for x in range(0, rowPosition):
            item = self.ui.tableWidget_2.item(x, 0)
            tt = item.checkState()
            if(tt == 2):
                accountID = self.ui.tableWidget_2.item(x, 0).text()
                video_path = self.ui.tableWidget_2.item(x, 2).text() if self.ui.tableWidget_2.item(x, 2).text() != '' else ''
                dataAccount = self.getData(accountID, '2')
                # print(dataAccount, accountID)
                if dataAccount['status'] == 0 and video_path != '':
                    userId = dataAccount['userId']
                    cookie = dataAccount['cookie']
                    token = dataAccount['token']
                    userAgent = dataAccount['userAgent']

                    list_profile.append({
                        'userId': userId,
                        'cookie': cookie,
                        'token': token,
                        'userAgent': userAgent,
                        'video_folder': video_path,
                        'row': x,
                    })
        if len(list_profile):
            self._threads = []
            obj = upload.uploadProfiles(listAccounts=list_profile, timeStart = start, timeEnd = end, limit = limit, rmHashtag=self.tag1, rmTitle=self.title1)
            thread = QThread()
            obj.moveToThread(thread)
            self._threads.append((thread, obj))
            # signal from object
            # obj.sign_chrome.connect(self.signChrome)
            obj.sign_msg.connect(self.msg)
            obj.sign_exit.connect(thread.quit)
            # # send signal from gui
            # self.SIGN_SYNC.connect(obj.getCookie)
            # run thread
            thread.started.connect(obj.run)
            thread.finished.connect(obj.deleteLater)
            thread.start()
        else:
            print('không có profile khả dụng')
    
    def runMultiUpload(self):
        try:
            list_profile = []
            rowPosition = self.ui.tableWidget_2.rowCount()
            start = int(self.ui.spinBox_2.text())
            end = int(self.ui.spinBox_3.text())
            limit = int(self.ui.spinBox_4.text())
            for x in range(0, rowPosition):
                item = self.ui.tableWidget_2.item(x, 0)
                tt = item.checkState()
                if(tt == 2):
                    accountID = self.ui.tableWidget_2.item(x, 0).text()
                    video_path = self.ui.tableWidget_2.item(x, 2).text() if self.ui.tableWidget_2.item(x, 2).text() != '' else ''
                    dataAccount = self.getData(accountID, '2')
                    # print(dataAccount, accountID)
                    if dataAccount['status'] == 0 and video_path != '':
                        userId = dataAccount['userId']
                        cookie = dataAccount['cookie']
                        token = dataAccount['token']
                        userAgent = dataAccount['userAgent']

                        list_profile.append({
                            'userId': userId,
                            'cookie': cookie,
                            'token': token,
                            'userAgent': userAgent,
                            'video_folder': video_path,
                            'row': x,
                        })
            if len(list_profile):
                self._threads = []
                thread_count = int(self.ui.thread_count.text())
                for y in range(thread_count):
                    worker = upload.multiUploadProfiles(x=y, thread_count=thread_count, listAccounts=list_profile, timeStart = start, timeEnd = end, limit = limit, rmHashtag=self.tag1, rmTitle=self.title1)
                    self._threads.append(worker)
                    worker.sign_msg.connect(self.msg)
                    worker.finished.connect(worker.deleteLater)
                    # worker.finished.connect(self.update_video)
                    worker.start()
            # obj = 
            # thread = QThread()
            # obj.moveToThread(thread)
            # self._threads.append((thread, obj))
            # # signal from object
            # # obj.sign_chrome.connect(self.signChrome)
            # obj.sign_msg.connect(self.msg)
            # obj.sign_exit.connect(thread.quit)
            # # # send signal from gui
            # # self.SIGN_SYNC.connect(obj.getCookie)
            # # run thread
            # thread.started.connect(obj.run)
            # thread.finished.connect(obj.deleteLater)
            # thread.start()
            else:
                print('không có profile khả dụng')
        except Exception:
            logging.error('Failed to run', exc_info=True)

    
    

    def runUploadPage(self):
        list_profile = []
        rowPosition = self.ui.tableWidget_3.rowCount()
        start = int(self.ui.spinBox_6.text())
        end = int(self.ui.spinBox_7.text())
        limit = int(self.ui.spinBox_5.text())
        for x in range(0, rowPosition):
            item = self.ui.tableWidget_3.item(x, 0)
            tt = item.checkState()
            if(tt == 2):
                accountID = self.ui.tableWidget_3.item(x, 0).text()
                video_path = self.ui.tableWidget_3.item(x, 2).text() if self.ui.tableWidget_3.item(x, 2).text() != '' else ''
                dataAccount = self.getData(accountID, '2')
                # print(dataAccount, accountID)
                if dataAccount['status'] == 0 and video_path != '':
                    userId = dataAccount['userId']
                    cookie = dataAccount['cookie']
                    token = dataAccount['token']
                    userAgent = dataAccount['userAgent']

                    list_profile.append({
                        'userId': userId,
                        'cookie': cookie,
                        'token': token,
                        'userAgent': userAgent,
                        'video_folder': video_path,
                        'row': x,
                    })
        if len(list_profile):
            self._threads = []
            obj = upload.uploadProfiles(listAccounts=list_profile, timeStart = start, timeEnd = end, limit = limit, rmHashtag=self.tag2, rmTitle=self.title2)
            thread = QThread()
            obj.moveToThread(thread)
            self._threads.append((thread, obj))
            # signal from object
            # obj.sign_chrome.connect(self.signChrome)
            obj.sign_msg.connect(self.msg2)
            obj.sign_exit.connect(thread.quit)
            # # send signal from gui
            # self.SIGN_SYNC.connect(obj.getCookie)
            # run thread
            thread.started.connect(obj.run)
            thread.finished.connect(obj.deleteLater)
            thread.start()
        else:
            print('không có profile khả dụng')

    def runMultiUploadPage(self):
        try:
            list_profile = []
            rowPosition = self.ui.tableWidget_3.rowCount()
            start = int(self.ui.spinBox_6.text())
            end = int(self.ui.spinBox_7.text())
            limit = int(self.ui.spinBox_5.text())
            for x in range(0, rowPosition):
                item = self.ui.tableWidget_3.item(x, 0)
                tt = item.checkState()
                if(tt == 2):
                    accountID = self.ui.tableWidget_3.item(x, 0).text()
                    video_path = self.ui.tableWidget_3.item(x, 2).text() if self.ui.tableWidget_3.item(x, 2).text() != '' else ''
                    dataAccount = self.getData(accountID, '2')
                    # print(dataAccount, accountID)
                    if dataAccount['status'] == 0 and video_path != '':
                        userId = dataAccount['userId']
                        cookie = dataAccount['cookie']
                        token = dataAccount['token']
                        userAgent = dataAccount['userAgent']

                        list_profile.append({
                            'userId': userId,
                            'cookie': cookie,
                            'token': token,
                            'userAgent': userAgent,
                            'video_folder': video_path,
                            'row': x,
                        })
            if len(list_profile):
                self._threads = []
                thread_count = int(self.ui.thread_count_2.text())
                for y in range(thread_count):
                    worker = upload.multiUploadProfiles(x=y, thread_count=thread_count, listAccounts=list_profile, timeStart = start, timeEnd = end, limit = limit, rmHashtag=self.tag2, rmTitle=self.title2)
                    self._threads.append(worker)
                    worker.sign_msg.connect(self.msg2)
                    worker.finished.connect(worker.deleteLater)
                    # worker.finished.connect(self.update_video)
                    worker.start()
            else:
                print('không có profile khả dụng')
        except Exception:
            logging.error('Failed to run upload page', exc_info=True)

    def msg(self, _type, row, text):
        if _type == 1:
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(str(text)))
        if _type == 2:
            i = QtWidgets.QListWidgetItem(text)
            if(row==1):
                i.setForeground(QtGui.QColor(255, 0, 0))
            if(row==2):
                i.setForeground(QtGui.QColor(255, 0, 255))
            self.ui.listWidget.insertItem(0, i)

    def msg2(self, _type, row, text):
        if _type == 1:
            self.ui.tableWidget_3.setItem(row, 3, QTableWidgetItem(str(text)))
        if _type == 2:
            i = QtWidgets.QListWidgetItem(text)
            if(row==1):
                i.setForeground(QtGui.QColor(255, 0, 0))
            if(row==2):
                i.setForeground(QtGui.QColor(255, 0, 255))
            self.ui.listWidget_2.insertItem(0, i)

    
        

# XU LY PAGE 
    def scanPage(self):
        self.ui.pushButton_4.setEnabled(False)
        list_profile = []
        rowPosition = self.ui.tableWidget.rowCount()
        for x in range(0, rowPosition):
            item = self.ui.tableWidget.item(x, 0)
            tt = item.checkState()
            if(tt == 2):
                accountID = self.ui.tableWidget.item(x, 0).text()
                platform = self.ui.tableWidget.item(x, 2).text()
                if platform == 'Page':
                    continue
                else:
                    dataAccount = self.getData(accountID)
                    if dataAccount['status'] == 0:
                        userId = dataAccount['userId']
                        cookie = dataAccount['cookie']
                        token = dataAccount['token']
                        userAgent = dataAccount['userAgent']
                        profile = dataAccount['profile']
                        list_profile.append({
                            'userId': userId,
                            'cookie': cookie,
                            'token': token,
                            'userAgent': userAgent,
                            'profile': profile
                        })

        if len(list_profile):      
            self._threads = []
            obj = scanpage.ScanPage(list_profile)
            thread = QThread()
            obj.moveToThread(thread)
            self._threads.append((thread, obj))
            # signal from object
            # obj.sign_chrome.connect(self.signChrome)
            obj.sign_data.connect(self.addPageToDatabase)
            obj.sign_exit.connect(thread.quit)
            # # send signal from gui
            # self.SIGN_SYNC.connect(obj.getCookie)
            # run thread
            thread.started.connect(obj.run)
            thread.finished.connect(obj.deleteLater)
            thread.finished.connect(lambda: self.ui.pushButton_4.setEnabled(True))
            thread.start()

    def addPageToDatabase(self, list_page):
        
        if len(list_page):
            for page in list_page:
                token = page['token']
                cookie = page['cookie']
                userId = page['userId']
                username = page['username']
                userAgent = page['userAgent']
                platform = page['platform']
                fanpageOfUser = page['fanpageOfUser']
                result = self.createOrUpdateAccount(profile='', name='', cookie=cookie, userAgent=userAgent, userId=userId, token=token, platform=platform, fanpageOfUser=fanpageOfUser, username=username)
                if result:
                    self.addPage(userId=userId, username=username, folder_upload='', fanpageOfUser=fanpageOfUser)
            self.showData()
            self.showDataPage()

    

    def addPage(self, userId, username, folder_upload, fanpageOfUser):
        try:
            conn = sqlite3.connect('db_app.db')
            cur = conn.cursor()
            try:
                cur.execute('INSERT INTO Fanpages( \
                    userId, \
                    username, \
                    folder_upload, \
                    fanpageOfUser \
                ) VALUES (?,?,?,?)',
                    ( userId, 
                    username, 
                    folder_upload,
                    fanpageOfUser))
            except Exception:
                import traceback 
                print(traceback.format_exc())
            conn.commit()
            conn.close()
            # self.Show_all()
            # self.statusBar().showMessage('New user Added')
        except Exception:
            import traceback 
            print(traceback.format_exc())

    def addAccountToDatabase(
        self, 
        profile,
        name, 
        cookie, 
        userAgent, 
        token, 
        platform, 
        userId, 
        username, 
        fanpageOfUser
    ):
        flag = True
        try:
            conn = sqlite3.connect('db_app.db')
            cur = conn.cursor()
            try:
                cur.execute('INSERT INTO Accounts( \
                    profile,\
                    name, \
                    cookie, \
                    userAgent, \
                    token, \
                    platform, \
                    userId, \
                    username, \
                    fanpageOfUser \
                ) VALUES (?,?,?,?,?,?,?,?,?)',
                    (profile,
                    name, 
                    cookie, 
                    userAgent,
                    token, 
                    platform, 
                    userId, 
                    username, 
                    fanpageOfUser))
            except Exception:
                flag = False
                import traceback 
                print(traceback.format_exc())
            conn.commit()
            conn.close()
            # self.Show_all()
            # self.statusBar().showMessage('New user Added')
        except Exception:
            flag = False
            import traceback 
            print(traceback.format_exc())
        return flag


    

    def getData(self, _id, _type = '1'):
        conn = sqlite3.connect('db_app.db')
        cur = conn.cursor()
        try:
            if _type == '1':
                cur.execute('SELECT `profile`, `userId`, `username`, `cookie`, `token`, `userAgent` FROM Accounts WHERE `id`=?',(_id,))
            if _type == '2':
                cur.execute('SELECT `profile`, `userId`, `username`, `cookie`, `token`, `userAgent` FROM Accounts WHERE `userId`=?',(_id,))
            data = cur.fetchone()
            profile, userId, username, cookie, token, userAgent = data
            return {
                'status': 0,
                'profile': profile,
                'userId': userId,
                'username': username,
                'cookie': cookie,
                'token': token,
                'userAgent': userAgent,
                
            }
        except:
            return {
                'status': 1
            }
    

    def showDataProfile(self):
        self.ui.tableWidget_2.clearContents()
        self.ui.tableWidget_2.setRowCount(0)
        conn = sqlite3.connect('db_app.db')
        cur = conn.cursor()
        cur.execute('SELECT `userId`, `username`, `folder_upload` FROM Profiles')
        data = cur.fetchall()
        if data:
            self.ui.tableWidget_2.insertRow(0)
            for row, form in enumerate(data):
                for column, item in enumerate(form):
                    if column == 0:
                        chkBoxItem = QTableWidgetItem(str(item))
                        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable |
                            QtCore.Qt.ItemIsEnabled)
                        chkBoxItem.setCheckState(QtCore.Qt.Checked)
                        self.ui.tableWidget_2.setItem(row, column, chkBoxItem)
                    else:
                        self.ui.tableWidget_2.setItem(row, column, QTableWidgetItem(str(item)))
                    column += 1

                row_positon = self.ui.tableWidget_2.rowCount()
                if row < len(data)-1:
                    self.ui.tableWidget_2.insertRow(row_positon)
        conn.close()

    def showDataPage(self):
        self.ui.tableWidget_3.clearContents()
        self.ui.tableWidget_3.setRowCount(0)
        conn = sqlite3.connect('db_app.db')
        cur = conn.cursor()
        cur.execute('SELECT `userId`, `username`, `folder_upload` FROM Fanpages')
        data = cur.fetchall()
        if data:
            self.ui.tableWidget_3.insertRow(0)
            for row, form in enumerate(data):
                for column, item in enumerate(form):
                    if column == 0:
                        chkBoxItem = QTableWidgetItem(str(item))
                        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable |
                            QtCore.Qt.ItemIsEnabled)
                        chkBoxItem.setCheckState(QtCore.Qt.Checked)
                        self.ui.tableWidget_3.setItem(row, column, chkBoxItem)
                    else:
                        self.ui.tableWidget_3.setItem(row, column, QTableWidgetItem(str(item)))
                    column += 1

                row_positon = self.ui.tableWidget_3.rowCount()
                if row < len(data)-1:
                    self.ui.tableWidget_3.insertRow(row_positon)
        conn.close()

    

    
    


    def edit_data(self, video_folder, uid, type_):
        conn = sqlite3.connect('db_app.db')
        cur = conn.cursor()
        if type_ == 0:
            # path = cur.execute('SELECT folder_upload from user WHERE folder =?',(video_folder,))
            # if path.fetchall() == []:
            cur.execute(
                'UPDATE Profiles SET folder_upload=? WHERE userId=?',(video_folder, uid))
            conn.commit()
            # else:
            #     self.ui.statusbar.showMessage(self._translate("MainWindow","Video folder already exists"))
            #     return False
            conn.close()
            self.ui.statusbar.showMessage("Videos folder saved")
            self.showDataProfile()
        if type_ == 1:
            # path = cur.execute('SELECT folder_upload from user WHERE folder =?',(video_folder,))
            # if path.fetchall() == []:
            cur.execute(
                'UPDATE Fanpages SET folder_upload=? WHERE userId=?',(video_folder, uid))
            conn.commit()
            # else:
            #     self.ui.statusbar.showMessage(self._translate("MainWindow","Video folder already exists"))
            #     return False
            conn.close()
            self.ui.statusbar.showMessage("Videos folder saved")
            self.showDataPage()

    
        
    def checkLicense(self):
        import app
        keytool = app.create_key("Reup Reels")
        http = app.HttpReq(self, key_reg=keytool, tool_name="Reup Reels")
        http.request()
        dirr = open('key.txt', 'w')
        dirr.write(str(keytool))
        dirr.close()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    windown = MyForm()
    windown.show()
    sys.exit(app.exec_())