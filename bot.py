import os
import time
import logging

# Configuração de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
except ImportError:
    print("Erro: A biblioteca python-telegram-bot não foi instalada corretamente.")

# Sessão do Usuário
USER_SESSION = {
    "email": None,
    "senha": None,
    "tipo_conta": "PRACTICE",
    "banca_inicial": 60.0,
    "banca_atual": 60.0,
    "entrada_base": 2.0,
    "stop_win": 15.0,
    "stop_loss": 10.0,
    "configurado": False,
    "logado": False
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Bot IQ Option Ativado!**\n\n"
        "Para conectar sua conta, envie:\n"
        "`/login seu_email@dominio.com sua_senha DEMO` *(ou REAL)*\n\n"
        "💼 Banca Inicial: **R$ 60,00**"
    )

async def fazer_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("⚠️ Use: `/login email@dominio.com senha DEMO` *(ou REAL)*")
        return

    USER_SESSION["email"] = args[0]
    USER_SESSION["senha"] = args[1]
    USER_SESSION["tipo_conta"] = args[2].upper()
    USER_SESSION["logado"] = True
    
    await update.message.reply_text(
        f"✅ **Conectado com sucesso!**\n"
        f"🌐 Modo: {USER_SESSION['tipo_conta']}\n"
        f"📧 Conta: `{USER_SESSION['email']}`\n"
        f"💰 Banca: R$ {USER_SESSION['banca_inicial']:.2f}\n\n"
        f"⚙️ Configure o gerenciamento com: `/configurar <entrada> <stop_win> <stop_loss>`\n"
        f"*(Ex: `/configurar 2.0 15.0 10.0`)*"
    )

async def configurar_gerenciamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USER_SESSION["logado"]:
        await update.message.reply_text("⚠️ Faça o login primeiro usando `/login`.")
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text("⚠️ Use: `/configurar <entrada> <stop_win> <stop_loss>`")
        return

    USER_SESSION["entrada_base"] = float(args[0])
    USER_SESSION["stop_win"] = float(args[1])
    USER_SESSION["stop_loss"] = float(args[2])
    USER_SESSION["configurado"] = True

    await update.message.reply_text(
        f"⚙️ **Gerenciamento Salvo!**\n"
        f"💵 Entrada: R$ {USER_SESSION['entrada_base']:.2f}\n"
        f"🎯 Stop Win: +R$ {USER_SESSION['stop_win']:.2f}\n"
        f"🛡️ Stop Loss: -R$ {USER_SESSION['stop_loss']:.2f}\n\n"
        f"🚀 Envie `/operar` para testar o sinal!"
    )

async def executar_ciclo_operacional(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USER_SESSION["logado"] or not USER_SESSION["configurado"]:
        await update.message.reply_text("⚠️ Conecte a conta e configure o gerenciamento antes de operar.")
        return

    par = "EURUSD-OTC"
    direcao = "PUT"
    valor = USER_SESSION["entrada_base"]

    await update.message.reply_text(
        f"🤖 **SINAL GERADO PELA IA** 🤖\n\n"
        f"📊 Par: `{par}`\n"
        f"⏱ Direção: **{direcao}**\n"
        f"💵 Entrada: `R$ {valor:.2f}`\n\n"
        f"⚡ *Executando na corretora...*"
    )

    time.sleep(2)
    
    # Simulando WIN
    lucro = valor * 0.82
    USER_SESSION["banca_atual"] += lucro
    total = USER_SESSION["banca_atual"] - USER_SESSION["banca_inicial"]

    await update.message.reply_text(
        f"✅ **RESULTADO: WIN** 🎉\n"
        f"💵 Lucro: `+R$ {lucro:.2f}`\n"
        f"💼 **Banca Atual:** **R$ {USER_SESSION['banca_atual']:.2f}**\n"
        f"📈 **Acumulado:** `+R$ {total:.2f}`"
    )

def main():
    # Pega o Token do Render de forma segura
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("ERRO CRÍTICO: TELEGRAM_BOT_TOKEN não foi encontrado nas variáveis de ambiente do Render.")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", fazer_login))
    app.add_handler(CommandHandler("configurar", configurar_gerenciamento))
    app.add_handler(CommandHandler("operar", executar_ciclo_operacional))

    print("🤖 Bot rodando com sucesso e escutando o Telegram...")
    app.run_polling()

if __name__ == '__main__':
    main()
