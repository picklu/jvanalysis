# analysis.py
#
# This script is based on the paper
# Exact analytical analysis of current densityâ€“voltage curves
# of dye-sensitized solar cells
# by sarker et al.,
# source: https://doi.org/10.1016/j.solener.2015.03.009
#
# author: subrata sarker <subrata_sarker@yahoo.com>
# date: 2017.10.21
#
import numpy as np
from scipy.optimize import leastsq, fmin_slsqp
from scipy.special import lambertw
from tabulate import tabulate


# constants
CHARGE_ELEM = 1.60217646e-19
BOLTZMANN_CONST = 1.3806503e-23


class AnalysisError(Exception):
    """Exception raised for errors in the analysis.

    Attributes:
        expression  -- input expression in which the error occurred
        message     -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        self.error = "%s: %s" %(expression, message)


class Analysis(object):
    """ Object for current density-voltage of dye-sensitized solar cells."""

    def __init__(self, data, area=0.25, temperature=25):
        """
        Takes file name of a current density-voltage (jV) data. 
        Imports the jV data and process the data for fitting.
        
        Note: 
            The first two columns in the data should correspond to 
            voltage and current, respectively.
        
        Attributes:
            data        -- ndarray of voltage/current data of dsscs
            area        -- active area (cm^2) of the cell
            temperature -- temperature (degree C) of the system during measueremnt of the jV data
        """
        self.data = data
        self.area = area
        self.temperature = 273 + temperature

        # load and set data for analysis
        self._load_data()
        self._set_data()
        self._set_pv_params()
        self._set_model_params()

    def _load_data(self):
        """ load data from the jV data file and 
        extract v_cell and j_cell from the data
        
        attributes:
            start   -- start index of the data for fitting
            stop    -- end index of the data for fitting
            length  -- total number of data points
            v_cell  -- voltage of the cell (V)
            j_cell  -- current density of the cell (mA/cm^2)
        """

        # sanity check for data
        data = np.copy(self.data)
        if not data.any():
            raise AnalysisError("DataNotFound", "There is no data!")

        # set data: if the data is in revese order then reset data
        # consider that photovoltage ranges from 0 to -Voc
        if data[0][0] < data[0][-1]:
            self.data = np.flip(data, axis=1)

        # power value of the iv data
        power = data[0] * data[1]
        indices = np.where(power <= 0)[0]
        try:
            start = indices[0]
            stop = indices[-1]
        except IndexError:
            raise AnalysisError("NoPowerData",
                                "There is no data between SC and OC")
        if stop - start < 0:
            raise AnalysisError("NoPowerData",
                                "There is no data between SC and OC")
        if stop - start < 20:
            raise AnalysisError("NoPowerData",
                                "There is not enough data between SC and OC")

        self.start = start
        self.stop = stop
        self.length = len(data[0])

        # set vcell and jcell
        self.v_cell = self.data[0]
        self.j_cell = self.data[1] / self.area

    def _set_data(self):
        """ set data for analysis
        
        attributes:
            power       -- voltage * current density (power) data of the cell (w/cm^2)
            photo-power -- power data of the cell between Voc and jsc (w/cm^2)
            pmax        -- maxima of the power of the cell (w/cm^2)
            flength     -- number of data points between Voc and jsc
            x           -- voltage of the cell between Voc and jsc (V)
            y           -- current density of the cell between Voc and jsc (mA/cm^2)
        """

        # set vcell, jcell, pmax
        self.power = self.v_cell * self.j_cell
        self.photo_power = self.power[self.start:self.stop]
        self._pmax = min(self.photo_power)
        self.flength = len(self.photo_power)

        # set photo power data: data between SC and OC
        self.x = self.v_cell[self.start:self.stop]
        self.y = self.j_cell[self.start:self.stop]

    def _set_pv_params(self):
        """ set Voc, jsc, ff and eff of the data 
        
        Attributes:
            voc -- open-circuit voltage of the cell (V)
            jsc -- short-circuit current density of the cell (mA/cm^2)
            ff  -- fill-factor of the cell
            eff -- efficiency of the cell (%)
        """
        self.voc = -self.x[-1]
        self.jsc = self.y[0]

        # set ff and eff
        self.ff = -self._pmax / (self.voc * self.jsc)
        self.eff = -self._pmax * 1000

    def get_pv_params(self):
        """ returns photovoltaic parameters """
        return (self.voc, self.jsc * 1000, self.ff, self.eff)

    def set_vcell(self, factor):
        """use this procedure only when unit of v_cell in not voltage
        
            param:
                factor: number to convert the unit of v_cell into voltage
        """
        self.v_cell *= factor
        self._set_data()

    def set_jcell(self, factor):
        """use this procedure only when unit of j_cell in not ampere
        
        param:
            factor: number to convert the unit of j_cell into A/cm^2
        """
        self.j_cell *= factor
        self._set_data()

    def _get_voc_jsc(self):
        """ returns Vcell and jsc"""
        return (self.voc, self.jsc)

    def _get_data_sc(self):
        """ returns data at around jsc """
        max_sc_len = len(self._get_data_max_sc()[0])
        sc_len = max_sc_len // 3
        return (self.x[:sc_len], self.y[:sc_len])

    def _get_data_max_sc(self):
        """returns data from Vmax to jsc
        """
        return (self.x[:np.where(self.photo_power == self._pmax)[0][0]],
                self.y[:np.where(self.photo_power == self._pmax)[0][0]])

    def _get_data_max_oc(self):
        """returns data from Vmax to Voc
        """
        return (self.x[np.where(self.photo_power == self._pmax)[0][0]:],
                self.y[np.where(self.photo_power == self._pmax)[0][0]:])

    def _set_model_params(self, corr_vcell=0, corr_jcell=0, smooth=0):
        """ perform the exact analysis of the experimental data

        parameters:
            correctVcell -- 0 or -1
            correctJcell -- 0 or any factor
            smoothing    -- 0 or 5

        returns extracted parameters
        """
        if corr_vcell:
            self.set_vcell(corr_vcell)
        elif corr_jcell:
            self.set_jcell(corr_jcell)
        elif smooth:
            self.poly_fit(smooth)

        #calculate Rtotal
        vcell, jcell = self._get_data_max_oc()
        grad_vcell = np.gradient(vcell, 1)

        # estimate Rtotal
        grad_jcell = np.gradient(jcell, 1)
        self.rTotal = abs(grad_vcell / grad_jcell)

        # fit y = ax + b for Rs and m
        vThermal = (BOLTZMANN_CONST * self.temperature) / CHARGE_ELEM
        xVals = 1 / (self.jsc - jcell)
        a, b = np.polyfit(xVals, self.rTotal, 1)
        self.ideality = a / vThermal  # m
        self.rSeries = b  # Rs

        # fit y = ax + b for Rs + Rsh
        scX, scY = self._get_data_sc()
        c, __ = np.polyfit(scX, scY, 1)

        # Rs = 1/c(=Rs + Rsh) - b(=Rs) (rShunt not always positive so abs is used)
        self.rShunt = abs(1 / c - b)

        # fit y = ax + b for m and j0
        self.rRecombination = self.rShunt * (self.rTotal - self.rSeries) / (
            self.rSeries + self.rShunt - self.rTotal)
        vPE = vcell - jcell * self.rSeries
        lrRecombination = np.log(self.rRecombination)
        lrRecombination = np.nan_to_num(lrRecombination)
        m, n = np.polyfit(vPE, lrRecombination, 1)

        self.nIdeality = 1 / (m * vThermal)
        self.jnot = 1 / (m * np.exp(n))
        self.jph = self.jsc

    def _get_params(self):
        """ returns major parameters involved in the doide model of DSSCs"""
        return (self.jph, self.jnot, self.ideality, self.rSeries, self.rShunt)
    
    def get_model_params(self):
        """ returns major parameters involved in the doide model of DSSCs
        
        N.B.: The return value of jsc and jnot are in mA/cm2
        """
        return (self.jph * 1000, self.jnot * 1000, self.ideality, self.rSeries, self.rShunt)

    def get_data_points(self):
        """returns number of data points
        """
        return self.length

    def get_fit_data_points(self):
        """ returns number of data points used in the analysis
        """
        return self.flength

    def calculate_jcell(self, vcell, params):
        """ calculate current density as a function of cell voltage (vcell)
        according using using the exact expression of the jV curves
        
        Params:
            jph     -- photocurrent density (A/cm^2)
            jnot    -- dark-saturation current density (A/cm^2)
            Rs      -- series resistance (Ohm.cm^2)
            Rsh     -- shunt resistance (Ohm.cm^2)

        returns cell current density (jcell in A/cm^2).
        """
        qE = CHARGE_ELEM
        kB = BOLTZMANN_CONST
        T = self.temperature

        # unpack other parameters
        jph, jnot, m, Rs, Rsh = params
        # calculate jcell as a function of vcell through exact analytical
        # expression of diode model equation
        jcell = (qE * vcell + (-lambertw(-qE * Rs * jnot * Rsh * \
            np.exp(Rsh * qE * (Rs * jph+Rs*jnot-vcell) / (m * kB * \
            T * (Rsh + Rs))) / (-Rs * m * kB * T-Rsh * m * kB * T)).real + \
            Rsh * qE * (Rs * jph + Rs * jnot - vcell)/(m*kB * T * \
            (Rsh + Rs))) * m * kB * T) / (qE * Rs)
        return jcell

    def _residuals(self, params, expt_vcell, expt_jcell):
        """ calculate error between experimental and calculated data
        
        params:
            params      -- list of parameters to be tuned to minimise function
            expt_vcell  -- experimental voltage data
            expt_jcell  -- experimental current density data
        
        returns the error as an array
        """
        err = expt_jcell - self.calculate_jcell(expt_vcell, params)
        return err

    def _sum_residuals(self, params):
        """ the term/function we want to minimize  """
        return sum(self._residuals(params, self.x, self.y)**2)

    def _constraints(self, params):
        """ all the values of the returned array will be >=0 at the end """
        return self.constraintY - self.calculate_jcell(self.constraintX,
                                                       params)

    def fit_without_bounds(self, constraintXy=([], [])):
        """ least square fit of the experimental data to the diode model equation

        returns fit parameters
        """
        p0 = self._get_params()
        params = leastsq(self._residuals, p0, args=(self.x, self.y))
        jscF, jnotF, mF, RsF, RshF = params[0]
        return (jscF * 1000, jnotF * 1000, mF, RsF, RshF)

    def fit_with_bounds(self, bound_limit=0.10, constraintXy=([], [])):
        """ least square fit of the experimental data to the diode model equation
        bounds and constraints can be used
        
        params:
            bound_limit     -- 0 to 1 (float)
            constraintXy    -- tuple of x and y contraint as list

        returns fit parameters
        """
        p0 = self._get_params()
        jph, jnot, ideality, Rs, Rsh = p0
        self.constraintX = np.array(constraintXy[0])
        self.constraintY = np.array(constraintXy[1])
        bounds = [(jph * (1 - bound_limit / 2), jph * (1 + bound_limit / 2)),
                  (jnot * (1 - bound_limit / 2), jnot *
                   (1 + bound_limit / 2)), (ideality * (1 - bound_limit / 2),
                                            ideality * (1 + bound_limit / 2)),
                  (Rs * (1 - bound_limit / 2),
                   Rs * (1 + bound_limit / 2)), (Rsh * (1 - bound_limit / 2),
                                                 Rsh * (1 + bound_limit / 2))]
        params = fmin_slsqp(
            self._sum_residuals,
            p0,
            f_ieqcons=self._constraints,
            bounds=bounds)
        jscFw, jnotFw, mFw, RsFw, RshFw = params
        return (jscFw * 1000, jnotFw * 1000, mFw, RsFw, RshFw)

    def display_model_params(self, bound_limit=0.10):
        """ print out the fit results """
        jscA, jnotA, mA, RsA, RshA = self.get_model_params()
        jscF, jnotF, mF, RsF, RshF = self.fit_without_bounds()
        jscFw, jnotFw, mFw, RsFw, RshFw = self.fit_with_bounds(bound_limit)

        table = [["Parameters", "jsc", "jnot", "ideality", "Rs", "Rsh"]]
        table.append(
            ["Unit", "mA/cm^2", "mA/cm^2", "N/A", "Ohm.cm^2", "Ohm.cm^2"])
        table.append([
            "Analyzed", "{:.2f}".format(jscA), "{:.2e}".format(
                jnotA), "{:.2f}".format(mA), "{:.2f}".format(RsA),
            "{:.2f}".format(RshA)
        ])
        table.append([
            "Fit without bounds", "{:.2f}".format(jscF),
            "{:.2e}".format(jnotF), "{:.2f}".format(mF),
            "{:.2f}".format(RsF), "{:.2f}".format(RshF)
        ])
        table.append([
            "Fit with bounds", "{:.2f}".format(jscFw), "{:.2e}".format(
                jnotFw), "{:.2f}".format(mFw), "{:.2f}".format(RsFw),
            "{:.2f}".format(RshFw)
        ])

        print("Fit results:")
        print(tabulate(table))

    def display_pv_params(self):
        """ print out the photovoltaic performance parameters """
        table = [["Voc (V)", "jsc (mA/cm^2)", "ff", "PCE (%)"]]
        voc, jsc, ff, eff = self.get_pv_params()
        table.append([
            "{:.2f}".format(voc), "{:.2f}".format(jsc),
            "{:.2f}".format(ff), "{:.2f}".format(eff)
        ])

        print("Photovoltaic Performance Parameters:")
        print(tabulate(table))

    def poly_fit(self, order=5):
        """ smoothing data using polyfit of the order=5 by default """
        a1, a2, a3, a4, a5, a6 = np.polyfit(self.v_cell, self.j_cell, order)
        p_jcell = a1*self.v_cell**5 + a2*self.v_cell**4 + a3*self.v_cell**3 + \
            a4*self.v_cell**2 + a5*self.v_cell + a6

        # reset data
        self.j_cell = p_jcell
        self._set_data()

    def __repr__(self):
        return self.__class__.__name__ + " jV data"