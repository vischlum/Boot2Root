# Dirty COW

On se connecte en ssh à la machine :
```
$ ssh laurie@<IP>
330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4
```

# Version KERNEL
On vérifie la version du Kernel : `uname -a`

On se rend compte que la version de Kernel (3.2.0-91) est vulnérable à la faille [Dirty COW](https://en.wikipedia.org/wiki/Dirty_COW).

Après quelques recherches sur le net, on trouve un exploit pour Dirty COW sur [Exploit DB](https://www.exploit-db.com/exploits/40839).

# Exploit
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

On se déplace dans le dossier `/root` et avec un `cat README`, on se rend compte que nous sommes root sur la machine!

# Explication de la faille
La faille [Dirty COW](https://dirtycow.ninja/) touche le noyau Linux à partir de la version 2.6.22 (Septembre 2007) jusqu’à la version 4.4.25 inclus. Elle a été corrigée depuis la version 4.4.26.  
Elle exploite les fonctionnalités Copy-On-Write (COW) du noyau, d’où son nom. C’est par ce biais que le pirate peut atteindre et écrire sur des espaces mémoire qui, normalement, ne sont qu’en lecture seule.  
De cette façon, il est possible de procéder à une élévation de privilèges et devenir root.

La faille Dirty COW a été découverte par Phil Oester.
Pour plus de détails, cette [vidéo Youtube](https://www.youtube.com/watch?v=kEsshExn7aE) explique bien les choses.
