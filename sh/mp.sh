#!/bin/bash

main () {
    MP_OLD=$(lpstat -s | grep usb | cut -d '=' -f2)
    MP_NEW=$(lpinfo -v | grep usb | cut -d '=' -f2)
    MP_NAME=$(lpinfo -v | grep usb | cut -d '?' -f1 | cut -d '/' -f3,4 | tr / _)
    if [ ! $MP_OLD ]
    then
        echo "Current printer id: None"
        MP_OLD="0"
    fi

    if [ $MP_NEW ]
    then
        echo "New printer id: $MP_NEW"
        if [ $MP_NEW != $MP_OLD ]
        then
            echo "Printer changed"
            lpadmin -x $MP_NAME
            lpadmin -p $MP_NAME -E -v usb://EPSON/LX-350?serial=$MP_NEW
            lpadmin -d $MP_NAME
        fi
        return 0
    fi
    return 1
}

main
