#! /bin/bash

HOME_DIR=$(pwd)
echo Home dir is $HOME_DIR
SSH_KEY="id_tunnel_rsa"
SCRIPT="/home/kat/install/kat_client/"
SERVER="kat@10.2.3.55"
main(){
    LAST_VERSION=$(cat VERSION)
    [ "$LAST_VERSION" == "" ] && LAST_VERSION=0
    CHECK_VERSION=$(ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${SERVER} "cat install/kat_client/VERSION")

    [ "$CHECK_VERSION" == "" ] && CHECK_VERSION=0

    if [ "$CHECK_VERSION" == "$LAST_VERSION" ]
    then
        echo "No need to update $LAST_VERSION to $CHECK_VERSION"
    else
        echo "Need to update $LAST_VERSION to $CHECK_VERSION"
        rsync -a -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" ${SERVER}:${SCRIPT} ${HOME_DIR}
        [ "$?" -eq "0" ] || echo "Can not download update"
        # chmod 740 ${HOME_DIR}
        # systemctl daemon-reload
        # systemctl restart kat-remote.service
    fi
}

main
