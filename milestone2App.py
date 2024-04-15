import tkinter as tk
from tkinter import ttk
import threading
from SQLaccess import *

class YelpDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yelp Business Data Viewer")
        self.geometry("1200x600")
        self.metric_var = tk.StringVar(value="none")
        self.create_widgets()
        self.layout_widgets()

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TLabel', background='#5e0000', foreground='white')
        self.style.configure('TFrame', background='#5e0000')
        self.style.configure('Treeview', background='#d3d3d3', foreground='black', rowheight=25)
        self.style.map('Treeview', background=[('selected', '#8e9598')])

        self.search_frame = tk.Frame(self, bg='#5e0000')
        self.result_frame = tk.Frame(self, bg='#5e0000')

        self.state_label = ttk.Label(self.search_frame, text="Select State:")
        self.state_var = tk.StringVar()
        self.state_dropdown = ttk.Combobox(self.search_frame, textvariable=self.state_var, state="readonly")

        self.city_label = ttk.Label(self.search_frame, text="Select City:")
        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(self.search_frame, textvariable=self.city_var, state="readonly")

        self.zipcode_label = ttk.Label(self.search_frame, text="Select Zipcode:")
        self.zipcode_var = tk.StringVar()
        self.zipcode_dropdown = ttk.Combobox(self.search_frame, textvariable=self.zipcode_var, state="readonly")

        self.category_label = ttk.Label(self.search_frame, text="Categories:")
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.search_frame, textvariable=self.category_var, state="readonly")

        self.setup_metric_radio_buttons()

        # Loading label (hidden by default)
        self.loading_label = ttk.Label(self.search_frame, text="Loading...", foreground="yellow")


        self.business_list = ttk.Treeview(self.result_frame, columns=('Name', 'Address', 'City', 'State', 'Zipcode', 'Category'), show='headings')
        self.business_list.heading('Name', text='Business Name')
        self.business_list.heading('Address', text='Address')
        self.business_list.heading('City', text='City')
        self.business_list.heading('State', text='State')
        self.business_list.heading('Zipcode', text='Zipcode')
        self.business_list.heading('Category',text='Category')
        for col in self.business_list['columns']:
            self.business_list.column(col, anchor="center", width=120)
        self.business_list.column('Address', width=180)

        self.category_dropdown.bind('<<ComboboxSelected>>', self.update_business_list)

        self.init_states()


    def setup_metric_radio_buttons(self):
        metrics_frame = ttk.Frame(self.search_frame)
        metrics_frame.pack(side=tk.BOTTOM, pady=2)

        ttk.Radiobutton(metrics_frame, text="Popular", variable=self.metric_var, value="popular", command=self.apply_metrics).pack(side=tk.LEFT)
        ttk.Radiobutton(metrics_frame, text="Successful", variable=self.metric_var, value="successful", command=self.apply_metrics).pack(side=tk.LEFT)
        ttk.Radiobutton(metrics_frame, text="Expensive", variable=self.metric_var, value="expensive", command=self.apply_metrics).pack(side=tk.LEFT)

    def layout_widgets(self):
        self.search_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=10, pady=10)
        self.result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.state_label.pack(pady=5)
        self.state_dropdown.pack(pady=5, fill=tk.X)
        self.city_label.pack(pady=5)
        self.city_dropdown.pack(pady=5, fill=tk.X)
        self.zipcode_label.pack(pady=5)
        self.zipcode_dropdown.pack(pady=5, fill=tk.X)
        self.category_label.pack(pady=5)
        self.category_dropdown.pack(pady=5, fill=tk.X)

        self.business_list.pack(fill=tk.BOTH, expand=True)

    def init_states(self):
        self.state_dropdown['values'] = [state[0] for state in list_states()]
        self.state_dropdown.bind('<<ComboboxSelected>>', self.update_cities)

    def update_cities(self, event=None):
        state = self.state_var.get()
        self.city_dropdown['values'] = [city[0] for city in list_cities(state)]
        self.city_dropdown.bind('<<ComboboxSelected>>', self.update_zipcodes)

    def update_zipcodes(self, event=None):
        city = self.city_var.get()
        state = self.state_var.get()
        self.zipcode_dropdown['values'] = [zipcode[0] for zipcode in list_zipcodes(city, state)]
        self.zipcode_dropdown.bind('<<ComboboxSelected>>', self.update_categories)

    def update_categories(self, event=None):
        zipcode = self.zipcode_var.get()
        self.category_dropdown['values'] = [category[0] for category in list_categories(zipcode)]
        self.category_dropdown.set('')

    def show_popular(self):
        for i in self.business_list.get_children():
            self.business_list.delete(i)
        for business in get_popular_businesses():
            self.business_list.insert('', 'end', values=business)

    def show_successful(self):
        for i in self.business_list.get_children():
            self.business_list.delete(i)
        for business in get_successful_businesses():
            self.business_list.insert('', 'end', values=business)

    def show_expensive(self):
        for i in self.business_list.get_children():
            self.business_list.delete(i)
        for business in get_expensive_businesses():
            self.business_list.insert('', 'end', values=business)

    
    def apply_metrics(self):
        self.loading_label.pack(side=tk.TOP, pady=5)
        self.update_idletasks()
        #I had to use threading to get the ui to work properly 
        thread = threading.Thread(target=self.fetch_and_display_metrics)
        thread.start()

    def fetch_and_display_metrics(self):

        selected_metric = self.metric_var.get()
        businesses = []
        if selected_metric == "popular":
            businesses = get_popular_businesses()
        elif selected_metric == "successful":
            businesses = get_successful_businesses()
        elif selected_metric == "expensive":
            businesses = get_expensive_businesses()

        self.after(0, self.update_business_list_ui, businesses)

    def update_business_list_ui(self, businesses):

        for i in self.business_list.get_children():
            self.business_list.delete(i)
        
        for business in businesses:
            self.business_list.insert('', 'end', values=business)

        self.loading_label.pack_forget()

        self.clear_dropdowns()

    def clear_dropdowns(self):
        self.state_var.set('')
        self.city_var.set('')
        self.zipcode_var.set('')
        self.category_var.set('')
        self.init_states()

    def update_business_list(self, event=None):
        state = self.state_var.get()
        city = self.city_var.get()
        zipcode = self.zipcode_var.get()
        category = self.category_var.get()
        self.business_list.delete(*self.business_list.get_children())
        for business in list_businesses_filtered(state, city, zipcode, category):
            self.business_list.insert('', 'end', values=business)

if __name__ == "__main__":
    app = YelpDataApp()
    app.mainloop()
