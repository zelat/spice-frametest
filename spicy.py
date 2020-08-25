# -*- coding: utf-8 -*-

import gi
gi.require_version('SpiceClientGtk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import SpiceClientGtk, SpiceClientGLib, GObject, Gtk

class Viewer(GObject.GObject):

    __gsignals__ = {
        "add-display-widget": (GObject.SignalFlags.RUN_FIRST, None, [object]),
        "size-allocate": (GObject.SignalFlags.RUN_FIRST, None, [object]),
        "focus-in-event": (GObject.SignalFlags.RUN_FIRST, None, [object]),
        "focus-out-event": (GObject.SignalFlags.RUN_FIRST, None, [object]),
        "pointer-grab": (GObject.SignalFlags.RUN_FIRST, None, []),
        "pointer-ungrab": (GObject.SignalFlags.RUN_FIRST, None, []),
        "connected": (GObject.SignalFlags.RUN_FIRST, None, []),
        "disconnected": (GObject.SignalFlags.RUN_FIRST, None, [str, str]),
        "auth-error": (GObject.SignalFlags.RUN_FIRST, None, [str, bool]),
        "auth-rejected": (GObject.SignalFlags.RUN_FIRST, None, [str]),
        "need-auth": (GObject.SignalFlags.RUN_FIRST, None, [bool, bool]),
        "agent-connected": (GObject.SignalFlags.RUN_FIRST, None, []),
        "grab-keys-pressed": (GObject.SignalFlags.RUN_FIRST, None, []),
    }

    def __init__(self, info):
        GObject.GObject.__init__(self)
        self._display = None
        self._info = info # 服务器信息

    # 建立与服务器的会话连接
    def open(self):
        fd = self._get_fd_for_open()
        if fd is not None:
            self._open_fd(fd)
        else:
            self._open_host()

    # 关闭与服务器的会话连接
    def close(self):
        raise NotImplementedError()

    # 获取用户创建的与服务器的套接字连接
    def _get_fd_for_open(self):
        None

    def remove_display_widget(self, widget):
        if self._display and self._display in widget.get_children():
            widget.remove(self._display)

    #######################################################

    # Internal API that will be overwritten by subclasses #

    #######################################################

    # 使用用户创建的套接字来建立会话连接
    def _open_fd(self, fd):
        raise NotImplementedError()

    # 使用连接协议自动创建的套接字来建立会话连接
    def _open_host(self):
        raise NotImplementedError()

class SpiceViewer(Viewer):

    def __init__(self, *args, **kwargs):
        Viewer.__init__(self, *args, **kwargs)
        self._spice_session = None

    def close(self):
        if self._display:
            self._display.destroy()
        self._spice_session.disconnect()

    def _open_fd(self, fd):
        self._create_session()
        self._spice_session.open_fd(fd)

    def _open_host(self):
        self._create_session()
        host, port, tlsport, password = self._info.get_conn_host()
        self._spice_session.set_property("host", str(host))
        if port:
            self._spice_session.set_property("port", str(port))
        if tlsport:
            self._spice_session.set_property("tls-port", str(tlsport))
        if password:
            self._spice_session.set_property("password", str(password))
        self._spice_session.connect()

    # 创建spice会话对象
    def _create_session(self):
        self._spice_session = SpiceClientGLib.Session.new()
        GObject.GObject.connect(self._spice_session, "channel-new", self._channel_new_cb)

    # channel创建信号回调函数
    def _channel_new_cb(self, session, channel):
        GObject.GObject.connect(channel, "open-fd", self._channel_open_fd_cb)

        if (type(channel) == SpiceClientGLib.MainChannel):
            GObject.GObject.connect(channel, "channel-event", self._channel_event_cb)
        elif (type(channel) == SpiceClientGLib.DisplayChannel and not self._display):
            # 创建显示部件
            channel_id = channel.get_property("channel-id")
            self._display = SpiceClientGtk.Display.new(session, channel_id)
            self.emit("add-display-widget", self._display)
            self._display.realize()
            self._display.connect("mouse-grab", self._mouse_grab_cb)
            self._display.connect("grab-keys-pressed", self._grab_keys_pressed_cb)
            self._display.show()
            channel.connect()
        # elif (type(channel) == SpiceClientGLib.InputsChannel):
        #     None
        # elif (type(channel) == SpiceClientGLib.PlaybackChannel):
        #     None

    # channel关联套接字句柄信号回调函数，当channel.connect()发现spice会话对象没有可用的套接字句柄时会触发此信号
    def _channel_open_fd_cb(self, channel, with_tls):
        None

    # channel事件信号回调函数
    def _channel_event_cb(self, channel, event):
        if event == SpiceClientGLib.ChannelEvent.CLOSED:
            self.emit("disconnected", None, None)
        elif event == SpiceClientGLib.ChannelEvent.ERROR_AUTH:
            if not self._spice_session.get_property("password"):
                self.emit("need-auth", True, False)
            else:
                self.emit("auth-error", channel.get_error().message, False)
        elif "ERROR" in str(event):
            self.emit("disconnected", channel.get_error().message, None)

    # 鼠标捕获信号回调函数
    def _mouse_grab_cb(self, display, status):
        if status:
            self.emit("pointer-grab")
        else:
            self.emit("pointer-ungrab")

    # 捕获键按下信号回调函数
    def _grab_keys_pressed_cb(self, display):
        self.emit("grab-keys-pressed")

class HostInfo():
    def __init__(self):
        self.gaddr = "172.118.18.13"
        self.gport = 5901
        self.gtlsport = None
        self.gpassword = "24olB8"

    def get_conn_host(self):
        host = self.gaddr
        port = self.gport
        tlsport = self.gtlsport
        password = self.gpassword
        return host, port, tlsport, password

def add_display_widget_cb(viewer, display):
    win.add(display)
    #win.fullscreen()

def grab_keys_pressed_cb(viewer):
    win.unfullscreen()

win = Gtk.Window(title="Spicy")
info = HostInfo()
viewer = SpiceViewer(info)
viewer.open()
viewer.connect("add-display-widget", add_display_widget_cb)
viewer.connect("grab-keys-pressed", grab_keys_pressed_cb)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

