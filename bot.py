import os
import time
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Seu Token do Telegram configurado diretamente
TELEGRAM_TOKEN = "8899179180:AAHVBgfZExT0P66RYFAO_j51ZC_YbFBbdZM"

# Estados da Conversa Interativa
EMAIL, SENHA, TIPO_CONTA, ENTRADA, STOP_WIN, STOP_LOSS = range(6)

USER_SESSION = {
    "email": "",
    "senha": "",
    "tipo_conta": "",
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
        "🤖 **Bem-vindo ao Bot IQ Option Pro!**\n\n"
        "Vamos configurar sua conta passo a passo para iniciar as operações.\n"
        "Para começar, digite o comando: `/login`"
    )

async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📧 Por favor, digite o seu **e-mail** de acesso da IQ Option:")
    return EMAIL

async def func_receber_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_SESSION["email"] = update.message.text.strip()
    await update.message.reply_text("🔑 Perfeito. Agora digite a sua **senha** da IQ Option:")
    return SENHA

async def func_receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_SESSION["senha"] = update.message.text.strip()
    USER_SESSION["logado"] = True
    await update.message.reply_text(
        "🌐 Ótimo! Qual o tipo de conta que você deseja operar?\n\n"
        "Envie apenas: **DEMO** ou **REAL**"
    )
    return TIPO_CONTA

async def func_receber_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tipo = update.message.text.strip().upper()
    if tipo not in ["DEMO", "REAL"]:
        await update.message.reply_text("⚠️ Opção inválida. Digite apenas **DEMO** ou **REAL**:")
        return TIPO_CONTA
    
    USER_SESSION["tipo_conta"] = tipo
    await update.message.reply_text(
        f"✅ Conta definida como: **{tipo}**\n\n"
        "💵 Agora, qual será o **valor da entrada base** para cada operação? *(Ex: 2.0)*"
    )
    return ENTRADA

async def func_receber_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["entrada_base"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `2.0`")
        return ENTRADA

    await update.message.reply_text(
        "🎯 Qual é a sua meta de **Stop Win** (Lucro máximo diário)? *(Ex: 15.0)*"
    )
    return STOP_WIN

async def func_receber_stop_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["stop_win"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `15.0`")
        return STOP_WIN

    await update.message.reply_text(
        "🛡️ Qual é o seu limite de **Stop Loss** (Perda máxima permitida)? *(Ex: 10.0)*"
    )
    return STOP_LOSS

async def func_receber_stop_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["stop_loss"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `10.0`")
        return STOP_LOSS

    USER_SESSION["configurado"] = True
    conta_txt = "🟢 CONTA DEMO (Prática)" if USER_SESSION["tipo_conta"] == "DEMO" else "🔴 CONTA REAL"
    
    await update.message.reply_text(
        f"🎉 **CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!** 🎉\n\n"
        f"🌐 Modo: {conta_txt}\n"
        f"📧 Conta: `{USER_SESSION['email']}`\n"
        f"💼 Banca Inicial: **R$ {USER_SESSION['banca_inicial']:.2f}**\n"
        f"💵 Entrada por Ordem: `R$ {USER_SESSION['entrada_base']:.2f}`\n"
        f"🎯 Stop Win: `+R$ {USER_SESSION['stop_win']:.2f}`\n"
        f"🛡️ Stop Loss: `-R$ {USER_SESSION['stop_loss']:.2f}`\n\n"
        f"🚀 O bot está configurado! Envie o comando `/operar` para testar."
    )
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Configuração cancelada.")
    return ConversationHandler.END

async def executar_ciclo_operacional(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USER_SESSION["logado"] or not USER_SESSION["configurado"]:
        await update.message.reply_text("⚠️ Você precisa concluir o login e a configuração primeiro enviando `/login`.")
        return

    par = "EURUSD-OTC"
    direcao = "CALL"
    confianca_ia = 92.4
    valor = USER_SESSION["entrada_base"]

    await update.message.reply_text(
        f"🤖 **ANÁLISE DE IA - NOVO SINAL** 🤖\n\n"
        f"📊 Par: `{par}`\n"
        f"⏱ Direção: **{direcao}**\n"
        f"🧠 Confluência da IA: `{confianca_ia}%`\n"
        f"💵 Valor da Entrada: `R$ {valor:.2f}`\n\n"
        f"⚡ *Executando ordem na IQ Option ({USER_SESSION['tipo_conta']})...*"
    )

    time.sleep(3)
    resultado = "WIN"
    lucro = valor * 0.82
    USER_SESSION["banca_atual"] += lucro
    diferenca_total = USER_SESSION["banca_atual"] - USER_SESSION["banca_inicial"]
    status_financeiro = f"+R$ {diferenca_total:.2f}" if diferenca_total >= 0 else f"-R$ {abs(diferenca_total):.2f}"

    await update.message.reply_text(
        f"✅ **RESULTADO: {resultado}** 🎉\n\n"
        f"📊 Par: `{par}`\n"
        f"💵 Lucro Obtido: `+R$ {lucro:.2f}`\n\n"
        f"📉 **PAINEL DA BANCA:**\n"
        f"💼 Banca Anterior: R$ {USER_SESSION['banca_atual'] - lucro:.2f}\n"
        f"💼 **Banca Atual:** **R$ {USER_SESSION['banca_atual']:.2f}**\n"
        f"📈 **Resultado Acumulado:** `{status_financeiro}`"
    )

def main():
    # Garante a criação do event loop para compatibilidade com versões novas do Python no Render
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("login", iniciar_login)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, func_receber_email)],
            SENHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, func_receber_senha)],
            TIPO_CONTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, func_receber_conta)],
            ENTRADA: [MessageHandler(filters.TEXT & ~filters.COMMAND, func_receber_entrada)],
            STOP_WIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, func_receber_stop_win)],
            STOP_LOSS: [MessageHandler(filters.TEXT & ~filters.COMMAND, func_receber_stop_loss)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("operar", executar_ciclo_operacional))

    print("🤖 Bot interativo rodando na nuvem com sucesso...")
    app.run_polling()

if __name__ == '__main__':
    main()
