import sys
import gc

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy, QButtonGroup, QWidget
from PyQt6 import QtGui
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

from ui.main_window_ui import Ui_MainWindow
from livesplit_data import LiveSplitData
from plot import Plot
from theme import Theme, ThemeVariant
from graph import Graph


class Window(QMainWindow, Ui_MainWindow):
    currentGraph: FigureCanvasQTAgg | None = None
    currentToolbar: NavigationToolbar | None = None
    lsd: LiveSplitData | None = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Livesplit Graphs")
        self.loadThemes()

        self.listSplits.clear()
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
    
    def loadThemes(self):
        for variant in ThemeVariant:
            self.color_options.addItem(variant.value)

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

        # remove old graph or placeholder
        self.removeGraphAndToolbar()

        # define new graph and toolbar
        fig = self.getFigure(Graph(checkedButton.text()))
        self.currentGraph = FigureCanvasQTAgg(fig)
        self.currentGraph.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding))
        self.currentToolbar = NavigationToolbar(canvas=self.currentGraph, parent=self)
        self.currentToolbar.setStyleSheet("background-color: white;")

        # TODO why is this here?
        plt.grid()
        plt.tight_layout()

        # add new graph to layout
        self.graph_layout.addWidget(self.currentToolbar)
        self.graph_layout.addWidget(self.currentGraph)     
            
    def getFigure(self, graph: Graph) -> Figure:
        plot = Plot(
            livesplit_data=self.lsd, 
            split_name=self.listSplits.currentItem().text(), 
            split_index=self.listSplits.currentRow(),
            theme=self.getTheme(self.color_options.currentText()), 
            show_outliers=self.check_showOutliers.isChecked()
        )

        # generate figure object
        match graph:
            case Graph.HISTOGRAM:
                self.lsd.extract_segment_data(
                    segment_index=self.listSplits.currentRow(),
                    show_outliers=self.check_showOutliers.isChecked(),
                )

                fig = plot.hist(self.lsd.segment_times["seg_times"])
            case Graph.MOVING_AVERAGE:
                self.lsd.extract_segment_data(
                    segment_index=self.listSplits.currentRow(),
                    show_outliers=self.check_showOutliers.isChecked(),
                )
        
                fig = plot.moving_avg(self.lsd.segment_times, self.lsd.avg_segment_times)

                # have to call this here, doesn't work in Plot class
                fig.canvas.mpl_connect("motion_notify_event", lambda event=None : plot.hover_scatter(event))
            case Graph.ATTEMPTS_OVER_TIME:
                fig = plot.attempts_over_time()
                fig.canvas.mpl_connect("motion_notify_event", lambda event=None : plot.hover_plot(event, graph=Graph.ATTEMPTS_OVER_TIME))
            case Graph.IMP_OVER_ATTEMPTS:
                fig = plot.imp_over_attempts()
            case Graph.IMP_OVER_TIME: 
                fig = plot.imp_over_time()
            case Graph.PB_OVER_TIME:
                fig = plot.personal_best_over_time()
                fig.canvas.mpl_connect("motion_notify_event", lambda event=None : plot.hover_plot(event, graph=Graph.PB_OVER_TIME))
            case Graph.PB_OVER_ATTEMPTS:
                fig = plot.personal_best_over_attempts()
                fig.canvas.mpl_connect("motion_notify_event", lambda event=None : plot.hover_plot(event, graph=Graph.PB_OVER_ATTEMPTS))
            case _:
                NotImplementedError("Graph not implemented.")
                return
        
        return fig

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
        self.graph_placeholder.setParent(None)
        gc.collect()
    
    def getTheme(self, theme_str: str):
        theme_variant = ThemeVariant.from_str(theme_str)
        return Theme.from_variant(theme_variant)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())