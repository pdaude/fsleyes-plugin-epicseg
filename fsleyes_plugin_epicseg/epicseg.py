#!/usr/bin/env python
#Author : Pierre Daudé <pierre-daude@hotmail.fr>
#
#epicseg.py

import wx
import fsleyes.actions as actions
import fsleyes.views.viewpanel as viewpanel
import fsleyes.controls.controlpanel as ctrlpanel
import fsleyes.actions as actions
import fsleyes.actions.copyoverlay  as copyoverlay
import numpy as np
from .threadfcn import *

class DialogOverlayChoice(wx.Dialog):
    def __init__(self, parent, overlayList):
        wx.Dialog.__init__(self, parent, title='Initializing Epic-segmentation')
        self.__overlayList = overlayList
        self.parent = parent
        self.initGUI()

    def initGUI(self):
        """
        Create a choice button  **Image** to allow the user to choose an image in the overlayList.
        Create a choice button **FCN** to allow the user to choose a FCN.
        Create a checklist Box **ROI** to allow the user to choose which roi to segment.
        """
        fgrid = wx.FlexGridSizer(4, 2, 5, 10)
        ImageText = wx.StaticText(self, label='Image', style=wx.ALIGN_LEFT)
        self.ImageOIChoice = wx.Choice(self, choices=[overlay.name for overlay in self.__overlayList])

        FCNOIText = wx.StaticText(self, label='FCN', style=wx.ALIGN_LEFT)
        self.FCNOIChoice = wx.Choice(self, choices=["U-Net"])
        
        LabelOIText = wx.StaticText(self, label='ROI', style=wx.ALIGN_LEFT)
        self.Checklist=wx.CheckListBox(self, choices=["Paracardial Fat","Epicardial Fat","Heart Ventricles"])
        OKbutton = wx.Button(self, -1, "Ok")
        OKbutton.Bind(wx.EVT_BUTTON, self.ClickedOnOk)

        fgrid.AddMany([(ImageText), (self.ImageOIChoice, 1, wx.EXPAND),(FCNOIText),(self.FCNOIChoice,1,wx.EXPAND),(LabelOIText),(self.Checklist,1,wx.EXPAND), (OKbutton)])
        self.SetSizer(fgrid)
        self.Fit()
        self.ShowModal()

    def ClickedOnOk(self, event):
        ImageOI_ind = self.ImageOIChoice.GetSelection()
        if ImageOI_ind == -1:
            return wx.MessageBox('You have to choose an image', 'Info',wx.OK | wx.ICON_EXCLAMATION)

        FCNOI_ind = self.FCNOIChoice.GetSelection()

        if FCNOI_ind == -1:
            return wx.MessageBox('You have to choose a Fully Convolutional Network', 'Info',wx.OK | wx.ICON_EXCLAMATION)
        


        ImageOI_name = self.ImageOIChoice.GetString(ImageOI_ind)
        FCNOI_name = self.FCNOIChoice.GetString(ImageOI_ind)
        LabelOI_names = self.Checklist.GetCheckedStrings()

        self.parent.FCNprediction(ImageOI_name,FCNOI_name,LabelOI_names)
        self.Destroy()

class PluginEpic(ctrlpanel.ControlPanel):
    """
        Create a button **EPIC-seg** and link it to :meth:`.PluginEpic.ClickedOnFCNButton`
        Connect :class:`fsleyes_plugin_epicseg.threadfcn.EVT_THREAD`: to :meth:`.PluginEpic.FCNThreadResult`
    """
    def __init__(self,parent,overlayList,displayCtx,frame):
        ctrlpanel.ControlPanel.__init__(self,parent,overlayList,displayCtx,frame)
        self.__overlayList = overlayList
        self.__displayCtx = displayCtx
        self.__frame = frame

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.FCNButton = wx.Button(self, -1, "EPIC-seg")
        self.FCNButton.Bind(wx.EVT_BUTTON, self.ClickedOnFCNButton)

        sizer.Add(self.FCNButton, flag=wx.ALIGN_CENTER, proportion=1,border=15)
        self.SetSizer(sizer)

        EVT_THREAD(self, self.FCNThreadResult)

    def ClickedOnFCNButton(self, evt):
        """
        Create the dialogbox :class:`.DialogOverlayChoice`
        """
        self.FCNDialog = DialogOverlayChoice(self, overlayList=self.__overlayList)

    def FCNprediction(self,ImageOI_name,FCNOI_name,LabelOI_names):
        """
        :param ImageOI_name: name of the image overlay chosen in the dialog box
        :param FCNOI_name: FCN chosen in the dialog box
        :param LabelOI_names: Labels chosen in the dialog box

        Linked to the dialogbox :class:`.DialogOverlayChoice`, it launch the :class:`fsleyes_plugin_epicseg.threadfcn.FCNThread`. 
        """
        ImageOI_overlay = self.__overlayList.find(ImageOI_name)
        pathOverlay = ImageOI_overlay.dataSource
        if pathOverlay  == None:
            return wx.MessageBox('The image {} have to be saved '.format(ImageOverlay.name), 'Info',wx.OK | wx.ICON_EXCLAMATION)

        self.FCNButton.Enable(False)
        self.Th = FCNThread(self, ImageOI_overlay ,FCNOI_name,LabelOI_names)


    def FCNThreadResult(self,event):
        """
        Get the event from :class:`fsleyes_plugin_epicseg.threadfcn.EVT_THREAD`: 
        Load the threshold NIFTI mask in FSLeyes
        """
        if event.data != None:
            overlay_name=event.data[0]
            mask=event.data[1]
            ImageOI_overlay = self.__overlayList.find(overlay_name)
            mask_name="{}_mask".format(overlay_name)
            self.createOverlay(mask_name,ImageOI_overlay,mask)
        self.FCNButton.Enable()
        return wx.MessageBox(event.msg, 'Info', wx.OK | wx.ICON_EXCLAMATION)


    def createOverlay(self, mask_name, overlay, data):
        """Create a 3D mask which has the same size as an
        overlay, and insert it into the overlay list.
        """
        if overlay is None:
            return

        # name = '{}_{}'.format(overlay.name, mask_name)
        name = mask_name
        new_ov = copyoverlay.copyImage(self.__overlayList,
                                       self.__displayCtx,
                                       overlay,
                                       createMask=False,
                                       copy4D=False,
                                       copyDisplay=False,
                                       name=name,
                                       data=data)
        self.__displayCtx.selectOverlay(new_ov)
        self.__displayCtx.getDisplay(new_ov).alpha=30
        if self.__displayCtx.getDisplay(new_ov).opts.name.find("VolumeOpts")!=-1:
            self.__displayCtx.getDisplay(new_ov).opts.cmap='hsv'

    @staticmethod
    def defaultLayout():
        return {
            'location' : wx.BOTTOM,
        }


    @staticmethod
    def supportedViews():
        from fsleyes.views.orthopanel import OrthoPanel
        return [OrthoPanel]



