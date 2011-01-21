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

public interface CommanderPrx extends Ice.ObjectPrx
{
    public void sendMessage(int message);
    public void sendMessage(int message, java.util.Map<String, String> __ctx);
}
