import asyncio
import os
import re

from datetime import datetime, timezone


class LockManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lock = asyncio.Lock()
        return cls._instance


def get_lock():
    return LockManager().lock


def bool_to_str(boo: bool):
    return '1' if boo else '0'


def str_to_bool(string: str):
    return False if string == '0' else True


def get_accounts():
    accounts_str = os.getenv('TWITTER_TOKEN').strip(",")
    accounts = {account.split(':')[0]: account.split(':')[1] for account in accounts_str.split(',')}  # accounts_str = 'username:token,username:token'
    return accounts


def get_utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('T', ' ')


# Checking only the format may still allow passage through languages ​​that do not exist
def validate_and_normalize_language(lang_code: str) -> str | None:
    if not lang_code or not isinstance(lang_code, str):
        return None

    normalized = lang_code.strip().lower().replace('_', '-')

    normalization_map = {
        'zh': 'zh-cn',
        'cn': 'zh-cn',
        'tw': 'zh-tw',
        'jp': 'ja',
        'kr': 'ko',
        'ua': 'uk'
    }
    normalized = normalization_map.get(normalized, normalized)

    pattern = r"^[a-z]{2,3}(-[a-z0-9]{2,4})?$"
    
    if re.match(pattern, normalized):
        return normalized

    return None


def clean_markdown(text: str) -> str:
    """Remove markdown syntax and return the visible text."""
    if not text:
        return ""

    # Handle links: [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\((?:[^\(\)]|\([^\(\)]*\))+\)', r'\1', text)

    # Handle escaped characters and other tokens
    # Group 1: escaped char, Group 2: markdown token
    pattern = r'\\(?P<escaped>.)|(?P<token>\*\*\*|\*\*|__|\*|_|~~|\|\||`|>>>|^> ?)'

    def replace(match):
        if match.group('escaped'):
            return match.group('escaped')
        return "" # remove tokens

    return re.sub(pattern, replace, text, flags=re.MULTILINE)


def get_visible_length(text: str) -> int:
    return len(clean_markdown(text))


def escape_markdown(text: str) -> str:
    """Escape Discord markdown characters in a string, but avoid breaking URLs."""
    if not text:
        return ""
    
    # Regex to identify URLs
    url_re = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
    
    parts = []
    last_idx = 0
    for match in url_re.finditer(text):
        # Escape the text before the URL
        before = text[last_idx:match.start()]
        parts.append(re.sub(r'([\\*_~|`\[\]\(\)])', r'\\\1', before))
        # Add the URL unescaped
        parts.append(match.group(0))
        last_idx = match.end()
    
    # Escape the remaining text
    after = text[last_idx:]
    parts.append(re.sub(r'([\\*_~|`\[\]\(\)])', r'\\\1', after))
    
    result = "".join(parts)
    
    # Escape block markers at line start: > # - +
    result = re.sub(r'^([#>+-])', r'\\\1', result, flags=re.MULTILINE)
    
    return result


def safe_truncate(text: str, max_len: int) -> tuple[str, bool]:
    visible_total = get_visible_length(text)
    if visible_total <= max_len:
        return text, False

    limit = max_len - 3
    if limit < 0:
        limit = 0

    visible_chars = 0
    result = ""
    stack = []

    # Regex for tokens
    token_re = re.compile(r"""
        (?P<escaped>\\.) |
        (?P<quote>^>[ ]?) |
        (?P<link>\[(?P<link_text>[^\]]+)\]\((?P<link_url>(?:[^\(\)]|\([^\(\)]*\))+)\)) |
        (?P<bold_italic>(?<![a-zA-Z0-9])\*\*\*|\*\*\*(?![a-zA-Z0-9])) |
        (?P<bold>(?<![a-zA-Z0-9])\*\*|\*\*(?![a-zA-Z0-9])) |
        (?P<underline>(?<![a-zA-Z0-9])__|__(?![a-zA-Z0-9])) |
        (?P<italic_star>(?<![a-zA-Z0-9])\*|\*(?![a-zA-Z0-9])) |
        (?P<italic_underscore>(?<![a-zA-Z0-9])_|_(?![a-zA-Z0-9])) |
        (?P<strike>~~) |
        (?P<spoiler>\|\|) |
        (?P<code>`+[^`]+`+) |
        (?P<newline>\n) |
        (?P<char>.)
    """, re.VERBOSE | re.DOTALL | re.MULTILINE)

    truncated_manually = False

    for match in token_re.finditer(text):
        if visible_chars >= limit:
            break

        groups = match.groupdict()

        if groups['escaped']:
            result += groups['escaped']
            visible_chars += 1
        elif groups['quote']:
            result += match.group(0)
        elif groups['link']:
            l_text = groups['link_text']
            l_url = groups['link_url']
            if visible_chars + len(l_text) > limit:
                avail = limit - visible_chars
                result += f"[{l_text[:avail]}...]({l_url})"
                visible_chars = limit
                truncated_manually = True
                break
            else:
                result += groups['link']
                visible_chars += len(l_text)
        elif any(groups[tag] for tag in ['bold_italic', 'bold', 'underline', 'italic_star', 'italic_underscore', 'strike', 'spoiler']):
            tag_text = match.group(0)
            result += tag_text
            if stack and stack[-1] == tag_text:
                stack.pop()
            else:
                stack.append(tag_text)
        elif groups['code']:
            code_text = match.group(0)
            m = re.match(r'^(`+)(.+)\1$', code_text)
            if m:
                ticks, content = m.group(1), m.group(2)
                if visible_chars + len(content) > limit:
                    avail = limit - visible_chars
                    result += f"{ticks}{content[:avail]}...{ticks}"
                    visible_chars = limit
                    truncated_manually = True
                    break
                else:
                    result += code_text
                    visible_chars += len(content)
            else:
                result += code_text
        elif groups['newline']:
            result += "\n"
            visible_chars += 1
        elif groups['char']:
            result += groups['char']
            visible_chars += 1

    if not truncated_manually:
        # If we broke because of limit, add ellipsis
        if visible_chars >= limit:
            result += '...'

    # Close any open tags
    while stack:
        result += stack.pop()

    return result, True
