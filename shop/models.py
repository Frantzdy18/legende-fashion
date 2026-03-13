from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



# ----- PRODUIT -----
class Product(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du produit")
    description = models.TextField(verbose_name="Description")
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créé par")
    image = models.ImageField(upload_to='product_images/', null=True, blank=True, verbose_name="Image")

    def __str__(self):
        return self.nom

# ----- PROFILE UTILISATEUR (BALANCE) -----
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.balance}$"

# ----- PURCHASE / ACHAT -----
class Purchase(models.Model):
    STATUS_CHOICES = [
        ('en_cours', 'En cours'),
        ('expedie', 'Expédié'),
        ('livre', 'Livré'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix payé")
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_cours'
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.nom} ({self.prix}$) - {self.statut}"

# ----- SIGNALS -----
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Kreye profile lè user kreye premye fwa."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile si li egziste."""
    if hasattr(instance, 'profile'):
        instance.profile.save()