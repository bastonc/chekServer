# This Python file uses the following encoding: utf-8
import sys
import json
import requests
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QWidget, QHBoxLayout, QAction, QSystemTrayIcon, QStyle, QMenu
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
QTableWidgetItem, QVBoxLayout

from checkServer import Ui_MainWindow

class checkThread (QObject):
    warn_signal = pyqtSignal(object)
    def __init__(self, parrent, row_number):
        super().__init__()
        self.parrent = parrent
        self.row_num = row_number
        self.flag = True

    def stopChek(self):
        self.flag = False

    def checkSite(self):
        ok_backround = "background: #238D43;"
        error_background = "background: #BF4030;"
        reset_background = "background: #2F2A29;"
        while self.flag:
            for i, server in enumerate(self.parrent.serversList):
                if i == self.row_num:
                    try:
                        #print (server['url_server'])
                        answer = requests.get(server['url_server'], timeout=(0.5, 3))

                        if answer:
                            if answer.status_code == 200:
                                self.parrent.string_list[i]['green'].setStyleSheet(ok_backround)
                                self.parrent.string_list[i]['red'].setStyleSheet(reset_background)
                                # self.parrent.string_list[i]['red']
                                self.parrent.string_list[i]['green'].setText(str(answer.status_code))
                                self.parrent.string_list[i]['red'].setText('')
                            else:
                                # print(answer.status_code)
                                self.parrent.string_list[i]['red'].setStyleSheet(error_background)
                                self.parrent.string_list[i]['green'].setStyleSheet(reset_background)
                                self.parrent.string_list[i]['red'].setText(str(answer.status_code))
                                self.parrent.string_list[i]['green'].setText('')
                        else:
                            self.parrent.string_list[i]['red'].setStyleSheet(error_background)
                            self.parrent.string_list[i]['green'].setStyleSheet(reset_background)
                            self.parrent.string_list[i]['red'].setText(str(answer.status_code))
                            self.parrent.string_list[i]['green'].setText('')

                    except requests.exceptions.RequestException:
                        self.parrent.string_list[i]['red'].setStyleSheet(error_background)
                        self.parrent.string_list[i]['green'].setStyleSheet(reset_background)
                        self.parrent.string_list[i]['red'].setText("Not in DNS")
                        self.parrent.string_list[i]['green'].setText('')
                        self.warn_signal.emit([
                            server['url_server'],
                            self.parrent.string_list[i]['red'].text()
                            ])



                    except requests.exceptions.ReadTimeout:
                        self.parrent.string_list[i]['red'].setStyleSheet(error_background)
                        self.parrent.string_list[i]['green'].setStyleSheet(reset_background)
                        self.parrent.string_list[i]['red'].setText("Ntwrk error")
                        self.parrent.string_list[i]['green'].setText('')

                    print("Check: ", server['url_server'])
                    if server['shift_server'] == '':
                        time_shift = 20
                    else:
                        time_shift = server['shift_server']
                    time.sleep(int(time_shift))

