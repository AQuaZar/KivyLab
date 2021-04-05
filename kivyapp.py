import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Line, Ellipse, Color, Rectangle
from kivy.clock import Clock
import time
from kivy.lang import Builder
from node import Node
import numpy as np
import collections
kivy.require('2.0.0')


class NodeLabel(Label):
    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        self.index = number


    def get_pos(self):
        Clock.schedule_once(lambda *args: self.parent.draw_lines())
        print(self.center_x, self.center_y)

class AppGraph(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.spacing = (20,20)
        self.padding = [10, 100, 10, 100]
        self.is_cycle = False
        self.queue_3 = []
        self.queue_7 = []
        self.node_data = dict()
        self.is_drawn = False
        self.check_popup = Popup(title='Warning! Cycle detected!',
                      content=Label(text='Please enter correct data, graph has to be acyclic.'),
                      size_hint=(None, None), size=(400, 200))

        self.check_popup.bind(on_dismiss=self.draw_app_graph_menu)
        self.screen_title = Label(text="Application Graph Editor", halign='center', font_size='30')
        self.blank = Label()
        #self.add_widget(self.blank)
        self.menu_button = Button(text="Return to Menu")
        self.inputs_num_widget = TextInput(text="Amount of Nodes")
        self.inputs_num = 0
        self.submit_amount = Button(text="Submit")
        self.matrix_button = Button(text="Show matrix")
        self.submit_amount.bind(on_press=self.add_node_editing)
        self.menu_button.bind(on_press=self.show_main_menu_screen)
        Window.bind(on_resize=self.draw_lines)
        self.draw_app_graph_menu(instance=self)

    def draw_app_graph_menu(self, instance):
        self.clear_widgets()
        self.canvas.clear()
        self.cols = 2
        self.spacing = (20, 20)
        self.padding = [10, 100, 10, 100]
        self.add_widget(self.screen_title)
        self.add_widget(self.menu_button)
        self.add_widget(self.inputs_num_widget)
        self.add_widget(self.submit_amount)
        self.add_widget(Label(size_hint_y=0.1))


    def show_main_menu_screen(self, instance):
        designer_app.screen_manager.current = "MainMenu"

    def add_node_editing(self, instance):
        self.cols = 3
        self.spacing = (10, 10)
        self.padding = [10, 10, 10, 10]
        self.add_widget((Label()))
        self.remove_widget(self.blank)
        self.remove_widget(self.menu_button)
        self.remove_widget(self.inputs_num_widget)
        self.remove_widget(self.submit_amount)
        self.add_widget(Label(text="#"))
        self.add_widget(Label(text="Weight"))
        self.add_widget(Label(text="Directs to nodes"))
        self.inputs_num = int(self.inputs_num_widget.text)
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
        self.add_widget(self.menu_button)
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
                directions = self.node_data[i][2].text.strip().split(' ')
                for direction in directions:
                    direction = list(map(int,direction.split('-')))
                    if len(direction) == 2:
                        node, direction_weight = direction
                    elif len(direction) == 1:
                        node = direction[0]
                        direction_weight = 1
                    if 1 <= node <= self.inputs_num and node != i:
                        self.matrix[i][node] = direction_weight
                        if isinstance(self, SystGraph):
                            self.matrix[node][i] = direction_weight

            #print(f"{number}: {weight} {directions}")
        print(self.matrix)

        depths_amount = []
        max_upper_amount = 0

        upper_amount_dict = dict()
        crit_time_dict = dict()
        for i in range(1, self.inputs_num + 1):
            crit_amount, crit_time = self.find_depth(i, is_first=True)
            crit_time_dict[i] = crit_time
            print(f"Node[{i}], Depth - {crit_amount}, Time - {crit_time}")
            #depths_time.append(crit_time)
            depths_amount.append(crit_amount)
            if not isinstance(self, SystGraph) and not self.is_cycle:
                upper_crit_amount, upper_crit_time = self.find_upper_depth(i, is_first=True)
                if upper_crit_amount > max_upper_amount:
                    max_upper_amount = upper_crit_amount
                print(f"Node[{i}], Upper Depth - {upper_crit_amount}, Upper Time - {upper_crit_time}")
                upper_amount_dict[i] = (upper_crit_amount, self.get_node_connectivity(i))
                print(f"Node[{i}], Connectivity {self.get_node_connectivity(i)}")


        if not isinstance(self, SystGraph) and not self.is_cycle:
            temp_sort = sorted(upper_amount_dict.items(), key=lambda item: item[1][0])
            for i in range(max_upper_amount + 1):
                same_amount = [x for x in temp_sort if x[1][0]==i]
                self.queue_7.append(sorted(same_amount, key=lambda item: item[1][1], reverse=True))
            print("tmp", temp_sort)

        self.queue_3 = sorted(crit_time_dict.items(), key=lambda item: item[1], reverse=True)
        print("Queue 3", self.queue_3)
        print("Queue 7", self.queue_7)

        self.matrix_popup = Popup(title='Matrix and Queues',
                                 content=Label(text=str(self.matrix)+f'\nQueue 3 {str(self.queue_3)}\nQueue 7 {self.queue_7}'),
                                 size_hint=(None, None), size=(self.width-30, 400))
        self.matrix_button.bind(on_press=self.matrix_popup.open)

        self.draw_graph(depths_amount)

    def draw_graph(self, depths):
        self.clear_widgets()
        max_depth = max(depths)
        c = collections.Counter(depths)
        graph_width = c.most_common(1)[0][1]

        self.cols = graph_width
        print("C1",c.most_common(1)[0][1])
        print("C0", c.most_common(1)[0][0])
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
                    self.add_widget(NodeLabel(row[y], text=str(row[y])))
                    y += 1
                else:
                    self.add_widget(Label())
            max_depth -= 1

        self.is_drawn = True
        self.add_widget(self.matrix_button)
        Clock.schedule_once(lambda *args: list(filter(lambda x: isinstance(x, NodeLabel),self.children))[0].get_pos())

    def draw_lines(self, *args):
        if self.is_drawn:
            self.canvas.clear()
            
            for node_1 in self.children:
                if isinstance(node_1, NodeLabel):
                    for node_2 in self.children:
                        if isinstance(node_2, NodeLabel):
                            with self.canvas:
                                Label(text=str(node_2.index), x=node_2.center_x, y=node_2.center_y)
                            if node_1.index!=node_2.index \
                                and self.matrix[node_1.index, node_2.index]:
                                with self.canvas:
                                    Color(1, 0.9, 0.2, 0.5)
                                    middle_x, middle_y = find_line_fraction_coords(node_1.center_x, node_1.center_y,
                                                                                   node_2.center_x, node_2.center_y,
                                                                                   1)
                                    tail_x, tail_y = find_line_fraction_coords(node_1.center_x, node_1.center_y,
                                                                                   node_2.center_x, node_2.center_y,
                                                                                   2)
                                    half_tail_x, half_tail_y = find_line_fraction_coords(node_1.center_x, node_1.center_y,
                                                                               node_2.center_x, node_2.center_y,
                                                                               3)
                                    if node_1.center_x == node_2.center_x:
                                        Line(bezier=(node_1.center_x,
                                                     node_1.center_y,
                                                     middle_x + 100,
                                                     middle_y,
                                                     node_2.center_x,
                                                     node_2.center_y),
                                             width=3)
                                        if not isinstance(self, SystGraph):
                                            Color(1, 0.1, 0.1, 0.9)
                                            Line(bezier=(tail_x + 40,
                                                         tail_y,
                                                         half_tail_x + 30,
                                                         half_tail_y,
                                                         node_2.center_x,
                                                         node_2.center_y),
                                                 width=6)
                                    elif node_1.center_y == node_2.center_y:
                                        Line(bezier=(node_1.center_x,
                                                     node_1.center_y,
                                                     middle_x,
                                                     middle_y + 100,
                                                     node_2.center_x,
                                                     node_2.center_y),
                                             width=3)
                                        if not isinstance(self, SystGraph):
                                            Color(1, 0.1, 0.1, 0.9)
                                            Line(bezier=(tail_x,
                                                         tail_y + 40,
                                                         half_tail_x,
                                                         half_tail_y + 30,
                                                         node_2.center_x,
                                                         node_2.center_y),
                                                 width=3)
                                    else:
                                        Line(points=[node_1.center_x,
                                                     node_1.center_y,
                                                     node_2.center_x,
                                                     node_2.center_y],
                                             width=3)
                                        if not isinstance(self, SystGraph):
                                            Color(1, 0.1, 0.1, 0.9)
                                            Line(points=[half_tail_x,
                                                         half_tail_y,
                                                         node_2.center_x,
                                                         node_2.center_y],
                                                 width=6)
                                    Label(text=str(node_2.index), x=node_2.center_x, y=node_2.center_y)
                                    Label(text=str(node_1.index), x=node_1.center_x, y=node_1.center_y)
                                    Color(0.5, 0.5, 0.5, 0.9)
                                    Ellipse(pos=((node_1.center_x-min(self.size)*0.1/2),
                                                 (node_1.center_y-min(self.size)*0.1/2)),
                                            size=(min(self.size)*0.1, min(self.size)*0.1))
                                    Ellipse(pos=((node_2.center_x-min(self.size)*0.1/2),
                                                 (node_2.center_y-min(self.size)*0.1/2)),
                                            size=(min(self.size)*0.1, min(self.size)*0.1))
                                    Rectangle(pos=(self.matrix_button.x,self.matrix_button.y), size=(40,40), text="Sample")



    def find_depth(self, node, bad_boys=None, is_first=False):
        if isinstance(node, int):
            if not bad_boys:
                bad_boys = []
                bad_boys.append(node)
            elif node in bad_boys:
                if not isinstance(self, SystGraph):
                    self.check_popup.open()
                    self.is_cycle = True
                    print("Warning! Cyclic Graph! ", node)
                return 0, 0
            else:
                bad_boys.append(node)
            matched_time = []
            matched_amount = []
            if not isinstance(self, SystGraph):
                bb_temp = tuple(bad_boys)
            #good_boys = bad_boys
            for row_elem in range(1, self.inputs_num + 1):
                if not isinstance(self, SystGraph):
                    bad_boys = [x for x in bb_temp]
                if self.matrix[node][row_elem] and node!=row_elem:
                    crit_amount, crit_time = self.find_depth(row_elem, bad_boys)
                    matched_amount.append(crit_amount + 1)
                    matched_time.append(crit_time + self.matrix[node][node])
            if not (matched_time and matched_amount):
                return (1, self.matrix[node][node])
            else:
                print("BB", bad_boys)
                if is_first and len(bad_boys) < self.inputs_num and isinstance(self, SystGraph):
                    self.check_popup.open()
                #print("Matched depths: ",matched)
                return max(matched_amount), max(matched_time)
        else:
            print("Wrong node number")
            return False

    def find_upper_depth(self, node, is_first=False):
        if isinstance(node, int):
            matched_time = []
            matched_amount = []
            # good_boys = bad_boys
            for row_elem in range(1, self.inputs_num + 1):
                if self.matrix[row_elem][node] and node != row_elem:
                    crit_amount, crit_time = self.find_upper_depth(row_elem)
                    if is_first:
                        matched_amount.append(crit_amount + 1)
                        matched_time.append(crit_time)
                    else:
                        matched_amount.append(crit_amount + 1)
                        matched_time.append(crit_time + self.matrix[node][node])
            if not (matched_time and matched_amount):
                return (0, self.matrix[node][node])
            else:
                # print("Matched depths: ",matched)
                return max(matched_amount), max(matched_time)
        else:
            print("Wrong node number")
            return False

    def get_node_connectivity(self, node):
        connectivity = 0
        for i in range(1,self.inputs_num + 1):
            if i != node:
                if self.matrix[node][i]:
                    connectivity += 1
                if self.matrix[i][node]:
                    connectivity += 1
        return connectivity


class SystGraph(AppGraph):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_title.text = "System Graph Editor"
        self.check_popup = Popup(title='Warning! Graph must be fully connected!',
                                 content=Label(text='Please enter correct data, each node must have path to another.'),
                                 size_hint=(None, None), size=(500, 200))
        self.check_popup.bind(on_dismiss=self.draw_app_graph_menu)


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


def find_line_fraction_coords(x1,y1,x2,y2,n):
    if n != 0:
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        n -= 1
        return find_line_fraction_coords(x,y,x2,y2,n)
    else:
        return x1, y1


if __name__ == '__main__':
    designer_app = DesignerApp()
    designer_app.run()
