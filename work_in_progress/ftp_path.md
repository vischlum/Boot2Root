# nmap
On commence par scanner tous les ports réseaux de la machine, pour identifier les potentielles voies d'accès : `nmap -p- <IP>` :
```
Not shown: 65529 closed ports
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
80/tcp  open  http
143/tcp open  imap
443/tcp open  https
993/tcp open  imaps
```

# dirb
Rien d'intéressant sur le site HTTP (port 80), et il n'y a rien à la racine HTTPS.  
On va donc utiliser [dirb](https://tools.kali.org/web-applications/dirb) pour déterminer les dossiers existants : `dirb https://<IP> /usr/share/wordlists/dirb/common.txt`. On trouve `/forum`, `/phpmyadmin` et `/webmail`. Commençons par le forum, puisque c'est le seul à ne pas nous imposer de nous connecter.

# forum
En arrivant sur le forum, on remarque tout de suite un topic intéressant « Probleme login ? », qui contient des logs d'authentification du serveur. En fouillant, on tombe sur le passage suivant :
```
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Received disconnect from 161.202.39.38: 3: com.jcraft.jsch.JSchException: Auth fail [preauth]
Oct 5 08:46:01 BornToSecHackMe CRON[7549]: pam_unix(cron:session): session opened for user lmezard by (uid=1040)
```
Grâce à cette faute de frappe, on obtient notre premier couple login/mot de passe : `lmezard | !q\]Ej?*5K5cy*AJ`. En testant, on se rend compte que ces identifiants nous permettent de nous connecter au forum, et de trouver ainsi l'adresse courriel `laurie@borntosec.net`.

# webmail
Avec `laurie@borntosec.net | !q\]Ej?*5K5cy*AJ`, on peut se connecter au webmail. En plus d'un enthousiasme débordant pour Windev, on trouve surtout les identifiants de la base de données :
```
Hey Laurie,
You cant connect to the databases now. Use root/Fg-'kKXBj87E:aJ$
Best regards.
```

# phpMyAdmin
On est root sur la base de données, on peut s'arrêter là :tada: