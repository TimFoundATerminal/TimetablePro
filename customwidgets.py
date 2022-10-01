import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from typing import Generic, TypeVar, Dict, List, Optional
import datetime


W = TypeVar("W")
ID = TypeVar("ID")


def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func


def bind_tree(widget, event, callback, add='', funcids: List[W] = None) -> List[ID]:
    """Binds an event to a widget and all its descendants"""
    # starts a list of the function ids if one has not already been started
    if funcids is None:
        funcids = list()
    # when an event is binded to a widget it returns a function id
    funcids.append(widget.bind(event, callback, add))
    # fetches all of the values of the dictionary stored in the attribute children
    for child in widget.children.values():
        # recursion
        funcids = bind_tree(child, event, callback, add, funcids)
    # returns back down the stack
    return funcids


def unbind_tree(widget, event):
    """Unbinds an event from a widget and all its descendants"""
    widget.unbind_all(event)
    for child in widget.children.values():
        unbind_tree(child, event)


def menu_tree(widget, *commands, **kwargs):
    """Adds a pop-up menu to a widget and all its descendants"""
    MenuManager(widget, *commands, **kwargs)
    for child in widget.children.values():
        menu_tree(child, *commands, **kwargs)


def colour_tree(widget, colour, **kwargs):
    """Adds a pop-up menu to a widget and all its descendants"""
    widget.config(bg=colour, **kwargs)
    for child in widget.children.values():
        colour_tree(child, colour, **kwargs)


def reverse_map_dict(dic, value):
    for name, val in dic.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if val == value:
            return name


class AutoResizeText(tk.Frame):
    def __init__(self, master, width=0, height=0, family=None, size=None, *args, **kwargs):

        tk.Frame.__init__(self, master, width=width, height=height)
        self.pack_propagate(False)

        self._min_width = width
        self._min_height = height

        self._textarea = tk.Text(self, *args, **kwargs)
        self._textarea.pack(expand=True, fill='both')

        if family is not None and size is not None:
            self._font = tkfont.Font(family=family, size=size)
        else:
            self._font = tkfont.Font(family=self._textarea.cget("font"))

        self._textarea.config(font=self._font)

        # I want to insert a tag just in front of the class tag
        # It's not necessary to give to this tag extra priority including it at the beginning
        # For this reason I am making this search
        self._autoresize_text_tag = "autoresize_text_" + str(id(self))
        list_of_bind_tags = list(self._textarea.bindtags())
        list_of_bind_tags.insert(list_of_bind_tags.index('Text'), self._autoresize_text_tag)

        self._textarea.bindtags(tuple(list_of_bind_tags))
        self._textarea.bind_class(self._autoresize_text_tag, "<KeyPress>", self._on_keypress)

    def _on_keypress(self, event):
        self._textarea.focus_set()

        if event.keysym == 'BackSpace':
            self._textarea.delete("%s-1c" % "insert")
            new_text = self._textarea.get("1.0", "end")
        elif event.keysym == 'Delete':
            self._textarea.delete("%s" % "insert")
            new_text = self._textarea.get("1.0", "end")
        # We check whether it is a punctuation or normal key
        elif len(event.char) == 1:
            if event.keysym == 'Return':
                # In this situation ord(event.char)=13, which is the CARRIAGE RETURN character
                # We want instead the new line character with ASCII code 10
                new_char = '\n'
            else:
                new_char = event.char

            old_text = self._textarea.get("1.0", "end")
            new_text = self._insert_character_into_message(old_text, self._textarea.index("insert"), new_char)

        else:
            # If it is a special key, we continue the binding chain
            return

        # Tk Text widget always adds a newline at the end of a line
        # This last character is also important for the Text coordinate system
        new_text = new_text[:-1]

        self._fit_to_size_of_text(new_text)

        # Finally we insert the new character
        if event.keysym != 'BackSpace' and event.keysym != 'Delete':
            self._textarea.insert("insert", new_char)

        return "break"

    @staticmethod
    def _insert_character_into_message(message, coordinate, char):
        target_row, target_column = map(int, coordinate.split('.'))

        this_row = 1
        this_column = 0
        index = 0

        for ch in message:
            if this_row == target_row and this_column == target_column:
                message = message[:index] + char + message[index:]
                return message

            index += 1

            if ch == '\n':
                this_row += 1
                this_column = 0
            else:
                this_column += 1

    def _fit_to_size_of_text(self, text):
        number_of_lines = 0
        widget_width = 0

        for line in text.split("\n"):
            widget_width = max(widget_width, self._font.measure(line))
            number_of_lines += 1

        # We need to add this extra space to calculate the correct width
        widget_width += 2 * self._textarea['bd'] + 2 * self._textarea['padx'] + self._textarea['insertwidth']

        if widget_width < self._min_width:
            widget_width = self._min_width

        self._textarea.configure(height=number_of_lines)
        widget_height = max(self._textarea.winfo_reqheight(), self._min_height)

        self.config(width=widget_width, height=widget_height)

        # If we don't call update_idletasks, the window won't be resized before an insertion
        self.update_idletasks()

    @property
    def tag(self):
        return self._autoresize_text_tag

    def focus(self):
        self._textarea.focus()

    def bind_textarea(self, event, handler, add=None):
        self._textarea.bind(event, handler, add)

    def get(self, start, end=None):
        return self._textarea.get(start, end)

    def update_textarea(self, text):
        self._textarea.delete('1.0', 'end')
        self._fit_to_size_of_text(text)
        self._textarea.insert('1.0', text)


def hex2rgb(str_rgb):
    try:
        rgb = str_rgb[1:]

        if len(rgb) == 6:
            r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
        elif len(rgb) == 3:
            r, g, b = rgb[0] * 2, rgb[1] * 2, rgb[2] * 2
        else:
            raise ValueError()
    except ValueError:
        raise ValueError("Invalid value %r provided for rgb color." % str_rgb)

    return tuple(int(v, 16) for v in (r, g, b))


class PlaceholderState(object):
                __slots__ = 'normal_color', \
                            'normal_font', \
                            'placeholder_text', \
                            'placeholder_color', \
                            'placeholder_font', \
                            'contains_placeholder'


