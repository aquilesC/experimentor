"""
    UUTrack.Model.workerSaver
    =========================
    When working with multi threading in Python it is important to define the function that will be run in a separate
    thread. workerSaver is just a function that will be moved to a separate, parallel thread to save data to disk
    without interrupting the acquisition.

    Since the workerSaver function will be passed to a different Process (via the *multiprocessing* package) the only
    way for it to receive data from other threads is via a Queue. The workerSaver will run continuously until it finds a
    string as the next item.

    To understand how the separate process is created, please refer to
    :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.movieSave`

    The general principle is

        >>> filename = 'name.hdf5'
        >>> q = Queue()
        >>> metadata = _session.serialize() # This prints a YAML-ready version of the session.
        >>> p = Process(target=workerSaver, args=(filename, metaData, q,))
        >>> p.start()
        >>> q.put([1, 2, 3])
        >>> q.put('Stop')
        >>> p.join()

    :copyright: 2017

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""
from datetime import datetime

import h5py
import numpy as np


def workerSaver(fileData, meta, q):
    """Function that can be run in a separate thread for continuously save data to disk.

    :param str fileData: the path to the file to use.
    :param str meta: Metadata. It is kept as a string in order to provide flexibility for other programs.
    :param Queue q: Queue that will store all the images to be saved to disk.
    """

    f = h5py.File(fileData, "a")  # This will append the file.
    now = str(datetime.now())
    g = f.create_group(now)

    keep_saving = True  # Flag that will stop the worker function if running in a separate thread.
                        # Has to be submitted via the queue a string 'exit'

    g.create_dataset('metadata', data=meta.encode("ascii","ignore"))
    i = 0
    j = 0
    first = True
    while keep_saving:
        while not q.empty() or q.qsize()>0:
            img = q.get()
            if isinstance(img, str):
                keep_saving = False
            elif first:  # First time it runs, creates the dataset
                x = img.shape[0]
                y = img.shape[1]
                allocate_memory = 250 # megabytes of memory to allocate
                allocate = int(allocate_memory/img.nbytes*1024*1024)
                print('Allocate: %s' % allocate)
                d = np.zeros((x,y,allocate),dtype='uint16')
                dset = g.create_dataset('timelapse', (x, y, allocate), maxshape=(x, y, None),  compression='gzip',  compression_opts=1, dtype='i2')  # The images are going to be stacked along the z-axis.
                #dset[:, :, i] = img                                                                 # The shape along the z axis will be increased as the number of images increase.
                # dset = g.create_dataset('thumbnail',data = imsave(img))
                d[:,:,i] = img
                i += 1
                first = False
            else:
                if i == allocate:
                    dset[:,:,j:j+allocate] = d
                    dset.resize((x,y,j+2*allocate))
                    d = np.zeros((x, y, allocate),dtype='uint16')
                    i = 0
                    j += allocate
                d[:, :, i] = img
                i+=1

    if j>0 or i>0:
        dset[:, :, j:j+allocate] = d # Last save before closing
    print('Finishing writing to disk...')
    f.flush()
    f.close()
    print('Finish writing to disk')


def clearQueue(q):
    """Clears the queue by reading it.

    :params q: Queue to be cleaned.
    """
    while not q.empty() or q.qsize()>0:
        q.get()
