Après avoir monté le fichier ISO depuis la VM Kali (par exemple avec `mount BornToSecHackMe-v1.1.iso iso/ -o loop`), on peut récupérer le fichier `casper/filesystem.squashfs` qui est le filesystem compressé. On utilise la commande `unsquashfs filesystem.squashfs` qui va décompresser le filesystem dans un dossier `squashfs-root`.  

À partir de là on peut accéder à tous les fichiers présents sur l'ISO monté.  
On trouve dans `/home/LOOKATME` un fichier `password` contenant les identifiants de l'utilisateur `lmezard` :
```
lmezard:G!@M6f4Eatau{sF"
```
De même, on peut accéder directement au `turtle` pour obtenir les identifiants SSH de `zaz` et gagner ainsi beaucoup de temps dans l'obtention du `root`.

Cet accès illimité au contenu de l'ISO permet de découvrir pas mal de choses intéressantes :
- le mot de passe de la base de données est aussi disponible dans `/var/www/forum/config/db_settings.php`.
- en fouillant sur le home de `ft_root`, deux fichiers surtout sont intéressants :
    - `.bash_history` : surtout de la config [Grub](https://en.wikipedia.org/wiki/GNU_GRUB), [Plymouth](https://en.wikipedia.org/wiki/Plymouth_(software)), [Remastersys](https://en.wikipedia.org/wiki/Remastersys)
    - `.viminfo` : idem
- dans `/root` :
    - `.bash_history` : on peut suivre pas à pas toute la mise en place de l'ISO :
        - (ligne 40) `chmod -R 777 templates_c/` => tellement utile pour le reverse shell :wink:
        - en regardant ce qui a été modifié dans `/etc/vsftpd.conf`, on comprend pourquoi seul `lmezard` arrive à se connecter en FTP : l'option `chroot_local_user` est activé, ce qui fait qu'un [chroot](https://en.wikipedia.org/wiki/Chroot) sera appliqué au dossier utilisateur lors de la connexion FTP. Pour des [raisons de sécurité](https://security.appspot.com/vsftpd/FAQ.txt), vsftpd bloque la connexion si l'utilisateur dispose des droits d'écriture sur le dossier monté en chroot, or `lmezard` est le seul compte utilisateur ne disposant (par défaut) pas des droits d'écriture sur son dossier `home`.
        - (ligne 403) `646da671ca01bb5d84dbb5fb2238dc8e` => on retrouve le mot de passe de `zaz`, juste après `adduser zaz`
        - (ligne 414) `gcc -m32 -z execstack -Wl,-z,norelro -fno-stack-protector main.c -o exploit_me` => le binaire `exploit_me` a été compilé sans les [protections contre les dépassements de mémoire tampon](https://en.wikipedia.org/wiki/Buffer_overflow_protection) afin de permettre son exploitation.
        - (ligne 528) `echo "kernel.randomize_va_space = 0" > /etc/sysctl.d/01-disable-aslr.conf` => désactivation de l'[*Address space layout randomization*](https://en.wikipedia.org/wiki/Address_space_layout_randomization) pour permettre le « bon » fonctionnement du `exploit_me`
        - (ligne 697) `apt-get --purge remove libapparmor` => désinstallation de [AppArmor](https://en.wikipedia.org/wiki/AppArmor) pour nous laisser les coudées franches sur l'ISO.
        - (ligne 798) `rm phpbackdoor.php` dans le dossier `/var/www/forum/templates_c/` => tout a été prévu
    - `.viminfo` : 
        - les modifications du fichier `/etc/ssh/sshd_config` autour des lignes 32 à 34 correspondent à
        ```
        #AuthorizedKeysFile	%h/.ssh/authorized_keys
        AllowUsers ft_root zaz thor laurie
        #DenyUsers *
        ```
        Ce qui explique pourquoi il n'est pas possible de se connecter en SSH avec `lmezard`.

## Sources des challenges :
* La bombe est reprise d'un cours de Carnegie Mellon (CMU), ce qui explique la référence à des serveurs en `***.cs.cmu.edu` dans le binaire.
* Le [turtle](https://vimvaders.github.io/hackcon2015/2015/08/20/ninja-turtles.html) et le [Iheartpwnage](https://vimvaders.github.io/hackcon2015/2015/08/20/frag-grenade.html) ont été repris de Hackcon 2015.
* L'enchainement MyLittleForum > SquirrelMail > root DB a été repris d'un [autre iso](https://www.ethicalhacker.net/forums/topic/de-ice-s1-140-walkthrough/)
