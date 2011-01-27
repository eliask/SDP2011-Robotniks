#!/usr/bin/env python

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst

class GstCapture(gtk.DrawingArea):
    def __init__(self, filename):
        gtk.DrawingArea.__init__(self)
        self.filename = filename

        self.pipeline = gst.parse_launch(
            "v4l2src ! ffmpegcolorspace !  autovideosink")

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.on_message)
        bus.connect('sync-message::element', self.on_sync_message)
        self.connect('realize', self.on_realize) #needed?

        self.pipeline.set_state(gst.STATE_PLAYING)

    def on_realize(self, widget):
        self.gc = widget.window.new_gc()

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.pipeline.set_state(gst.STATE_NULL)

    def on_sync_message(self, bus, message):
        print "sync msg!"
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == 'prepare-xwindow-id':
            # Assign the viewport
            imagesink = message.src
            imagesink.set_property('force-aspect-ratio', True)
            gtk.gdk.threads_enter()
            imagesink.set_xwindow_id(self.window.xid)
            self.got_frame()
            gtk.gdk.threads_leave()

    def got_frame(self):
        drawable = self.window
        colormap = drawable.get_colormap()
        print "Size:",drawable.get_size()
        pixbuf = gtk.gdk.Pixbuf( gtk.gdk.COLORSPACE_RGB,
                                 0, 8, *drawable.get_size())
        # pixbuf = pixbuf.get_from_drawable(
        #     drawable, colormap, 0,0,0,0, *drawable.get_size() )

        print "Saved file: %s" % self.filename
        pixbuf.save(self.filename, 'png')

class GTK_Main(object):
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.size = (768,576)
        self.window.set_default_size(*self.size)
        self.window.connect("destroy", gtk.main_quit)
        self.capture = GstCapture("test.png")
        self.window.add(self.capture)
        self.window.show_all()

GTK_Main()
gtk.gdk.threads_init()
gtk.main()
