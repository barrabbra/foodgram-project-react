from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, validate_slug
from django.db import models

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
    slug = models.CharField(
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


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        help_text='Название фрукта, овоща, соуса или иной продукт',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Применяйте наиболее подходящую единицу измерения',
    )

    class Meta:
        ordering = ['id']
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


class Recipe(models.Model):
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Например "Оливье"',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение для вашего рецепта',
        upload_to='images/',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание блюда, инструкция по приготовлению, советы и т.д.',
    )
    cooking_time = models.IntegerField(
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
        ordering = ['pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}\n{self.text}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        help_text='Выберите ингредиент',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Требуемое количество для рецепта (целое число)',
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return self.ingredient.name


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        User,
        related_name='followings',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='Уникальная запись подписчик - автор',
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    favorite = models.ForeignKey(
        Recipe,
        related_name='in_favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'favorite'],
                name='Уникальная запись пользователь - рецепт',
            )
        ]