def add_placeholder_to(entry, placeholder, color="grey", font=None):
    normal_color = entry.cget("fg")
    normal_font = entry.cget("font")

    if font is None:
        font = normal_font

    state = PlaceholderState()
    state.normal_color = normal_color
    state.normal_font = normal_font
    state.placeholder_color = color
    state.placeholder_font = font
    state.placeholder_text = placeholder
    state.contains_placeholder = True

    def on_focusin(event, entry=entry, state=state):
        if state.contains_placeholder:
            entry.delete(0, "end")
            entry.config(fg=state.normal_color, font=state.normal_font)

            state.contains_placeholder = False

    def on_focusout(event, entry=entry, state=state):
        if entry.get() == '':
            entry.insert(0, state.placeholder_text)
            entry.config(fg=state.placeholder_color, font=state.placeholder_font)

            state.contains_placeholder = True

    entry.insert(0, placeholder)
    entry.config(fg=color, font=font)

    entry.bind('<FocusIn>', on_focusin, add="+")
    entry.bind('<FocusOut>', on_focusout, add="+")

    entry.__setattr__("placeholder_state", state)

    return state


class SearchBox(tk.Frame):
    def __init__(self, master, frame_background=None, entry_width=30, entry_font=None, entry_background="white", entry_highlightthickness=1, button_text="Search", button_ipadx=10, button_background="#009688", button_foreground="#000000", button_font=None, opacity=0.8, placeholder=None, placeholder_font=None, placeholder_color="grey", spacing=3, command=None):
        tk.Frame.__init__(self, master, bg=frame_background)

        self._command = command

        self.entry = tk.Entry(self, width=entry_width, background=entry_background, highlightcolor=button_background, highlightthickness=entry_highlightthickness)
        self.entry.pack(side="left", fill="both", ipady=1, padx=(0, spacing))

        if entry_font:
            self.entry.configure(font=entry_font)

        if placeholder:
            add_placeholder_to(self.entry, placeholder, color=placeholder_color, font=placeholder_font)

        self.entry.bind("<Escape>", lambda event: self.entry.nametowidget(".").focus())
        self.entry.bind("<Return>", self._on_execute_command)

        opacity = float(opacity)

        if button_background.startswith("#"):
            r, g, b = hex2rgb(button_background)
        else:
            # Color name
            r, g, b = master.winfo_rgb(button_background)

        r = int(opacity*r)
        g = int(opacity*g)
        b = int(opacity*b)

        if r <= 255 and g <= 255 and b <= 255:
            self._button_active_background = '#%02x%02x%02x' % (r, g, b)
        else:
            self._button_active_background = '#%04x%04x%04x' % (r, g, b)

        self._button_background = button_background

        self.button_label = tk.Label(self, text=button_text, background=button_background, foreground=button_foreground, font=button_font)
        if entry_font:
            self.button_label.configure(font=button_font)

        self.button_label.pack(side="left", fill="y", ipadx=button_ipadx)

        self.button_label.bind("<Enter>", self._state_active)
        self.button_label.bind("<Leave>", self._state_normal)

        self.button_label.bind("<ButtonRelease-1>", self._on_execute_command)

    def get_text(self):
        entry = self.entry
        if hasattr(entry, "placeholder_state"):
            if entry.placeholder_state.contains_placeholder:
                return ""
            else:
                return entry.get()
        else:
            return entry.get()

    def set_text(self, text):
        entry = self.entry
        if hasattr(entry, "placeholder_state"):
            entry.placeholder_state.contains_placeholder = False

        entry.delete(0, tk.END)
        entry.insert(0, text)

    def focus(self):
        self.entry.focus()

    def _on_execute_command(self, event):
        text = self.get_text()
        self._command(text)

    def _state_normal(self, event):
        self.button_label.configure(background=self._button_background)

    def _state_active(self, event):
        self.button_label.configure(background=self._button_active_background)


class CentreFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(9999, weight=1)
        self.grid_columnconfigure(9999, weight=1)


