Sur l'iso on peut récupérer le fichier `casper/filesystem.squashfs` qui est le filesystem compressé.
On utilise la commande `unsquashfs filesystem.squashfs` qui va décompresser le filesystem dans un dossier `squashfs-root`.
À partir de là on a access à tous les fichiers présents sur l'iso monté.
On trouve dans home/LOOKATME un fichier `password` contenant les credentials du user lmezard:
>	``lmezard:G!@M6f4Eatau{sF"``

