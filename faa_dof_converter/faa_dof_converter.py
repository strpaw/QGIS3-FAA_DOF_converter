# -*- coding: utf-8 -*-
"""
/***************************************************************************
 faa_dof_converter
                                 A QGIS plugin
 Converts FAA DOF file into CSV, KML, Shapefile formats
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-09-30
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Paweł Strzelewicz
        email                : @
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import *
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox, QWidget, QFileDialog
from qgis.core import *
from osgeo import ogr, osr

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .faa_dof_converter_dialog import faa_dof_converterDialog
import os.path
import csv
from . faa_dof_tools import *

w = QWidget()


class faa_dof_converter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.input_file = ""
        self.output_file = ""
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'faa_dof_converter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = faa_dof_converterDialog()

        self.dlg.pushButtonSelectInput.clicked.connect(self.select_input_file)
        self.dlg.pushButtonSelectOutput.clicked.connect(self.select_output_file)
        self.dlg.pushButtonConvert.clicked.connect(self.convert_faa_dof)
        self.dlg.progressBar.setValue(0)
        self.dlg.progressBar.setMaximum(100)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&FAA_DOF_converter')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'faa_dof_converter')
        self.toolbar.setObjectName(u'faa_dof_converter')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('faa_dof_converter', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/faa_dof_converter/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'FAA_DOF_converter'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&FAA_DOF_converter'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def check_input(self):
        """ Check if input and output files are selected
        :return: check_result (bool): result of check, True if input and output files selected, False otherwise
        """
        check_result = True
        err_msg = ""

        if self.dlg.lineEditInputFile.text() == "":
            check_result = False
            err_msg += "Select input file.\n"

        if self.dlg.comboBoxOutputType.currentIndex() == 0:
            check_result = False
            err_msg += "Choose output format.\n"

        if self.dlg.lineEditOutputFile.text() == "":
            check_result = False
            err_msg += "Select output file.\n"

        if check_result is False:
            QMessageBox.critical(w, "Message", err_msg)
        return check_result

    def select_input_file(self):
        """ Opens open file dialog window to select input FAA DOF file """
        input_file = QFileDialog.getOpenFileName(self.dlg, "Select input file ", "", '*.dat')
        self.dlg.lineEditInputFile.setText(input_file[0])
        self.input_file = input_file[0]
        return input_file

    def select_output_file(self):
        """ Opens save file dialog window to select output file """
        if self.dlg.comboBoxOutputType.currentIndex() == 1:  # CSV file
            output_file = QFileDialog.getSaveFileName(self.dlg, "Select output CSV file ", "", '*.csv')
            self.dlg.lineEditOutputFile.setText(output_file[0])
            self.output_file = output_file[0]
            return output_file
        if self.dlg.comboBoxOutputType.currentIndex() == 2:  # Shapefile
            output_file = QFileDialog.getSaveFileName(self.dlg, "Select output CSV file ", "", '*.shp')
            self.dlg.lineEditOutputFile.setText(output_file[0])
            self.output_file = output_file[0]
            return output_file
        if self.dlg.comboBoxOutputType.currentIndex() == 3:  # KML file
            output_file = QFileDialog.getSaveFileName(self.dlg, "Select output CSV file ", "", '*.kml')
            self.dlg.lineEditOutputFile.setText(output_file[0])
            self.output_file = output_file[0]
            return output_file

    def convert_faa_dof(self):
        """ Converts FAA DOF file to selected format """
        if self.check_input():
            lines_count = 0
            with open(self.input_file, 'r') as DOF_file:
                line_nr = 0
                for line in DOF_file:
                    line_nr += 1
                lines_count = line_nr
            if self.dlg.comboBoxOutputType.currentIndex() == 1:
                obs_csv_field_names = ['STATE_CTRY',  # Country code,
                                       'ID',  # Obstacle ID
                                       'VERIF_STAT',  # Verification status
                                       'LAT_DMS',  # Obstacle latitude, DMS format
                                       'LON_DMS',  # Obstacle longitude, DMS format
                                       'LAT_DD',  # Obstacle latitude, DD format
                                       'LON_DD',  # Obstacle longitude, DD format
                                       'TYPE',  # Obstacle type
                                       'AGL_FEET',  # height above ground in meters
                                       'AMSL_FEET',  # height above mean sea level in meters
                                       'H_ACC',  # horizontal accuracy
                                       'H_ACC_UOM',  # horizontal accuracy - unit of measurement
                                       'V_ACC',  # vertical accuracy
                                       'V_ACC_UOM',  # vertical accuracy - unit of measurement
                                       'LIGHT',  # Information related to lighting
                                       'MARK',  # Information related to marking
                                       'JDATE']
                with open(self.input_file, 'r') as DOF_file:
                    with open(self.output_file, 'w', newline='') as out_csv:
                        writer = csv.DictWriter(out_csv, fieldnames=obs_csv_field_names, delimiter=',')
                        writer.writeheader()
                        line_nr = 0
                        for line in DOF_file:
                            line_nr += 1
                            if line_nr < 5:
                                continue
                            else:
                                obstacle = ObstacleFAADOF(line, coordinates_dd=True, decode_values=True)
                                writer.writerow({'STATE_CTRY': obstacle.ctry_name,
                                                 'ID': obstacle.obs_number,
                                                 'VERIF_STAT': obstacle.verif_stat_desc,
                                                 'LAT_DMS': obstacle.lat_dms,
                                                 'LON_DMS': obstacle.lon_dms,
                                                 'LAT_DD': obstacle.lat_dd,
                                                 'LON_DD': obstacle.lon_dd,
                                                 'TYPE': obstacle.obs_type,
                                                 'AGL_FEET': obstacle.agl_height,
                                                 'AMSL_FEET': obstacle.amsl_height,
                                                 'H_ACC': obstacle.h_acc_value,
                                                 'H_ACC_UOM': obstacle.h_acc_uom,
                                                 'V_ACC': obstacle.v_acc_value,
                                                 'V_ACC_UOM': obstacle.v_acc_uom,
                                                 'LIGHT': obstacle.lighting_desc,
                                                 'MARK': obstacle.marking_desc,
                                                 'JDATE': obstacle.jdate})
                                progress = (line_nr / lines_count) * 100
                                self.dlg.progressBar.setValue(progress)

            if self.dlg.comboBoxOutputType.currentIndex() == 2 or self.dlg.comboBoxOutputType.currentIndex() == 3:
                # Set reference system
                crs = QgsCoordinateReferenceSystem()
                crs.createFromId(4326)
                # Defining fields for feature attributes
                dof_fields = QgsFields()
                dof_fields.append(QgsField("ST_NAME", QVariant.String))  # US state or country code
                dof_fields.append(QgsField("ID", QVariant.String))  # Obstacle OAS number = obstacle id
                dof_fields.append(QgsField("VERIF_STAT", QVariant.String))  # Verification status
                dof_fields.append(QgsField("LAT_DMS", QVariant.String))  # Obstacle latitude, DMS format
                dof_fields.append(QgsField("LON_DMS", QVariant.String))  # Obstacle longitude, DMS format
                dof_fields.append(QgsField("TYPE", QVariant.String))  # Obstacle type
                dof_fields.append(QgsField("AGL_FEET", QVariant.Int))  # Above ground level height, feet
                dof_fields.append(QgsField("AMSL_FEET", QVariant.Int))  # Above mean sea level height, feet
                dof_fields.append(QgsField("H_ACC", QVariant.Int))  # Horizontal accuracy
                dof_fields.append(QgsField("H_ACC_UOM", QVariant.String))  # Horizontal accuracy - unit of measurement
                dof_fields.append(QgsField("V_ACC", QVariant.Int))  # Vertical accuracy
                dof_fields.append(QgsField("V_ACC_UOM", QVariant.String))  # Vertical accuracy - unit of measurement
                dof_fields.append(QgsField("LIGHTING", QVariant.String))  # Information related to lighting
                dof_fields.append(QgsField("MARKING", QVariant.String))  # Information related to marking
                dof_fields.append(QgsField("JDATE", QVariant.String))  # Julian date, date of action

                if self.dlg.comboBoxOutputType.currentIndex() == 2:
                    writer = QgsVectorFileWriter(self.output_file, "CP1250", dof_fields, QgsWkbTypes.Point, crs,
                                                 "ESRI Shapefile")
                elif self.dlg.comboBoxOutputType.currentIndex() == 3:
                    writer = QgsVectorFileWriter(self.output_file, "CP1250", dof_fields, QgsWkbTypes.Point, crs,
                                                 "KML")
                feat = QgsFeature()

                with open(self.input_file, 'r') as DOF_file:
                    line_nr = 0
                    for line in DOF_file:
                        line_nr += 1
                        if line_nr < 5:  # Skip first 4 lines
                            continue
                        else:
                            obstacle = ObstacleFAADOF(line, coordinates_dd=True, decode_values=True)

                            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(obstacle.lon_dd),
                                                                                float(obstacle.lat_dd))))
                            feat.setAttributes([obstacle.oas_code,
                                                obstacle.obs_number,
                                                obstacle.verif_stat_code,
                                                obstacle.lat_dms,
                                                obstacle.lon_dms,
                                                obstacle.obs_type,
                                                int(obstacle.agl_height),
                                                int(obstacle.amsl_height),
                                                int(obstacle.h_acc_value),
                                                obstacle.h_acc_uom,
                                                int(obstacle.v_acc_value),
                                                obstacle.v_acc_uom,
                                                obstacle.lighting_code,
                                                obstacle.marking_desc,
                                                obstacle.jdate])
                            writer.addFeature(feat)
                            progress = (line_nr / lines_count) * 100
                            self.dlg.progressBar.setValue(progress)

                del writer
            if self.dlg.checkBoxAddOutputToMap.isChecked():
                self.iface.addVectorLayer(self.output_file, '', "ogr")

        return

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
