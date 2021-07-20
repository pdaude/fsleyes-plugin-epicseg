#!/usr/bin/env python
#Author : Pierre Daudé <pierre-daude@hotmail.fr>
#
#threadfcn.py defines plugin thread class.

"""This module provides the :class:`.FCNThread`.
The :class: `.THREAD_Event` gives information on the thread progress to the main frame.
"""
import wx
from threading import Thread
import os.path as op
import os
import tensorflow as tf
import keras
import numpy as np

EVT_THREAD_ID = wx.NewId()


def EVT_THREAD(win, func):
    """Thread Event."""
    win.Connect(-1, -1, EVT_THREAD_ID, func)

def rescale_intensity(image, thres=(1.0, 99.0)):
    """ Rescale the image intensity to the range of [0, 1] """
    val_l, val_h = np.percentile(image, thres)
    image2 = image
    image2[image < val_l] = val_l
    image2[image > val_h] = val_h
    image2 = (image2.astype(np.float32) - val_l) / (val_h - val_l)
    return image2

def crop_image(image, cx, cy, size):
        """ Crop a 3D image using a bounding box centred at (cx, cy) with specified size """
        X, Y = image.shape[:2]
        r1 ,r2 = int(size[0] / 2),int(size[1] / 2)
        x1, x2 = cx - r1, cx + r1
        y1, y2 = cy - r2, cy + r2
        x1_, x2_ = max(x1, 0), min(x2, X)
        y1_, y2_ = max(y1, 0), min(y2, Y)
        # Crop the image
        crop = image[x1_: x2_, y1_: y2_]
        # Pad the image if the specified size is larger than the input image size
        if crop.ndim == 3:
            crop = np.pad(crop,((x1_ - x1, x2 - x2_), (y1_ - y1, y2 - y2_), (0, 0)),'constant')
        elif crop.ndim == 4:
            crop = np.pad(crop,((x1_ - x1, x2 - x2_), (y1_ - y1, y2 - y2_), (0, 0), (0, 0)),'constant')
        elif crop.ndim == 2:
            crop = np.pad(crop,((x1_ - x1, x2 - x2_), (y1_ - y1, y2 - y2_)),'constant')
        else:
            print('Error: unsupported dimension, crop.ndim = {0}.'.format(crop.ndim))
            exit(0)
        return crop



class THREAD_Event(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self,msg,data=None):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_THREAD_ID)
        self.data = data
        self.msg = msg



class FCNThread(Thread):
    """
    :param wxObject: the wx.Panel link to this thread
    :param imageOverlay: image overlay chosen in the dialog box
    :param FCNOI_name: name of the FCN chosen in the dialog box
    :param LabelOI_names: name of the ROI(s) chosen in the dialog box
    
    """
    

    def __init__(self, wxObject, imageOverlay ,FCNOI_name,LabelOI_names):
        """
        """
        Thread.__init__(self)

        self.wxObject = wxObject
        self.imageOverlay = imageOverlay
        self.FCN_name=FCNOI_name
        self.label_names_list= LabelOI_names


        self.start()  # start the thread
    def run(self):
        """
        """
        if self.FCN_name=="U-Net":
            path_model_UNet = op.join(op.dirname(op.abspath(__file__)),'UNet48_first_layer')
            FCN_model=keras.models.load_model(path_model_UNet)

        
        img_size=self.imageOverlay.shape
        img_sqz=np.squeeze(np.copy(self.imageOverlay[:]))
        img_sqz_size=img_sqz.shape
        #Crop image
        crop_shape=(256,192)
        ct_th=99.0
        X,Y =img_sqz_size[0],img_sqz_size[1]
        cx,cy =int(X/2), int(Y/2)
        cropped_img=crop_image(img_sqz,cx,cy,crop_shape)
        cropped_img_size=cropped_img.shape
        predict_label=np.zeros(cropped_img_size)
        cropped_img= rescale_intensity(cropped_img, (1.0,ct_th))
        if len(cropped_img_size)==2:
            return wx.PostEvent(self.wxObject, THREAD_Event('FCN can not handle 2D image',None))

        elif len(cropped_img_size)==3:
            for t in range(cropped_img_size[-1]):
                frames=np.mod(np.array([-1,0,1])+t,cropped_img_size[-1])
                img=cropped_img[...,frames.tolist()]
                
                pred_val = tf.cast(tf.argmax(FCN_model(img[np.newaxis,...]), axis=-1), dtype=tf.int32)
                predict_label[...,t]=np.squeeze(pred_val.numpy())
        else:
             return wx.PostEvent(self.wxObject, THREAD_Event('FCN can not handle 4D image',None))

        #Remove labels which are not chosen by the user
        labels_names=["Paracardial Fat","Epicardial Fat","Heart Ventricles"]
        labels_list=[1,2,3]
        label_to_remove=list(set(labels_names).symmetric_difference(self.label_names_list))
        for label_name in label_to_remove:
            label=labels_list[labels_names.index(label_name)]
            predict_label[predict_label==label]=0

        Xc,Yc =predict_label.shape[0],predict_label.shape[1]
        cxc,cyc =int(Xc/2), int(Yc/2)
        output_label_sqz=crop_image(predict_label,cxc,cyc,img_sqz_size)
        output_label=np.reshape(output_label_sqz,img_size)

        
        wx.PostEvent(self.wxObject, THREAD_Event('Done ! \n Your image has been cropped to (256,192) in order to fit the model',(self.imageOverlay.name,output_label)))

    
    
    
