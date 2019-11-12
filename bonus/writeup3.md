# eXplore
Une fois connecté sur la machine (par exemple en SSH avec l'utilisateur laurie), la commande `mount` nous apprend que l'ISO est monté sur `/cdrom` : `/dev/sr0 on /cdrom type iso9660 (ro,noatime)`.  
En regardant dans `/cdrom`, on découvre que l'ISO utilise le chargeur d'amorçage [Syslinux](https://en.wikipedia.org/wiki/SYSLINUX), dans sa variante [Isolinux](https://wiki.syslinux.org/wiki/index.php?title=ISOLINUX).  

# eXpand
Voici le contenu de `isolinux.cfg` :  
```
default live
prompt 0
timeout 0

menu title BornToSec
menu background splash.png
menu color title 1;37;44 #c0ffffff #00000000 std

label live
  menu label live - boot the Live System
  kernel /casper/vmlinuz
  append  file=/cdrom/preseed/custom.seed boot=casper initrd=/casper/initrd.gz quiet splash --
```
La [documentation Syslinux](https://wiki.syslinux.org/wiki/index.php?title=Directives/special_keys#Escape_keys) nous apprend que l'on peut éviter le lancement de la commande `DEFAULT` en appuyant sur la touche <kbd>Maj</kbd> (entre autres) au moment du démarrage. Cela nous permet d'accéder à l'invite de commande Syslinux.

# eXploit
1. Au lancement de la VM, il suffit de rester appuyé sur <kbd>Maj</kbd>.
2. Sur l'invite de commande Syslinux, entrer `live init=/bin/bash` (pourquoi `live` ? Car c'est le label défini dans `isolinux.cfg`).
3. On est bien connecté sur l'ISO en tant que root.

# eXterminate
`rm -rf / --no-preserve-root` :wink: