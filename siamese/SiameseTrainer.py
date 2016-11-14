#/usr/bin/python
# --------------------------------------------------------
# Written by Sai Prabhakar, CMU
# --------------------------------------------------------
import sys
import os
os.environ['GLOG_minloglevel'] = '3'

import argparse
import numpy as np
import cv2
import caffe

#import cPickle
#import heapq
#TODO change utils to helper
#from utils.blob import im_to_blob
from pythonlayers.helpers import im_to_blob
#import math

#import matplotlib.pyplot as plt

import IPython

im_target_size = 227

#TODO: manual training (forward backward)
#TODO: convert manual training to step function

blob = caffe.proto.caffe_pb2.BlobProto()
data = open('placesOriginalModel/places205CNN_mean.binaryproto', 'rb').read()
blob.ParseFromString(data)
arr = np.array(caffe.io.blobproto_to_array(blob))
arr = np.squeeze(arr.transpose((2, 3, 1, 0)))
im_scaley = float(im_target_size) / float(256)
im_scalex = float(im_target_size) / float(256)
meanarr = cv2.resize(
    arr,
    None,
    None,
    fx=im_scalex,
    fy=im_scaley,
    interpolation=cv2.INTER_LINEAR)


def _get_image_blob(img_name):

    im = cv2.imread(img_name)
    im_orig = im.astype(np.float32, copy=True)

    #im_orig -= 140.8

    im_shape = im_orig.shape
    im_shape = im_orig.shape
    im_size = im_shape[0:2]  #rows, colmns y,x

    im_scaley = float(im_target_size) / float(im_size[0])
    im_scalex = float(im_target_size) / float(im_size[1])
    im = cv2.resize(
        im_orig,
        None,
        None,
        fx=im_scalex,
        fy=im_scaley,
        interpolation=cv2.INTER_LINEAR)

    processed_ims = im - meanarr
    #processed_ims = im
    #IPython.embed()
    blob = im_to_blob(processed_ims)

    return blob


def _get_blobs(f1, f2, sim):
    """Convert an image and RoIs within that image into network inputs."""
    blobs = {'data': None, 'data_p': None, 'sim': None}
    blobs['data'] = _get_image_blob(f1)
    blobs['data_p'] = _get_image_blob(f2)
    blobs['sim'] = sim.astype(np.float, copy=False)
    #print "blobs containing", blobs['rois'].shape
    return blobs


class SiameseWrapper(object):
    """A simple wrapper around Caffe's solver.
    This wrapper gives us control over he snapshotting process, which we
    use to unnormalize the learned bounding-box regression weights.
    """

    def __init__(self,
                 solver_prototxt,
                 pretrainaedSiameseModel=None,
                 pretrained_model=None,
                 pretrained_model_proto=None,
                 train=1):
        """Initialize the SolverWrapper."""
        import pdb
        pdb.set_trace()
        if train == 1:
            self.solver = caffe.SGDSolver(solver_prototxt)
        else:
            self.siameseTestNet = caffe.Net(
                'siameseModels/siamesePlaces.prototxt', pretrained_model,
                caffe.TEST)

        if pretrainedSiameseModel is not None:
            print('Loading pretrained model '
                  'weights from {:s}').format(pretrainedSiameseModel)
            if train == 1:
                self.solver.net.copy_from(pretrainedSiameseModel)
            else:
                self.siameseTestNet.copy_from(pretrainedSiameseModel)

        elif pretrained_model is not None:

            self.caffenet = caffe.Net(pretrained_model_proto, pretrained_model,
                                      caffe.TEST)

            if train == 1:
                self.solver.net.copy_from(pretrained_model)
            else:
                self.siameseTestNet.copy_from(pretrained_model)
            #IPython.embed()
            #caffenet=[]
        else:
            print('Initializing completely from scratch .... really ?')

        self.solver.test_nets[0].share_with(self.solver.net)

    def testCode(self, fileName):
        f = open(fileName)
        lines = [line.rstrip('\n') for line in f]
        imageDict = {}
        imlist = []

        if train == 1:
            currentNet = self.solver.net
        else:
            currentNet = self.siameseTestNet

        for i in lines:
            temp = i.split(' ')
            imageDict[temp[0]] = int(temp[1])
            imlist.append(temp[0])

        for i in range(len(imlist)):
            for j in range(i, len(imlist)):
                sim1 = np.array([
                    1
                ])  # np.array( [int(imageDict[ imlist[i] ] == imageDict[ imlist[j] ])] )

                blobs = _get_blobs('data/' + imlist[i], 'data/' + imlist[j],
                                   sim1)
                blobs_out1 = currentNet.forward(
                    data=blobs['data'].astype(
                        np.float32, copy=False),
                    data_p=blobs['data_p'].astype(
                        np.float32, copy=False),
                    sim=blobs['sim'].astype(
                        np.float32, copy=False), )
                loss1 = blobs_out1['loss']
                print i, j, imageDict[imlist[i]], imageDict[imlist[j]], loss1


