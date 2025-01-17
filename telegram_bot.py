from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your bot token
BOT_TOKEN = "7796219770:AAGfV11YB4YbuTSZFDLODbt7BJo4qaNfpbE"

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Send me a .ttf file, and I will convert it into a .h file for you."
    )

# Function to handle file uploads
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document

    # Check if the uploaded file is a .ttf file
    if document.file_name.endswith(".ttf"):
        await update.message.reply_text("Processing your .ttf file...")

        # Download the file
        file = await context.bot.get_file(document.file_id)
        input_file_path = document.file_name
        await file.download_to_drive(input_file_path)

        # Convert the .ttf file to .h format
        output_file_path = input_file_path + ".h"
        convert_ttf_to_h(input_file_path, output_file_path)

        # Send the converted file back to the user
        await update.message.reply_document(document=open(output_file_path, "rb"))
        await update.message.reply_text("Here is your converted .h file!")
    else:
        await update.message.reply_text("Please send a valid .ttf file.")

# Function to convert a .ttf file to a .h file
def convert_ttf_to_h(input_path: str, output_path: str) -> None:
    with open(input_path, "rb") as ttf_file, open(output_path, "w") as h_file:
        # Write the .h file header
        h_file.write(f"// Converted from {input_path}\n")
        h_file.write("const unsigned char font_data[] = {\n")

        # Read the .ttf file and write its content as hexadecimal
        byte = ttf_file.read(1)
        while byte:
            h_file.write(f"0x{byte.hex()}, ")
            byte = ttf_file.read(1)
        h_file.write("\n};\n")

# Main function to set up and run the bot
def main():
    # Initialize the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers for commands and file uploads
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Run the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
