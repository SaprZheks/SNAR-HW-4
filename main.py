import pandas as pd
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import numpy as np

d = {}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame()
        self.geometry("1000x600")
        self.resizable(0, 0)

        self.lb_sep = tk.Label(self, text="Разделитель csv:")
        self.lb_sep.place(rely=0.02, relx=0.05)

        sep = ["  ;", "  ,", "  |"]
        self.menu_choose_sep = ttk.Combobox(self, values=sep, state="readonly")
        self.menu_choose_sep.place(rely=0.02, relx=0.15)
        self.menu_choose_sep.set(sep[0])

        self.lb_beacon = tk.Label(self, text="Коорд. маяков:")
        self.lb_beacon.place(rely=0, relx=0.52)
        self.beacon_coords = ttk.Combobox(self, state="readonly")
        self.beacon_coords.place(width=100, rely=0.05, relx=0.52)

        self.lb_p = tk.Label(self, text="Псевдодальность:")
        self.lb_p.place(rely=0, relx=0.64)
        self.pseudorange = ttk.Combobox(self, state="readonly")
        self.pseudorange.place(width=100, rely=0.05, relx=0.64)

        self.lb_ri = tk.Label(self, text="Шум:")
        self.lb_ri.place(rely=0, relx=0.76)
        self.noise = ttk.Combobox(self, state="readonly")
        self.noise.place(width=100, rely=0.05, relx=0.76)

        self.lb_t = tk.Label(self, text="Погрешность\nчасов:")
        self.lb_t.place(rely=-0.005, relx=0.88)
        self.fault = tk.Entry(self, text="1")
        self.fault.place(width=100, rely=0.05, relx=0.88)

        self.btn_file = tk.Button(self, text="Выбрать файл",
                                  command=self.choose_file)
        self.btn_file.place(rely=0.02, relx=0.35)

        self.btn_create_table = tk.Button(self, text="Создать",
                                          command=self.create_table)
        self.btn_create_table.place(rely=0.6, relx=0.85)

        frame1 = tk.LabelFrame(self, text="Ваша табличка")
        frame1.place(height=250, width=500, rely=0.1, relx=0.5)

        self.tv1 = ttk.Treeview(frame1)
        self.tv1.place(relheight=1, relwidth=1)

        treescrolly = tk.Scrollbar(frame1, orient="vertical",
                                   command=self.tv1.yview)
        treescrollx = tk.Scrollbar(frame1, orient="horizontal",
                                   command=self.tv1.xview)
        self.tv1.configure(xscrollcommand=treescrollx.set,
                           yscrollcommand=treescrolly.set)
        treescrollx.pack(side="bottom", fill="x")
        treescrolly.pack(side="right", fill="y")
        self.canv = tk.Canvas(self, width=500, height=500, bg="white")
        self.drawing()

    def drawing(self):
        self.canv.delete("all")
        self.canv.create_line(250, 500, 250, 0, width=2, arrow=tk.LAST)
        self.canv.create_line(0, 250, 500, 250, width=2, arrow=tk.LAST)
        for _ in range(0, 240, 22):
            self.canv.create_line(250 + _, 247, 250 + _, 253, width=2)
            self.canv.create_line(250 - _, 247, 250 - _, 253, width=2)
            self.canv.create_line(247, 250 + _, 253, 250 + _, width=2)
            self.canv.create_line(247, 250 - _, 253, 250 - _, width=2)
        self.canv.place(rely=0.1, relx=0)

    def choose_file(self):
        csvsep = self.menu_choose_sep.get()[2:]
        if csvsep:
            filetypes = (("Таблица с данными ", "*.csv"),)
            filename = fd.askopenfilename(title="Открыть файл", initialdir="/",
                                          filetypes=filetypes)
            self.df_raw = pd.read_csv(filename, sep=csvsep)
            headers = list(self.df_raw.columns)

            self.beacon_coords['values'] = headers
            self.beacon_coords.set(headers[0])
            self.pseudorange['values'] = headers
            self.pseudorange.set(headers[1])
            self.noise['values'] = headers
            self.noise.set(headers[2])

    def create_table(self):
        self.clear_table()
        d["Коорд. маяков"] = self.beacon_coords.get()
        d["Псевдодальность"] = self.pseudorange.get()
        d["Шум"] = self.noise.get()
        for i in d:
            self.df[i] = self.df_raw[d[i]]
        self.tv1["column"] = list(d.keys())
        self.tv1["show"] = "headings"
        for column in self.df.columns:
            self.tv1.heading(column, text=column)

        df_rows = self.df.to_numpy().tolist()
        for row in df_rows:
            self.tv1.insert("", "end",
                            values=row)
        self.drawing()
        self.draw_points(self.df["Коорд. маяков"].tolist())
        self.calc(self.df)

    def clear_table(self):
        self.tv1.delete(*self.tv1.get_children())
        return None

    def draw_points(self, points_raw):
        points = []
        for i in points_raw:
            x, y = map(float, i.replace("(", "").replace(")", "").split(","))
            points.append([x, y])

        max_scale = max(list(map(lambda point: max([abs(point[0]), abs(point[1])]), points)))
        self.k = 220 / max_scale

        self.canv.create_text(40, 20, text="Ц.Д.= " + str(max_scale / 10), justify=tk.CENTER, font="Verdana 10")
        for i in range(1, 11):
            self.canv.create_text(250 + 22 * i, 240, text=(int(max_scale / (10 / i))), justify=tk.CENTER,
                                  font="Verdana 6")
            self.canv.create_text(260, 250 - 22 * i, text=(int(max_scale / (10 / i))), justify=tk.CENTER,
                                  font="Verdana 6")
            self.canv.create_text(250 - 22 * i, 240, text=(-int(max_scale / (10 / i))), justify=tk.CENTER,
                                  font="Verdana 6")
            self.canv.create_text(262, 250 + 22 * i, text=(-int(max_scale / (10 / i))), justify=tk.CENTER,
                                  font="Verdana 6")

        for i in range(len(points)):
            x = 250 + points[i][0] * self.k
            y = 250 - points[i][1] * self.k
            ro = float(self.df["Псевдодальность"][i]) * self.k
            t_i = float(self.df["Шум"][i]) * self.k
            tau = float(self.fault.get()) * self.k

            self.canv.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')
            self.canv.create_text(x, y - 10, text=str(i + 1), justify=tk.CENTER, font="Verdana 10")
            self.canv.create_oval(x - ro, y - ro, x + ro, y + ro, width=tau + t_i, outline="orange")

    def calc(self, df_raw):
        df = pd.DataFrame({"x": [], "y": [], "r": [], "ro": []})
        for i in range(df_raw.shape[0]):
            x, y = map(float, df_raw["Коорд. маяков"][i].replace("(", "").replace(")", "").split(","))
            df.loc[i] = [x, y, df_raw["Шум"][i], df_raw["Псевдодальность"][i]]
        print(df)

        ro = np.array(df['ro'])
        x = np.array(df['x'])
        y = np.array(df['y'])
        r = np.array(df['ro'])
        x_0 = 0
        y_0 = 0
        f = f_i(x_0, y_0, x, y)
        H = np.full((len(ro), 3), 1.)
        for i in range(H.shape[0]):
            j = 0
            H[i, j] = df_dx(x_0, y_0, x[i], y[i])
            j = 1
            H[i, j] = df_dy(x_0, y_0, x[i], y[i])
        z = ro - f
        R = np.diag(r)
        X_ = np.dot(H.T, np.linalg.inv(R))
        X_ = np.dot(X_, H)
        X_ = np.linalg.inv(X_)
        X_ = np.dot(X_, H.T)
        X_ = np.dot(X_, np.linalg.inv(R))
        X_ = np.dot(X_, z)
        point = X_[:2]
        print(point)
        x, y = point[0] * self.k, point[1] * self.k
        self.canv.create_oval(250 + x - 8, 250 - y - 8, 250 + x + 8, 250 - y + 8, fill="red")


def f_i(x, y, x_i, y_i):
    return np.sqrt((x - x_i) ** 2 + (y - y_i) ** 2)


def df_dx(x_0, y_0, x_i, y_i):
    return (x_0 - x_i) / np.sqrt((x_0 - x_i) ** 2 + (y_0 - y_i) ** 2)


def df_dy(x_0, y_0, x_i, y_i):
    return (y_0 - y_i) / np.sqrt((x_0 - x_i) ** 2 + (y_0 - y_i) ** 2)


if __name__ == "__main__":
    app = App()
    app.mainloop()

