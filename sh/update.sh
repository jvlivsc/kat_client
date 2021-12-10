#! /bin/bash

HOME_DIR="/opt/kat_client/"
SSH_KEY="../id_tunnel_rsa"
SCRIPT="/home/kat/install/kat_client/"
SERVER=""

main(){
    app_version=$(head -n 1 "../VERSION" | cut -d '.' -f2)
    [ -z $app_version ] && app_version=0
    echo "Application version: $app_version"

    new_version=$(ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${SERVER} "head -n 1 install/kat_client/VERSION | cut -d '.' -f2")
    new_version=${new_version//[$'\t\r\n']}
    [ -z $new_version ] && new_version=0
    echo "New version: $new_version"

    if [ $new_version -gt $app_version ]
    then
        echo "Updating $app_version to $new_version"
        rsync -a -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" ${SERVER}:${SCRIPT} ${HOME_DIR}
        echo "last command returns $?"
        [ $? -eq 0 ] || return "Can not download update"
        # chmod 740 ${HOME_DIR}
        systemctl daemon-reload
        systemctl restart kat-client.service
        echo "Done!"
    else
        echo "No updates needed"
    fi
    return 0
}

main
