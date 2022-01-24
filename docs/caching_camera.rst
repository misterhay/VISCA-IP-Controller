:py:class:`CachingCamera`
=========================

The :py:class:`visca_over_ip.CachingCamera` class is a subclass of the :py:class:`Camera` class (see :doc:`camera`).
:py:class:`CachingCamera` is designed to reduce superfluous network traffic in real-time applications.
**CachingCamera has exactly the same API as Camera**.
There are some important drawbacks to using this class however, and it only improves the performance of a few :py:class:`Camera` methods.

An example application
----------------------

Let's say you want to bind the zoom speed of a camera to the position of a joystick.
To accomplish that, you might write code something like this::

    from visca_over_ip import Camera

    cam = Camera('192.168.0.123')

    def main_loop():
        zoom_speed = get_joystick_zoom_axis()  # imaginary method to read the value of a joystick axis
        cam.zoom(zoom_speed)

Whenever your user is not moving the joystick (which will be most of the time),
the camera is going to be bombarded with instructions to *not zoom* which is kind of a waste.
If we substitute :py:class:`CachingCamera` for :py:class:`Camera` in the above example,
the class will be smart enough to tell the camera to stop zooming just once.
Subsequent ``cam.zoom(0)`` calls will not send a message to the camera.
As soon as the user moves the joystick, communications to the camera will resume.

Methods with caching behavior
-----------------------------

:py:meth:`CachingCamera.get_focus_mode`

:py:meth:`CachingCamera.set_focus_mode`

:py:meth:`CachingCamera.pantilt`

:py:meth:`CachingCamera.zoom`

.. _caching_drawbacks:

Drawbacks
---------

This class depends on having exclusive control over a camera.
That means that if you have some other software or two instances of the same software interfacing with a camera,
:py:class:`CachingCamera` may cause unexpected behavior.

CachingCamera also only has benefits if methods are called multiple times with the same parameters.
In many applications, this doesn't happen.
