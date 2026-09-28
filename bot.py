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

from iqoptionapi.stable_api import IQ_Option

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token do seu Telegram configurado diretamente
TELEGRAM_TOKEN = "8899179180:AAHVBgfZExT0P66RYFAO_j51ZC_YbFBbdZM"

# Estados da Conversa Interativa de Login e Configuração
EMAIL, SENHA, TIPO_CONTA, ENTRADA, STOP_WIN, STOP_LOSS = range(6)

USER_SESSION = {
    "api": None,
    "email": "",
    "senha": "",
    "tipo_conta": "PRACTICE",
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
        "🤖 **Bot IQ Option Pro - Conexão Direta** 🤖\n\n"
        "Este robô utiliza a conexão via Python puro para operar na sua conta.\n\n"
        "Para iniciar, envie o comando: `/login`"
    )

async def iniciar_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📧 Por favor, digite o seu **e-mail** da IQ Option:")
    return EMAIL

async def func_receber_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_SESSION["email"] = update.message.text.strip()
    await update.message.reply_text("🔑 Perfeito. Agora digite a sua **senha** da IQ Option:")
    return SENHA

async def func_receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_SESSION["senha"] = update.message.text.strip()
    
    await update.message.reply_text("🔄 *Estabelecendo conexão direta com os servidores da corretora...*")
    
    try:
        # Inicializa a classe de conexão oficial da API
        api = IQ_Option(USER_SESSION["email"], USER_SESSION["senha"])
        
        # Tenta conectar explicitamente
        check, reason = api.connect()
        
        if check:
            USER_SESSION["api"] = api
            USER_SESSION["logado"] = True
            await update.message.reply_text(
                "✅ **Conexão Direta Realizada com Sucesso!**\n\n"
                "🌐 Qual o tipo de conta que você deseja operar?\n"
                "Envie apenas: **DEMO** ou **REAL**"
            )
            return TIPO_CONTA
        else:
            USER_SESSION["logado"] = False
            # Mensagem detalhada caso a corretora recuse por segurança ou dados incorretos
            motivo_falha = str(reason) if reason else "Bloqueio de segurança/Credenciais inválidas"
            await update.message.reply_text(
                f"❌ **Falha na Conexão:** `{motivo_falha}`\n\n"
                "Dica: Se persistir, verifique se a conta possui autenticação de dois fatores ativa ou tente novamente com `/login`."
            )
            return ConversationHandler.END
            
    except Exception as e:
        erro_msg = str(e)
        if "Expecting value" in erro_msg or "JSONDecodeError" in erro_msg:
            await update.message.reply_text(
                "⚠️ **Aviso de Proteção da Corretora (Cloudflare):**\n"
                "O servidor em nuvem teve o IP desafiado pela segurança da corretora. "
                "Tente refazer o deploy no Render para alterar o IP ou use `/login` novamente em instantes."
            )
        else:
            await update.message.reply_text(f"⚠️ Erro crítico na API: `{erro_msg}`")
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
    
    saldo_atual = api.get_balance()
    USER_SESSION["banca_inicial"] = saldo_atual
    USER_SESSION["banca_atual"] = saldo_atual
    
    await update.message.reply_text(
        f"✅ Conta definida para: **{tipo}**\n"
        f"💰 **Saldo Atual na Corretora:** R$ {saldo_atual:.2f}\n\n"
        "💵 Qual será o **valor da entrada base** para cada ordem? *(Ex: 2.0)*"
    )
    return ENTRADA

async def func_receber_entrada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["entrada_base"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `2.0`")
        return ENTRADA

    await update.message.reply_text("🎯 Qual é a sua meta de **Stop Win** (Lucro diário)? *(Ex: 15.0)*")
    return STOP_WIN

async def func_receber_stop_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        USER_SESSION["stop_win"] = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text("⚠️ Digite um número válido. Exemplo: `15.0`")
        return STOP_WIN

    await update.message.reply_text("🛡️ Qual é o seu limite de **Stop Loss** (Perda máxima)? *(Ex: 10.0)*")
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
        f"🎉 **CONFIGURAÇÃO CONCLUÍDA!** 🎉\n\n"
        f"🌐 Modo: {conta_txt}\n"
        f"📧 Conta: `{USER_SESSION['email']}`\n"
        f"💼 Banca Atual: **R$ {USER_SESSION['banca_atual']:.2f}**\n"
        f"💵 Entrada por Ordem: `R$ {USER_SESSION['entrada_base']:.2f}`\n"
        f"🎯 Stop Win: `+R$ {USER_SESSION['stop_win']:.2f}`\n"
        f"🛡️ Stop Loss: `-R$ {USER_SESSION['stop_loss']:.2f}`\n\n"
        f"🚀 Tudo pronto! Envie o comando `/operar` para executar uma ordem real na corretora."
    )
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Configuração cancelada.")
    return ConversationHandler.END

async def executar_ciclo_operacional(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USER_SESSION["logado"] or not USER_SESSION["configurado"]:
        await update.message.reply_text("⚠️ Você precisa concluir o login e a configuração primeiro enviando `/login`.")
        return

    api = USER_SESSION["api"]
    par = "EURUSD-OTC"
    direcao = "call"
    duracao = 1
    valor = USER_SESSION["entrada_base"]

    await update.message.reply_text(
        f"🤖 **EXECUTANDO ORDEM DIRETA** 🤖\n\n"
        f"📊 Par: `{par}`\n"
        f"⏱ Direção: **{direcao.upper()}**\n"
        f"💵 Valor: `R$ {valor:.2f}`\n\n"
        f"⚡ *Enviando requisição para a API da corretora...*"
    )

    try:
        check, order_id = api.buy(valor, par, direcao, duracao)
        
        if check:
            await update.message.reply_text(f"✅ Ordem aceita! ID: `{order_id}`. Aguardando expiração...")
            
            time.sleep(65)
            
            lucro = api.get_profit(order_id)
            USER_SESSION["banca_atual"] = api.get_balance()
            
            resultado = "WIN" if lucro > 0 else "LOSS"
            diferenca_total = USER_SESSION["banca_atual"] - USER_SESSION["banca_inicial"]
            status_financeiro = f"+R$ {diferenca_total:.2f}" if diferenca_total >= 0 else f"-R$ {abs(diferenca_total):.2f}"

            await update.message.reply_text(
                f"🏁 **RESULTADO: {resultado}**\n\n"
                f"📊 Par: `{par}`\n"
                f"💵 Lucro/Prejuízo: `R$ {lucro:.2f}`\n\n"
                f"📉 **PAINEL DA BANCA:**\n"
                f"💼 **Banca Atual:** **R$ {USER_SESSION['banca_atual']:.2f}**\n"
                f"📈 **Acumulado:** `{status_financeiro}`"
            )
        else:
            await update.message.reply_text("⚠️ A corretora rejeitou a ordem enviada.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao processar a ordem: `{str(e)}`")

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

    print("🤖 Bot de conexão direta rodando na nuvem...")
    app.run_polling()

if __name__ == '__main__':
    main()