class SiameseTrainWrapper2(object):
    """A simple wrapper around Caffe's solver.
    This wrapper gives us control over he snapshotting process, which we
    use to unnormalize the learned bounding-box regression weights.
    """

    def __init__(self,
                 solver_prototxt,
                 pretrainedSiameseModel=None,
                 pretrained_model=None,
                 pretrained_model_proto=None,
                 train=1):
        """Initialize the SolverWrapper."""

        if train == 1:
            self.solver = caffe.SGDSolver(solver_prototxt)
        else:
            self.siameseTestNet = caffe.Net(
                'siameseModels/siamesePlaces.prototxt', pretrained_model,
                caffe.TEST)

        if pretrainedSiameseModel is not None:
            print('Loading pretrained model '
                  'weights from {:s}').format(pretrainedSiameseModel)
            if train == 1:
                self.solver.net.copy_from(pretrainedSiameseModel)
            else:
                self.siameseTestNet.copy_from(pretrainedSiameseModel)

        elif pretrained_model is not None:

            self.caffenet = caffe.Net(pretrained_model_proto, pretrained_model,
                                      caffe.TEST)

            if train == 1:
                self.solver.net.copy_from(pretrained_model)
            else:
                self.siameseTestNet.copy_from(pretrained_model)
            #IPython.embed()
            #caffenet=[]
        else:
            print('Initializing completely from scratch .... really ?')

        self.solver.test_nets[0].share_with(self.solver.net)

    def testCode(self):
        '''f= open(fileName)
        lines = [line.rstrip('\n') for line in f]
        imageDict={}
        imlist=[]

        if train==1:
          currentNet= self.solver.net
        else:
          currentNet= self.siameseTestNet

        for i in lines:
          temp= i.split(' ')
          imageDict[ temp[0] ]= int(temp[1])
          imlist.append( temp[0] )'''

        #import ipdb
        #ipdb.set_trace()
        #self.solver.test_nets[0].forward()
        #self.solver.net.forward()
        #self.solver.test_nets[0].blobs['conv1'].data[0,0,1,1:5]
        #self.solver.net.blobs['conv1'].data[0,0,1,1:5]
        #import IPython
        #IPython.embed()

        for k in range(100):
            disLoss = 0
            simLoss = 0
            simC = 0
            disC = 0
            for i in range(131):
                self.solver.step(1)
                loss1 = self.solver.net.blobs['loss'].data
                # self.solver.net.layers[0].source_file
                # self.solver.test_nets[0].forward()
                #import IPython
                #IPython.embed()
                if self.solver.net.blobs['sim'].data == 1:
                    if self.solver.net.layers[0].m_batch_1[0][
                            1] != self.solver.net.layers[0].m_batch_2[0][1]:
                        print "1 error found"
                    simC += 1
                    simLoss += loss1
                else:
                    if self.solver.net.layers[0].m_batch_1[0][
                            1] == self.solver.net.layers[0].m_batch_2[0][1]:
                        print "2 error found"
                    disC += 1
                    disLoss += loss1
                #simLoss+= loss1#self.solver.net.blobs['loss'].data
                #print i
                #print i, loss1, self.solver.net.blobs[
                #    'sim'].data#, self.solver.net.layers[0].m_batch_1[0][
                #1], self.solver.net.layers[0].m_batch_2[0][1]
            print "**** net loss", simLoss / (simC + 0.1), disLoss / (
                disC + 0.1), simC, disC


def siameseTrainer(siameseSolver, fileName, pretrained_model,
                   pretrained_model_proto):
    #numImagePair = 1  #len(imdb.image_index)
    # timers
    #_t = {'im_detect' : Timer(), 'misc' : Timer()}

    sw = SiameseTrainWrapper2(
        siameseSolver,
        pretrained_model=pretrained_model,
        pretrained_model_proto=pretrained_model_proto,
        train=1)
    # import IPython
    # IPython.embed()

    sw.testCode()

    #sw = SiameseWrapper(siameseSolver, pretrained_model=pretrained_model, pretrained_model_proto= pretrained_model_proto, train=0 )

    #sw.testCode( fileName)
