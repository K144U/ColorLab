# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 19:40:09 2020

@author: priscillababiak
"""

import os
import re
import sys
import traceback
import pandas as pd
import numpy as np
from dataManager.CIE_XYZ import CIElab
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from ui.testgui2 import Ui_MainWindow

illum = pd.read_csv('dataManager/illuminants.csv')

class RGBImage(QMainWindow): 
    
    def __init__(self) -> None:
        super().__init__()
        self.gui = Ui_MainWindow()
        self.gui.setupUi(self)
        self.gui.pushButton.clicked.connect(self.click)
        self.gui.pushButton_2.clicked.connect(self.loadFiles)
        self.show()
        
    def click(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Spectra File(s)",
            "",
            "Spectra (*.csv *.xls *.xlsx);;All files (*)",
        )
        if not files:
            return
        self.filepath = os.path.dirname(files[0])
        self.filelist = sorted(os.path.basename(f) for f in files)
        self.gui.lineEdit.setText("; ".join(self.filelist))
        self.gui.lineEdit.setReadOnly(False)
        
     

    def loadFiles(self):
        self.statusBar().clearMessage()
        datatype = 0
        if self.gui.radioButton.isChecked():
            datatype = 0
        if self.gui.radioButton_2.isChecked():
            datatype = 1
        if self.gui.radioButton_3.isChecked():
            datatype = 2
        filelist = self.filelist
        spec_illum = str(self.gui.comboBox.currentText()) # specify the illuminant
        image_title = str(self.gui.lineEdit_2.text())
        image_aspect = float(self.gui.lineEdit_3.text())
        calc_rgb = True # do you want to calculate rgb values?

        # xyz bar values for illuminant
        x_bar = [0.001368,0.002236,0.004243,0.00765,0.01431,0.02319,0.04351,0.07763,0.13438,0.21477,0.2839,0.3285, \
                 0.34828,0.34806,0.3362,0.3187,0.2908,0.2511,0.19536,0.1421,0.09564,0.05795,0.03201,0.0147,0.0049, \
                 0.0024,0.0093,0.0291,0.06327,0.1096,0.1655,0.22575,0.2904,0.3597,0.43345,0.51205,0.5945,0.6784, \
                 0.7621,0.8425,0.9163,0.9786,1.0263,1.0567,1.0622,1.0456,1.0026,0.9384,0.85445,0.7514,0.6424,0.5419, \
                 0.4479,0.3608,0.2835,0.2187,0.1649,0.1212,0.0874,0.0636,0.04677,0.0329,0.0227,0.01584,0.011359, \
                 0.008111,0.00579,0.004109,0.002899,0.002049,0.00144,0.001,0.00069,0.000476,0.000332,0.000235,0.000166, \
                 0.000117,8.3e-05,5.9e-05,4.2e-05]
        
        y_bar= [3.9e-05,6.4e-05,0.00012,0.000217,0.000396,0.00064,0.00121,0.00218,0.004,0.0073,0.0116,0.01684,0.023, \
                0.0298,0.038,0.048,0.06,0.0739,0.09098,0.1126,0.13902,0.1693,0.20802,0.2586,0.323,0.4073,0.503,0.6082,\
                0.71,0.7932,0.862,0.91485,0.954,0.9803,0.99495,1,0.995,0.9786,0.952,0.9154,0.87,0.8163,0.757,0.6949, \
                0.631,0.5668,0.503,0.4412,0.381,0.321,0.265,0.217,0.175,0.1382,0.107,0.0816,0.061,0.04458,0.032,0.0232, \
                0.017,0.01192,0.00821,0.005723,0.004102,0.002929,0.002091,0.001484,0.001047,0.00074,0.00052,0.000361, \
                0.000249,0.000172,0.00012,8.5e-05,6e-05,4.2e-05,3e-05,2.1e-05,1.5e-05]
        			
        z_bar = [0.00645,0.01055,0.02005,0.03621,0.06785,0.1102,0.2074,0.3713,0.6456,1.03905,1.3856,1.62296,1.74706,1.7826, \
                 1.77211,1.7441,1.6692,1.5281,1.28764,1.0419,0.81295,0.6162,0.46518,0.3533,0.272,0.2123,0.1582,0.1117, \
                 0.07825,0.05725,0.04216,0.02984,0.0203,0.0134,0.00875,0.00575,0.0039,0.00275,0.0021,0.0018,0.00165,0.0014, \
                 0.0011,0.001,0.0008,0.0006,0.00034,0.00024,0.00019,0.0001,5e-05,3e-05,2e-05,1e-05,0,0,0,0,0,0,0,0,0,0,0,0,0, \
                 0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        num_files = len(filelist)

        lab_values = np.zeros((num_files,6))
        delta = np.zeros((1,num_files))
        i = 0

        # pull first timestamp (only meaningful for kinetic series)
        if num_files > 1:
            first_time = filelist[0].split('_')[-1]
            first_t = [int(word) for word in first_time.split('.') if word.isdigit()]
        
        # check that image title name is valid
        #re1 =  re.compile(r"^[^<>/{}[\]~`]*$")
        chars_to_be_removed = r'^[^<>/{}[\]~`]*$&#@!;,:'
        filtered_chars = filter(lambda item: item not in chars_to_be_removed, image_title)
        image_name = ''.join(filtered_chars)
        if not os.path.isdir('images/'):
            os.mkdir('images/')
        image_name = r'images/' + image_name + '.png'

        # If the user picked a single file with more than 2 columns, treat it
        # as a wide-format concentration series (one wavelength column + one
        # transmission/absorbance column per concentration).
        if num_files == 1:
            full_path = os.path.join(self.filepath, filelist[0])
            try:
                if full_path.lower().endswith(('.xls', '.xlsx')):
                    peek = pd.read_excel(full_path)
                else:
                    peek = pd.read_csv(full_path, sep=None, engine='python')
            except Exception:
                traceback.print_exc()
                peek = None
            if peek is not None and peek.shape[1] > 2:
                self._loadConcentrationSeries(
                    peek, datatype, spec_illum, image_title, image_aspect,
                    image_name, calc_rgb, x_bar, y_bar, z_bar,
                )
                return

        # if re1.match(image_title):
        #     print ("Image name is valid!")
        #     image_name = r'images/' + image_name + '.png'
        # else:
        #     error_msg = 'Image name is invalid.  Please rename your file.'
        #     print(error_msg)
        #     sys.exit()

        for file in filelist:
            
            #check if the file is a file, or a directory
            base_dir = self.filepath
            file_name = file
            full_path = os.path.join(base_dir, file_name)
            isdir = os.path.isdir(full_path)
            if isdir:
                print('Skipping ',file,' it is a directory!')
                continue
            else:
                if file.endswith('.csv'):
                    try:
                        uvvis_data = pd.read_csv(r"{0}/{1}".format(self.filepath,file), sep=None, engine='python')
                    except:
                        print(file + ' is corrupt!')
                        
                        if file==filelist[-1]:
                            print('***************************')
                            print('All files are corrupt!')
                            print('***************************')
                            sys.exit(0)
                        else:
                            continue
                elif file.endswith(('.xls', '.xlsx')):
                    try:
                        uvvis_data = pd.read_excel(r"{0}/{1}".format(self.filepath,file))
                    except:
                        print(file + ' is corrupt!')
                        
                        if file==filelist[-1]:
                            print('***************************')
                            print('All files are corrupt!')
                            print('***************************')
                            sys.exit(0)
                        else:
                            continue
                    
                else:
                    try:
                        uvvis_data = pd.read_table(r"{0}/{1}".format(self.filepath,file), engine='python')
                    except:
                        print(file + ' is corrupt!')
                        
                        if file==filelist[-1]:
                            print('***************************')
                            print('All files are corrupt!')
                            print('***************************')
                            sys.exit(0)
                        else:
                            continue
                    
                check_data = len(uvvis_data)
                if check_data == 0:
                    continue
                
                try:
                    cx,cy,_,rr,gg,bb = CIElab(spec_illum,illum,datatype,uvvis_data,x_bar,y_bar,z_bar,calc_rgb)
                    lab_values[i,0] = cx
                    lab_values[i,1] = cy
                    lab_values[i,2] = 0
                    lab_values[i,3] = rr
                    lab_values[i,4] = gg
                    lab_values[i,5] = bb
                    
                    # extract timestamp (kinetic series only)
                    if num_files > 1:
                        curr_time = file.split('_')[-1]
                        curr_t = [int(word) for word in curr_time.split('.') if word.isdigit()]
                        if curr_t[0] > 3660:
                            seconds_convert = 3600
                            units = 'Hours'
                        else:
                            seconds_convert = 60
                            units = 'Minutes'

                        delta[0,i] = (curr_t[0] - first_t[0])/seconds_convert

                    i += 1 # end for loop
                except:
                    print('***********************************************************')
                    print('Could not convert data in ' + file)
                    traceback.print_exc()
                    print('***********************************************************')
                    
                    if file==filelist[-1]:
                        sys.exit(0)

        # remove rows that were not filled
        lab_values =  lab_values[~np.all(lab_values == 0, axis=1)]
        new_num_files = len(lab_values)
        
        if new_num_files == 1:
            # generate image from the degradation data
            scalar = 1
            newdim = scalar*new_num_files
            n = 0
        
            colormat = np.zeros([newdim,newdim,3], dtype=np.uint16)
            for i in range(new_num_files):
                colormat[:,n:n+scalar] = lab_values[i,3:]
                n += scalar
        else:
        
            if seconds_convert == 3600: delta = delta*60
        
            # define the size of the matrix
            delta_delta = np.around(np.diff(delta))
            first_t = 1
        
            temp_dim = int(np.sum(delta_delta))
            colormat = np.zeros((temp_dim,temp_dim,3), dtype=np.uint8)
            for i in range(new_num_files-1):
                for k in range(int(delta_delta[0,i])):
                    if first_t:
                        colormat[:,i+k] = lab_values[i,3:]
                        curr_idx = i+k
                        first_t = 0
                    else:
                        curr_idx = curr_idx+1
                        colormat[:,curr_idx] = lab_values[i,3:]
                
            # resize array
            colormat = colormat[0:curr_idx+1,0:curr_idx+1,:]
            
        len_colormat = len(colormat)

        if (len_colormat > 1):
            fig, ax = plt.subplots(1,1)
            # figure out axis ticks
            # f_idx = new_num_files*0
            # s_idx = round(new_num_files*0.33)
            # t_idx = round(new_num_files*0.66)
            # l_idx = new_num_files-1
            # ax.set_xticks([f_idx,s_idx,t_idx,l_idx])
            # label_list = [str(round(delta[0,f_idx])),str(round(delta[0,s_idx])),
            #                    str(round(delta[0,t_idx])),str(round(delta[0,l_idx]))]
            # ax.set_xticklabels(label_list)
            if seconds_convert == 3600:
                ax.imshow(colormat,extent=[delta[0,0],np.max(delta)/60,delta[0,0],np.max(delta)/60],
                      aspect=image_aspect)
            else:
                ax.imshow(colormat,extent=[delta[0,0],np.max(delta),delta[0,0],np.max(delta)],
                      aspect=image_aspect)
            ax.axes.get_yaxis().set_visible(False)
            ax.set_xlabel(units)
            ax.set_title(image_title)
            fig.savefig(image_name)
        else:
            fig, ax = plt.subplots(1,1)
            ax.imshow(colormat,aspect=image_aspect)
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
            ax.set_title(image_title)
            fig.savefig(image_name)

        try:
            self._saveChromaticityDiagram(lab_values, image_title, image_name,
                                           x_bar, y_bar, z_bar)
        except Exception:
            traceback.print_exc()

        self.gui.statusbar.showMessage("Finished!")

    def _loadConcentrationSeries(self, df, datatype, spec_illum, image_title,
                                 image_aspect, image_name, calc_rgb,
                                 x_bar, y_bar, z_bar):
        # First column is wavelength axis; remaining columns are spectra at
        # successive concentrations. Header format expected: "<value> <unit>",
        # e.g. "30 mM" or "12.5 uM".
        wavelength_col = df.columns[0]
        spectrum_cols = list(df.columns[1:])

        header_re = re.compile(r'^\s*([+-]?\d+(?:\.\d+)?)\s*(\S.*?)?\s*$')
        parsed = []
        for c in spectrum_cols:
            m = header_re.match(str(c))
            if m:
                value = float(m.group(1))
                unit = (m.group(2) or '').strip()
                parsed.append((value, unit, c))

        if not parsed:
            self.gui.statusbar.showMessage(
                "Could not parse concentration headers in selected file"
            )
            return

        parsed.sort(key=lambda t: t[0])
        concentrations = np.array([p[0] for p in parsed])
        unit = parsed[0][1] or 'concentration'
        cols_in_order = [p[2] for p in parsed]
        n = len(parsed)

        target_col = {0: 'Absorbance', 1: 'Transmission', 2: 'FT'}[datatype]

        # Auto-scale percent transmission to fraction (existing CIE math
        # assumes T in [0, 1]; user supplied 0-100 percent).
        scale = 1.0
        if datatype == 1:
            sample_max = float(np.nanmax(df[cols_in_order].to_numpy()))
            if sample_max > 1.5:
                scale = 0.01

        lab_values = np.zeros((n, 6))
        for i, col in enumerate(cols_in_order):
            sub = pd.DataFrame({
                'Wavelength': df[wavelength_col],
                target_col: df[col] * scale if datatype == 1 else df[col],
            })
            try:
                cx, cy, _, rr, gg, bb = CIElab(
                    spec_illum, illum, datatype, sub,
                    x_bar, y_bar, z_bar, calc_rgb,
                )
                lab_values[i] = [cx, cy, 0, rr, gg, bb]
            except Exception:
                print('Could not convert column ' + str(col))
                traceback.print_exc()
                continue

        # Drop rows that stayed zero (failed conversions).
        mask = ~np.all(lab_values == 0, axis=1)
        lab_values = lab_values[mask]
        concentrations = concentrations[mask]
        n = len(lab_values)
        if n == 0:
            self.gui.statusbar.showMessage("No spectra could be converted")
            return

        if n > 1:
            # Width of each color band proportional to the gap to the next
            # concentration (rounded to integer pixels, minimum 1).
            gaps = np.maximum(np.around(np.diff(concentrations)), 1).astype(int)
            temp_dim = int(np.sum(gaps))
            colormat = np.zeros((temp_dim, temp_dim, 3), dtype=np.uint8)
            curr_idx = 0
            first = True
            for i in range(n - 1):
                for k in range(int(gaps[i])):
                    if first:
                        colormat[:, i + k] = lab_values[i, 3:]
                        curr_idx = i + k
                        first = False
                    else:
                        curr_idx += 1
                        colormat[:, curr_idx] = lab_values[i, 3:]
            colormat = colormat[0:curr_idx + 1, 0:curr_idx + 1, :]

            fig, ax = plt.subplots(1, 1)
            ax.imshow(
                colormat,
                extent=[concentrations[0], np.max(concentrations),
                        concentrations[0], np.max(concentrations)],
                aspect=image_aspect,
            )
            ax.axes.get_yaxis().set_visible(False)
            ax.set_xlabel(unit)
            ax.set_title(image_title)
            fig.savefig(image_name)
        else:
            colormat = np.zeros((1, 1, 3), dtype=np.uint16)
            colormat[0, 0] = lab_values[0, 3:]
            fig, ax = plt.subplots(1, 1)
            ax.imshow(colormat, aspect=image_aspect)
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
            ax.set_title(image_title)
            fig.savefig(image_name)

        try:
            self._saveChromaticityDiagram(lab_values, image_title, image_name,
                                           x_bar, y_bar, z_bar)
        except Exception:
            traceback.print_exc()

        self.gui.statusbar.showMessage("Finished!")

    def _saveChromaticityDiagram(self, lab_values, image_title, image_name,
                                 x_bar, y_bar, z_bar):
        """Save a CIE 1931 xy chromaticity diagram alongside the color strip.

        lab_values rows are [cx, cy, _, r, g, b]. Row r/g/b are 0-255 ints
        but may be floats; we normalise to 0-1 for matplotlib.
        """
        from matplotlib.path import Path

        x_bar_a = np.asarray(x_bar, dtype=float)
        y_bar_a = np.asarray(y_bar, dtype=float)
        z_bar_a = np.asarray(z_bar, dtype=float)

        # Spectral locus: chromaticity coords for each wavelength sample.
        denom = x_bar_a + y_bar_a + z_bar_a
        good = denom > 0
        locus_x = x_bar_a[good] / denom[good]
        locus_y = y_bar_a[good] / denom[good]
        locus = np.column_stack([locus_x, locus_y])
        locus_closed = np.vstack([locus, locus[:1]])  # close polygon for fill

        # Build a filled-gamut RGB background by computing sRGB at each (x, y)
        # cell on a grid, then masking points outside the locus polygon.
        res = 256
        grid_x = np.linspace(0.0, 0.8, res)
        grid_y = np.linspace(0.0, 0.9, res)
        gx, gy = np.meshgrid(grid_x, grid_y)
        gz = 1.0 - gx - gy
        with np.errstate(divide='ignore', invalid='ignore'):
            X = np.where(gy > 0, gx / gy, 0.0)
            Y = np.ones_like(gy)
            Z = np.where(gy > 0, gz / gy, 0.0)
        R = X * 3.2410 + Y * -1.5374 + Z * -0.4986
        G = X * -0.9692 + Y * 1.8760 + Z * 0.0416
        B = X * 0.0556 + Y * -0.2040 + Z * 1.0570
        RGB = np.dstack([R, G, B])
        RGB = np.clip(RGB, 0.0, 1.0)
        # Gamma (sRGB) - vectorized form of the per-channel function in CIE_XYZ.
        below = RGB < 0.0031308
        RGB = np.where(below, 12.92 * RGB, 1.055 * np.power(RGB, 0.41666) - 0.055)
        # Normalize each cell so the brightest channel hits 1.0 - this matches
        # the conventional appearance of CIE diagrams (Y=1 produces very dim
        # colors otherwise).
        peak = np.max(RGB, axis=2, keepdims=True)
        RGB = np.where(peak > 0, RGB / np.maximum(peak, 1e-6), RGB)
        RGB = np.clip(RGB, 0.0, 1.0)

        # Mask points outside the spectral locus polygon.
        locus_path = Path(locus_closed)
        pts = np.column_stack([gx.ravel(), gy.ravel()])
        inside = locus_path.contains_points(pts).reshape(gx.shape)
        alpha = inside.astype(float)
        rgba = np.dstack([RGB, alpha])

        fig, ax = plt.subplots(1, 1, figsize=(7, 6.5))
        ax.imshow(rgba, origin='lower', extent=[0.0, 0.8, 0.0, 0.9],
                  aspect='auto', interpolation='bilinear')

        # Spectral locus outline + purple line.
        ax.plot(locus_closed[:, 0], locus_closed[:, 1], color='black', lw=1.0)

        # D65 white point.
        d65_x, d65_y = 0.31271, 0.32902
        ax.plot(d65_x, d65_y, marker='o', markersize=6,
                markerfacecolor='white', markeredgecolor='black')
        ax.annotate('White (D65)', xy=(d65_x, d65_y),
                    xytext=(d65_x + 0.015, d65_y - 0.01),
                    fontsize=9, color='black')

        # Data points + connector lines from D65.
        for row in lab_values:
            cx, cy = float(row[0]), float(row[1])
            if cx == 0.0 and cy == 0.0:
                continue
            r, g, b = float(row[3]) / 255.0, float(row[4]) / 255.0, float(row[5]) / 255.0
            r, g, b = max(0.0, min(1.0, r)), max(0.0, min(1.0, g)), max(0.0, min(1.0, b))
            ax.plot([d65_x, cx], [d65_y, cy], color=(r, g, b), lw=1.2)
            ax.plot(cx, cy, marker='o', markersize=5,
                    markerfacecolor=(r, g, b), markeredgecolor='black',
                    markeredgewidth=0.5)

        ax.set_xlim(0.0, 0.8)
        ax.set_ylim(0.0, 0.9)
        ax.set_xlabel('x co-ordinate')
        ax.set_ylabel('y co-ordinate')
        ax.set_title(image_title)
        ax.grid(True, color='gray', alpha=0.25, linewidth=0.5)

        out_path = image_name[:-4] + '_chromaticity.png' \
            if image_name.lower().endswith('.png') else image_name + '_chromaticity.png'
        fig.savefig(out_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
