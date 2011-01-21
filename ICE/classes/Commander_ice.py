# **********************************************************************
#
# Copyright (c) 2003-2009 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

# Ice version 3.3.1
# Generated from file `Commander.ice'

import Ice, IcePy, __builtin__

if not Ice.__dict__.has_key("_struct_marker"):
    Ice._struct_marker = object()

# Start of module Robotnik
_M_Robotnik = Ice.openModule('Robotnik')
__name__ = 'Robotnik'

if not _M_Robotnik.__dict__.has_key('Commander'):
    _M_Robotnik.Commander = Ice.createTempClass()
    class Commander(Ice.Object):
        def __init__(self):
            if __builtin__.type(self) == _M_Robotnik.Commander:
                raise RuntimeError('Robotnik.Commander is an abstract class')

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::Robotnik::Commander')

        def ice_id(self, current=None):
            return '::Robotnik::Commander'

        def ice_staticId():
            return '::Robotnik::Commander'
        ice_staticId = staticmethod(ice_staticId)

        #
        # Operation signatures.
        #
        # def sendMessage(self, message, current=None):

        def __str__(self):
            return IcePy.stringify(self, _M_Robotnik._t_Commander)

        __repr__ = __str__

    _M_Robotnik.CommanderPrx = Ice.createTempClass()
    class CommanderPrx(Ice.ObjectPrx):

        def sendMessage(self, message, _ctx=None):
            return _M_Robotnik.Commander._op_sendMessage.invoke(self, ((message, ), _ctx))

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_Robotnik.CommanderPrx.ice_checkedCast(proxy, '::Robotnik::Commander', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_Robotnik.CommanderPrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

    _M_Robotnik._t_CommanderPrx = IcePy.defineProxy('::Robotnik::Commander', CommanderPrx)

    _M_Robotnik._t_Commander = IcePy.defineClass('::Robotnik::Commander', Commander, (), True, None, (), ())
    Commander.ice_type = _M_Robotnik._t_Commander

    Commander._op_sendMessage = IcePy.Operation('sendMessage', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, (), (((), IcePy._t_int),), (), None, ())

    _M_Robotnik.Commander = Commander
    del Commander

    _M_Robotnik.CommanderPrx = CommanderPrx
    del CommanderPrx

# End of module Robotnik
