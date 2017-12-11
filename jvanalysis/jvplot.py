import numpy as np
from jvanalysis.analysis import Analysis, AnalysisError
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d, Span


DATA_FOLDER = "/home/ubuntu/workspace/jvanalysis/data"
TOOLS = "wheel_zoom,box_zoom,reset,save"

def resources(title, width=200, height=100):
    """ return bokeh resources for plot
    """
    data = np.transpose(np.loadtxt("/home/ubuntu/workspace/jvanalysis/data/D1_SCtoOC_SR500mVps.txt"))
    label = ""
    try:
        jv = Analysis(data)
        j = jv.calculate_jcell(jv.v_cell, jv._get_model_params())
        label = "calculated"
    except AnalysisError as e:
        print(e.error)
    except Exception as e:
        label = e
        print(e)
    
    plot = figure(title=title, tools=TOOLS, plot_width=width, 
                plot_height=height,sizing_mode='scale_width')
    
    # Vertical line
    vline = Span(location=0, dimension='height', line_color='gray', line_width=1)
    # Horizontal line
    hline = Span(location=0, dimension='width', line_color='gray', line_width=1)
    plot.renderers.extend([vline, hline])
    
    if label == "calculated":
        # line plot
        plot.circle(jv.v_cell, jv.j_cell*1000, legend="experimental", line_color="green", fill_color=None, line_width=2)
        plot.line(jv.v_cell, j*1000, legend="calculated", line_color="red", line_width=2)    
    else:
        # line plot
        plot.circle(data[0], data[1]*1000/0.25, legend="experimental", line_color="green", fill_color=None, line_width=2)
        plot.line(data[0], data[1]*1000/0.25, legend="failed", line_color="blue", line_width=2)
    plot.x_range = Range1d(-0.6, 0.1)
    plot.y_range = Range1d(-5, 20)
    plot.legend.location = "top_left"
    plot.xaxis.axis_label = "Voltage (V)"
    plot.yaxis.axis_label = r"Current Density (mA/cm^2)"
    
    script, div = components(plot)
    
    return (div, script)

def get_resources(title, data, width=200, height=120):
    """ return bokeh resources for plot
    """
    plot = figure(title=title, tools=TOOLS, plot_width=width, 
                plot_height=height,sizing_mode='scale_width')
    # Vertical line
    vline = Span(location=0, dimension='height', line_color='gray', line_width=1)
    # Horizontal line
    hline = Span(location=0, dimension='width', line_color='gray', line_width=1)
    plot.renderers.extend([vline, hline])
    
    plot.circle(data["vexp"], np.array(data["jexp"])*1000, legend="experimental", line_color="green", fill_color=None, line_width=2)
    plot.line(data["vexp"], np.array(data["jcal"])*1000, legend="calculated", line_color="red", line_width=2)    
    plot.x_range = Range1d(-(((((data["voc"]*10)//2)*2)/10)+0.2), 0.1)
    plot.y_range = Range1d(-2, (data["jsc"]//2)*2+2)
    plot.legend.location = "top_left"
    plot.xaxis.axis_label = "Voltage (V)"
    plot.yaxis.axis_label = r"Current Density (mA/cm^2)"
    
    script, div = components(plot)
    
    return (div, script)

def get_analyzed_params(data, area, temperature):
    """ return a dictionary of all parameters 
        of a solar cell after analyzing the data.
    """
    try:
        jv_analyzed = Analysis(np.array(data), area, temperature)
        v_exp = jv_analyzed.v_cell
        j_exp = jv_analyzed.j_cell.tolist()
        model_params = jv_analyzed._get_model_params()
        j_cal = jv_analyzed.calculate_jcell(v_exp, model_params).tolist()
        v_exp = v_exp.tolist()
        
        results = jv_analyzed.get_pv_params()
        results.update({"vexp": v_exp, "jexp": j_exp, "jcal": j_cal})
        results.update(jv_analyzed.get_model_params())
        return results
    except:
        return {}
    