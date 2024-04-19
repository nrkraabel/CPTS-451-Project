
import threading
import traceback
from SQLaccess import *
import sys
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5 import uic
from typing import Any

qtCreatorFile = Path("milestone3UI.ui")
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class myApp(QMainWindow):
    def __init__(self):
        super(myApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.init_states()
        self.ui.state_combo.currentTextChanged.connect(self.state_changed)
        self.ui.city_list.currentItemChanged.connect(self.city_changed)
        self.ui.zip_list.currentItemChanged.connect(self.zip_changed)
        self.ui.category_list.currentItemChanged.connect(self.category_changed)
        self.ui.refresh_button.clicked.connect(self.update_successful_popular_expensive)
        self.ui.zipstatistics_categories.horizontalHeader().setStretchLastSection(True)

        self.business_columns = [
            ("b.name", "Name"),
            ("b.address", "Address"),
            ("b.city", "City"),
            ("b.review_rating", "Review Rating"),
            ("b.num_checkins", "Checkin Count"),
            ("b.categoryName", "Catagory")
        ]

    def error_box(self, message: str, title: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def init_states(self):
        try:
            state_tuples = list_states()
            state_strings = [state[0] for state in state_tuples]
            self.ui.state_combo.addItems(state_strings)
        except Exception as e:
            print("Error loading states:", str(e))
            self.error_box("Unable to load states from database!", "Database Error")

    def state_changed(self):
        self.ui.city_list.clear()
        selected_state = self.ui.state_combo.currentText()
        try:
            city_tuples = list_cities(selected_state)
            city_strings = [city[0] for city in city_tuples]
            self.ui.city_list.addItems(city_strings)
        except Exception as e:
            print("Error loading cities:", str(e))
            self.error_box("Unable to load cities from database!", "Database Error")

    def city_changed(self):
        self.ui.zip_list.clear()
        try:
            selected_state = self.ui.state_combo.currentText()
            selected_city = self.ui.city_list.currentItem().text()
            zip_tuples = list_zipcodes(selected_city, selected_state)
            zip_strings = [zip[0] for zip in zip_tuples]
            self.ui.zip_list.addItems(zip_strings)
        except Exception as e:
            print("Error loading zip codes:", str(e))
            self.error_box("Unable to load zip codes from database!", "Database Error")

    def zip_changed(self):
        self.ui.category_list.clear()
        self.clearTable(self.ui.zipstatistics_categories)
        self.clearTable(self.ui.business_table)
        self.ui.refresh_button.setEnabled(False)

        currentItem = self.ui.zip_list.currentItem()
        if currentItem is not None:
            selected_zip = currentItem.text()
            self.ui.refresh_button.setEnabled(True)
            try:
                category_tuples = list_categories(selected_zip)
                category_strings = [category[0] for category in category_tuples]
                self.ui.category_list.addItems(category_strings)
                
                basic_stats, categories = get_zipcode_details(selected_zip)
                if basic_stats:
                    self.ui.zipstatistics_population.setText(str(basic_stats[0]))  # Population
                    self.ui.zipstatistics_income.setText(str(basic_stats[1]))  # Average income
                    self.ui.zipstatistics_businesses.setText(str(basic_stats[2]))  # Total businesses
                else:
                    self.ui.zipstatistics_population.setText("N/A")
                    self.ui.zipstatistics_income.setText("N/A")
                    self.ui.zipstatistics_businesses.setText("N/A")

                self.ui.zipstatistics_categories.setRowCount(len(categories))
                self.ui.zipstatistics_categories.setColumnCount(2)  
                self.ui.zipstatistics_categories.setHorizontalHeaderLabels(["Category", "Count"])
                self.ui.zipstatistics_categories.verticalHeader().setVisible(False)

                for i, (category, count) in enumerate(categories):
                    self.ui.zipstatistics_categories.setItem(i, 0, QTableWidgetItem(category))
                    self.ui.zipstatistics_categories.setItem(i, 1, QTableWidgetItem(str(count)))

            except Exception as e:
                print("Error loading categories or statistics:", str(e))
                self.error_box("Unable to load data from database!", "Database Error")
        else:
            # clearing things 
            self.ui.zipstatistics_population.clear()
            self.ui.zipstatistics_income.clear()
            self.ui.zipstatistics_businesses.clear()
            self.clearTable(self.ui.zipstatistics_categories)


    def category_changed(self):
        self.clearTable(self.ui.business_table) 
        selected_state = self.ui.state_combo.currentText()
        selected_city = self.ui.city_list.currentItem().text()
        selected_zip = self.ui.zip_list.currentItem().text() if self.ui.zip_list.currentItem() else None
        selected_category = self.ui.category_list.currentItem().text() if self.ui.category_list.currentItem() else None
        print(selected_state, selected_city, selected_zip, selected_category)

        try:
            business_data = list_businesses_filtered(selected_state, selected_city, selected_zip, selected_category)  
            self.updateTable(self.ui.business_table, business_data, [col[1] for col in self.business_columns])
        except Exception as e:
            print("Error loading businesses:", str(e))
            self.error_box("Unable to load businesses from database!", "Database Error")


    def clearTable(self, table: QTableWidget) -> None:
        table.clearContents()
        table.setRowCount(0)
        table.setColumnCount(0)

    def update_successful_popular_expensive(self):
        selected_zip = self.ui.zip_list.currentItem().text() if self.ui.zip_list.currentItem() else None
        if selected_zip:
            try:
                popular_businesses = get_popular_businesses(selected_zip)
                successful_businesses = get_successful_businesses(selected_zip)
                expensive_businesses = get_expensive_businesses(selected_zip)

                print("Popular:", popular_businesses)
                print("Successful:", successful_businesses)
                print("Expensive:", expensive_businesses)

                self.updateTable(self.ui.popular_table, popular_businesses, ["Name", "Address", "City", "State", "Zipcode", "Category"])
                self.updateTable(self.ui.successful_table, successful_businesses, ["Name", "Address", "City", "State", "Zipcode", "Category"])
                self.updateTable(self.ui.expensive_table, expensive_businesses, ["Name", "Address", "City", "State", "Zipcode", "Category"])
            except Exception as e:
                print("Error updating tables:", str(e))
                self.error_box("Unable to update tables with business data!", "Database Error")
        else:
            # Clear tables
            self.updateTable(self.ui.popular_table, [], ["Name", "Address", "City", "State", "Zipcode", "Category"])
            self.updateTable(self.ui.successful_table, [], ["Name", "Address", "City", "State", "Zipcode", "Category"])
            self.updateTable(self.ui.expensive_table, [], ["Name", "Address", "City", "State", "Zipcode", "Category"])

    def updateTable(self, table: QTableWidget, business_tuples, headers):
        if not business_tuples: 
            table.clearContents()
            table.setRowCount(1) 
            table.setColumnCount(1) 
            table.setHorizontalHeaderLabels(["Message"])
            no_data_item = QTableWidgetItem("No data available")
            no_data_item.setTextAlignment(Qt.AlignCenter)  
            table.setItem(0, 0, no_data_item)
            table.setSpan(0, 0, 1, len(headers)) 
        else:
            table.setRowCount(len(business_tuples))
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            for row, business in enumerate(business_tuples):
                for col, item in enumerate(business):
                    table.setItem(row, col, QTableWidgetItem(str(item)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myApp() 
    window.show()
    sys.exit(app.exec_())
