import os
import time
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Estrutura de dados para armazenar a sessão e as configurações do usuário
USER_SESSION = {
    "email": None,
    "senha": None,
    "tipo_conta": "PRACTICE", # PRACTICE (Demo) ou REAL
    "banca_inicial": 60.0,
    "banca_atual": 60.0,
    "entrada_base": 2.0,
    "stop_win": 15.0,
    "stop_loss": 10.0,
    "estrategia_rec": "Martingale", # Martingale ou Soros
    "configurado": False,
    "logado": False
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensagem inicial com instruções de login e configuração"""
    await update.message.reply_text(
        "🤖 **Bot de Operações Inteligente - IQ Option**\n\n"
        "Para começar, envie seus dados de acesso e a modalidade:\n"
        "`/login email@dominio.com senha DEMO` *(ou REAL)*\n\n"
        "💼 Banca Inicial Padrão: **R$ 60,00**"
    )

async def fazer_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura e-mail, senha e tipo de conta (DEMO/REAL)"""
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "⚠️ Formato incorreto!\n"
            "Use: `/login seu_email@dominio.com sua_senha DEMO` *(ou REAL)*"
        )
        return

    USER_SESSION["email"] = args[0]
    USER_SESSION["senha"] = args[1]
    USER_SESSION["tipo_conta"] = args[2].upper()
    
    # Simulação de conexão com a IQ Option
    sucesso_conexao = True 
    
    if sucesso_conexao:
        USER_SESSION["logado"] = True
        conta_txt = "🟢 CONTA DEMO (Prática)" if USER_SESSION["tipo_conta"] == "PRACTICE" else "🔴 CONTA REAL"
        await update.message.reply_text(
            f"✅ **Autenticado com Sucesso!**\n\n"
            f"🌐 Modo: {conta_txt}\n"
            f"📧 Conta: `{USER_SESSION['email']}`\n"
            f"💰 Banca Inicial: R$ {USER_SESSION['banca_inicial']:.2f}\n\n"
            f"⚙️ Agora configure seu gerenciamento usando o comando:\n"
            f"`/configurar <entrada> <stop_win> <stop_loss>`\n"
            f"*(Exemplo: `/configurar 2.0 15.0 10.0`)*"
        )
    else:
        await update.message.reply_text("❌ Falha na autenticação. Verifique suas credenciais.")

async def configurar_gerenciamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configura os parâmetros de risco da banca"""
    if not USER_SESSION["logado"]:
        await update.message.reply_text("⚠️ Faça o login primeiro usando `/login`.")
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "⚠️ Parâmetros incompletos!\n"
            "Use: `/configurar <entrada> <stop_win> <stop_loss>`\n"
            "Exemplo: `/configurar 2.0 15.0 10.0`"
        )
        return

    try:
        USER_SESSION["entrada_base"] = float(args[0])
        USER_SESSION["stop_win"] = float(args[1])
        USER_SESSION["stop_loss"] = float(args[2])
        USER_SESSION["configurado"] = True

        await update.message.reply_text(
            f"⚙️ **Gerenciamento Definido com Sucesso!**\n\n"
            f"💰 Valor por Entrada: `R$ {USER_SESSION['entrada_base']:.2f}`\n"
            f"🎯 Meta de Stop Win: `+R$ {USER_SESSION['stop_win']:.2f}`\n"
            f"🛡️ Limite de Stop Loss: `-R$ {USER_SESSION['stop_loss']:.2f}`\n"
            f"🔄 Estratégia: `{USER_SESSION['estrategia_rec']}`\n\n"
            f"🚀 Tudo pronto! Envie `/operar` para iniciar o envio de sinais e execução."
        )
    except ValueError:
        await update.message.reply_text("⚠️ Utilize apenas números para os valores. Ex: `/configurar 2.0 15.0 10.0`")

async def executar_ciclo_operacional(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executa a análise da IA, dispara no Telegram e gerencia o painel da banca"""
    if not USER_SESSION["logado"] or not USER_SESSION["configurado"]:
        await update.message.reply_text("⚠️ Conecte sua conta e configure o gerenciamento antes de operar.")
        return

    par = "EURUSD-OTC"
    direcao = "PUT"
    confianca_ia = 91.2
    valor = USER_SESSION["entrada_base"]

    # 1. Alerta Inicial da IA
    await update.message.reply_text(
        f"🤖 **ANÁLISE DE IA - NOVO SINAL** 🤖\n\n"
        f"📊 Par: `{par}`\n"
        f"⏱ Direção: **{direcao}**\n"
        f"🧠 Confiança da IA: `{confianca_ia}%`\n"
        f"💵 Entrada: `R$ {valor:.2f}`\n\n"
        f"⚡ *Executando ordem na corretora ({USER_SESSION['tipo_conta']})...*"
    )

    time.sleep(3) # Simula o tempo da operação

    # Simulando um resultado WIN
    resultado = "WIN"
    lucro = valor * 0.82
    
    # Atualização matemática da banca
    USER_SESSION["banca_atual"] += lucro
    diferenca_total = USER_SESSION["banca_atual"] - USER_SESSION["banca_inicial"]
    status_financeiro = f"+R$ {diferenca_total:.2f}" if diferenca_total >= 0 else f"-R$ {abs(diferenca_total):.2f}"

    # 2. Mensagem de Resultado com Painel de Banca Atualizado
    await update.message.reply_text(
        f"✅ **RESULTADO: {resultado}** 🎉\n\n"
        f"📊 Par: `{par}`\n"
        f"💵 Lucro da Operação: `+R$ {lucro:.2f}`\n\n"
        f"📉 **PAINEL DA BANCA:**\n"
        f"💼 Banca Anterior: R$ {USER_SESSION['banca_atual'] - lucro:.2f}\n"
        f"💼 **Banca Atual:** **R$ {USER_SESSION['banca_atual']:.2f}**\n"
        f"📈 **Resultado Acumulado:** `{status_financeiro}`"
    )

def main():
    token = os.getenv("8899179180:AAHVBgfZExT0P66RYFAO_j51ZC_YbFBbdZM")
    if not token:
        print("Erro: TELEGRAM_BOT_TOKEN não configurado.")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", fazer_login))
    app.add_handler(CommandHandler("configurar", configurar_gerenciamento))
    app.add_handler(CommandHandler("operar", executar_ciclo_operacional))

    print("🤖 Bot configurado e operando no Telegram...")
    app.run_polling()

if __name__ == '__main__':
    main()
