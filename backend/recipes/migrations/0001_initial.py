# Generated by Django 4.0.1 on 2022-02-12 07:34

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название фрукта, овоща, соуса или иной продукт', max_length=200, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(help_text='Применяйте наиболее подходящую единицу измерения', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Например "Оливье"', max_length=200, verbose_name='Название рецепта')),
                ('image', models.ImageField(help_text='Загрузите изображение для вашего рецепта', upload_to='recipes/images/', verbose_name='Изображение')),
                ('text', models.TextField(help_text='Описание блюда, инструкция по приготовлению, советы и т.д.', verbose_name='Описание')),
                ('cooking_time', models.PositiveIntegerField(help_text='Время приготовления (в минутах), целое число', validators=[django.core.validators.MinValueValidator(1, 'Время приготовления не может быть меньше 1 минуты')], verbose_name='Время приготовления')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название тега')),
                ('color', models.CharField(help_text='Цвет в HEX, #RRGGBB', max_length=7, unique=True, verbose_name='Цвет тега')),
                ('slug', models.SlugField(help_text='Допустимы буквы латинского алфавита, цифры 0-9 и знак "_"', max_length=200, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')], verbose_name='Адрес страницы')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipes', models.ManyToManyField(related_name='in_shopping_carts', to='recipes.Recipe', verbose_name='Рецепты')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(help_text='Требуемое количество для рецепта (целое число)', verbose_name='Количество')),
                ('ingredient', models.ForeignKey(help_text='Выберите ингредиент', null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.ingredient', verbose_name='Ингредиент')),
            ],
            options={
                'verbose_name': 'Ингредиент рецепта',
                'verbose_name_plural': 'Ингредиенты рецепта',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', to='recipes.RecipeIngredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.Tag'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='Уникальная запись ингредиент - единица измерения'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='recipes',
            field=models.ManyToManyField(related_name='in_favorite', to='recipes.Recipe', verbose_name='Рецепты'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user',), name='Уникальная запись пользовательская корзина'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('ingredient', 'amount'), name='Уникальная запись рецепт - количество'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user',), name='Уникальная запись избранное пользователя'),
        ),
    ]
