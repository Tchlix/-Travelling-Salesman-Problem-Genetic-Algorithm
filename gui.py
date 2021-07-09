import tkinter as tk
import numpy as np
from cities import *
from _thread import start_new_thread
from tsp_genetic import TSPGenetic
from tqdm import tqdm
from os.path import exists

class GUI(tk.Tk):
    def __init__(self, width, height):
        tk.Tk.__init__(self)
        self.title('Genetic')
        self.resizable(False, False)
        self.width = width
        self.height = height

        #DEFAULT VALUES
        self.iteration = 100
        self.population = 100
        self.elite = 10
        self.mutation = 0.01

        self.settings = Settings(self)
        self.settings_open = False
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(column=0, row=0, sticky = "nsew")
        self.canva = tk.Canvas(self.main_frame, bg="white", width = self.width, height = self.height)
        self.canva.pack()

        self.canva.bind("<Button-1>", self.__draw_point)
        self.canva.bind("<Button-2>", self.clear)
        self.bind("<r>", self.__generate_random)
        self.bind("<c>", self.__abort)
        self.bind("<space>", self.__calculate_tsp)
        self.bind("<Button-3>", self.__switch_frame)
        self.points = []
        self.thread_free = True
        self.abort = False

    def __abort(self, event=None):
        self.abort = True

    def __calculate_tsp(self, event=None):
        if self.thread_free and len(self.points) > 1 and not self.settings_open:
            self.thread_free = False
            self.settings.switch_state(False)
            start_new_thread(self.__thread_calculate_tsp, ())


    def __thread_calculate_tsp(self):
        print(f"Points:{len(self.points)} Population:{self.population} Elite:{self.elite} Mutation:{self.mutation}")
        lenghts = count_distances(self.points)
        tsp = TSPGenetic(np.array(lenghts), self.population, self.elite, self.mutation)
        pbar = tqdm(range(self.iteration))
        for i in pbar:
            if(self.abort):
                break;
            tsp.solve_genetic()
            order, distance = tsp.update_solution()
            pbar.set_postfix({'Distance': str(distance)})
            sorted_coordinates = []
            for x in order:
                sorted_coordinates.append(self.points[x])
            sorted_coordinates.append(self.points[order[0]])
            self.canva.delete("line")
            self.canva.create_line(sorted_coordinates, fill="red", tags = "line")
            self.canva.update()
        self.settings.switch_state(True)
        self.thread_free = True
        self.abort = False

    def __generate_random(self, event=None):
        if self.thread_free and not self.settings_open:
            new_points = generate_random_cities(5, (3, self.width), (3, self.height))
            self.points.extend(new_points)
            self.__draw_points(new_points)

    def read_points_from_file(self, path):
        new_points = read_cities_from_file(path)
        self.points.extend(new_points)
        self.__draw_points(new_points)

    def __draw_point(self, event):
        if self.thread_free:
            self.canva.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3, fill="black", tags = "point")
            self.points.append(((float)(event.x),(float)(event.y)))

    def clear(self, event=None):
        if self.thread_free:
          self.canva.delete("point","line")
          self.points.clear()

    def __draw_points(self, points):
        for point in points:
            self.canva.create_oval(point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3, fill="black", tags = "point")

    def __switch_frame(self, event=None):
        if self.settings_open:
            self.settings.switch_state(False)
            self.focus()
            self.main_frame.tkraise()
            self.settings_open = False
        else:
            if self.thread_free:
                self.settings.switch_state(True)
            self.settings.tkraise()
            self.settings_open = True

    def run(self):
        self.mainloop()

class Settings(tk.Frame):

    def __init__(self, parent:GUI):
        tk.Frame.__init__(self, parent, width=parent.width, height=parent.height)
        self.grid(column=0, row=0, sticky = "nsew")
        self.parent = parent
        title = tk.Label(self, text="Settings", font=("Courier", 44))
        title.pack(side="top", pady=10)

        self.Iteration = tk.IntVar(value = parent.iteration)
        self.Population = tk.IntVar(value = parent.population)
        self.Elite = tk.IntVar(value = parent.elite)
        self.Mutation = tk.DoubleVar(value = parent.mutation)
        self.GraphSource = tk.StringVar(value= '')

        tk.Label(self, text = 'Iteration',font=("Fixedsys", 25)).pack()
        self.e1 = tk.Entry(self, justify='center',font=("Fixedsys", 20), textvariable = self.Iteration)
        self.e1.pack()
        tk.Label(self, text = 'Population',font=("Fixedsys", 25)).pack()
        self.e2 = tk.Entry(self, justify='center',font=("Fixedsys", 20), textvariable = self.Population)
        self.e2.pack()

        tk.Label(self, text = 'Elite',font=("Fixedsys", 25)).pack()
        self.e3 = tk.Entry(self, justify='center',font=("Fixedsys", 20), textvariable = self.Elite)
        self.e3.pack()

        tk.Label(self, text = 'Mutation',font=("Fixedsys", 25)).pack()
        self.e4 = tk.Entry(self, justify='center',font=("Fixedsys", 20), textvariable = self.Mutation)
        self.e4.pack()

        tk.Label(self, text='Graph source (optional)', font=("Fixedsys", 25)).pack()
        self.e5 = tk.Entry(self, justify='center', font=("Fixedsys", 20), textvariable=self.GraphSource)
        self.e5.pack()

        self.save_button = tk.Button(self,justify='center',font=("Fixedsys", 20), text = "SAVE", command = self.__save)
        self.save_button.pack()

    def __save(self):
        if(self.Iteration.get() > 0 and self.Elite.get() > 0 and self.Population.get() > 0 and self.Mutation.get() > 0):
            if(self.Elite.get() < self.Population.get()):
                self.parent.iteration = self.Iteration.get()
                self.parent.population = self.Population.get()
                self.parent.elite = self.Elite.get()
                self.parent.mutation = self.Mutation.get()
                if self.GraphSource.get() != '' and exists(self.GraphSource.get()):
                    self.parent.clear()
                    self.parent.read_points_from_file(self.GraphSource.get())
            else:
                print("Number of elites must be smaller than population")
        else:
            print("Values must be higher than 0")

    def switch_state(self,enable):
        if enable:
            self.e1.config(state='normal')
            self.e2.config(state='normal')
            self.e3.config(state='normal')
            self.e4.config(state='normal')
            self.e5.config(state='normal')
            self.save_button.config(state='normal')
        else:
            self.e1.config(state='disabled')
            self.e2.config(state='disabled')
            self.e3.config(state='disabled')
            self.e4.config(state='disabled')
            self.e5.config(state='disabled')
            self.save_button.config(state='disabled')