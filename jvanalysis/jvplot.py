import numpy as np
from jvanalysis.analysis import Analysis, AnalysisError
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d
from bokeh.resources import INLINE

DATA_FOLDER = "/home/ubuntu/workspace/jvanalysis/data"
TOOLS = "wheel_zoom,box_zoom,reset,save"

def resources():
    """ return bokeh resources for plot
    """
    data1 = np.transpose(np.loadtxt("/home/ubuntu/workspace/jvanalysis/data/D1_OCtoSC_SR500mVps.txt"))
    data2 = np.transpose(np.loadtxt("/home/ubuntu/workspace/jvanalysis/data/D1_SCtoOC_SR500mVps.txt"))
    plot = figure(
                    title="Current vs Voltage Curves of DSSCS", 
                    tools=TOOLS,
                    plot_width=400, 
                    plot_height=400
                )
    plot.line(data1[0], data1[1] * 1000 / 0.25, legend="D1_OCtoSC_SR500mVps", line_color="blue", line_width=2)
    plot.line(data2[0], data2[1] * 1000 / 0.25, legend="D1_SCtoOC_SR500mVps", line_color="red", line_width=2)    
    plot.x_range = Range1d(-0.6, 0.1)
    plot.y_range = Range1d(-5, 20)
    plot.legend.location = "bottom_right"
    plot.xaxis.axis_label = "Voltage (V)"
    plot.yaxis.axis_label = r"Current Density (mA/cm^2)"
    
    script, div = components(plot)
    bkjs=INLINE.render_js()
    bkcss=INLINE.render_css()
    
    return (div, script, bkjs, bkcss)