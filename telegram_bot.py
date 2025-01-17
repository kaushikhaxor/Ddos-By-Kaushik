import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Function to convert TTF to .h
def ttf_to_header(ttf_file_path, output_file_path):
    try:
        with open(ttf_file_path, 'rb') as f:
            font_data = f.read()

        array_name = os.path.splitext(os.path.basename(ttf_file_path))[0]
        header_content = f"// Font file: {os.path.basename(ttf_file_path)}\n"
        header_content += f"// Converted to .h by Telegram Bot\n\n"
        header_content += f"const unsigned char {array_name}[] = {{\n"

        for i, byte in enumerate(font_data):
            header_content += f"0x{byte:02X}, "
            if (i + 1) % 12 == 0:  # Wrap lines every 12 bytes
                header_content += "\n"
        header_content = header_content.rstrip(", \n") + "\n};\n"

        with open(output_file_path, 'w') as f:
            f.write(header_content)

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a .ttf font file, and I'll convert it to a .h file for you.")

# File handler
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type == "font/ttf":
        file_id = file.file_id
        file_name = file.file_name

        # Download the TTF file
        ttf_file_path = f"./{file_name}"
        output_file_path = f"./{os.path.splitext(file_name)[0]}.h"
        file_obj = await context.bot.get_file(file_id)
        await file_obj.download_to_drive(ttf_file_path)

        # Convert to .h
        if ttf_to_header(ttf_file_path, output_file_path):
            with open(output_file_path, 'rb') as f:
                await update.message.reply_document(f, filename=os.path.basename(output_file_path))
            os.remove(ttf_file_path)  # Cleanup
            os.remove(output_file_path)
        else:
            await update.message.reply_text("Failed to convert the font file. Please try again.")
    else:
        await update.message.reply_text("Please send a valid .ttf file.")

# Main function
def main():
    # Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
