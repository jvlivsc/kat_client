#!/bin/bash

SERVER=$1
USER=$2
SSH_PORT=$3
VNC_PORT=$4
# echo "$SERVER $USER $SSH_PORT $VNC_PORT"

main () {
    # Проверка pid файла на существование
    if [ -f /var/run/autossh_tunnel.pid ]
    then
        # существутет
        read FILE_PID < /var/run/autossh_tunnel.pid
        # проверяем существует ли процесс
        # echo "dBug" "PID файл существует: PID=$FILE_PID"
        if ps -p $FILE_PID &>/dev/null
        then
            # процесс существует
            # echo "dBug" "Процесс с PID=$FILE_PID активен"
            PROCESS_PID=$(ps aux | grep "autossh" | grep "localhost:6080 $USER@$SERVER" | awk '{print $2}')
            if [ "$FILE_PID" == "$PROCESS_PID" ]
            then
                # echo "dBug" "$FILE_PID == $PROCESS_PID"
                #Процесс тот, ищём детей
                CHILDREN=$(pgrep -P $PROCESS_PID)
                # echo "dBug" "CHILDREN=$CHILDREN"
                if [ "$CHILDREN" != "" ]
                then
                    if [ "$(echo "$CHILDREN" | wc -l)" -eq "1" ]
                    then
                        if ps aux | grep "localhost:6080 $USER@$SERVER" | awk '{print $2}' | grep -q $CHILDREN
                        then
                            CHILD_PID=$(ps x | grep "localhost:6080 $USER@$SERVER" | grep $CHILDREN)
                            #ребёнок есть, все ок
                            # echo "dBug" "CHILD: $CHILD_PID"
                            # echo "dBug" "Процессы активны, выходим из проверки"
                        else
                            #ищём заблудшие души, убиваем, удаляем и континюе
                            # echo "dBug" "ssh тунеля не обнаружено"
                            if ! ping -c 1 ${SERVER}
                            then
                                # echo && myLog "dBug" "Сервер не доступен"
                                # echo && myLog "dBug" "Continue: go to next loop"
                                return 1
                            fi
                        fi
                    fi
                else
                    # echo "dBug" "убиваем процесс $FILE_PID и удаляем PID-файл"
                    kill -9 $FILE_PID
                    rm -f /var/run/autossh_tunnel.pid
                    # echo "dBug" "Continue: going to text loop"
                    return 1
                fi
            else
                #не тот
                # echo "dBug" "PID файл не соответствует активному autossh процессу"
                if ps aux | grep "autossh" | grep -q "localhost:6080 $USER@$SERVER"
                then
                    # echo "dBug" "$FILE_PID != $(ps x | grep "autossh" | grep "localhost:6080 $USER@$SERVER")"
                    #убиваем его и его дитей, удаляем и континюе
                    FOUND_PID=$(ps aux | grep "autossh" | grep "localhost:6080 $USER@$SERVER" | awk '{print $2}')
                    # echo "dBug" "FINDED_PID=$FOUND_PID"
                    for Kill_Count in $FOUND_PID
                    do
                        # echo "dBug" "Родитель: $Kill_Count"
                        for Child_Count in $(pgrep -P $Kill_Count)
                        do
                            # echo "dBug" "Убит ребёнок: $Child_Count"
                            kill Child_Count
                        done
                        # echo "dBug" "Убит родитель: $Kill_Count"
                        kill $Kill_Count
                    done
                    # echo "dBug" "Удаляем PID-файл"
                    rm -f /var/run/autossh_tunnel.pid
                    # echo "dBug" "Выходим из проверки"
                fi
            fi
        else
            #Процесс не существует
            #проверяем систему
            # echo "dBug" "Процесса с PID $FILE_PID не существует"
            # echo "dBug" "Очистка системы"
            if ps aux | grep "autossh" | grep -q "localhost:6080 $USER@$SERVER"
            then
                ASSH_PROCESS_PID=$(ps aux | grep "autossh" | grep "localhost:6080 $USER@$SERVER" | awk '{print $2}')
                for Kill_Count in $ASSH_PROCESS_PID
                do
                    # echo "dBug" "Убит autossh: $Kill_Count"
                    kill $Kill_Count
                done
            fi
            if ps aux | grep "ssh" | grep -q "localhost:6080 $USER@$SERVER"
            then
                SSH_PROCESS_PID=$(ps aux | grep "ssh" | grep  "localhost:6080 $USER@$SERVER" | awk '{print $2}')
                for Kill_Count in $SSH_PROCESS_PID
                do
                    # echo "dBug" "Убит ssh $Kill_Count"
                    kill $Kill_Count
                done
            fi
            # echo "dBug" "Удаляем PID файл"
            rm -f /var/run/autossh_tunnel.pid
            # echo "dBug" "Выходим из проверки"
        fi
    else
        #нету
        #поднимаем тунель
        # echo "dBug" "PID файла не существует"
        # echo "dBug" "Поднимает тунель"
        nice autossh -M $RANDOM -N -i "../id_tunnel_rsa" -o "StrictHostKeyChecking=no" -o "ExitOnForwardFailure=yes" -o "ServerAliveInterval=5" -o "ServerAliveCountMax=3" -R $SSH_PORT:localhost:22 -R $VNC_PORT:localhost:6080 $USER@$SERVER 2 &
        FILE_PID=$!
        # echo "dBug" "autossh PID -> $FILE_PID"
        echo $FILE_PID > /var/run/autossh_tunnel.pid
        # echo "dBug" "Выходим из проверки"
    fi
    return 0
}

main
