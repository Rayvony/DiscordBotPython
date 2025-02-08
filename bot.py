import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Flag para controlar el ciclo de mensajes
mensaje_activado = False

# Este evento se ejecuta cuando el bot está listo
@bot.event
async def on_ready():
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

        # Crear un botón
        button = discord.ui.Button(label="¡Rescatar!", style=discord.ButtonStyle.primary, custom_id="rescue_button")

        # Crear una vista con el botón
        view = discord.ui.View()
        view.add_item(button)

        # Enviar un mensaje con un fondo oscuro (usando un embed)
        embed = discord.Embed(
            title="¡Rescata al lagartito! 🦎",
            description="Haz clic en el botón para rescatar al lagartito.",
            color=discord.Color.from_rgb(169, 27, 171)  # Fondo oscuro
        )
        embed.set_footer(text="¡Espera! El lagartito te necesita.")
        
        await canal.send(embed=embed, view=view)

# Función para manejar la interacción del botón
@bot.event
async def on_interaction(interaction: discord.Interaction):
    # Verificar si la interacción es un componente (botón)
    if interaction.type == discord.InteractionType.component:
        # Verificar si el usuario hizo clic en el botón correcto
        if interaction.data.get("custom_id") == "rescue_button":
            # Lógica de lo que pasa cuando el botón es presionado (ejemplo: sumar puntos)
            await interaction.response.send_message("¡Has rescatado al lagartito! 🎉 Puntos ganados.", ephemeral=True)

# Comando Slash para detener el envío de mensajes aleatorios
@bot.tree.command(name="detener", description="Detener el envío de mensajes aleatorios.")
@app_commands.guild_only()
async def detener(interaction: discord.Interaction):
    global mensaje_activado  # Usamos la variable global

    if not mensaje_activado:
        await interaction.response.send_message("El ciclo de mensajes no está activo en este momento.", ephemeral=True)
        return

    mensaje_activado = False  # Cambiar el estado del flag a False para detener el ciclo
    await interaction.response.send_message("El ciclo de mensajes ha sido detenido.")

bot.run(TOKEN)
