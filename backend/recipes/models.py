from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, validate_slug
from django.db import models
from django.urls import reverse

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет тега',
        help_text='Цвет в HEX, #RRGGBB',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Адрес страницы',
        help_text='Допустимы буквы латинского алфавита, цифры 0-9 и знак "_"',
        validators=[validate_slug],
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', args=[self.slug])


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        help_text='Название фрукта, овоща, соуса или иной продукт',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Применяйте наиболее подходящую единицу измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='Уникальная запись ингредиент - единица измерения',
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        help_text='Выберите ингредиент',
        on_delete=models.SET_NULL,
        null=True,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Требуемое количество для рецепта (целое число)',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'amount'],
                name='Уникальная запись рецепт - количество',
            )
        ]

    def __str__(self):
        return self.ingredient.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        RecipeIngredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Например "Оливье"',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение для вашего рецепта',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание блюда, инструкция по приготовлению, советы и т.д.',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления (в минутах), целое число',
        validators=[
            MinValueValidator(
                1,
                'Время приготовления не может быть меньше 1 минуты',
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}\n{self.text}'

    def get_absoulute_url(self):
        return reverse('recipe', args=[self.pk])


class Favorite(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
        related_name='in_favorite',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='Уникальная запись избранное пользователя',
            )
        ]


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
        related_name='in_shopping_carts',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='Уникальная запись пользовательская корзина',
            )
        ]
