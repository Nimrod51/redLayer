#! python3  # noqa: E265

"""
/***************************************************************************
 idtVen - class idtVen_albero
                                 A QGIS plugin
 compilazione assistita metadati regione veneto
                              -------------------
        begin                : 2014-12-04
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Enrico Ferreguti
        email                : enricofer@gmail.com
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

# standard library
import logging
import os

# PyQGIS
from qgis.core import QgsPointXY, QgsTextAnnotation, QgsProject
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QTextDocument
from qgis.PyQt.QtWidgets import QDialog, QApplication
from qgis.PyQt.QtCore import QSizeF

# create the dialog for zoom to point
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_note_dialog.ui'))

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Helper Functions ######
# ##################################

def px_size_to_mm(qsizef_px):
    """Convert pixel size to millimeters for Qt6 compatibility."""
    dpi = QApplication.primaryScreen().logicalDotsPerInch() or 96.0
    # 25.4 mm per inch
    return QSizeF(qsizef_px.width() * 25.4 / dpi, qsizef_px.height() * 25.4 / dpi)


# ############################################################################
# ########## Classes ###############
# ##################################

class sketchNoteDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(sketchNoteDialog, self).__init__(parent)
        self.setupUi(self)
        self.hide()
        self.buttonBox.accepted.connect(self.mkNote)
        self.buttonBox.rejected.connect(self.cancel)
        self.note = None
        self.iface = iface

    def setPoint(self, segment):
        self.point = self.midPoint(segment)

    def getNote(self):
        return self.note

    def getAnnotation(self):
        try:
            return self.textItem
        except Exception as err:
            logger.error(err)
            return None

    def cancel(self):
        self.note = ""

    def mkNote(self):
        self.textItem = self.mkAnnotation(self.noteText.toPlainText())
        self.note = self.noteText.toPlainText()
        self.noteText.clear()

    def mkAnnotation(self, doc):
        if self.point:
            # Create QTextDocument with the text
            text_doc = QTextDocument(doc)
            
            # Create QgsTextAnnotation
            annotation = QgsTextAnnotation()
            annotation.setMapPosition(self.point)
            
            # Set the document first
            annotation.setDocument(text_doc)
            
            # For Qt6 compatibility, ensure proper sizing
            try:
                # Convert pixel size to mm for Qt6 compatibility
                size_mm = px_size_to_mm(text_doc.size())
                annotation.setFrameSizeMm(size_mm)
            except:
                # Fallback: use a reasonable default size in mm
                annotation.setFrameSizeMm(QSizeF(100, 50))
            
            # Ensure the annotation is visible by setting additional properties
            annotation.setVisible(True)
            
            # Make sure it has a visible frame and fill
            annotation.setHasFixedMapPosition(True)
            
            # Add to project annotation manager
            QgsProject.instance().annotationManager().addAnnotation(annotation)
            
            return annotation  # Return QgsTextAnnotation directly
        else:
            return None

    def midPoint(self, s):
        x = (s.vertexAt(0).x() + s.vertexAt(1).x())/2
        y = (s.vertexAt(0).y() + s.vertexAt(1).y())/2
        return QgsPointXY(x, y)

    @staticmethod
    def newPoint(iface, segment, txt=None):
        dialog = sketchNoteDialog(iface)

        dialog.setPoint(segment)
        if not txt:
            result = dialog.exec()
            dialog.show()
            if QDialog.DialogCode.Accepted:
                return dialog.getAnnotation()
            else:
                return None
        else:
            return dialog.mkAnnotation(txt)
