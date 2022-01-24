Tutorial
========

Installation
------------

Run a command something like this to download and install the package from PyPI:

``pip install visca_over_ip``


Package Contents
----------------

``visca_over_ip`` exports two main classes that you'll interact with.
They are :py:class:`visca_over_ip.Camera` which allows for control and querying of a camera with VISCA over IP,
and its subclass :py:class:`visca_over_ip.CachingCamera` which offers some performance improvements with a few :ref:`drawbacks<caching_drawbacks>`.

You can skip straight to the :doc:`camera` if you like API docs, or you can read the rest of this tutorial for some example usage.

Simple Usage
-------------

In this example we will cause the camera to pan left and right at half speed as if it was shaking its head::

    import time
    from visca_over_ip import Camera

    cam = Camera('192.168.0.123')  # Your camera's IP address or hostname here

    while True:
        cam.pantilt(pan_speed=-12, tilt_speed=0)
        time.sleep(1)  # wait one second
        cam.pantilt(pan_speed=12, tilt_speed=0)



Multiple Cameras
----------------

In this example, we will recall the first preset on one camera and the third preset on another camera::

    from_visca_over_ip import Camera

    cam = Camera('192.168.0.101')
    cam.recall_preset(0)
    cam.close_connection()  # Important when switching between cameras

    cam = Camera('192.168.0.102')
    cam.recall_preset(2)
    cam.close_connection()  # less important here, but doesn't hurt

.. note::
    It is not possible to simultaneously control two cameras which use the same port.
    If you desire simultaneous control of multiple cameras without switching as in the above example,
    you will need to set up your cameras to use different ports.