class CreateContainer(tk.Frame):
    def __init__(self, parent, grandparent, controller, pages=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.parent = parent
        self.grandparent = grandparent
        self.controller = controller
        self.page_id = 0
        self.frames = {}

        if pages is not None:
            for F in pages:
                self.add_page(F)
            self.show_frame(pages[0])

    def add_page(self, page):
        frame = page(self, self.grandparent, self.controller)
        self.frames[page] = frame
        frame.grid(row=0, column=0, stick="nsew")

    def add_init_page(self, page):
        self.page_id += 1
        page.grid(in_=self, row=0, column=0, stick="nsew")
        self.frames[self.page_id] = page
        return self.page_id

    def show_frame(self, name):
        frame = self.frames[name]
        try:
            frame.tkraise()
        except KeyError:
            raise KeyError("'{}' is not a page in this Window".format(frame))

    def show_init_frame(self, page):
        if page in self.frames.values():
            page.tkraise()
        else:
            raise KeyError("'{}' is not a page in this Window".format(page))


class FancyListbox(tk.Listbox):

    def __init__(self, parent, *args, **kwargs):
        tk.Listbox.__init__(self, parent, *args, **kwargs)

        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Delete", command=self.delete_selected)
        self.popup_menu.add_command(label="Select All", command=self.select_all)

        self.bind("<Button-3>", self.popup)  # Button-2 on Aqua

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def delete_selected(self):
        for i in self.curselection()[::-1]:
            self.delete(i)

    def select_all(self):
        self.selection_set(0, 'end')


class BottomBar(tk.Frame):
    def __init__(self, parent, font=None):
        super().__init__(parent, bg="white")
        self.grid_configure(sticky="ew")
        self.button_frame = tk.Frame(self, bg="white")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(9999, pad=5)
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.pack(side="right", fill="both", expand=True)
        self.button_id = 0
        self.buttons = {}
        self.gridded_buttons = []
        self.output_label = tk.Label(self, font=font, text="", fg="black")
        self.output_label.pack(side="left", pady=5, padx=10)

    def add_button(self, **options):
        self.button_id += 1
        self.buttons[self.button_id] = ttk.Button(self.button_frame, **options)
        self.buttons[self.button_id].grid(row=0, column=self.button_id, padx=3, pady=5)
        self.buttons[self.button_id].grid_remove()
        return self.button_id

    def show_button(self, button_id):
        if button_id not in self.buttons.keys() or button_id in self.gridded_buttons:
            return
        self.buttons[button_id].grid()
        self.gridded_buttons.append(button_id)

    def hide_button(self, button_id):
        if button_id not in self.buttons.keys() or button_id not in self.gridded_buttons:
            return
        self.buttons[button_id].grid_remove()
        self.gridded_buttons.remove(button_id)

    def hide_all_buttons(self):
        for button_id in self.gridded_buttons:
            self.buttons[button_id].grid_remove()
        self.gridded_buttons.clear()

    def configure_button(self, button_id, **options):
        if button_id not in self.buttons.keys():
            return
        self.buttons[button_id].config(**options)

    def configure_output(self, **options):
        self.output_label.config(**options)

    def clear_output(self):
        self.output_label.config(fg="black", text="")


class IndividualTableCell(tk.Frame):
    def __init__(self, parent, prd_id, subject="", teacher="", classroom="", bg="white", **kwargs):
        super().__init__(parent, borderwidth=1, relief="solid", bg=bg, **kwargs)
        self.prd_id = prd_id
        self.state = 0
        self.bg = bg
        self.grid_propagate(0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(9999, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(9999, weight=1)
        self.subject = tk.Label(self, text=subject, bg=bg)
        self.subject.grid(row=1, column=1)
        self.teacher = tk.Label(self, text=teacher, bg=bg)
        self.teacher.grid(row=1, column=2)
        self.classroom = tk.Label(self, text=classroom, bg=bg, width=9)
        self.classroom.grid(row=2, column=1, columnspan=2)

    def update_subject(self, text):
        self.subject.config(text=self.convert_nonetype(text))

    def update_teacher(self, text):
        self.teacher.config(text=self.convert_nonetype(text))

    def update_classroom(self, text):
        self.classroom.config(text=self.convert_nonetype(text))

    def update_column_width(self, width):
        self.classroom.config(width=width)

    def temporary_colour(self, colour):
        colour_tree(self, colour)

    def interphase_colour(self, colour=None):
        if colour is not None:
            self.bg = colour
        self.temporary_colour(self.bg)

    def clear_cell(self):
        self.subject.config(text="")
        self.teacher.config(text="")
        self.classroom.config(text="")

    @staticmethod
    def convert_nonetype(text):
        if text is None:
            return ""
        return text


class IndividualTable(tk.Frame):
    def __init__(self, parent, title_colour="grey", table_colour="#ffffff", active_colour="#008080"):
        super().__init__(parent, borderwidth=1, relief="solid")
        self.prd_id_map = {}
        self.selection = 0
        self.selected_tiles = []
        self.selection_cmds = []
        self.selected_tile, self.selected_prd_id = None, None
        self.bg, self.active_bg, self.heading_bg = table_colour, active_colour, title_colour
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.title_cell = IndividualTableCell(self,
                                              None,
                                              bg=title_colour,
                                              height=50,
                                              width=150)
        self.title_cell.grid(row=1, column=1, rowspan=2, columnspan=2, sticky="nsew")
        weekone = tk.Frame(self, borderwidth=1, relief="solid")
        weekone.grid(row=1, column=3, columnspan=5, sticky="nsew")
        tk.Label(weekone, bg=title_colour, text="Week 1").pack(expand=True, fill="both")
        weektwo = tk.Frame(self, borderwidth=1, relief="solid")
        weektwo.grid(row=1, column=8, columnspan=5, sticky="nsew")
        tk.Label(weektwo, bg=title_colour, text="Week 2").pack(expand=True, fill="both")
        for week in range(2):
            day = 1
            while day <= 5:
                day_frame = tk.Frame(self, borderwidth=1, relief="solid")
                tk.Label(day_frame, bg=title_colour, text=weekdays[day-1]).pack(expand=True, fill="both")
                day_frame.grid(row=2, column=(day + (5 * week) + 2), sticky="nsew")
                day += 1
        for period in range(3, 8):
            period_frame = tk.Frame(self, borderwidth=1, relief="solid")
            tk.Label(period_frame, bg=title_colour, text="Period "+str(period-2)).pack(expand=True, fill="both")
            period_frame.grid(column=1, columnspan=2, row=period, sticky="nsew")
        prd_id = 0
        for column in range(3, 13):
            for row in range(3, 8):
                prd_id += 1
                tile = IndividualTableCell(self, prd_id, bg=table_colour, height=50, width=75)
                self.prd_id_map[prd_id] = tile
                tile.grid(row=row, column=column, sticky="nsew")

    def enable_selection(self, tiles=None):
        self.selection = True
        if tiles is None:
            tiles = self.prd_id_map.values()
        self.add_tile_bind(tiles, "<Button-1>", self.select_tile)

    @staticmethod
    def add_tile_bind(tiles, event, command):
        if callable(command):
            for tile in tiles:
                bind_tree(tile, event, command)
        else:
            raise TypeError("'{}' is not a callable object".format(command))

    @staticmethod
    def remove_tile_bind(tiles, event):
        for tile in tiles:
            unbind_tree(tile, event)

    @staticmethod
    def get_parent(widget):
        while hasattr(widget, "prd_id") is False:
            widget = widget.master
        return widget

    def select_tile(self, event):
        tile = self.get_parent(event.widget)
        self.clear_selected_tile()
        self.selected_tile = tile
        self.selected_tile.interphase_colour(colour=self.active_bg)
        for cmd in self.selection_cmds:
            cmd()

    def clear_selected_tile(self):
        if self.selected_tile is not None:
            self.selected_tile.interphase_colour(colour=self.bg)

    def add_selection_command(self, command):
        if callable(command):
            self.selection_cmds.append(command)
        else:
            raise TypeError("'{}' is not a callable object".format(command))

    def add_selected_tiles(self, colour, prd_id):
        tile = self.prd_id_map[prd_id]
        self.selected_tiles.append(tile)
        tile.temporary_colour(colour)

    def clear_selected_tiles(self):
        for tile in self.selected_tiles:
            tile.interphase_colour()
        self.selected_tiles.clear()

    def get_cell_prd_id(self, prd_id):
        return self.prd_id_map[prd_id]

    def get_selected_tile(self):
        return self.selected_tile

    def update_cell_prd_id(self, prd_id, subject, teacher, classroom):
        self.update_cell_subject(prd_id, subject)
        self.update_cell_teacher(prd_id, teacher)
        self.update_cell_classroom(prd_id, classroom)

    def update_cell_subject(self, prd_id, text):
        self.prd_id_map[prd_id].update_subject(text)

    def update_cell_teacher(self, prd_id, text):
        self.prd_id_map[prd_id].update_teacher(text)

    def update_cell_classroom(self, prd_id, text):
        self.prd_id_map[prd_id].update_classroom(text)

    def update_title(self, firstname, surname, year):
        self.title_cell.update_subject(firstname)
        self.title_cell.update_teacher(surname)
        self.title_cell.update_classroom(year)

    def clear_title(self):
        self.update_title("", "", "")

    def clear_timetable(self):
        self.selected_tile, self.selected_prd_id = None, None
        for tile in self.selected_tiles:
            tile.interphase_colour(self.bg)
        for tile in self.prd_id_map.values():
            tile.clear_cell()
        self.selected_tiles.clear()

    def clear_table(self):
        self.update_title("", "", "")
        self.clear_timetable()


class ScrolledFrame(tk.Frame):
    def __init__(self, parent, framebackground="#ffffff", **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.prop = True

        # creating the scrollbars
        self.x_scrollbar = ttk.Scrollbar(self, orient='horizontal')
        self.x_scrollbar.grid(row=1, column=0, sticky='ew', columnspan=2)
        self.y_scrollbar = ttk.Scrollbar(self)
        self.y_scrollbar.grid(row=0, column=1, sticky='ns')
        # creating a canvas
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        # placing a canvas into frame
        self.canvas.grid(row=0, column=0, sticky='nsew')
        # associating scrollbar commands to canvas scrolling
        self.x_scrollbar.config(command=self.canvas.xview)
        self.y_scrollbar.config(command=self.canvas.yview)

        # creating a frame to insert into the canvas
        self.interior = tk.Frame(self.canvas)

        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor='nw')

        self.canvas.config(xscrollcommand=self.x_scrollbar.set,
                           yscrollcommand=self.y_scrollbar.set,
                           scrollregion=(0, 0, 100, 100))

        self.configure_background(framebackground)
        self.canvas.bind('<Configure>', self._configure_scrollregion)
        self.interior.bind('<Enter>', self._bound_to_mousewheel)
        self.interior.bind('<Leave>', self._unbound_to_mousewheel)

    def configure_background(self, colour):
        self.canvas.config(bg=colour)
        self.interior.config(bg=colour)

    def set_size(self, width=None, height=None):
        self.config(width=width, height=height)

    def propagate(self, flag=True):
        self.prop = flag

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _configure_scrollregion(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion='0 0 %s %s' % size)
        if self.prop:
            self._configure_canvas_(*size)

    def _configure_canvas(self, width, height):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())
        if self.interior.winfo_reqheight() != self.canvas.winfo_height():
            # update the canvas's height to fit the inner frame
            self.canvas.config(height=self.interior.winfo_reqheight())

    def _configure_canvas_(self, width, height):
        if width != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=width)
        if height != self.canvas.winfo_height():
            # update the canvas's height to fit the inner frame
            self.canvas.config(height=height)


class VerticalScrolledFrame(tk.Frame):
    def __init__(self, parent, framebackground="#ffffff", **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # creating the scrollbars
        self.y_scrollbar = ttk.Scrollbar(self)
        self.y_scrollbar.grid(row=0, column=1, sticky='ns')
        # creating a canvas
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        # placing a canvas into frame
        self.canvas.grid(row=0, column=0, sticky='nsew')
        # associating scrollbar commands to canvas scrolling
        self.y_scrollbar.config(command=self.canvas.yview)

        # creating a frame to insert into the canvas
        self.interior = tk.Frame(self.canvas)

        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor='nw')

        self.canvas.config(yscrollcommand=self.y_scrollbar.set,
                           scrollregion=(0, 0, 100, 100))

        self.configure_background(framebackground)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.interior.bind('<Enter>', self._bound_to_mousewheel)
        self.interior.bind('<Leave>', self._unbound_to_mousewheel)

    def configure_background(self, colour):
        self.canvas.config(bg=colour)
        self.interior.config(bg=colour)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _configure_canvas(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion='0 0 %s %s' % size)
        if self.interior.winfo_reqheight() != self.canvas.winfo_height():
            # update the canvas's height to fit the inner frame
            self.canvas.config(height=self.interior.winfo_reqheight())
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())


