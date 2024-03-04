import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon, QPixmap
from SQLaccess import *


qtCreatorFile = "milestone1UI.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class milestone1(QMainWindow):
    def __init__(self):
        super(milestone1, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadStateList()
        self.ui.stateList.currentTextChanged.connect(self.stateChange)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChange)
    
    def loadStateList(self):
        try:
            results = list_states()
            for row in results:
                self.ui.stateList.addItem(row[0])
        except Exception as e:
            print(f'query failed: {e}')
        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()
        
    def setupBusinessTable(self, results):
        style = "::section {background-color: #f3f3f3; }"
        self.ui.businessTable.horizontalHeader().setStyleSheet(style)
        self.ui.businessTable.setColumnCount(len(results[0]))
        self.ui.businessTable.setRowCount(len(results))
        self.ui.businessTable.setHorizontalHeaderLabels(['Business Name', 'City', 'State'])
        self.ui.businessTable.resizeColumnsToContents()
        self.ui.businessTable.setColumnWidth(0, 300)
        self.ui.businessTable.setColumnWidth(1, 100)
        self.ui.businessTable.setColumnWidth(2, 50)
        for currentRowCount, row in enumerate(results):
            for colCount, item in enumerate(row):
                self.ui.businessTable.setItem(currentRowCount, colCount, QTableWidgetItem(str(item)))

    def stateChange(self):
        self.ui.cityList.clear()
        state = self.ui.stateList.currentText()
        if(self.ui.stateList.currentIndex() >= 0):
            try:
                resultscities = list_cities(state)
                for row in resultscities:
                    self.ui.cityList.addItem(row[0])
            except Exception as e:
                print(f'query failed: {e}')
            for i in reversed(range(self.ui.businessTable.rowCount())):
                self.ui.businessTable.removeRow(i)
            try:
                results = list_businesses_state(state)
                self.setupBusinessTable(results)
            except Exception as e:
                print(f'query failed: {e}')

    def cityChange(self):
       if self.ui.stateList.currentIndex() >= 0 and len(self.ui.cityList.selectedItems()) > 0:
        try:
            state = self.ui.stateList.currentText()
            cityItem = self.ui.cityList.selectedItems()[0]
            city = cityItem.text() if cityItem else None
            if city:
                # print(f"Fetching businessesfor {city}, {state}")
                for i in reversed(range(self.ui.businessTable.rowCount())):
                    self.ui.businessTable.removeRow(i)
                results = list_businesses_state_city(city, state)
                # print(f"Results: {results}")
                if results:
                    self.setupBusinessTable(results)
                else:
                    print("No results found.")
            else:
                print("No city selected.")
        except Exception as e:
            print(f'Query failed: {e}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone1()
    window.show()
    sys.exit(app.exec_())
