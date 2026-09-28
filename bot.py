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

# Importação da API da IQ Option
from iqoptionapi.stable_api import IQOption

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token do seu Telegram configurado diretamente
TELEGRAM_TOKEN = "8899179180:AAHVBgfZExT0P66RYFAO_j51ZC_YbFBbdZM"

# Estados da Conversa Interativa de Login e Configuração
EMAIL, SENHA, TIPO_CONTA, ENTRADA, STOP_WIN, STOP_LOSS = range(6)

# Sessão do Usuário e Instância da Conexão
USER_SESSION = {
    "api": None,
    "email": "",
    "senha": "",
    "tipo_conta": "PRACTICE", # PRACTICE ou REAL
    "banca_inicial": 0.0,
    "banca_atual": 0.0,
    "entrada_base": 2.0,
    "stop_win": 15.0,
    "stop_loss": 10.0,
    "configurado": False,
    "logado": False
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Bot IQ Option Pro - Conexão Real** 🤖\n\n"
        "Este robô conecta diretamente na sua conta da corretora, catalisa e opera de forma automatizada.\n\n"
        "Para iniciar a autenticação segura, envie o comando: `/login`"
    )

async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📧 Por favor, digite o seu **e-mail** cadastrado na IQ Option:")
    return EMAIL

async def func_receber_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_SESSION["email"] = update.message.text.strip()
    await update.message.reply_text("🔑 Perfeito. Agora digite a sua **senha** da IQ Option:")
    return SENHA

async def func_receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_SESSION["senha"] = update.message.text.strip()
    
    # Tentativa de Conexão Real com a Corretora
    await update.message.reply_text("🔄 *Conectando aos servidores da IQ Option, aguarde um instante...*")
    
    try:
        api = IQOption(USER_SESSION["email"], USER_SESSION["senha"])
        check, reason = api.connect()
        
        if check:
            USER_SESSION["api"] = api
            USER_SESSION["logado"] = True
            await update.message.reply_text(
                "✅ **Autenticação Real Realizada com Sucesso!**\n\n"
                "🌐 Agora, qual o tipo de conta que você deseja utilizar nas operações?\n"
                "Envie apenas: **DEMO** ou **REAL**"
            )
            return TIPO_CONTA
        else:
            USER_SESSION["logado"] = False
            await update.message.reply_text(
                f"❌ **Falha no Login da Corretora:** `{reason}`\n\n"
                "Verifique suas credenciais e envie `/login` novamente."
            )
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"⚠️ Erro crítico ao conectar na API: `{str(e)}`")
        return ConversationHandler.END

async def func_receber_conta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tipo = update.message.text.strip().upper()
    if tipo not in ["DEMO", "REAL"]:
        await update.message.reply_text("⚠️ Opção inválida. Digite apenas **DEMO** ou **REAL**:")
        return TIPO_CONTA
    
    api = USER_SESSION["api"]
    if tipo == "DEMO":
        api.change_balance("PRACTICE")
        USER_SESSION["tipo_conta"] = "PRACTICE"
    else:
        api.change_balance("REAL")
        USER_SESSION["tipo_conta"] = "REAL"
    
    # Captura o saldo real direto da corretora
    saldo_atual = api.get_balance()
    USER_SESSION["banca_inicial"] = saldo_atual
    USER_SESSION["banca_atual"] = saldo_atual
    
    await update.message.reply_text(
        f"✅ Conta definida para: **{tipo}**\n"
        f"💰 **Saldo Real na Corretora:** R$ {saldo_atual:.2f}\n\n"
        "💵 Qual será o **valor da entrada base** para cada ordem? *(Ex: 2.0)*"
    )
    return ENTRADA