class HorizontalScrolledFrame(tk.Frame):
    def __init__(self, parent, framebackground="#ffffff", **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # creating the scrollbars
        self.x_scrollbar = ttk.Scrollbar(self, orient='horizontal')
        self.x_scrollbar.grid(row=1, column=0, sticky='ew', columnspan=2)
        # creating a canvas
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        # placing a canvas into frame
        self.canvas.grid(row=0, column=0, sticky='nsew')
        # associating scrollbar commands to canvas scrolling
        self.x_scrollbar.config(command=self.canvas.xview)

        # creating a frame to insert into the canvas
        self.interior = tk.Frame(self.canvas)

        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor='nw')

        self.canvas.config(xscrollcommand=self.x_scrollbar.set,
                           scrollregion=(0, 0, 100, 100))

        self.configure_background(framebackground)
        self.canvas.bind('<Configure>', self._configure_canvas)

    def configure_background(self, colour):
        self.canvas.config(bg=colour)
        self.interior.config(bg=colour)

    def _configure_canvas(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion='0 0 %s %s' % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())
        if self.interior.winfo_reqheight() != self.canvas.winfo_height():
            # update the canvas's height to fit the inner frame
            self.canvas.config(height=self.interior.winfo_reqheight())


class SpreadSheetFrame(VerticalScrolledFrame):
    def __init__(self, parent, rows=0, columns=0, **kwargs):
        VerticalScrolledFrame.__init__(self, parent, **kwargs)
        self.rows = rows
        self.columns = columns
        self.x_axis = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for column in range(columns):
            tk.Label(self.interior, text=self.x_axis[column]).grid(row=0, column=column+1)
        for row in range(rows):
            tk.Label(self.interior, text=str(row+1)).grid(row=row+1)
        self.cells = {}
        for row in range(rows):
            cell_row = {}
            for column in range(columns):
                cell_row[self.x_axis[column]] = tk.Entry(self.interior)
                cell_row[self.x_axis[column]].grid(row=row+1, column=column+1)
            self.cells[row+1] = cell_row

    def reference_to_directory(self, reference):
        if reference[0] not in self.x_axis:
            return False
        try:
            x_coordinate = reference[0]
            y_coordinate = int(reference[1:])
            return self.cells[y_coordinate][x_coordinate]
        except ValueError:
            return False
        except KeyError:
            return False

    def configure_cell(self, reference, **kwargs):
        directory = self.reference_to_directory(reference)
        if directory is not False:
            directory.configure(**kwargs)
        else:
            return False

    def configure_all_cells(self, **kwargs):
        for row in range(1, self.rows+1):
            for column in range(self.columns):
                self.cells[row][self.x_axis[column]].configure(**kwargs)

    def set_cell(self, reference, text):
        directory = self.reference_to_directory(reference)
        if directory is not False:
            directory.delete(0, "end")
            directory.insert(0, text)
        else:
            return False

    def set_all_cells(self, text):
        for row in range(1, self.rows+1):
            for column in range(self.columns):
                self.cells[row][self.x_axis[column]].delete(0, "end")
                self.cells[row][self.x_axis[column]].insert(0, text)

    def get_cell(self, reference):
        directory = self.reference_to_directory(reference)
        if directory is not False:
            return directory.get()
        else:
            return False


