#! /bin/bash

HOME_DIR="/opt/kat_client/"
SSH_KEY="../id_tunnel_rsa"
SCRIPT="/home/kat/install/kat_client/"
SERVER="kat@10.2.3.55"

main(){
    LAST_VERSION=$(head -n 1 "VERSION" | cut -d '.' -f2)
    [ -z $LAST_VERSION ] && LAST_VERSION=0
    echo "Last version: $LAST_VERSION"

    CHECK_VERSION=$(ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${SERVER} "head -n 1 install/kat_client/VERSION | cut -d '.' -f2")
    CHECK_VERSION=${CHECK_VERSION//[$'\t\r\n']}
    [ -z $CHECK_VERSION ] && CHECK_VERSION=0
    echo "New version: $CHECK_VERSION"

    if [ $CHECK_VERSION -le $LAST_VERSION ]
    then
        echo "No need to update"
    else
        echo "Updating $LAST_VERSION to $CHECK_VERSION"
        rsync -a -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" ${SERVER}:${SCRIPT} ${HOME_DIR}
        [ $? -eq 0 ] || echo "Can not download update"; return $?
        # chmod 740 ${HOME_DIR}
        systemctl daemon-reload
        systemctl restart kat-client.service
        echo "Done!"
    fi
    return 0
}

main