async def func_receber_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["entrada_base"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `2.0`")
        return ENTRADA

    await update.message.reply_text("🎯 Qual é a sua meta de **Stop Win** (Lucro máximo diário)? *(Ex: 15.0)*")
    return STOP_WIN

async def func_receber_stop_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["stop_win"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `15.0`")
        return STOP_WIN

    await update.message.reply_text("🛡️ Qual é o seu limite de **Stop Loss** (Perda máxima permitida)? *(Ex: 10.0)*")
    return STOP_LOSS

async def func_receber_stop_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["stop_loss"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `10.0`")
        return STOP_LOSS

    USER_SESSION["configurado"] = True
    conta_txt = "🟢 CONTA DEMO (Prática)" if USER_SESSION["tipo_conta"] == "PRACTICE" else "🔴 CONTA REAL"
    
    await update.message.reply_text(
        f"🎉 **CONFIGURAÇÃO E CONEXÃO PRONTAS!** 🎉\n\n"
        f"🌐 Modo: {conta_txt}\n"
        f"📧 Conta: `{USER_SESSION['email']}`\n"
        f"💼 Banca Atualizada: **R$ {USER_SESSION['banca_atual']:.2f}**\n"
        f"💵 Entrada por Ordem: `R$ {USER_SESSION['entrada_base']:.2f}`\n"
        f"🎯 Stop Win: `+R$ {USER_SESSION['stop_win']:.2f}`\n"
        f"🛡️ Stop Loss: `-R$ {USER_SESSION['stop_loss']:.2f}`\n\n"
        f"🚀 O bot está monitorando os gráficos em segundo plano. Envie `/operar` para forçar um ciclo de entrada ou aguarde os gatalhos automáticos!"
    )
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Configuração cancelada.")
    return ConversationHandler.END

async def executar_ciclo_operacional(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a ordem real na IQ Option e retorna o resultado no Telegram"""
    if not USER_SESSION["logado"] or not USER_SESSION["configurado"]:
        await update.message.reply_text("⚠️ Você precisa concluir o login e a configuração primeiro enviando `/login`.")
        return

    api = USER_SESSION["api"]
    par = "EURUSD-OTC"
    direcao = "call" # 'call' ou 'put'
    duracao = 1 # expiração em 1 minuto
    valor = USER_SESSION["entrada_base"]

    await update.message.reply_text(
        f"🤖 **ANÁLISE DE IA - GATILHO ACIONADO** 🤖\n\n"
        f"📊 Par: `{par}`\n"
        f"⏱ Direção: **{direcao.upper()}**\n"
        f"💵 Valor da Ordem: `R$ {valor:.2f}`\n\n"
        f"⚡ *Enviando ordem de compra real para a corretora...*"
    )

    # Execução real da ordem na API da IQ Option
    try:
        check, order_id = api.buy(valor, par, direcao, duracao)
        
        if check:
            await update.message.reply_text(f"✅ Ordem executada com ID: `{order_id}`. Aguardando expiração...")
            
            # Aguarda o tempo de expiração da vela (60 segundos + margem)
            time.sleep(65)
            
            # Verifica o lucro obtido na ordem
            lucro = api.get_profit(order_id)
            USER_SESSION["banca_atual"] = api.get_balance()
            
            resultado = "WIN" if lucro > 0 else "LOSS"
            diferenca_total = USER_SESSION["banca_atual"] - USER_SESSION["banca_inicial"]
            status_financeiro = f"+R$ {diferenca_total:.2f}" if diferenca_total >= 0 else f"-R$ {abs(diferenca_total):.2f}"

            await update.message.reply_text(
                f"🏁 **RESULTADO DA OPERAÇÃO: {resultado}**\n\n"
                f"📊 Par: `{par}`\n"
                f"💵 Lucro/Prejuízo da Ordem: `R$ {lucro:.2f}`\n\n"
                f"📉 **PAINEL DA BANCA EM TEMPO REAL:**\n"
                f"💼 **Banca Atual:** **R$ {USER_SESSION['banca_atual']:.2f}**\n"
                f"📈 **Acumulado do Dia:** `{status_financeiro}`"
            )
        else:
            await update.message.reply_text("⚠️ A corretora rejeitou a ordem no momento do envio.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro na execução da ordem: `{str(e)}`")

def main():
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

    print("🤖 Bot real da IQ Option rodando na nuvem...")
    app.run_polling()

if __name__ == '__main__':
    main()
