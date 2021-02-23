import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from node import Node
import numpy as np
import collections
kivy.require('2.0.0')


class NodeLabel(Label):
    pass

class AppGraph(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.spacing = (20,20)
        self.padding = [50, 10, 50, 10]
        self.node_data = dict()

        self.add_widget(Label(text="Application Graph Editor", halign='center', font_size='30'))
        self.blank = Label(size_hint_y=0.5)
        self.add_widget(self.blank)

        self.inputs_num = TextInput(text="Amount of Nodes")
        self.add_widget(self.inputs_num)
        self.submit_amount = Button(text="Submit")
        self.add_widget(self.submit_amount)
        self.add_widget(Label(size_hint_y=0.1))
        self.add_widget(Label(size_hint_y=0.1))
        self.submit_amount.bind(on_press=self.add_node_editing)

    def add_node_editing(self, instance):
        self.cols = 3
        self.remove_widget(self.blank)
        self.remove_widget(self.inputs_num)
        self.remove_widget(self.submit_amount)
        self.add_widget(Label(text="#"))
        self.add_widget(Label(text="Weight"))
        self.add_widget(Label(text="Directs to nodes"))
        self.inputs_num = int(self.inputs_num.text)
        for i in range(1, self.inputs_num + 1):
            self.add_widget(Label(text=f"{i}"))

            weight = TextInput()
            directions = TextInput()
            self.add_widget(weight)
            self.add_widget(directions)
            self.node_data[i] = [i, weight, directions]

        self.matrix = np.zeros((self.inputs_num + 1, self.inputs_num + 1))
        print(self.matrix)
        self.add_widget((Label()))
        self.add_widget((Label()))
        self.gen_button = Button(text="Generate")
        self.add_widget(self.gen_button)
        self.gen_button.bind(on_press=self.fill_matrix)

    def fill_matrix(self, instance):
        print("Generate app grph")
        for i in range(1, self.inputs_num + 1):
            #number = self.node_data[i][0]
            weight = int(self.node_data[i][1].text.strip())
            self.matrix[i][i] = weight
            if self.node_data[i][2].text != '':
                directions = list(map(int, self.node_data[i][2].text.strip().split(' ')))
                for node in directions:
                    if 1 <= node <= self.inputs_num and node!=i:
                        self.matrix[i][node] = 1
            #print(f"{number}: {weight} {directions}")
        print(self.matrix)

        depths = []
        for i in range(1, self.inputs_num + 1):
            depths.append(self.find_depth(i))
            print(f"Node[{i}], Depth - {depths[i-1]}")

        self.draw_graph(depths)

    def draw_graph(self, depths):
        self.clear_widgets()
        max_depth = max(depths)
        c = collections.Counter(depths)
        graph_width = c.most_common(1)[0][1]

        self.cols = graph_width
        print("C",c.most_common(1)[0][1])
        print(c)
        print('max depth', max_depth)
        #print("max drw data", max(drawing_data[1]))

        for i in range(max_depth):
            row = []
            y = 0
            for j in range(1, self.inputs_num + 1):
                if depths[j-1] == max_depth:
                    row.append(j)
            print("Row: ", row)
            half_empty = (graph_width - len(row)) / 2
            for z in range(graph_width):
                #print("z, he, gw-he", z, half_empty,graph_width-half_empty)
                if half_empty <= z < graph_width-half_empty:
                    self.add_widget(NodeLabel(text=str(row[y])))
                    y += 1
                else:
                    self.add_widget(Label())

            max_depth -= 1

    def find_depth(self, node, bad_boys=None):
        if isinstance(node, int):
            if not bad_boys:
                bad_boys = []
                bad_boys.append(node)
            elif node in bad_boys:
                print("Warning! Cyclic Graph! ", node)
                return 0
            else:
                bad_boys.append(node)
                #print("Whatcha gonna do when they come for you? ", bad_boys)
            matched = []
            bb_temp = tuple(bad_boys)
            for row_elem in range(1, self.inputs_num + 1):
                bad_boys = [x for x in bb_temp]
                if self.matrix[node][row_elem] and node!=row_elem:

                    matched.append(self.find_depth(row_elem, bad_boys) + 1)
            if not matched:
                return 1
            else:
                print("Matched depths: ",matched)
                return max(matched)
        else:
            print("Wrong node number")
            return False

class SystGraph(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = (0,20)
        self.lab = Label(text="TEST Syst GRAPH")
        self.add_widget(self.lab)


class MainMenu(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = (0,5)
        self.padding = [200,100,200,100]

        self.app_graph_button = Button(text="New Application Graph")
        self.add_widget(self.app_graph_button)
        self.app_graph_button.bind(on_press=self.show_app_graph_screen)

        self.syst_graph_button = Button(text="New System Graph")
        self.add_widget(self.syst_graph_button)
        self.syst_graph_button.bind(on_press=self.show_syst_graph_screen)

        self.exit_button = Button(text="Exit")
        self.add_widget(self.exit_button)
        self.exit_button.bind(on_press=self.exit)

    def show_app_graph_screen(self, instance):
        designer_app.screen_manager.current = "AppGraph"

    def show_syst_graph_screen(self, instance):
        designer_app.screen_manager.current = "SystGraph"

    def exit(self, instance):
        designer_app.get_running_app().stop()
        Window.close()



class DesignerApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        self.main_menu = MainMenu()
        screen = Screen(name="MainMenu")
        screen.add_widget(self.main_menu)
        self.screen_manager.add_widget(screen)

        self.app_graph = AppGraph()
        screen = Screen(name="AppGraph")
        screen.add_widget(self.app_graph)
        self.screen_manager.add_widget(screen)

        self.syst_graph = SystGraph()
        screen = Screen(name="SystGraph")
        screen.add_widget(self.syst_graph)
        self.screen_manager.add_widget(screen)

        return self.screen_manager


if __name__ == '__main__':
    designer_app = DesignerApp()
    designer_app.run()
