from enum import Enum

class ThemeVariant(Enum):
    SHADOW = "Shadow"
    ALPINE = "Alpine"
    DARK_MAGIC_GIRL = "Dark Magic Girl"
    SUPERUSER = "Superuser"
    SEWING_TIN_LIGHT = "Sewing Tin Light"
    MIAMI = "Miami"
    DOTS = "Dots"

    @staticmethod
    def from_str(theme):
        match str(theme).lower():
            case "shadow":
                return ThemeVariant.SHADOW
            case "alpine":
                return ThemeVariant.ALPINE
            case "dark magic girl":
                return ThemeVariant.DARK_MAGIC_GIRL
            case "superuser":
                return ThemeVariant.SUPERUSER
            case "sewing tin light":
                return ThemeVariant.SEWING_TIN_LIGHT
            case "miami":
                return ThemeVariant.MIAMI
            case "dots":
                return ThemeVariant.DOTS
            case _:
                raise NotImplementedError("This theme variant is not implemented")
            
    
class Theme():
    def __init__(self, figure_color, axes_color, title_color, ticks_color, xy_label_color, plot_color, scatter_color, hist_color, plot2_color, pb_color):
        self.figure_color = figure_color
        self.axes_color = axes_color
        self.title_color = title_color
        self.ticks_color = ticks_color
        self.xy_label_color = xy_label_color
        self.plot_color = plot_color
        self.scatter_color = scatter_color
        self.hist_color = hist_color
        self.plot2_color = plot2_color
        self.pb_color = pb_color
    
    @staticmethod
    def shadow():
        return Theme(
            figure_color = "black", 
            axes_color = "black", 
            title_color = "#444444", 
            ticks_color = "#444444", 
            xy_label_color = "#444444",
            plot_color = "magenta",
            scatter_color = "white",
            hist_color = "white",
            plot2_color = "white",
            pb_color = "red",
        )
    
    @staticmethod
    def alpine():
        return Theme(
            figure_color = "#6c687f", 
            axes_color = "#77738c", 
            title_color = "white", 
            ticks_color = "white", 
            xy_label_color = "white",
            plot_color = "red",
            scatter_color = "white",
            hist_color = "white",
            plot2_color = "white",
            pb_color = "blue",
        )
    
    @staticmethod
    def dark_magic_girl():
        return Theme(
            figure_color = "#071823", 
            axes_color = "#091f2c", 
            title_color = "white", 
            ticks_color = "white", 
            xy_label_color = "white",
            plot_color = "#81cfbe",
            scatter_color = "#f5b1cc",
            hist_color = "#f5b1cc",
            plot2_color = "#f5b1cc",
            pb_color = "#4373FF",
        )
    
    @staticmethod
    def superuser():
        return Theme(
            figure_color = "#1f232c", 
            axes_color = "#262a33", 
            title_color = "#43ffaf", 
            ticks_color = "#43ffaf", 
            xy_label_color = "#43ffaf",
            plot_color = "white",
            scatter_color = "#43ffaf",
            hist_color = "white",
            plot2_color = "#FF5F5F",
            pb_color = "#FF3AFF",
        )
    
    @staticmethod
    def sewing_tin_light():
        return Theme(
            figure_color = "#c8cedf", 
            axes_color = "#ffffff", 
            title_color = "#2d2076", 
            ticks_color = "#2d2076", 
            xy_label_color = "#2d2076",
            plot_color = "black",
            scatter_color = "#2d2076",
            hist_color = "#2d2076",
            plot2_color = "#2d2076",
            pb_color = "red",
        )
    
    @staticmethod
    def miami():
        return Theme(
            figure_color = "#0f0f10", 
            axes_color = "#18181a", 
            title_color = "#e4609b", 
            ticks_color = "#e4609b", 
            xy_label_color = "#e4609b",
            plot_color = "white",
            scatter_color = "#05DFD7",
            hist_color = "#05DFD7",
            plot2_color = "#05DFD7",
            pb_color = "#e4609b",
        )
    
    @staticmethod
    def dots():
        return Theme(
            figure_color = "#0E1019", 
            axes_color = "#121520", 
            title_color = "#616883", 
            ticks_color = "#616883", 
            xy_label_color = "#616883",
            plot_color = "white",
            scatter_color = "#DA3333",
            hist_color = "#DA3333",
            plot2_color = "#DA3333",
            pb_color = "#007300",
        )
    
    @staticmethod
    def from_variant(variant: ThemeVariant):
        match variant:
            case ThemeVariant.SHADOW:
                return Theme.shadow()
            case ThemeVariant.ALPINE:
                return Theme.alpine()
            case ThemeVariant.DARK_MAGIC_GIRL:
                return Theme.dark_magic_girl()
            case ThemeVariant.SUPERUSER:
                return Theme.superuser()
            case ThemeVariant.SEWING_TIN_LIGHT:
                return Theme.sewing_tin_light()
            case ThemeVariant.MIAMI:
                return Theme.miami()
            case ThemeVariant.DOTS:
                return Theme.dots()
            case _:
                raise NotImplementedError("No support for this theme")
                   