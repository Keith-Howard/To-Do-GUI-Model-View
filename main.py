import sys
import json
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

qt_creator_file = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
tick = QtGui.QImage('tick.png')


class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, data_file, *args, todos=None, **kwargs):
        super(TodoModel, self).__init__(*args, **kwargs)
        self.todos = todos or []
        self.data_file = data_file

    def data(self, index, role):
        if role == Qt.DisplayRole:
            _, text = self.todos[index.row()]
            return text

        if role == Qt.DecorationRole:
            status, _ = self.todos[index.row()]
            if status:
                return tick

    def load(self):
        try:
            with open(self.data_file, 'r') as f:
                self.todos = json.load(f)
        except Exception:
            pass

    def save(self):
        with open(self.data_file, 'w') as f:
            data = json.dump(self.todos, f)

    def add_todo(self, text):
        self.todos.append((False, text))

    def set_row_action(self, row, action):
        status, text = self.todos[row]
        if action == "complete":
            self.todos[row] = (True, text)
        else:
            self.todos[row] = (False, text)

    def rowCount(self, index):
        return len(self.todos)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, data_file):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.model = TodoModel(data_file)
        self.model.load()
        self.todoView.setModel(self.model)
        self.addButton.pressed.connect(self.add)
        self.deleteButton1.pressed.connect(self.delete)
        self.completeButton.pressed.connect(self.complete)
        self.uncheckButton.pressed.connect(self.uncheck)

    def add(self):
        """
        Add an item to our todo list, getting the text from the QLineEdit .todoEdit
        and then clearing it.
        """
        text = self.todoEdit.text()
        if text:  # Don't add empty strings.
            # Access the list via the model.
            text = text.strip()
            if len(text) > 0:
                self.model.add_todo(text)
                # Trigger refresh.
                self.model.layoutChanged.emit()
                #  Empty the input
                self.todoEdit.setText("")
                self.model.save()

    def delete(self):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model.todos[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()
            self.model.save()

    def update_completion_status(self, method):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            self.model.set_row_action(row, method)
            # .dataChanged takes top-left and bottom right, which are equal
            # for a single selection.
            self.model.dataChanged.emit(index, index)
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()
            self.model.save()

    def complete(self):
        self.update_completion_status('complete')

    def uncheck(self):
        self.update_completion_status('uncheck')


app = QtWidgets.QApplication(sys.argv)
window = MainWindow('data.db')
window.show()
app.exec_()
