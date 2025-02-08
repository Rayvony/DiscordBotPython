import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import time
import json
import os
from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario para almacenar los puntos de los usuarios
user_points = {}

# Ruta del archivo donde guardaremos los puntos
data_folder = "data"
file_path = os.path.join(data_folder, "user_points.json")

# Flag para controlar el ciclo de mensajes
mensaje_activado = False

# Cargar los puntos desde el archivo al iniciar el bot
def load_points():
    global user_points
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                user_points = json.load(f)
        except json.JSONDecodeError:
            print("El archivo de puntos está vacío o corrupto. Inicializando puntos vacíos.")
            user_points = {}  # Inicializar como un diccionario vacío si hay error al cargar el archivo
    else:
        user_points = {} 
# Guardar los puntos en el archivo cuando el bot se apaga
def save_points():
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    with open(file_path, "w") as f:
        json.dump(user_points, f)

# Este evento se ejecuta cuando el bot está listo
@bot.event
async def on_ready():
    load_points()  # Cargar los puntos al iniciar el bot
    print(f'✅ Bot conectado como {bot.user}')
    # Sincronizar los Slash Commands para que estén disponibles
    await bot.tree.sync()

# Comando Slash para iniciar el envío de mensajes aleatorios con un botón interactivo
@bot.tree.command(name="iniciar", description="Comienza a enviar mensajes con botón interactivo.")
@app_commands.guild_only()  # Asegura que solo se puede usar en un servidor
async def iniciar(interaction: discord.Interaction, canal: discord.TextChannel, tiempo: int):
    global mensaje_activado  # Usamos la variable global para cambiar su valor

    # Verificar si el invocador tiene permisos de administrador
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("No tienes permisos suficientes para usar este comando.", ephemeral=True)
        return

    # Si el ciclo ya está activo, informar al usuario
    if mensaje_activado:
        await interaction.response.send_message("El ciclo de mensajes ya está activo.", ephemeral=True)
        return

    # Cambiar el estado del flag para que el ciclo empiece
    mensaje_activado = True
    await interaction.response.send_message(f'Bot comenzará a enviar mensajes en {canal.mention} cada intervalo aleatorio de hasta {tiempo} segundos.')

    # Iniciar el ciclo de mensajes
    await enviar_mensajes(canal, tiempo)

# Función para enviar mensajes aleatorios en intervalos de tiempo aleatorios
async def enviar_mensajes(canal: discord.TextChannel, tiempo: int):
    global mensaje_activado  # Accedemos al flag global

    while mensaje_activado:  # El ciclo continuará hasta que el flag sea False
        intervalo = random.randint(0, tiempo)  # Intervalo aleatorio entre 0 y el valor de 'tiempo'
        await asyncio.sleep(intervalo)

        mensaje = "¡Rescata al lagartito! 🦎"  # Mensaje que se enviará

        # Crear un botón
        button = discord.ui.Button(label="¡Rescatar!", style=discord.ButtonStyle.primary, custom_id="rescue_button")

        # Crear una vista con el botón
        view = discord.ui.View()
        view.add_item(button)

        # Crear un Embed con color de barra lateral (izquierda)
        embed = discord.Embed(
            title="¡Ventana Emergente!",
            description="Haz clic en el botón para rescatar al lagartito.",
            color=discord.Color.from_rgb(169, 27, 171)
        )
        embed.set_footer(text="¡Espera! El lagartito te necesita.")
        
        timestamp = time.time()

        await canal.send(content=mensaje, embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())
        
        bot.last_message_timestamp = timestamp

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.get("custom_id") == "rescue_button":
            current_time = time.time()
            elapsed_time = current_time - bot.last_message_timestamp

            points = max(0, 5 - int(elapsed_time))

            user_id = interaction.user.id
            if user_id not in user_points:
                user_points[user_id] = 0

            user_points[user_id] += points

            save_points()

            await interaction.response.send_message(
                f"¡Has rescatado al lagartito! 🎉 Puntos ganados: {points}. Total de puntos: {user_points[user_id]}",
                ephemeral=True)

@bot.tree.command(name="leaderboard", description="Muestra el leaderboard de puntos.")
@app_commands.guild_only()
async def leaderboard(interaction: discord.Interaction):
    if not user_points:
        await interaction.response.send_message("No hay jugadores con puntos aún.", ephemeral=True)
        return

    # Ordenar los jugadores por puntos en orden descendente
    leaderboard = sorted(user_points.items(), key=lambda x: x[1], reverse=True)

    # Crear el embed
    embed = discord.Embed(
        title="Leaderboard",
        description="Aquí están los mejores jugadores según sus puntos",
        color=discord.Color.from_rgb(169, 27, 171)
    )

    # Añadir los jugadores al embed
    for idx, (user_id, points) in enumerate(leaderboard[:10], 1):  # Limitar a los primeros 10 jugadores
        try:
            user = await bot.fetch_user(user_id)
            # Aseguramos que la primera letra del nombre esté en mayúscula
            user_name = user.name.capitalize()
            # Mostrar nombre y puntos en la misma línea
            embed.add_field(name=f"{idx}. {user_name}", value=f"{points} puntos", inline=True)
        except discord.NotFound:
            # Si no se puede encontrar el usuario (por ejemplo, si ha sido eliminado)
            embed.add_field(name=f"{idx}. Usuario eliminado", value=f"{points} puntos", inline=True)

    # Enviar el embed
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="detener", description="Detener el envío de mensajes aleatorios.")
@app_commands.guild_only()
async def detener(interaction: discord.Interaction):
    global mensaje_activado

    if not mensaje_activado:
        await interaction.response.send_message("El ciclo de mensajes no está activo en este momento.", ephemeral=True)
        return

    mensaje_activado = False 
    await interaction.response.send_message("El ciclo de mensajes ha sido detenido.")

@bot.event
async def on_close():
    save_points()

bot.run(TOKEN)
