import re

class TextProcessor:
    MAX_MESSAGE_LENGTH = 4000

    @staticmethod
    def convert_markdown_to_slack(markdown_text):
        def convert_headers(match):
            header_content = match.group(2)
            # Remove any existing bold and italic within the header
            header_content = re.sub(r'\*\*(.*?)\*\*', r'\1', header_content)
            header_content = re.sub(r'\*(.*?)\*', r'\1', header_content)
            header_content = re.sub(r'_(.*?)_', r'\1', header_content)
            header_content = re.sub(r'_(.*?)_', r'\1', header_content)
            header_content = re.sub(r'~(.*?)~', r'\1', header_content)
            # Make the entire header bold for Slack
            return f"*{header_content}*"

        # Convert headers to bold
        header_pattern = re.compile(r'^(#+\s*)(.*)', re.MULTILINE)
        slack_text = header_pattern.sub(convert_headers, markdown_text)
        
        # Convert bold
        slack_text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', slack_text)
        
        # Convert italic _text_ to _text_
        slack_text = re.sub(r'_(.*?)_', r'_\1_', slack_text)
        slack_text = re.sub(r'_(.*?)_', r'_\1_', slack_text)
        
        # Convert strikethrough
        slack_text = re.sub(r'~(.*?)~', r'~\1~', slack_text)

        return slack_text

    @staticmethod
    def split_text_by_paragraphs(text):
        paragraphs = text.split("\n\n")
        messages = []
        current_message = ""

        for paragraph in paragraphs:
            if len(current_message) + len(paragraph) + 1 > TextProcessor.MAX_MESSAGE_LENGTH:
                # Append the current message if it reaches the limit
                messages.append(current_message)
                current_message = paragraph  # Start a new message
            else:
                if current_message:
                    current_message += "\n\n"
                current_message += paragraph

        # Append any remaining message
        if current_message:
            messages.append(current_message)

        return messages
