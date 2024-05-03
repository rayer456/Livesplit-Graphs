from enum import Enum, unique

@unique
class Graph(Enum):
    HISTOGRAM = "Histogram"
    MOVING_AVERAGE = "Moving Average"
    ATTEMPTS_OVER_TIME = "Attempts Over Time"
    IMP_OVER_TIME = "Improvement Over Time"
    IMP_OVER_ATTEMPTS = "Improvement Over Attempts"
    PB_OVER_TIME = "PB Over Time"
    PB_OVER_ATTEMPTS = "PB Over Attempts"

    @staticmethod
    def from_str(label):
        match str(label).lower():
            case 'hist'|'histogram':
                return Graph.HISTOGRAM
            case 'moving avg'|'moving average':
                return Graph.MOVING_AVERAGE
            case 'attempts over time'|'aot':
                return Graph.ATTEMPTS_OVER_TIME
            case 'imp over time'|'improvement over time':
                return Graph.IMP_OVER_TIME
            case 'imp over attempts'|'improvement over attempts':
                return Graph.IMP_OVER_ATTEMPTS
            case 'pb over time':
                return Graph.PB_OVER_TIME
            case 'pb over attempts':
                return Graph.PB_OVER_ATTEMPTS
            case _:
                raise NotImplementedError("This graph is not implemented")
