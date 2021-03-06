
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from genume.registry.registry import Registry
from genume.registry.category import CategoryEntry
from genume.exports.terminal import print_enumeration


def main():
    MainWindow()
    Gtk.main()


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="genume")
        self.set_default_size(500, 350)

        reg = Registry()
        reg.update()
        print_enumeration(reg.root)  # TODO remove, here for debugging

        # setup the layout
        self.set_titlebar(self.generate_header_bar())
        self.add(self.generate_main_view(reg))

        # handle events
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

        # store state
        self.reg = reg

    def refresh(self):
        """Updates the registry and refreshes the view"""
        # TODO improve
        self.reg.update()
        current_page = self.subtrees_container.get_current_page()
        self.remove(self.get_child())
        self.add(self.generate_main_view(self.reg))
        self.show_all()
        self.subtrees_container.set_current_page(current_page)

    def generate_header_bar(self):

        bar = Gtk.HeaderBar(
            title="genume",
            show_close_button=True
        )

        menu_button = Gtk.MenuButton()
        menu_button.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        menu_button.set_popup(self.generate_header_bar_menu())
        bar.pack_end(menu_button)

        refresh_button = Gtk.Button()
        refresh_button.add(Gtk.Image(stock=Gtk.STOCK_REFRESH))
        refresh_button.connect("clicked", self.request_refresh)
        bar.pack_start(refresh_button)

        return bar

    def generate_header_bar_menu(self):
        """Generates and returns a menu for the header bar menu button"""

        menu = Gtk.Menu(halign=Gtk.Align.END)

        def add(name, func):
            item = Gtk.MenuItem(name)
            item.connect("activate", func)
            menu.append(item)

        def add_separator():
            menu.append(Gtk.SeparatorMenuItem())

        add("Refresh", self.request_refresh)
        add_separator()
        add("Close", self.request_close)

        # TODO extend the menu

        menu.show_all()
        return menu

    def generate_main_view(self, reg):
        """Generate and return the content of the window"""

        grid = Gtk.Box()
        roots_container = self.generate_roots_container()
        grid.pack_start(roots_container, False, False, 0)
        subtrees_container = self.generate_subtrees_container()
        grid.pack_start(subtrees_container, True, True, 0)

        # fill the layout

        for name, entry in reg.root.items():
            if isinstance(entry, CategoryEntry):

                self.generate_root_and_subtree(name, entry, roots_container, subtrees_container)
            else:
                print("Scripts on the root scripts folder are not supported, yet")  # TODO implement

        self.subtrees_container = subtrees_container
        return grid

    def generate_root_and_subtree(self, name, entry: CategoryEntry, roots_container, subtrees_container):
        """Generate a root tab and the corresponding subtree view"""

        root = self.generate_root(name, entry)
        roots_container.add(root)

        subtree = self.generate_subtree(name, entry)
        subtrees_container.append_page(subtree, Gtk.Label(label=name))

        # setup the events
        root.page_index = subtrees_container.get_n_pages() - 1
        root.connect("clicked", self.show_root)

    def generate_roots_container(self):

        return Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            border_width=6
        )

    def generate_root(self, name, entry: CategoryEntry):
        """Generate the tab like button that correspond to the given entry"""

        return Gtk.Button(
            label=name
        )

    def generate_subtrees_container(self):

        return Gtk.Notebook(
            show_tabs=False
        )

    def generate_subtree(self, name, entry: CategoryEntry):
        """Generate the list like view that correspond to the given entry"""

        # create the store

        store = Gtk.ListStore(str, str)
        for name, entry in entry.items():
            if isinstance(entry, CategoryEntry):
                print("Scripts on the sub root folders are not supported, yet")  # TODO implement
            else:
                store.append([name, repr(entry)])

        # create the tree view

        tree = Gtk.TreeView(store)
        for i, column_title in enumerate(["Name", "Value"]):
            tree.append_column(Gtk.TreeViewColumn(
                column_title,
                Gtk.CellRendererText(),
                text=i
            ))
        return tree

    def show_root(self, button):
        """Changes to the tab given by the page_index value of the button"""
        self.subtrees_container.set_current_page(button.page_index)

    def request_refresh(self, _):
        self.refresh()

    def request_close(self, _):
        self.close()