class ChekMain(QMainWindow):
    def __init__(self):
        super(ChekMain, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.thread_list = []
        self.initUI()
        self.statusBar().hide()



    def initUI(self):


        self.table_widgets = QTableWidget()
        self.table_widgets.verticalHeader().hide()
        self.table_widgets.horizontalHeader().hide()
        self.table_widgets.setContentsMargins(10, 0, 10, 0)
        self.updateUI()
        self.setWindowIcon(QIcon("logo.png"))
        self.setWindowTitle("Server checker")
        self.setFixedWidth(320)
        self.show()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        '''
            Объявим и добавим действия для работы с иконкой системного трея
            show - показать окно
            hide - скрыть окно
            exit - выход из программы
        '''
        show_action = QAction("Show", self)
        show_action.setIcon(QIcon("show.png"))
        quit_action = QAction("Exit", self)
        quit_action.setIcon(QIcon("quit.png"))
        hide_action = QAction("Hide", self)
        hide_action.setIcon(QIcon("hide.png"))
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(app.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.show()
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Check Server",
            "Check Server was minimized to Tray",
            QSystemTrayIcon.Information,
            600
        )

    def updateUI(self):
        if self.thread_list != []:
            self.stopThreads()
        self.serversList = self.getAllServers()
        self.string_list = []
        for server in self.serversList:
            widgets_string = {'green': QPushButton(),
                              'red': QPushButton(),
                              'label': QLabel(server['name_server'])
                              }
            self.string_list.append(widgets_string)
        print(self.string_list[0]['label'])
        desktop = QApplication.desktop()
        self.table_widgets.setRowCount(len(self.serversList))
        self.table_widgets.setColumnCount(3)
        for i, server in enumerate(self.serversList):
            print(i, server)
            self.table_widgets.setCellWidget(i, 0, self.string_list[i]['label'])
            self.table_widgets.setCellWidget(i, 1, self.string_list[i]['green'])
            self.table_widgets.setCellWidget(i, 2, self.string_list[i]['red'])
        width_coordinate = desktop.width() - 350
        height_coordinate = desktop.height() - 200
        self.setGeometry(width_coordinate,
                         height_coordinate,
                         width_coordinate + 310,
                         (len(self.serversList) * 30) + 55)
        self.table_widgets.setFixedHeight((len(self.serversList) * 30)+25)
        self.main_lay = QVBoxLayout()
        self.main_lay.addWidget(self.table_widgets)
        self.ui.horizontalLayoutWidget.hide()
        self.ui.centralwidget.setLayout(self.main_lay)
        self.table_widgets.repaint()
        self.menu()

        self.runThreads()
#        print(self.serversList)

    def runThreads(self):

        self.class_check = []
        for i in range(len(self.serversList)):
            self.thread_list.append(QThread())
        for i in range(len(self.serversList)):
            self.class_check.append(checkThread(self, i))
        for i in range(len(self.serversList)):
            self.class_check[i].moveToThread(self.thread_list[i])
            self.class_check[i].warn_signal.connect(self.reciev_warn_signal)
            self.thread_list[i].started.connect(self.class_check[i].checkSite)
            self.thread_list[i].start()

    @pyqtSlot(object)
    def reciev_warn_signal(self, info_object):
        if self.isHidden() or self.isMinimized():
            self.tray_icon.showMessage(
                "WARN!",
                info_object[0]+" have problem: " + info_object[1],
                QSystemTrayIcon.Information,
                2000
            )

    def stopThreads(self):
        for thread in self.thread_list:
            thread.exit(0)


    def menu(self):
        self.hideAction = QAction("Hide")
        self.ui.actionConfig.setIcon(QIcon("config.png"))
        self.hideAction.setIcon(QIcon("hide.png"))
        self.ui.actionQuit.setIcon(QIcon("quit.png"))
        self.ui.actionConfig.triggered.connect(self.openConfigMenu)
        self.ui.actionQuit.triggered.connect(app.exit)
        self.ui.menuMenu.addSeparator()

        self.ui.menuMenu.addAction(self.hideAction)
        self.hideAction.triggered.connect(self.hide_form)



    def hide_form(self):
        self.hide()
        print("hide")

    def openConfigMenu(self):
        self.menu_window = Config_window(self)
        self.menu_window.show()
        print("I'am config menu")

    def getAllServers(self):
        with open("servers.json") as f:
            json_string = f.read()
        serversList = json.loads(json_string)
        return serversList

class Config_window(QWidget):
    def __init__(self, parrent):
        super().__init__()
        self.parrent = parrent
        self.initUI()
        self.fillData()
    def fillData(self):
        for i, server in enumerate(self.parrent.serversList):
            self.table.setRowCount(len(self.parrent.serversList))
            self.table.setItem(i, 0, QTableWidgetItem(server['name_server']))
            self.table.setItem(i, 1, QTableWidgetItem(server['url_server']))
            self.table.setItem(i, 2, QTableWidgetItem(server['shift_server']))
            self.remove_btn = QPushButton("Del: " + str(i))
            self.remove_btn.setFixedWidth(50)
            self.remove_btn.setFixedHeight(25)
            self.remove_btn.clicked.connect(self.removeRow)
            self.table.setCellWidget(i, 3, self.remove_btn)
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
            self.table.repaint()

    def removeRow(self):
        sender_btn = self.sender()
        sender_string = sender_btn.text()
        #print("Hi:", sender_btn.text())
        str_num = int(sender_string.replace("Del: ", ''))
        print("Hi:", str(str_num))
        for i in range(self.table.rowCount()):
            if i == str_num:
                print (i, str_num, self.table.rowCount())
                #self.parrent.thread_list.pop(i)
                self.parrent.class_check[i].stopChek()
                self.parrent.class_check.pop(i)
                #self.parrent.string_list[i].pop(i)
                self.parrent.serversList.pop(i)
                #self.parrent.thread_list[i]
                #self.table.removeCellWidget(i,3)
                self.saveJsonToFile(self.parrent.serversList)

                self.table.removeRow(i)
                self.table.repaint()
                self.fillData()
                self.parrent.updateUI()

    def initUI(self):
        desktop = QApplication.desktop()
        # self.setGeometry(100,100,210,100)
        width_coordinate = desktop.width() - 350
        height_coordinate = desktop.height() - 420

        self.setGeometry(width_coordinate,
                         height_coordinate,
                         350,
                         420)
        #self.setFixedWidth(350)
        #self.setFixedHeight(400)
        self.table = QTableWidget()
        #self.table.acti
        self.table.setRowCount(25)
        self.table.setColumnCount(4)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(["Name", "URL", "Shift(sec)"])

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_config)

        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.clicked.connect(self.close)
        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedWidth(30)
        self.plus_btn.clicked.connect(self.addRow)

        self.button_lay = QHBoxLayout()
        self.button_lay.addWidget(self.plus_btn)
        self.button_lay.addSpacing(50)
        self.button_lay.addWidget(self.cancel_btn)
        self.button_lay.addWidget(self.save_btn)

        self.main_lay = QVBoxLayout()
        self.main_lay.addWidget(self.table)
        self.main_lay.addLayout(self.button_lay)
        self.setLayout(self.main_lay)
    def save_config(self):
        clean_list = []
        for row_num in range(self.table.rowCount()):
            if self.table.item(row_num,0) != None and\
                    self.table.item(row_num,0).text() != "":
                name = self.table.item(row_num, 0).text()
                if self.table.item(row_num,1) != None and\
                    self.table.item(row_num,1).text() != "":
                    url = self.table.item(row_num,1).text()
                    shift = self.table.item(row_num, 2).text()
                    server_dict = {'name_server':name,
                                   'url_server':url,
                                   'id_server': '0',
                                   'shift_server': shift}

                    clean_list.append(server_dict)

                else:
                    self.table.item(row_num, 1).setBackground(QColor(200, 50, 50, 200))
            else:
                #self.table.setItem(row_num, 0, QTableWidgetItem("Required"))
                self.table.item(row_num,0).setBackground(QColor(200,50,50,200))

        if clean_list != []:
            self.saveJsonToFile(clean_list)
            self.parrent.updateUI()
        self.close()

    def saveJsonToFile(self, list):
        json_string = json.dumps(list)
        with open("servers.json", "w") as f:
            f.write(json_string)
        self.parrent.updateUI()

        #self.close()
    def addRow(self):
        print("add Row")
        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount()-1, 0, QTableWidgetItem("Server "+str(self.table.rowCount())))
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(""))
        self.table.setItem(self.table.rowCount() - 1, 2, QTableWidgetItem(""))


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("Server checker")
    app.setApplicationDisplayName("Server checker")
    application = ChekMain()
    sys.exit(app.exec_())
