import sys
import gc

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy, QButtonGroup, QWidget
from PyQt6 import QtGui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

from ui.main_window_ui import Ui_MainWindow
from livesplit_data import LiveSplitData
from plot import Plot
from theme import Theme


class Window(QMainWindow, Ui_MainWindow):
    currentGraph: QWidget | None = None
    currentToolbar: NavigationToolbar | None = None
    lsd: LiveSplitData | None = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Livesplit Graphs")

        self.listSplits.clear()
        self.statusbar.hide()
        self.connectSignalsSlots()

        # REMOVE testing
        self.lsd = LiveSplitData("E:/Livesplit-new/layouts/Grand Theft Auto V - Trevor%.lss")
        self.loadSplitsList()

    def connectSignalsSlots(self):
        self.actionOpen.triggered.connect(self.selectFile)
        self.listSplits.itemClicked.connect(self.loadGraph)
        self.check_showOutliers.clicked.connect(self.loadGraph)
        self.color_options.currentIndexChanged.connect(self.loadGraph)
        self.option_buttons.buttonClicked.connect(self.loadGraph)
    
    def selectFile(self):
        fileDialog = QFileDialog.getOpenFileName(
            self,
            caption="Select a Livesplit file",
            filter="*.lss"
        )
        livesplit_path = fileDialog[0]

        if livesplit_path != "":
            self.lsd = LiveSplitData(livesplit_path)
            self.loadSplitsList()
        
    def loadSplitsList(self):
        self.listSplits.clear()
        self.listSplits.addItems(self.lsd.split_names)
    
    def loadGraph(self):
        checkedButton = self.option_buttons.checkedButton()
        if checkedButton is None or self.lsd is None:
            return
        
        if self.listSplits.currentItem() is None:
            self.listSplits.setCurrentRow(0)

        plot = Plot(
            livesplit_data=self.lsd, 
            split_name=self.listSplits.currentItem().text(), 
            theme=self.setTheme(self.color_options.currentText()), 
            show_outliers=self.check_showOutliers.isChecked()
        )

        match checkedButton.text():
            case "Histogram":
                fig = plot.hist()
            case "Moving Average":
                fig = plot.moving_avg()
            case "Attempts Over Time":
                fig = plot.attempts_over_time()
            case "Improvement Over Attempts":
                fig = plot.imp_over_attempts()
            case "Improvement Over Time":
                fig = plot.imp_over_time()
            case "Finished Runs Over Time":
                fig = plot.finished_runs_over_time()
            case "PB Over Time":
                fig = plot.personal_best_over_time()
            case "PB Over Attempts":
                fig = plot.personal_best_over_attempts()
            case _:
                print("Forgot to add case")
                return
        
        # TODO why is this here?
        plt.grid()
        plt.tight_layout()

        # remove old graph or placeholder
        self.removeGraphAndToolbar()
        self.graph_placeholder.setParent(None)

        # define new graph and toolbar
        self.currentGraph = FigureCanvasQTAgg(fig)
        self.currentGraph.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding))
        self.currentToolbar = NavigationToolbar(canvas=self.currentGraph, parent=self)
        self.currentToolbar.setStyleSheet("background-color: white;")

        # add new graph to layout
        self.graph_layout.addWidget(self.currentToolbar)
        self.graph_layout.addWidget(self.currentGraph)     
    
            
    def removeCurrentGraph(self):
        if self.currentGraph is None:
            return

        plt.close("all")
        self.currentGraph.setParent(None)
        self.graph_layout.removeWidget(self.currentGraph)
        self.currentGraph = None
            
    def removeCurrentToolbar(self):
        if self.currentToolbar is None:
            return
        
        self.currentToolbar.setParent(None)
        self.graph_layout.removeWidget(self.currentToolbar)
        self.currentToolbar = None

    def removeGraphAndToolbar(self):
        self.removeCurrentGraph()
        self.removeCurrentToolbar()
        gc.collect()
    
    def setTheme(self, theme):
        match theme:
            case "Shadow":
                return Theme(
                    figure_color = "black", 
                    axes_color = "black", 
                    title_color = "white", 
                    ticks_color = "white", 
                    xy_label_color = "white",
                    plot_color = "magenta",
                    scatter_color = "white",
                    hist_color = "white"
                )
            case "Alpine":
                return Theme(
                    figure_color = "#6c687f", 
                    axes_color = "#77738c", 
                    title_color = "white", 
                    ticks_color = "white", 
                    xy_label_color = "white",
                    plot_color = "red",
                    scatter_color = "white",
                    hist_color = "white"
                )
            case "Dark Magic Girl":
                return Theme(
                    figure_color = "#071823", 
                    axes_color = "#091f2c", 
                    title_color = "white", 
                    ticks_color = "white", 
                    xy_label_color = "white",
                    plot_color = "#81cfbe",
                    scatter_color = "#f5b1cc",
                    hist_color = "#f5b1cc"
                )
            case "Superuser":
                return Theme(
                    figure_color = "#1f232c", 
                    axes_color = "#262a33", 
                    title_color = "#43ffaf", 
                    ticks_color = "#43ffaf", 
                    xy_label_color = "#43ffaf",
                    plot_color = "white",
                    scatter_color = "#43ffaf",
                    hist_color = "white"
                )
            case "Sewing Tin Light":
                return Theme(
                    figure_color = "#c8cedf", 
                    axes_color = "#ffffff", 
                    title_color = "#2d2076", 
                    ticks_color = "#2d2076", 
                    xy_label_color = "#2d2076",
                    plot_color = "black",
                    scatter_color = "#2d2076",
                    hist_color = "#2d2076"
                )
            case "Miami":
                return Theme(
                    figure_color = "#0f0f10", 
                    axes_color = "#18181a", 
                    title_color = "#e4609b", 
                    ticks_color = "#e4609b", 
                    xy_label_color = "#e4609b",
                    plot_color = "white",
                    scatter_color = "#e4609b",
                    hist_color = "#e4609b"
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())