# Réponses aux questions


## Prise en main
### Question 1
C'est une topologie en étoile. Le serveur est le centre de l'étoile et les clients sont les branches.

### Question 2
Les messages sont lisible en clair sur le serveur. Il est donc possible de les lire et de les modifier.
La confidentialité n'est pas garantie. 
On peut alors faire une attaque dites de l'homme du milieu.

### Question 3
Cela viole le principe de Kerckhoffs: "Le système doit être matériellement, sinon
mathématiquement indéchiffrable"

### Question 4
Mettre un chiffremment permettrait de garantir, au moins en partie, la confidentialité des messages.



## Chiffrement 
### Question 1
La fonction uRandom permet de générer une chaine de caractère aléatoire de longueur donnée en paramètre. 
Si elle est utilisé peu après le démarage avec une ancienne version de python son random n'aura pas assez d'entropie pour générer des nombres aléatoires. Il fallait donc attendre un peu avant de l'utiliser.
Sur python 3.5.0 la fonction uRandom fait un appel de fonction qui attendent que le système ait assez d'entropie pour générer des nombres aléatoires.

### Question 2
Si ses primitives cryptographiques sont brisé, alors toutes les applications qui utilisent ces primitives sont brisé. On peut en conclure que les utiliser n'est pas forcément dangereux si correctement utilisé.

### Question 3
Le chiffrement préserve la confidentialité des données mais pas leur intégrité. Le chiffrement permet de cacher les données mais pas de s'assurer qu'elles n'ont pas été modifiées. Un serveur malveillant peut alors modifier les données pour les rendre inutilisable.

### Question 4
Ici, il manque un système qui permet de vérifier l'intégrité des données.



## Authenticated Symmetric Encryption
### Question 1
Fernet est moins risqué que AES car au moment de déchiffrer le message, ça vérifie l'intégrité de celui ci en utilisant un timestamp et une valeur au début du message (0x80). Si le message a été modifié, le déchiffrement échoue et on sait alors que le message à été altéré.

### Question 2
Ce type d'attaque s'appelle une attaque par rejeu. Cela consiste a retransmettre un message déjà reçu ayant servie a l'authentification afin de se faire passer pour l'un des utilisateur authentifié en utilisant le même message d'authentification.

### Question 3
Pour éviter ce type d'attaque, on peut utiliser une limite de temsp avec l'aide du timestamp. On limite par exemple à 15s la durée max d'écart possible entre le timestamp du message et le timestamp actuel.

## TTL
### Question 1
Aucune différence n'est visible, la longueur du message reste la même.

### Question 2
En retirant 45s au timestamp, le message est considéré comme invalide et le déchiffrement échoue alors. Cela est du à la vérification du timestamp et du fait que l'on accepte un écart maximum de 30s.

### Question 3
Dans la pratique, il faut réduire le temps pour sécuriser les messages car en 30s, une machine aurait le temps de faire une attaque par rejeu.
L'autre limite également c'est que si il y a de la latence sur la connexion, les messages peuvent être considérés comme invalides alors qu'ils ne le sont pas.


## Regard critique
Le serveur est non sécurisé et n'a pas d'autentification. Il est donc possible de se connecter à celui ci sans être authentifié. N'importe quel client un peu modifié ou autre logiciel utilisant le même port pourrait faire transiter des informations par le serveur autre que des messages. Avec suffisament de requêtes cela pourrait faire planter le serveur et les clients connecté au serveur.
Ajouter un système d'authentification et ajout d'un header dans les message permettrait de limiter ces soucis. 
Le port 6666 peut également poser problème. Même si il est utilisé par les chat, il est également très utilisé par les virus donc il n'est pas très recommandé d'ouvrir ce port en publique sans avoir une analyse réseau sur ce qu'il se passe sur ce port.