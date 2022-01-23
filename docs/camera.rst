:py:class:`Camera` Reference
============================

.. autoclass:: visca_over_ip.Camera
    :members: __init__, close_connection,
        set_power, pantilt, pantilt_home, pantilt_reset, get_pantilt_position,
        zoom, zoom_to, get_zoom_position,
        increase_exposure_compensation, decrease_exposure_compensation, set_focus_mode, get_focus_mode, manual_focus,
        save_preset, recall_preset

.. note::
    The :py:class:`Camera` class has more public methods than are documented here.
    You're free to use these methods, although you should consider them a work-in-progress.
