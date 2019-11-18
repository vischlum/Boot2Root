# Dirty COW

On se connecte en ssh a la machine avec les credentials:
```
ssh laurie@<IP>
330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4
```

On verifie la version du Kernel
```
uname -a
```

On se rend compte que la version de Kernel (3.2.0-91) est vulnerable a la faille Dirty COW.



La faille Dirty COW touche le noyau Linux a partir de la version 2.6.22 (Septembre 2007) jusqu'a la version 4.4.25 inclus. Elle a ete corrige depuis la version 4.4.26.
Elle exploite les fonctionnalites Copy-On-Write (COW) du noyau, d'ou son nom. C'est par ce biais que le pirate peut atteindre et ecrire sur des espaces memoire qui, normalement, ne sont qu'en lecture seule. 
De cette facon, il est possible de faire une elevation de privileges et devenir root.

Dirty COW a ete decouverte par Phil Oester.
```
Lien: https://www.youtube.com/watch?v=kEsshExn7aE
```