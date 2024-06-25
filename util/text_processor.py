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
        paragraphs = text.split("\n")
        messages = []
        current_message = ""
        in_code_block = False
        code_block_leading_spaces = 0

        for paragraph in paragraphs:
            match = re.match(r'^(\s*)```[a-zA-Z]+$', paragraph)
            if match:
                in_code_block = True
                code_block_leading_spaces = len(match.group(1))
            if re.match(r'^\s*```$', paragraph) and in_code_block:
                in_code_block = False
            
            if not in_code_block and not re.match(r'^\s*```$', paragraph):
                paragraph = TextProcessor.convert_markdown_to_slack(paragraph)
            
            if len(current_message) + len(paragraph) + 1 + (4+code_block_leading_spaces if in_code_block else 0) > TextProcessor.MAX_MESSAGE_LENGTH:
                # Append the current message if it reaches the limit
                if in_code_block and not re.match(r'^```[a-zA-Z]+$', paragraph):
                    current_message = current_message + "\n" + " " * code_block_leading_spaces + "```"
                    messages.append(current_message)
                    current_message = " " * code_block_leading_spaces + "```\n" + paragraph
                else:
                    messages.append(current_message)
                    current_message = paragraph
            else:
                if current_message:
                    current_message += "\n"
                current_message += paragraph

        # Append any remaining message
        if current_message:
            messages.append(current_message)

        return messages