class MenuManager:

    cmd_id_map = {}
    menu_commands = {}
    menu_widgets = {}
    cmds_id = 0

    def __init__(self, parent, *commands, **kwargs):
        """Manages pop-up menus within the program"""
        if commands not in self.cmd_id_map.keys():
            cmd_id = self.cmds_id
            self.cmd_id_map[commands] = cmd_id
            # create new pop up menu
            menu = PopUpMenu(parent, *commands, **kwargs)
            self.menu_commands[cmd_id] = menu
            #  increment cmd_id by one to remain unique
            MenuManager.cmds_id += 1
        else:  # menu for commands already exists
            # fetch cmd_id for given commands
            cmd_id = self.cmd_id_map[commands]
        self.menu_widgets[parent] = cmd_id
        parent.bind("<Button-3>", self.popup)

    def popup(self, event):
        """Displays menu linked to event.widget"""
        # finds the menu id for the widget
        menu_id = self.menu_widgets[event.widget]
        # links menu id to the menu object using dictionary
        menu = self.menu_commands[menu_id]
        try:
            menu.post(event.x_root, event.y_root)
        finally:
            menu.grab_release()


class PopUpMenu(tk.Menu):
    """Subclass of tk.Menu to handle commands as tuple"""
    def __init__(self, parent, *commands, **kwargs):
        super().__init__(parent, tearoff=0, **kwargs)
        # command : Tuple[Tuple[str, function]
        for command in commands:
            self.add_command(label=command[0], command=command[1])


class TableCellFrame(tk.Frame):
    def __init__(self, parent, text="", bg="white", escape_command=None, enter_command=None):
        super().__init__(parent, bg=bg, borderwidth=1, relief="solid")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.background = bg
        self.entry = tk.Entry(self, bg=self.background, bd=0, relief="flat", width=2)
        self.entry.bind("<Escape>", escape_command)
        self.entry.bind("<Return>", enter_command)
        self.text = tk.Label(self, text=text, bg=bg)
        self.text.grid(row=1, column=1)

    def __repr__(self):
        return self.text.cget("text")

    def interphase(self):
        self.entry.grid_remove()
        self.entry.delete(0, "end")
        self.text.grid(row=1, column=1)

    def edit_phase(self):
        self.text.grid_remove()
        self.entry.insert(0, self.get_text())
        self.entry.grid(row=1, column=1)

    def complete_edit(self):
        self.text.config(text=self.get_proposed_text())
        self.interphase()

    def disable_edit(self):
        self.entry.config(state="disabled")

    def enable_edit(self):
        self.entry.config(state="active")

    def add_bind(self, event, command):
        self.bind(event, command)
        self.text.bind(event, command)

    def remove_bind(self, event):
        self.unbind(event)
        self.text.unbind(event)

    def add_menu(self, *commands):
        MenuManager(self, *commands)
        MenuManager(self.text, *commands)

    def configure_background(self, colour):
        self.background = colour
        self.config(bg=colour)
        self.text.config(bg=colour)
        self.entry.config(bg=colour)

    def configure_text(self, text):
        self.text.config(text=text)

    def get_text(self):
        return self.text.cget("text")

    def get_proposed_text(self):
        return self.entry.get()

    def configure_cell(self, **kwargs):
        self.text.config(**kwargs)


