import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy
from PyQt6 import QtGui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

from ui.main_window_ui import Ui_MainWindow
from livesplit_data import LiveSplitData
from plot import Plot
from theme import Theme


class Window(QMainWindow, Ui_MainWindow):
    optionButtons: list[QPushButton] = []
    graphWidgets: list = []
    toolbars:list = []
    lsd: LiveSplitData|None = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Livesplit Graphs")

        self.listSplits.clear()
        self.statusbar.hide()
        self.setOptionButtons()
        self.connectSignalsSlots()

        # REMOVE testing
        self.lsd = LiveSplitData("trevis.lss")
        self.loadSplitsList()
        #self.option_impOverTime.click()

    def connectSignalsSlots(self):
        self.actionOpen.triggered.connect(self.selectFile)
        self.listSplits.itemClicked.connect(self.loadGraph)
        self.check_showOutliers.clicked.connect(self.outliers)
        self.option_hist.clicked.connect(self.loadGraph)
        self.option_movingAvg.clicked.connect(self.loadGraph)
        self.option_attemptsOverTime.clicked.connect(self.loadGraph)
        self.option_impOverTime.clicked.connect(self.loadGraph)
        self.option_impOverAttempts.clicked.connect(self.loadGraph)
        self.option_finishedRunsOverTime.clicked.connect(self.loadGraph)
        self.option_personalBestOverAttempts.clicked.connect(self.loadGraph)
        self.option_personalBestOverTime.clicked.connect(self.loadGraph)
        self.color_options.currentIndexChanged.connect(self.loadGraph)
    
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
        for option in self.optionButtons:
            if option.isChecked():
                graphChoice = option.text()
                break
        else:
            # no option selected
            return

        self.removeOldGraph()
        self.removeOldToolbar()

        if self.listSplits.currentItem() is None:
            if self.lsd is None:
                return
            self.listSplits.setCurrentRow(0)

        showOutliers = self.check_showOutliers.isChecked()
        splitName = self.listSplits.currentItem().text()
        graphTheme: Theme = self.setTheme(self.color_options.currentText())
        
        

        self.lsd.extract_segment_data(splitName)
        plot = Plot(self.lsd, splitName, graphTheme, showOutliers)

        match graphChoice:
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
        
        plt.grid()
        plt.tight_layout()
        graph = FigureCanvasQTAgg(fig)
        graph.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding))

        toolbar = NavigationToolbar(graph, self)
        toolbar.setStyleSheet("background-color: white;")

        self.placeholder.setParent(None)

        self.graphWidgets.append(graph)
        self.toolbars.append(toolbar)
        self.graph_layout.addWidget(toolbar)
        self.graph_layout.addWidget(graph)     

    def outliers(self):
        if len(self.graphWidgets) != 0:
            self.loadGraph()

    def setOptionButtons(self):
        for i in range(self.options_gridLayout.count()):
            widget = self.options_gridLayout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                self.optionButtons.append(widget)
            
    def removeOldGraph(self):
        plt.close("all")
        if len(self.graphWidgets) != 0:
            lastGraph = self.graphWidgets.pop()
            lastGraph.setParent(None)
            self.graph_layout.removeWidget(lastGraph)
            
    def removeOldToolbar(self):
        if len(self.toolbars) != 0:
            lastToolbar = self.toolbars.pop()
            lastToolbar.setParent(None)
            self.graph_layout.removeWidget(lastToolbar)
    
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