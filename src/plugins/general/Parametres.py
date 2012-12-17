# -*- coding:utf-8 -*-
# Copyright © 2011 Clément Schaff, Mahdi Ben Jelloul

"""
openFisca, Logiciel libre de simulation du système socio-fiscal français
Copyright © 2011 Clément Schaff, Mahdi Ben Jelloul

This file is part of openFisca.

    openFisca is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    openFisca is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with openFisca.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt4.QtGui import QDockWidget, QFileDialog, QMessageBox
from PyQt4.QtCore import SIGNAL
from src.views.ui_parametres import Ui_Parametres
from src.parametres.paramData import XmlReader, Tree2Object
from src.parametres.paramModel import PrestationModel
from src.parametres.Delegate import CustomDelegate, ValueColumnDelegate
from src.core.config import CONF
from src.core.qthelpers_new import get_icon
import os
from src.plugins.TODO__init__ import OFPluginWidget

class ParamWidget(OFPluginWidget, Ui_Parametres):
    """
    Parameters Widget
    """
    CONF_SECTION = 'parameters'
#    CONFIGWIDGET_CLASS = ParametersConfigPage



    def __init__(self, parent = None):
        super(ParamWidget, self).__init__(parent)
        self.setupUi(self)
        self.setLayout(self.verticalLayout)
        country = CONF.get('simulation', 'country')
        self._file = country + '/param/param.xml' 
        
        
        self.__parent = parent

        self.connect(self.save_btn, SIGNAL("clicked()"), self.saveXml)
        self.connect(self.open_btn, SIGNAL("clicked()"), self.loadXml)
        self.connect(self.reset_btn, SIGNAL("clicked()"), self.reset)
        
        
        self.initialize()

    def reset(self):
        self.initialize()
        self.changed()
            
    def changed(self):
        self.emit(SIGNAL('changed()'))
    
    def initialize(self):
        self._date = CONF.get('simulation', 'datesim')
        self.label.setText(u"Date : %s" %( str(self._date)) )
        print self._file
        print self._date
        self._reader = XmlReader(self._file, self._date)
        self._rootNode = self._reader.tree
        self._rootNode.rmv_empty_code()
                
        self._model = PrestationModel(self._rootNode, self)
        self.connect(self._model, SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.changed)

        self.uiTree.setModel(self._model)
        self.selectionModel = self.uiTree.selectionModel()
        self.uiTree.setColumnWidth(0,230)
        self.uiTree.setColumnWidth(1,70)
        self.uiTree.setColumnWidth(2,70)
        delegate = CustomDelegate(self)
        delegate.insertColumnDelegate(1, ValueColumnDelegate(self))
        delegate.insertColumnDelegate(2, ValueColumnDelegate(self))
        self.uiTree.setItemDelegate(delegate)
    
    def getParam(self, defaut = False):
        obj = Tree2Object(self._rootNode, defaut)
        obj.datesim = self._date
        return obj

    def saveXml(self):
        reformes_dir = CONF.get('paths', 'reformes_dir')
        default_fileName = os.path.join(reformes_dir, 'sans-titre')
        fileName = QFileDialog.getSaveFileName(self,
                                               u"Enregistrer une réforme", default_fileName, u"Paramètres OpenFisca (*.ofp)")
        if fileName:
#            try:
                self._rootNode.asXml(fileName)
#            except Exception, e:
#                QMessageBox.critical(
#                    self, "Erreur", u"Impossible d'enregistrer le fichier : " + str(e),
#                    QMessageBox.Ok, QMessageBox.NoButton)


    def loadXml(self):
        reformes_dir = CONF.get('paths', 'reformes_dir')
        fileName = QFileDialog.getOpenFileName(self,
                                               u"Ouvrir une réforme", reformes_dir, u"Paramètres OpenFisca (*.ofp)")
        if not fileName == '':
            try: 
                loader = XmlReader(str(fileName))
                CONF.set('simulation', 'datesim',str(loader._date))
                self.initialize()
                self._rootNode.load(loader.tree)
                self.changed()
            except Exception, e:
                QMessageBox.critical(
                    self, "Erreur", u"Impossible de lire le fichier : " + str(e),
                    QMessageBox.Ok, QMessageBox.NoButton)

    def get_plugin_title(self):
        """
        Return plugin title
        Note: after some thinking, it appears that using a method
        is more flexible here than using a class attribute
        """
        return "Parameters"

    
    def get_plugin_icon(self):
        """
        Return plugin icon (QIcon instance)
        Note: this is required for plugins creating a main window
              (see SpyderPluginMixin.create_mainwindow)
              and for configuration dialog widgets creation
        """
        return get_icon('qt.png')
            
    def get_plugin_actions(self):
        """
        Return a list of actions related to plugin
        Note: these actions will be enabled when plugin's dockwidget is visible
              and they will be disabled when it's hidden
        """
        raise NotImplementedError
    
    def register_plugin(self):
        """
        Register plugin in OpenFisca's main window
        """
        self.main.add_dockwidget(self)


    def refresh_plugin(self):
        '''
        Update
        '''
        pass