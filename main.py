#!/usr/bin/env python3
import os
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QMessageBox,
    QStyle,
    QAbstractItemView,
    QLabel,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QPainter, QIcon

def set_dark_theme(app: QApplication):
    """Sets a dark theme for the application by configuring the QPalette."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)

STYLE_SHEET = """
/* Dark theme for buttons */
QPushButton {
    background-color: #2b2b2b;
    border: 1px solid #3d3d3d;
    padding: 5px;
    min-width: 30px;
    color: white;
}

QPushButton:hover {
    background-color: #3d3d3d;
}

/* Dark theme for scrollbars */
QScrollBar:vertical {
    border: none;
    background: #2b2b2b;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #666666;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* Dark theme for line edit */
QLineEdit {
    background-color: #2b2b2b;
    border: 1px solid #3d3d3d;
    color: white;
    padding: 5px;
}

/* Dark theme for tree widget header */
QHeaderView::section {
    background-color: #2b2b2b;
    color: white;
    padding: 5px;
    border: 1px solid #3d3d3d;
}

QTreeWidget {
    border: 1px solid #3d3d3d;
    background-color: #1e1e1e;
}

/* Dark theme for dialog windows */
QMessageBox, QDialog {
    background-color: #2b2b2b;
    color: white;
}

QMessageBox QLabel, QDialog QLabel {
    color: white;
}

QMessageBox QPushButton, QDialog QPushButton {
    min-width: 70px;
    padding: 5px 15px;
}

QFileDialog {
    background-color: #2b2b2b;
    color: white;
}

QFileDialog QTreeView, QFileDialog QListView {
    background-color: #1e1e1e;
    color: white;
    border: 1px solid #3d3d3d;
}

QFileDialog QTreeView::item:selected, QFileDialog QListView::item:selected {
    background-color: #404040;
}

/* Dark theme for horizontal scrollbars */
QScrollBar:horizontal {
    border: none;
    background: #2b2b2b;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #666666;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""

class QProgressIndicator(QLabel):
    """A simple loading spinner widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(100, 100)
        self.hide()

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def start(self):
        if self.parentWidget():
            x = (self.parentWidget().width() - self.width()) // 2
            y = (self.parentWidget().height() - self.height()) // 2
            self.move(x, y)
        self.show()
        self.timer.start(100)

    def stop(self):
        self.timer.stop()
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background (spinner circle) with rounded corners
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

        painter.save()
        # Translate to center of the widget for rotation
        center = self.rect().center()
        painter.translate(center)
        painter.rotate(self.angle)

        # Setup font and color for the spinner text
        font = painter.font()
        font.setPointSize(48)
        painter.setFont(font)
        painter.setPen(QColor("white"))

        # Get bounding rect for "⟳" and draw text centered at (0,0)
        text = "⟳"
        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(text)
        painter.drawText(-text_rect.center().x(), -text_rect.center().y(), text)
        painter.restore()

class MyTreeWidgetItem(QTreeWidgetItem):
    def __lt__(self, other):
        # Get current sort column from the header
        column = self.treeWidget().header().sortIndicatorSection()
        if column == 1:  # "Size" column: compare numeric file sizes stored in UserRole
            self_value = self.data(1, Qt.ItemDataRole.UserRole)
            other_value = other.data(1, Qt.ItemDataRole.UserRole)
            try:
                return float(self_value) < float(other_value)
            except (ValueError, TypeError):
                pass
        return super().__lt__(other)

class DirectoryScanner(QThread):
    """Worker thread for scanning directory contents"""
    finished = pyqtSignal()  # Signal when scanning is complete
    item_found = pyqtSignal(str, str, bool)  # Signal for each found item (name, size, isDir)
    error = pyqtSignal(str)  # Signal for errors

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def calculate_size(self, path):
        """Recursive size calculation"""
        total_size = 0
        if os.path.isfile(path):
            try:
                total_size += os.path.getsize(path)
            except Exception:
                pass
        elif os.path.isdir(path):
            try:
                for entry in os.scandir(path):
                    total_size += self.calculate_size(entry.path)
            except Exception:
                pass
        return total_size

    def run(self):
        try:
            entries = os.listdir(self.folder_path)
            for entry in entries:
                full_path = os.path.join(self.folder_path, entry)
                size = self.calculate_size(full_path)
                is_dir = os.path.isdir(full_path)
                self.item_found.emit(entry, str(size), is_dir)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class MoveWorker(QThread):
    """Worker thread for performing safe move (copy then delete) operations."""
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, items, src_folder, dest_folder, parent=None):
        super().__init__(parent)
        self.items = items
        self.src_folder = src_folder
        self.dest_folder = dest_folder

    def run(self):
        import shutil
        try:
            for item in self.items:
                src = os.path.join(self.src_folder, item)
                dest = os.path.join(self.dest_folder, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dest)
                    os.remove(src)
                elif os.path.isdir(src):
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                    shutil.rmtree(src)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class PaneWidget(QWidget):
    """
    A widget representing one pane (either left or right) containing:
     - Top Row: folder selection, current folder path, reload & delete buttons.
     - Middle Row: a tree view showing the folder's contents.
     - Bottom Row: move button to transfer selected items between panes.
    """
    def __init__(self, side: str, parent=None):
        super().__init__(parent)
        self.side = side  # "left" or "right"
        self.init_ui()
        # Reparent the spinner to the pane (self) so it is not obscured by the tree widget's viewport
        self.loading_indicator = QProgressIndicator(self)
        # Set the fixed size for the spinner; it will be repositioned in resizeEvent
        self.loading_indicator.setGeometry(0, 0, 100, 100)

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # --- Top Row ---
        self.topRow = QHBoxLayout()
        # Folder selection button
        self.folderButton = QPushButton()
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.folderButton.setIcon(folder_icon)
        self.folderButton.clicked.connect(self.select_folder)
        self.topRow.addWidget(self.folderButton)

        # Parent folder navigation button
        self.parentButton = QPushButton()
        parent_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogToParent)
        self.parentButton.setIcon(parent_icon)
        self.parentButton.clicked.connect(self.go_to_parent_folder)
        self.topRow.addWidget(self.parentButton)

        # Text field displaying current folder path
        self.folderLineEdit = QLineEdit()
        self.topRow.addWidget(self.folderLineEdit)

        # Reload button
        self.reloadButton = QPushButton()
        reload_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.reloadButton.setIcon(reload_icon)
        self.reloadButton.clicked.connect(self.reload_folder)
        self.topRow.addWidget(self.reloadButton)

        # Delete button
        self.deleteButton = QPushButton()
        delete_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.deleteButton.setIcon(delete_icon)
        self.deleteButton.clicked.connect(self.delete_selected)
        self.topRow.addWidget(self.deleteButton)

        self.layout.addLayout(self.topRow)

        # --- Middle Row: Tree View ---
        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(["Name", "Size"])
        self.treeWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeWidget.setSortingEnabled(True)  # Enable sorting
        header = self.treeWidget.header()
        # Don't automatically stretch the last column.
        header.setStretchLastSection(False)
        # Set the "Name" column (index 0) to Stretch mode so it always fills the remaining space.
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # Set the "Size" column (index 1) to Interactive so the user can manually resize it.
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(1, 80)
        # Set initial sort indicator
        header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        # Connect header clicks to our sorting handler
        header.sectionClicked.connect(self.handle_header_clicked)
        # Enable double-click navigation in the tree view
        self.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.layout.addWidget(self.treeWidget)

        # --- Bottom Row: Move and Tree Buttons ---
        self.bottomRow = QHBoxLayout()
        self.moveButton = QPushButton(">" if self.side == "left" else "<")
        self.moveButton.clicked.connect(self.move_items)
        self.treeButton = QPushButton()
        # Use a standard icon for a detailed view as a substitute for a tree icon.
        tree_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.treeButton.setIcon(tree_icon)
        self.treeButton.clicked.connect(self.copy_folder_tree)
        self.bottomRow.addStretch()
        self.bottomRow.addWidget(self.moveButton)
        self.bottomRow.addWidget(self.treeButton)
        self.bottomRow.addStretch()
        self.layout.addLayout(self.bottomRow)

    def select_folder(self):
        """Opens a folder selection dialog and loads the selected folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.expanduser("~"))
        if folder:
            self.folderLineEdit.setText(folder)
            self.load_directory(folder)

    def load_directory(self, folder):
        """
        Loads the contents of the given folder into the tree view.
        Uses a separate thread for directory scanning.
        """
        self.treeWidget.clear()
        if not os.path.isdir(folder):
            return

        self.loading_indicator.start()
        self.treeWidget.setEnabled(False)

        # Create and configure the scanner thread
        self.scanner = DirectoryScanner(folder)
        
        def on_item_found(name, size, is_dir):
            numeric_size = float(size)
            item = MyTreeWidgetItem([name, self.calculate_size(numeric_size)])
            # Store the raw size as numeric value in UserRole for sorting
            item.setData(1, Qt.ItemDataRole.UserRole, numeric_size)
            if is_dir:
                folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
                item.setIcon(0, folder_icon)
                item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicator)
            self.treeWidget.addTopLevelItem(item)

        def on_error(error_msg):
            QMessageBox.critical(self, "Error", f"Could not list directory: {error_msg}")

        def on_finished():
            self.loading_indicator.stop()
            self.treeWidget.setEnabled(True)
            self.scanner = None

        self.scanner.item_found.connect(on_item_found)
        self.scanner.error.connect(on_error)
        self.scanner.finished.connect(on_finished)
        QTimer.singleShot(0, self.scanner.start)

    def calculate_size(self, size, decimal_places=2):
        """Formats the size in bytes into a human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0
        return f"{size:.{decimal_places}f} PB"

    def reload_folder(self):
        """Reloads the current folder indicated in the text field."""
        folder = self.folderLineEdit.text()
        if folder:
            self.load_directory(folder)

    def delete_selected(self):
        """
        Asks for confirmation before deleting selected items from
        both the file system and the view.
        """
        items = self.treeWidget.selectedItems()
        if not items:
            return

        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            "Are you sure you want to delete the selected items? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            folder = self.folderLineEdit.text().strip()
            for item in items:
                full_path = os.path.join(folder, item.text(0))
                try:
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    elif os.path.isdir(full_path):
                        import shutil
                        shutil.rmtree(full_path)
                except Exception as e:
                    QMessageBox.warning(self, "Delete Error", f"Error deleting '{full_path}':\n{e}")

                # Remove item from view
                index = self.treeWidget.indexOfTopLevelItem(item)
                if index != -1:
                    self.treeWidget.takeTopLevelItem(index)
                else:
                    parent = item.parent()
                    if parent:
                        parent.removeChild(item)

    def move_items(self):
        """
        Moves the selected items from this pane to the other pane
        using a safe move (copy then delete) operation in the file system.
        After the move, both panes are refreshed.
        """
        items = self.treeWidget.selectedItems()
        if not items:
            return
        moved_items = [item.text(0) for item in items]
        direction = "to right" if self.side == "left" else "to left"
        reply = QMessageBox.question(
            self,
            "Confirm Move",
            f"Are you sure you want to move items {moved_items} {direction} pane?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Get the source and destination folders from the text fields.
        src_folder = self.folderLineEdit.text().strip()
        dest_folder = self.otherPane.folderLineEdit.text().strip() if hasattr(self, "otherPane") else ""
        if not src_folder or not dest_folder:
            QMessageBox.critical(self, "Error", "Both source and destination folders must be set.")
            return

        # Start the move operation in a background thread.
        self.loading_indicator.start()
        self.treeWidget.setEnabled(False)
        if hasattr(self.otherPane, "treeWidget"):
            self.otherPane.treeWidget.setEnabled(False)

        self.move_worker = MoveWorker(moved_items, src_folder, dest_folder)
        self.move_worker.error.connect(lambda err: QMessageBox.critical(self, "Move Error", err))

        def on_finished():
            self.loading_indicator.stop()
            self.treeWidget.setEnabled(True)
            if hasattr(self.otherPane, "treeWidget"):
                self.otherPane.treeWidget.setEnabled(True)
            self.move_worker = None
            # Refresh both panes to display updated folder contents.
            self.reload_folder()
            if hasattr(self, "otherPane"):
                self.otherPane.reload_folder()

        self.move_worker.finished.connect(on_finished)
        self.move_worker.start()

    def handle_header_clicked(self, index):
        """
        Sorts the tree when a header is clicked.
        When index 0 ("Name") is clicked, sort ascending by name.
        When index 1 ("Size") is clicked, sort descending by filesize.
        """
        if index == 0:
            self.treeWidget.sortItems(0, Qt.SortOrder.AscendingOrder)
        elif index == 1:
            self.treeWidget.sortItems(1, Qt.SortOrder.DescendingOrder)

    def copy_folder_tree(self):
        """
        Generates an ASCII tree only for the selected items in the view.
        For a selected folder, recursively traverses its subfolders/files.
        Copies the resulting tree to the system clipboard and displays a success message.
        """
        folder = self.folderLineEdit.text().strip()
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Error", "Please select a valid folder first.")
            return

        selected_items = self.treeWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "No items selected.")
            return

        tree_lines = []
        for idx, item in enumerate(selected_items):
            name = item.text(0)
            full_path = os.path.join(folder, name)
            # Use a connector for the top-level selected item
            connector = "└─ " if idx == len(selected_items) - 1 else "├─ "
            tree_lines.append(connector + name)
            if os.path.isdir(full_path):
                # Determine extra prefix based on connector for the top-level item.
                # Use 3 characters: "   " for last items and "│  " for non-last.
                extra_prefix = "   " if connector.startswith("└") else "│  "
                # Pass the extra prefix into build_ascii_tree so that the branches appear properly.
                sub_lines = self.build_ascii_tree(full_path, prefix=extra_prefix)
                tree_lines.extend(sub_lines)

        tree_str = "\n".join(tree_lines)
        clipboard = QApplication.clipboard()
        clipboard.setText(tree_str)
        QMessageBox.information(self, "Copied", "Folder tree copied to clipboard!")

    def build_ascii_tree(self, path, prefix=""):
        """
        Recursively builds an ASCII representation of the folder tree.
        """
        lines = []
        try:
            entries = sorted(os.listdir(path))
        except Exception as e:
            lines.append(prefix + f"Error accessing {path}: {e}")
            return lines

        for idx, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            connector = "└─ " if idx == len(entries) - 1 else "├─ "
            lines.append(prefix + connector + entry)
            if os.path.isdir(full_path):
                # Determine extra prefix based on connector for the top-level item.
                # Use 3 characters: "   " for last items and "│  " for non-last.
                extra_prefix = "   " if connector.startswith("└") else "│  "
                # Pass the extra prefix into build_ascii_tree so that the branches appear properly.
                sub_lines = self.build_ascii_tree(full_path, prefix + extra_prefix)
                lines.extend(sub_lines)
        return lines

    def go_to_parent_folder(self):
        """
        Navigates to the parent folder of the current folder.
        """
        current = self.folderLineEdit.text().strip()
        if not current:
            return
        parent_folder = os.path.dirname(current)
        if parent_folder and os.path.isdir(parent_folder):
            self.folderLineEdit.setText(parent_folder)
            self.load_directory(parent_folder)
        else:
            QMessageBox.information(self, "Info", "No parent folder available.")

    def on_item_double_clicked(self, item, column):
        """
        When an item is double-clicked, if it represents a folder,
        navigate into that folder.
        """
        folder = self.folderLineEdit.text().strip()
        if not folder or not os.path.isdir(folder):
            return
        subfolder = os.path.join(folder, item.text(0))
        if os.path.isdir(subfolder):
            self.folderLineEdit.setText(subfolder)
            self.load_directory(subfolder)

class MainWindow(QMainWindow):
    """
    The main application window containing two resizable panes
    (left and right) side by side.
    """
    def __init__(self):
        super().__init__()
        import sys, os
        if getattr(sys, "frozen", False):
            # The application is running in frozen mode, so the bundled files
            # are in a temporary folder accessible via sys._MEIPASS
            base_path = sys._MEIPASS
        else:
            # Running as a script
            base_path = os.path.abspath(".")
        icon_path = os.path.join(base_path, "assets", "folder.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet(STYLE_SHEET)
        self.setWindowTitle("SubfolderSize GUI")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Create left and right panes.
        self.leftPane = PaneWidget("left")
        self.rightPane = PaneWidget("right")

        # Link the panes so each knows its counterpart.
        self.leftPane.otherPane = self.rightPane
        self.rightPane.otherPane = self.leftPane

        main_layout.addWidget(self.leftPane)
        main_layout.addWidget(self.rightPane)
        # Each pane gets equal space.
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_dark_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())