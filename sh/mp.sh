#!/bin/bash

main () {
    MP_OLD_SERIAL=$(lpstat -s | grep usb | cut -d '=' -f2)
    MP_NEW_URL=$(lpinfo -v | grep usb | cut -d ' ' -f2)
    MP_NEW_SERIAL=$(echo $MP_NEW_URL | cut -d '=' -f2)
    MP_NEW_NAME=$(echo $MP_NEW_URL | cut -d '?' -f1 | cut -d '/' -f3,4 | tr / _)

    if [ ! $MP_OLD_SERIAL ]
    then
        echo "Current printer id: None"
        MP_OLD="0"
    fi

    if [ $MP_NEW_SERIAL ]
    then
        echo "New printer id: $MP_NEW_SERIAL"
        if [ $MP_NEW_SERIAL != $MP_OLD_SERIAL ]
        then
            echo "Printer changed"
            lpadmin -x $MP_NEW_NAME
            lpadmin -p $MP_NEW_NAME -E -v usb://EPSON/LX-350?serial=$MP_NEW_SERIAL
            lpadmin -d $MP_NEW_NAME
        fi
        return 0
    fi
    return 1
}

main
