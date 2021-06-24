def basic_text_cleaning(text: str) -> str:
    """
    Dummy cleaner that clean the subreddit received text removing newline noise.
    Args:
        text: string to clean

    Returns: str cleaned

    """
    text = text.replace("\\n", "")
    return text
