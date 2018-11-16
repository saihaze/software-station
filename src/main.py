#!/usr/local/bin/python3.6
"""
Copyright (c) 2017, GhostBSD. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistribution's of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistribution's in binary form must reproduce the above
   copyright notice,this list of conditions and the following
   disclaimer in the documentation and/or other materials provided
   with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES(INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, GObject
import threading
# from time import sleep

from pkgngHandler import search_packages, available_package_origin
from pkgngHandler import available_package_dictionary, isntalled_package_origin
from pkgngHandler import isntalled_package_dictionary
from xpm import xpmPackageCategory

global pkg_to_install
pkg_to_install = []

global pkg_to_uninstall
pkg_to_uninstall = []


class TableWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title("Software Station")
        self.connect("delete-event", Gtk.main_quit)
        self.set_size_request(850, 500)
        # Creating the toolbar
        toolbar = Gtk.Toolbar()
        # toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        self.box1 = Gtk.VBox(False, 0)
        self.add(self.box1)
        self.box1.show()
        self.box1.pack_start(toolbar, False, False, 0)
        self.previousbutton = Gtk.ToolButton()
        self.previousbutton.set_label("Back")
        self.previousbutton.set_is_important(True)
        self.previousbutton.set_icon_name("go-previous")
        self.previousbutton.set_sensitive(False)
        toolbar.insert(self.previousbutton, -1)
        self.nextbutton = Gtk.ToolButton()
        self.nextbutton.set_label("Forward")
        self.nextbutton.set_is_important(True)
        self.nextbutton.set_icon_name("go-next")
        self.nextbutton.set_sensitive(False)
        toolbar.insert(self.nextbutton, -2)

        radiotoolbutton1 = Gtk.RadioToolButton(label="All Software")
        radiotoolbutton1.set_icon_name("package_system")
        self.available_or_installed = 'available'
        radiotoolbutton1.connect("toggled", self.all_or_installed, "available")
        toolbar.insert(radiotoolbutton1, -3)
        radiotoolbutton2 = Gtk.RadioToolButton(label="Installed Software",
                                               group=radiotoolbutton1)
        radiotoolbutton2.set_icon_name("system")
        radiotoolbutton2.connect("toggled", self.all_or_installed, "installed")
        toolbar.insert(radiotoolbutton2, -4)
        separatortoolitem = Gtk.SeparatorToolItem()
        toolbar.insert(separatortoolitem, -5)
        toolitem = Gtk.ToolItem()
        toolbar.insert(toolitem, -6)
        toolitem.set_expand(True)
        self.entry = Gtk.Entry()
        self.entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                           "search")
        self.entry.connect("key-release-event", self.search_release)
        hBox = Gtk.HBox(False, 0)
        toolitem.add(hBox)
        hBox.show()
        hBox.pack_start(self.entry, False, False, 0)
        self.apply_button = Gtk.Button()
        self.apply_button.set_label("Apply")
        # self.apply_button.set_is_important(True)
        # self.apply_button.set_stock_id('gtk-apply')
        apply_img = Gtk.Image()
        apply_img.set_from_icon_name('gtk-apply', 1)
        self.apply_button.set_image(apply_img)
        self.apply_button.set_property("tooltip-text", "Apply change on the system")
        self.apply_button.set_sensitive(False)
        hBox.pack_end(self.apply_button, False, False, 0)
        # toolbar.insert(self.apply_button, -1)
        self.cancel_button = Gtk.Button()
        self.cancel_button.set_label("Cancel")
        # self.cancel_button.set_is_important(True)
        cancel_img = Gtk.Image()
        cancel_img.set_from_icon_name('gtk-apply', 1)
        self.cancel_button.set_image(cancel_img)
        self.cancel_button.set_sensitive(False)
        self.cancel_button.set_property("tooltip-text", "Cancel changes")
        hBox.pack_end(self.cancel_button, False, False, 0)
        # toolbar.insert(self.cancel_button, -2)

        # Creating a notebook to swith
        self.mainstack = Gtk.Stack()
        self.mainstack.show()
        self.mainstack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.box1.pack_start(self.mainstack, True, True, 0)

        mainwin = self.MainBook()
        self.mainstack.add_named(mainwin, "mainwin")

        # state = Gtk.Notebook()
        # state.show()
        self.pkg_statistic = Gtk.Label('adlk;fjalkdjfajdlkfj')
        self.pkg_statistic.set_use_markup(True)
        self.pkg_statistic.set_xalign(0.0)
        self.progress = Gtk.ProgressBar()
        self.progress.set_show_text(True)
        grid = Gtk.Grid()
        # grid.set_row_spacing(1)
        grid.set_column_spacing(10)
        grid.set_margin_left(10)
        grid.set_margin_right(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        grid.attach(self.pkg_statistic, 0, 0, 4, 1)
        grid.attach(self.progress, 4, 0, 6, 1)
        grid.show()
        self.box1.pack_start(grid, False, False, 0)
        self.show_all()
        self.initial_thread('initial')

    def all_or_installed(self, widget, data):
        if widget.get_active():
            self.available_or_installed = data
            self.treeview.set_cursor(1)
            self.treeview.set_cursor(0)
            if data == 'available':
                avail = self.available_pkg['avail']
                msg = "Packages available:"
                self.pkg_statistic.set_text(f'<small>{msg} {avail}</small>')
                self.pkg_statistic.set_use_markup(True)
            else:
                installed = self.installed_pkg['avail']
                msg = "Installed packages:"
                self.pkg_statistic.set_text(f'<small>{msg} {installed}</small>')
                self.pkg_statistic.set_use_markup(True)
            print(data)

    def sync_orgin(self):
        self.pkg_origin = available_package_origin()

    def sync_packages(self):
        self.installed_origin = isntalled_package_origin()
        self.installed_pkg = isntalled_package_dictionary(self.installed_origin)
        self.available_pkg = available_package_dictionary(self.pkg_origin)

    def update_progress(self, fraction, msg):
        self.progress.set_fraction(fraction)
        self.progress.set_text(msg)

    def sync_alvailable(self):
        self.progress.show()
        GLib.idle_add(self.update_progress, 0.4, 'store packages origin')
        self.category_store_sync2()
        # GObject.idle_add(self.category_store_sync2)
        avail = self.available_pkg['avail']
        msg = "Packages available:"
        self.pkg_statistic.set_text(f'<small>{msg} {avail}</small>')
        self.pkg_statistic.set_use_markup(True)
        GLib.idle_add(self.update_progress, 0.7, 'Loading all packages')
        # GObject.idle_add(self.store_all_pkgs)
        self.store_all_pkgs()
        GLib.idle_add(self.update_progress, 1.0, 'completed')
        self.progress.hide()
        GObject.idle_add(self.stop_tread)

    def available_thread(self):
        self.thr = threading.Thread(target=self.sync_alvailable, args=())
        self.thr.setDaemon(True)
        self.thr.start()

    def initial_sync(self):
        self.pkg_statistic.set_text('<small>Syncing statistic</small>')
        self.pkg_statistic.set_use_markup(True)
        self.progress.set_fraction(0.1)
        self.progress.set_text('syncing packages origins')
        self.sync_orgin()
        self.progress.set_fraction(0.3)
        self.progress.set_text('syncing packages data')
        self.sync_packages()
        self.progress.set_fraction(0.5)
        self.progress.set_text('store packages origin')
        self.category_store_sync()
        avail = self.available_pkg['avail']
        msg = "Packages available:"
        self.pkg_statistic.set_text(f'<small>{msg} {avail}</small>')
        self.pkg_statistic.set_use_markup(True)
        # self.progress.show()
        # self.progress.set_fraction(0.7)
        # self.progress.set_text('Loading all packages')
        # GObject.idle_add(self.store_all_pkgs)
        self.progress.set_fraction(1)
        self.progress.set_text('completed')
        self.progress.hide()
        GObject.idle_add(self.stop_tread)

    def stop_tread(self):
        self.thr.join()

    def initial_thread(self, sync):
        self.thr = threading.Thread(target=self.initial_sync, args=())
        self.thr.setDaemon(True)
        self.thr.start()
        # thr.join()

    def selected_software(self, view, event):
        selection = self.pkgtreeview.get_selection()
        (model, iter) = selection.get_selected()
        print(model[iter][1])

    def category_store_sync(self):
        self.store.clear()
        for category in self.pkg_origin:
            xmp_data = xpmPackageCategory()[category]
            xmp = GdkPixbuf.Pixbuf.new_from_xpm_data(xmp_data)
            self.store.append([xmp, category])
        self.treeview.set_cursor(0)

    def store_all_pkgs(self):
        self.pkg_store.clear()
        pixbuf = Gtk.IconTheme.get_default().load_icon('emblem-package', 42, 0)
        pkg_d = self.available_pkg['all']
        pkg_list = list(pkg_d.keys())
        pkg_list.sort()
        for pkg in pkg_list:
            version = pkg_d[pkg]['version']
            size = pkg_d[pkg]['size']
            installed = pkg_d[pkg]['installed']
            self.pkg_store.append([pixbuf, pkg, version, size, installed])

    def search_release(self, widget, event):
        searchs = widget.get_text()
        print(searchs)
        pixbuf = Gtk.IconTheme.get_default().load_icon('emblem-package', 42, 0)
        if len(searchs) > 1:
            self.pkg_store.clear()
            # xmp = GdkPixbuf.Pixbuf.new_from_xpm_data(softwareXpm())
            for pkg in search_packages(searchs):
                version = self.available_pkg['all'][pkg]['version']
                size = self.available_pkg['all'][pkg]['size']
                installed = self.available_pkg['all'][pkg]['installed']
                self.pkg_store.append([pixbuf, pkg, version, size, installed])

    def selection_category(self, tree_selection):
        (model, pathlist) = tree_selection.get_selected_rows()
        self.pkg_store.clear()
        path = pathlist[0]
        tree_iter = model.get_iter(path)
        value = model.get_value(tree_iter, 1)
        pixbuf = Gtk.IconTheme.get_default().load_icon('emblem-package', 42, 0)
        # xmp = GdkPixbuf.Pixbuf.new_from_xpm_data(softwareXpm())
        if self.available_or_installed == 'available':
            pkg_d = self.available_pkg[value]
        else:
            try:
                pkg_d = self.installed_pkg[value]
            except KeyError:
                pkg_d = {}
        pkg_list = list(pkg_d.keys())
        for pkg in pkg_list:
            version = pkg_d[pkg]['version']
            size = pkg_d[pkg]['size']
            installed = pkg_d[pkg]['installed']
            self.pkg_store.append([pixbuf, pkg, version, size, installed])

    def add_and_rm_pkg(self, cell, path, model):
        model[path][4] = not model[path][4]
        pkg = model[path][1]
        if pkg not in pkg_to_uninstall and pkg not in pkg_to_install:
            if model[path][4] is False:
                pkg_to_uninstall.extend([pkg])
            else:
                pkg_to_install.extend([pkg])
        else:
            if pkg in pkg_to_uninstall and model[path][4] is True:
                pkg_to_uninstall.remove(pkg)
            elif pkg in pkg_to_install and model[path][4] is False:
                pkg_to_install.remove(pkg)
        if pkg not in pkg_to_uninstall and pkg not in pkg_to_install:
            self.apply_button.set_sensitive(False)
            self.cancel_button.set_sensitive(False)
        else:
            self.apply_button.set_sensitive(True)
            self.cancel_button.set_sensitive(True)
        print('package to install', pkg_to_install)
        print('package to uninstall', pkg_to_uninstall)

    def MainBook(self):
        self.table = Gtk.Table(12, 10, True)
        self.table.show_all()
        category_sw = Gtk.ScrolledWindow()
        category_sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        category_sw.set_policy(Gtk.PolicyType.AUTOMATIC,
                               Gtk.PolicyType.AUTOMATIC)
        self.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.treeview = Gtk.TreeView(self.store)
        self.treeview.set_model(self.store)
        self.treeview.set_rules_hint(True)
        cell = Gtk.CellRendererPixbuf()
        column = Gtk.TreeViewColumn("Pixbuf", cell)
        column.add_attribute(cell, "pixbuf", 0)
        self.treeview.append_column(column)
        cell2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn(None, cell2, text=0)
        column2.set_attributes(cell2, text=1)
        self.treeview.append_column(column2)
        self.treeview.set_reorderable(True)
        self.treeview.set_headers_visible(False)
        self.category_tree_selection = self.treeview.get_selection()
        self.category_tree_selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.category_tree_selection.connect("changed", self.selection_category)
        category_sw.add(self.treeview)
        category_sw.show()

        pkg_sw = Gtk.ScrolledWindow()
        pkg_sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        pkg_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pkg_store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str, str, bool)
        self.pkgtreeview = Gtk.TreeView(self.pkg_store)
        self.pkgtreeview.set_model(self.pkg_store)
        self.pkgtreeview.set_rules_hint(True)
        # self.pkgtreeview.connect_after("button_press_event",
        #                                self.selected_software)
        self.pkgtreeview.connect_after("button_press_event",
                                       self.selected_software)
        self.check_cell = Gtk.CellRendererToggle()
        self.check_cell.set_property('activatable', True)
        self.check_cell.connect('toggled', self.add_and_rm_pkg, self.pkg_store)
        check_column = Gtk.TreeViewColumn("Check", self.check_cell)
        check_column.add_attribute(self.check_cell, "active", 4)
        self.pkgtreeview.append_column(check_column)
        pixbuf_cell = Gtk.CellRendererPixbuf()
        pixbuf_column = Gtk.TreeViewColumn('Icon', pixbuf_cell)
        pixbuf_column.add_attribute(pixbuf_cell, "pixbuf", 0)
        self.pkgtreeview.append_column(pixbuf_column)
        name_cell = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn('Package Name', name_cell, text=1)
        # name_column.set_sizing(Gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        name_column.set_fixed_width(250)
        name_column.set_sort_column_id(1)
        self.pkgtreeview.append_column(name_column)
        version_cell = Gtk.CellRendererText()
        version_column = Gtk.TreeViewColumn('Version', version_cell, text=2)
        version_column.set_fixed_width(150)
        version_column.set_sort_column_id(2)
        self.pkgtreeview.append_column(version_column)
        size_cell = Gtk.CellRendererText()
        size_column = Gtk.TreeViewColumn('Size', size_cell, text=3)
        size_column.set_sort_column_id(3)
        self.pkgtreeview.append_column(size_column)
        # self.pkgtreeview.set_headers_visible(False)
        self.pkg_tree_selection = self.pkgtreeview.get_selection()
        # self.pkg_tree_selection.set_mode(Gtk.SelectionMode.NONE)
        # tree_selection.connect("clicked", self.selected_software)
        pkg_sw.add(self.pkgtreeview)
        # iconview = Gtk.IconView.new()
        # iconview.set_model(self.pkg_store)
        # iconview.set_pixbuf_column(0)
        # iconview.set_text_column(1)
        # iconview.connect("item-activated", self.selected_software)
        # iconview.set_tooltip_column(2)
        # pkg_sw.add(iconview)
        pkg_sw.show()
        # table.attach(toolbar, 0, 10, 0, 2)
        self.table.attach(category_sw, 0, 2, 0, 12)
        self.table.attach(pkg_sw, 2, 10, 0, 12)
        self.show()
        return self.table


TableWindow()
Gtk.main()
