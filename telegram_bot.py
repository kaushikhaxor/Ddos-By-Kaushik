import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

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
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a .ttf font file, and I'll convert it to a .h file for you.")

# File handler
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type == "font/ttf":
        file_id = file.file_id
        file_name = file.file_name

        # Download the TTF file
        ttf_file_path = f"./{file_name}"
        output_file_path = f"./{os.path.splitext(file_name)[0]}.h"
        file_obj = context.bot.get_file(file_id)
        file_obj.download(ttf_file_path)

        # Convert to .h
        if ttf_to_header(ttf_file_path, output_file_path):
            with open(output_file_path, 'rb') as f:
                update.message.reply_document(f, filename=os.path.basename(output_file_path))
            os.remove(ttf_file_path)  # Cleanup
            os.remove(output_file_path)
        else:
            update.message.reply_text("Failed to convert the font file. Please try again.")
    else:
        update.message.reply_text("Please send a valid .ttf file.")

# Main function
def main():
    # Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
    updater = Updater("YOUR_BOT_TOKEN")
    dispatcher = updater.dispatcher

    # Add command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_file))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
