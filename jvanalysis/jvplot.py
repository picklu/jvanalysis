import numpy as np
from jvanalysis.analysis import Analysis, AnalysisError
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d, Span
from bokeh.resources import INLINE


DATA_FOLDER = "/home/ubuntu/workspace/jvanalysis/data"
TOOLS = "wheel_zoom,box_zoom,reset,save"

def resources(width=140, height=100):
    """ return bokeh resources for plot
    """
    data = np.transpose(np.loadtxt("/home/ubuntu/workspace/jvanalysis/data/D1_SCtoOC_SR500mVps.txt"))
    label = ""
    try:
        jv = Analysis(data)
        j = jv.calculate_jcell(jv.v_cell, jv._get_params())
        label = "calculated"
    except AnalysisError as e:
        print(e.error)
    except Exception as e:
        label = e
        print(e)
    
    plot = figure(
                    title="Current vs Voltage Curves of DSSCS", 
                    tools=TOOLS,
                    plot_width=width, 
                    plot_height=height,
                    sizing_mode='scale_width'
                )
    
    # Vertical line
    vline = Span(location=0, dimension='height', line_color='gray', line_width=1)
    # Horizontal line
    hline = Span(location=0, dimension='width', line_color='gray', line_width=1)
    plot.renderers.extend([vline, hline])
    
    if label == "calculated":
        # line plot
        plot.circle(jv.v_cell, jv.j_cell*1000, legend="experimental", line_color="blue", line_width=2)
        plot.line(jv.v_cell, j*1000, legend="calculated", line_color="red", line_width=2)    
    else:
        # line plot
        plot.circle(data[0], data[1]*1000/0.25, legend="experimental", line_color="blue", line_width=2)
        plot.line(data[0], data[1]*1000/0.25, legend="failed", line_color="blue", line_width=2)
    plot.x_range = Range1d(-0.6, 0.1)
    plot.y_range = Range1d(-5, 20)
    plot.legend.location = "top_left"
    plot.xaxis.axis_label = "Voltage (V)"
    plot.yaxis.axis_label = r"Current Density (mA/cm^2)"
    
    script, div = components(plot)
    
    return (div, script)