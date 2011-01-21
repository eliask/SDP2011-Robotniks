// **********************************************************************
//
// Copyright (c) 2003-2009 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************

// Ice version 3.3.1

package Robotnik;

public final class CommanderPrxHelper extends Ice.ObjectPrxHelperBase implements CommanderPrx
{
    public void
    sendMessage(int message)
    {
        sendMessage(message, null, false);
    }

    public void
    sendMessage(int message, java.util.Map<String, String> __ctx)
    {
        sendMessage(message, __ctx, true);
    }

    @SuppressWarnings("unchecked")
    private void
    sendMessage(int message, java.util.Map<String, String> __ctx, boolean __explicitCtx)
    {
        if(__explicitCtx && __ctx == null)
        {
            __ctx = _emptyContext;
        }
        int __cnt = 0;
        while(true)
        {
            Ice._ObjectDel __delBase = null;
            try
            {
                __delBase = __getDelegate(false);
                _CommanderDel __del = (_CommanderDel)__delBase;
                __del.sendMessage(message, __ctx);
                return;
            }
            catch(IceInternal.LocalExceptionWrapper __ex)
            {
                __handleExceptionWrapper(__delBase, __ex, null);
            }
            catch(Ice.LocalException __ex)
            {
                __cnt = __handleException(__delBase, __ex, null, __cnt);
            }
        }
    }

    public static CommanderPrx
    checkedCast(Ice.ObjectPrx __obj)
    {
        CommanderPrx __d = null;
        if(__obj != null)
        {
            try
            {
                __d = (CommanderPrx)__obj;
            }
            catch(ClassCastException ex)
            {
                if(__obj.ice_isA("::Robotnik::Commander"))
                {
                    CommanderPrxHelper __h = new CommanderPrxHelper();
                    __h.__copyFrom(__obj);
                    __d = __h;
                }
            }
        }
        return __d;
    }

    public static CommanderPrx
    checkedCast(Ice.ObjectPrx __obj, java.util.Map<String, String> __ctx)
    {
        CommanderPrx __d = null;
        if(__obj != null)
        {
            try
            {
                __d = (CommanderPrx)__obj;
            }
            catch(ClassCastException ex)
            {
                if(__obj.ice_isA("::Robotnik::Commander", __ctx))
                {
                    CommanderPrxHelper __h = new CommanderPrxHelper();
                    __h.__copyFrom(__obj);
                    __d = __h;
                }
            }
        }
        return __d;
    }

    public static CommanderPrx
    checkedCast(Ice.ObjectPrx __obj, String __facet)
    {
        CommanderPrx __d = null;
        if(__obj != null)
        {
            Ice.ObjectPrx __bb = __obj.ice_facet(__facet);
            try
            {
                if(__bb.ice_isA("::Robotnik::Commander"))
                {
                    CommanderPrxHelper __h = new CommanderPrxHelper();
                    __h.__copyFrom(__bb);
                    __d = __h;
                }
            }
            catch(Ice.FacetNotExistException ex)
            {
            }
        }
        return __d;
    }

    public static CommanderPrx
    checkedCast(Ice.ObjectPrx __obj, String __facet, java.util.Map<String, String> __ctx)
    {
        CommanderPrx __d = null;
        if(__obj != null)
        {
            Ice.ObjectPrx __bb = __obj.ice_facet(__facet);
            try
            {
                if(__bb.ice_isA("::Robotnik::Commander", __ctx))
                {
                    CommanderPrxHelper __h = new CommanderPrxHelper();
                    __h.__copyFrom(__bb);
                    __d = __h;
                }
            }
            catch(Ice.FacetNotExistException ex)
            {
            }
        }
        return __d;
    }

    public static CommanderPrx
    uncheckedCast(Ice.ObjectPrx __obj)
    {
        CommanderPrx __d = null;
        if(__obj != null)
        {
            try
            {
                __d = (CommanderPrx)__obj;
            }
            catch(ClassCastException ex)
            {
                CommanderPrxHelper __h = new CommanderPrxHelper();
                __h.__copyFrom(__obj);
                __d = __h;
            }
        }
        return __d;
    }

    public static CommanderPrx
    uncheckedCast(Ice.ObjectPrx __obj, String __facet)
    {
        CommanderPrx __d = null;
        if(__obj != null)
        {
            Ice.ObjectPrx __bb = __obj.ice_facet(__facet);
            CommanderPrxHelper __h = new CommanderPrxHelper();
            __h.__copyFrom(__bb);
            __d = __h;
        }
        return __d;
    }

    protected Ice._ObjectDelM
    __createDelegateM()
    {
        return new _CommanderDelM();
    }

    protected Ice._ObjectDelD
    __createDelegateD()
    {
        return new _CommanderDelD();
    }

    public static void
    __write(IceInternal.BasicStream __os, CommanderPrx v)
    {
        __os.writeProxy(v);
    }

    public static CommanderPrx
    __read(IceInternal.BasicStream __is)
    {
        Ice.ObjectPrx proxy = __is.readProxy();
        if(proxy != null)
        {
            CommanderPrxHelper result = new CommanderPrxHelper();
            result.__copyFrom(proxy);
            return result;
        }
        return null;
    }
}
