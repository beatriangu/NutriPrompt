import markdown

def markdown_to_html(markdown_text: str) -> str:
    return markdown.markdown(markdown_text, extensions=["tables"])