class TeacherPeriodsNode(tk.Frame):
    def __init__(self, parent, bg="white", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.background = bg
        self.event, self.command = None, None
        self.row_id = 0
        self.rows = {}

    def update_colour(self, colour):
        self.background = colour
        self.config(bg=colour)
        for node in self.rows.values():
            for lbl in node:
                lbl.config(bg=colour)

    def add_bind(self, event, command):
        self.event, self.command = event, command

    def remove_bind(self):
        self.unbind(self.event)
        for node in self.rows.values():
            for lbl in node:
                lbl.unbind(self.event)
        self.event, self.command = None, None

    def add_row(self, code, per):
        self.row_id += 1
        code_lbl = tk.Label(self, text=code, bg=self.background)
        per_lbl = tk.Label(self, text=str(per), bg=self.background)
        if self.event is not None:
            code_lbl.bind(self.event, self.command)
            per_lbl.bind(self.event, self.command)
        self.rows[self.row_id] = (code_lbl, per_lbl)
        code_lbl.grid(row=self.row_id, column=0)
        per_lbl.grid(row=self.row_id, column=1)
        return self.row_id

    def delete_rows(self):
        for node in self.rows.values():
            for lbl in node:
                lbl.destroy()
        self.reset_row_id()

    def reset_row_id(self):
        self.row_id = 0


class GridFrame(tk.Frame):
    def __init__(self, parent, bg="white", **kwargs):
        super().__init__(parent, bg=bg, borderwidth=1, relief="solid", **kwargs)
        self.blank = True
        self.colour = bg
        self.state = 0
        self.row, self.column = 0, 0

    def __repr__(self):
        return "Blank"

    def update_colour(self, colour):
        colour_tree(self, colour)

    def is_blank(self):
        return self.blank

    def get_row_column(self):
        return self.row, self.column

    def update_grid(self, row, column):
        self.grid_forget()
        self.grid_self(row, column)

    def remove_grid(self):
        self.grid_forget()

    def grid_self(self, row=None, column=None):
        try:
            self.row, self.column = int(row), int(column)
        except TypeError:
            raise TypeError("row and column arguments must be integer values")
        self.grid(row=self.row, column=self.column, sticky="nsew")


class SubjectClassTableNode(GridFrame):
    def __init__(self, parent, blk_name="", cls_name="", num_per=0, bg="white", **kwargs):
        GridFrame.__init__(self, parent, bg=bg, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(9999, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(9999, weight=1)
        self.blank = False
        self.background = bg
        self.tchrs_map = {}
        self.event, self.command = None, None
        self.row, self.column = 0, 0
        self.block_lbl = tk.Label(self, text=blk_name, bg=bg)
        self.block_lbl.grid(row=1, column=1, columnspan=2, sticky="w")
        self.class_lbl = tk.Label(self, text=cls_name, bg=bg)
        self.class_lbl.grid(row=2, column=1, columnspan=2, sticky="w")
        self.num_per_lbl = tk.Label(self, text=str(num_per), bg=bg)
        self.num_per_lbl.grid(row=3, column=1, sticky="w")
        self.teacher_periods = TeacherPeriodsNode(self, bg=bg)
        self.teacher_periods.grid(row=3, column=2)

    def __repr__(self):
        return self.block_lbl.cget("text")

    def add_tchr(self, tchr_id, code, per):
        self.tchrs_map[self.teacher_periods.add_row(code, per)] = tchr_id

    def delete_tchrs(self):
        self.teacher_periods.delete_rows()
        self.tchrs_map.clear()

    def remove_bind(self):
        self.unbind(self.event)
        self.block_lbl.unbind(self.event)
        self.class_lbl.unbind(self.event)
        self.num_per_lbl.unbind(self.event)
        self.teacher_periods.remove_bind()

    def configure_background(self, colour):
        self.background = colour
        self.config(bg=colour)
        self.block_lbl.config(bg=colour)
        self.class_lbl.config(bg=colour)
        self.num_per_lbl.config(bg=colour)
        self.teacher_periods.update_colour(colour)


class Table(ScrolledFrame):
    def __init__(self, parent, bg="white", activebackground="#008080", headingbackground="grey", **kwargs):
        ScrolledFrame.__init__(self, parent, **kwargs)
        self.table = tk.Frame(self.interior, borderwidth=1, relief="solid")
        self.table.grid(row=0, column=0)
        self.selection = True
        self.menu_cmds = None
        self.selection_cmds = []
        self.selected_cell = None
        self.height, self.width = 0, 0
        self.row_id, self.column_id, self.cell_id = 0, 0, 0
        self.cells = {}
        self.row_id_map, self.column_id_map = {}, {}
        self.event, self.command = None, None
        self.row_titles, self.column_titles, self.contents = [], [], {}
        self.bg, self.activebackground, self.headingbackground = bg, activebackground, headingbackground
        self.apex = GridFrame(self.table, bg=self.headingbackground)
        tk.Label(self.apex, text="Testing", bg=self.headingbackground).grid(row=0)
        self.apex.grid_self(row=0, column=0)

    def add_row(self, title):
        self.height += 1
        self.row_id += 1
        self.row_titles.append(TableCellFrame(self.table, text=str(title), bg=self.headingbackground))
        self.row_titles[-1].grid(row=self.row_id, column=0, sticky="nsew")
        self.row_id_map[self.row_id] = self.row_id
        self.contents[self.row_id] = {}
        for column_id in self.column_id_map.keys():
            cell = self._create_cell()
            self.contents[self.row_id][column_id] = cell
            cell.grid_self(row=self.row_id_map[self.row_id], column=self.column_id_map[column_id])
        return self.row_id

    def add_column(self, title):
        self.width += 1
        self.column_id += 1
        self.column_titles.append(TableCellFrame(self.table, text=str(title), bg=self.headingbackground))
        self.column_titles[-1].grid(row=0, column=self.column_id, sticky="nsew")
        self.column_id_map[self.column_id] = self.column_id
        for row_id in self.row_id_map.keys():
            cell = self._create_cell()
            self.contents[row_id][self.column_id] = cell
            cell.grid_self(row=self.row_id_map[row_id], column=self.column_id_map[self.column_id])
        return self.column_id

    def _create_cell(self):
        self.cell_id += 1
        cell = GridFrame(self.table, bg=self.bg)
        self._refresh_cell(cell)
        self.cells[self.cell_id] = cell
        return cell

    def _refresh_cell(self, cell):
        if self.selection:
            bind_tree(cell, "<Button-1>", self.select_cell)
        if self.menu_cmds is not None:
            menu_tree(cell, *self.menu_cmds)

    def get_table_colours(self):
        return self.bg, self.activebackground, self.headingbackground

    def enable_selection(self):
        self.selection = True
        for cell in self.cells:
            bind_tree(cell, "<Button-1>", self.select_cell)

    def add_selection_command(self, command):
        if callable(command):
            self.selection_cmds.append(command)
        else:
            raise TypeError("'{}' is not a callable object".format(command))

    def select_cell(self, event):
        widget = event.widget
        while hasattr(widget, "blank") is False:
            widget = widget.master
        self.clear_selected_cell()
        self.selected_cell = widget
        colour_tree(self.selected_cell, self.activebackground)
        for cmd in self.selection_cmds:
            cmd()

    def get_cell(self, row_id, column_id):
        return self.contents[row_id][column_id]

    def clear_selected_cell(self):
        if self.selected_cell is not None:
            colour_tree(self.selected_cell, self.bg)

    def get_selected_cell(self):
        return self.selected_cell

    def get_selected_cell_id(self):
        return reverse_map_dict(self.cells, self.selected_cell)

    def get_selected_cell_co(self):
        for row in self.contents.keys():
            for col in self.contents[row].keys():
                if self.contents[row][col] == self.selected_cell:
                    return row, col

    def add_pop_up_menu(self, *commands):
        self.menu_cmds = commands
        for cell in self.cells.values():
            menu_tree(cell, *self.menu_cmds)

    def reset_cell_id(self):
        self.cell_id = 0

    def clear_table(self):
        for cell in self.cells.values():
            cell.destroy()
        for row in self.row_titles:
            row.destroy()
        for column in self.column_titles:
            column.destroy()
        self.selected_cell = None
        self.height, self.width = 0, 0
        self.row_id, self.column_id, self.cell_id = 0, 0, 0
        self.cells = {}
        self.row_id_map, self.column_id_map = {}, {}
        self.event, self.command = None, None
        self.row_titles, self.column_titles, self.contents = [], [], {}


class HorizontalTable(HorizontalScrolledFrame):
    def __init__(self, parent, bg="white", activebackground="#008080", headingbackground="grey", **kwargs):
        HorizontalScrolledFrame.__init__(self, parent, **kwargs)
        self.table = tk.Frame(self.interior, borderwidth=1, relief="solid")
        self.table.grid(row=0, column=0)
        self.selection = True
        self.slctn_evt = []
        self.menu_cmds = None
        self.selected_tile = None
        self.height, self.length, self.title_id, self.tile_id = 0, 0, 0, 0
        self.tiles = {}
        self.title_id_rows = {}
        self.title_ids = []
        self.event, self.command = None, None
        self.row_headers, self.contents = [], {}
        self.bg, self.activebackground, self.headingbackground = bg, activebackground, headingbackground

    def add_row(self, title):
        self.title_id += 1
        self.row_headers.append(TableCellFrame(self.table, text=str(title), bg="grey"))
        self.row_headers[-1].grid(row=self.title_id, column=0, sticky="nsew")
        self.title_ids.append(self.title_id)
        self.title_id_rows[self.title_id] = self.title_id
        self.contents[self.title_id] = list()
        return self.title_id

    def add_tile(self, title_id, blk, cls, num_per):
        if title_id not in self.title_ids:
            raise TypeError("'{}' is not a recognised title_id")
        length = len(self.contents[title_id])
        for tile in range(length):
            if self.contents[title_id][tile].is_blank():
                row, column = self.contents[title_id][tile].get_row_column()
                self.contents[title_id][tile].remove_grid()
                self.contents[title_id][tile] = self._create_tile(blk, cls, num_per)
                self.contents[title_id][tile].grid_self(row, column)
                return self.tile_id
        self.contents[title_id].append(self._create_tile(blk, cls, num_per))
        self.length = len(self.contents[title_id])
        self.fill_spaces()
        self.contents[title_id][-1].grid(row=self.title_id_rows[title_id], column=self.length, sticky="nsew")
        return self.tile_id

    def add_teacher(self, tile_id, tchr_id, tchr_code, num_prds):
        tile = self.tiles[tile_id]
        tile.add_tchr(tchr_id, tchr_code, num_prds)
        self._refresh_tile(tile)

    def _create_tile(self, blk, cls, num_per):
        self.tile_id += 1
        tile = SubjectClassTableNode(self.table, blk, cls, num_per)
        self._refresh_tile(tile)
        self.tiles[self.tile_id] = tile
        return tile

    def _refresh_tile(self, tile):
        if self.selection:
            bind_tree(tile, "<Button-1>", self.select_tile)
        if self.menu_cmds is not None:
            menu_tree(tile, *self.menu_cmds)

    def fill_spaces(self):
        for title_id in self.contents.keys():
            tiles = self.length - len(self.contents[title_id])
            for tile in range(0, tiles):
                self.contents[title_id].append(GridFrame(self.table))
                row = self.title_id_rows[title_id]
                column = self.length - tile
                self.contents[title_id][-1].grid_self(row, column)

    def add_selection_event(self, function):
        if callable(function):
            self.slctn_evt.append(function)

    def enable_selection(self):
        self.selection = True
        for tile in self.tiles:
            bind_tree(tile, "<Button-1>", self.select_tile)

    def select_tile(self, event):
        widget = event.widget
        while hasattr(widget, "blank") is False:
            widget = widget.master
        self.clear_selected_tile()
        self.selected_tile = widget
        self.selected_tile.configure_background("#008080")
        for function in self.slctn_evt:
            function()

    def clear_selected_tile(self):
        if self.selected_tile is not None:
            self.selected_tile.configure_background("#ffffff")

    def get_selected_tile(self):
        return self.selected_tile

    def get_selected_tile_id(self):
        return reverse_map_dict(self.tiles, self.selected_tile)

    def add_pop_up_menu(self, *commands):
        self.menu_cmds = commands
        for tile in self.tiles.values():
            menu_tree(tile, *self.menu_cmds)

    def reset_tile_id(self):
        self.tile_id = 0

    def clear_table_contents(self):
        for title_id in self.contents.keys():
            row = self.contents[title_id]
            for tile in row:
                tile.grid_remove()
            self.contents[title_id].clear()
        self.tiles.clear()


class VerticalTable(VerticalScrolledFrame):
    """Vertical table with columns and dynamic rows"""
    def __init__(self, parent, columns=None, bg="white", activebackground="#008080", headingbackground="grey", **kwargs):
        # calls the initialiser of the superclass
        VerticalScrolledFrame.__init__(self, parent, **kwargs)
        self.table = tk.Frame(self.interior, borderwidth=1, relief="solid")
        self.table.grid(row=0, column=0)
        if type(columns) is list or type(columns) is tuple:
            if type(columns) is tuple:
                columns = list(columns)
        else:
            raise TypeError("CustomTableFrame() requires a list or tuple for column headings")
        self.width = len(columns)
        self.event, self.command, self.commands, self.initialise, self.validation = None, None, None, None, None
        self.column_headings, self.contents, self.new_contents = [], [], []
        self.bg, self.activebackground, self.headingbackground = bg, activebackground, headingbackground
        self.selected_row, self.selected_row_index, self.row_id = None, None, 0
        # creates the column headings at the top of the table
        for i, item in enumerate(columns, 0):
            self.column_headings.append(TableCellFrame(self.table, text=str(item), bg="grey"))
            self.column_headings[-1].grid(row=0, column=i, sticky="nsew")

    def configure_column_weight(self, weight=1):
        """Changes the weight of the columns within the table"""
        for c in range(self.width):
            self.table.grid_columnconfigure(c, weight=weight)

    def enable_editing(self, initialise, validation):
        """Records initialise and validation functions -> bool"""
        self.initialise = initialise
        self.validation = validation

    def validation_command(self, event):
        """Checks edit is valid under validation function"""
        if self.validation is None:
            self.complete_edit()
            return
        selected_row_text = list(x.get_proposed_text() for x in self.selected_row)
        response = self.validation(*selected_row_text)
        if response:
            self.complete_edit()
        elif not response:
            self.interphase_selected_row(None)
        else:
            pass

    def interphase_selected_row(self, event):
        """Transitions row to its normal working state"""
        self.enable_binds()
        for item in self.selected_row:
            item.interphase()
        self.update_idletasks()
        self._configure_canvas(None)

    def complete_edit(self):
        """Commit edit to table"""
        self.enable_binds()
        for item in self.selected_row:
            item.complete_edit()
        self.update_idletasks()
        self._configure_canvas(None)

    def edit_selected_row(self):
        """Transitions row into edit state"""
        if self.initialise is None or self.selected_row is None:
            return
        self.disable_binds()
        for item in self.selected_row:
            item.edit_phase()
        self.initialise(*self.selected_row)
        self.update_idletasks()
        self._configure_canvas(None)

    def add_pop_up_menu(self, *commands):
        """Adds popup menu to the table"""
        self.commands = commands

    def add_bind(self, event, command):
        """Applies bind to the table"""
        self.event = event
        self.command = command

    def remove_bind(self):
        """Removes bind from the table"""
        self.disable_binds()
        self.event, self.command = None, None

    def select_row(self, event):
        """Highlights the row when it is selected"""
        if hasattr(event.widget, "text"):
            widget = event.widget
        else:
            widget = event.widget.master
        for i, row in enumerate(self.contents):
            if widget in row:
                self.clear_selected_row()
                self.selected_row, self.selected_row_index = row, i
        for cell in self.selected_row[1:]:
            cell.configure_background(self.activebackground)

    def clear_selected_row(self):
        """Transitions row to its normal working state"""
        if self.selected_row is not None:
            for cell in self.selected_row[1:]:
                cell.configure_background(self.bg)

    def add_row(self, *args, index=None):
        """Adds a new row to the table"""
        # makes sure the number of args matches the width
        if len(args) != self.width:
            raise TypeError("add_row() requires {} positional arguments".format(str(self.width)))
        text_row = list(map(str, args))
        row = [self.row_id]
        self.new_contents = self.contents.copy()
        for i, item in enumerate(text_row, 0):
            row.append(TableCellFrame(self.table,
                                      text=item,
                                      bg=self.bg,
                                      escape_command=self.interphase_selected_row,
                                      enter_command=self.validation_command))
        if index is None:
            self.new_contents.append(row)
        else:
            self.new_contents.insert(index, row)
        self.update_table()
        self.row_id += 1
        return self.row_id-1

    def remove_selected_row(self):
        """Removes selected row from the table"""
        return self.remove_row(self.selected_row_index)

    def remove_row_by_id(self, row_id):
        """Removes row linked to row_id from the table"""
        for index, row in enumerate(self.contents):
            if row[0] == row_id:
                return self.remove_row(index)
        return None

    def remove_row(self, row_index):
        """Removes the row from the table"""
        if row_index is None:
            return None
        if type(row_index) is not int:
            try:
                row = int(row_index)
            except ValueError:
                raise ValueError("remove_row() could not convert {} to an integer".format(str(row_index)))
        self.new_contents = self.contents.copy()
        deleted_row = self.new_contents.pop(row_index)
        if deleted_row == self.selected_row:
            self.selected_row, self.selected_row_index = None, None
        self.update_table()
        return deleted_row[0]

    def get_selected_row(self):
        """Returns a tuple of strings of the contents of the row"""
        if self.selected_row is None:
            return None
        temp = []
        for item in self.selected_row[1:]:
            temp.append(item.get_text())
        return tuple(temp)

    def get_selected_row_index(self):
        """Returns the selected rows index"""
        return self.selected_row_index

    def get_selected_row_id(self):
        """Returns the selected rows id"""
        try:
            return self.selected_row[0]
        except TypeError:
            return None

    def get_row(self, index):
        """Returns the objects of the widgets within the selected row index"""
        return tuple(self.contents[index][1:])

    def enable_binds(self):
        """Enables binds on the table"""
        for r, row in enumerate(self.contents, 1):
            for item in row[1:]:
                if self.event == "<Button-1>":
                    item.add_bind("<Button-1>", combine_funcs(self.select_row, self.command))
                else:
                    item.add_bind("<Button-1>", self.select_row)
                    item.add_bind(self.event, self.command)

    def disable_binds(self):
        """Disables binds on the table"""
        for r, row in enumerate(self.contents, 1):
            for item in row:
                item.remove_bind("<Button-1>")
                item.remove_bind(self.event)

    def reset_row_id(self):
        """Resets the row_id back to zero"""
        self.row_id = 0

    def update_table(self):
        """Updates the table when a change has been made"""
        self.clear_table()
        for r, row in enumerate(self.new_contents, 1):
            for c, item in enumerate(row[1:], 0):
                if self.commands is not None:
                    item.add_menu(*self.commands)
                item.grid(row=r, column=c, sticky="nsew")
        self.update_idletasks()
        self._configure_canvas(None)
        self.contents = self.new_contents.copy()
        self.enable_binds()

    def clear_table(self):
        """Clears the table but keeps the headings"""
        self.clear_selected_row()
        for r, row in enumerate(self.contents, 0):
            for c in range(1, len(row)):
                self.contents[r][c].grid_remove()
        self.contents.clear()


class Date:
    def __init__(self):
        date_today = datetime.date.today()
        self.day = date_today.day
        self.month = date_today.month
        self.year = date_today.year

    def __repr__(self):
        return self.get_date()

    def get_date(self):
        day = str(self.day)
        if len(day) != 2:
            day = "0"+day
        month = str(self.month)
        if len(month) != 2:
            month = "0"+month
        year = str(self.year)[2:]
        return "/".join((day, month, year))


class Calender(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=1, relief="solid")

        self.date = Date()

        self.months = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")

        self.day_var = tk.IntVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.IntVar()

        self.date_label = tk.Label(self, text=self.date.get_date())
        self.date_label.grid(row=0, column=0)

        self.month_combobox = ttk.Combobox(self, textvariable=self.month_var, values=self.months)
        self.month_combobox.bind("<<ComboboxSelected>>", self.update_date_month)
        self.month_combobox.grid(row=0, column=1)

        self.year_combobox = ttk.Combobox(self, textvariable=self.year_var, values=list(range(1900, 2100)))
        self.year_combobox.bind("<<ComboboxSelected>>", None)
        self.year_combobox.grid(row=0, column=2)

    def update_date_month(self, event):
        print(event)


if __name__ == "__main__":
    class MainWindow(tk.Tk):
        def __init__(self):
            super().__init__()
            # self.hframe = HorizontalScrolledFrame(self)
            self.table = IndividualTable(self, table_colour="white", title_colour="light blue")
            # self.hframe.pack()
            self.table.pack()

    app = MainWindow()
    app.mainloop()
