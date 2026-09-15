"""
Soundex algorithm implementation for phonetic matching of names.
"""

def soundex(name: str) -> str:
    """
    Computes the Soundex code for a given string (e.g., individual name or entity name).
    Soundex codes consist of a letter followed by three numerical digits.
    """
    if not name:
        return "0000"

    # Convert to uppercase and filter out non-alphabetic characters
    cleaned = "".join([c.upper() for c in name if c.isalpha()])
    if not cleaned:
        return "0000"

    first_letter = cleaned[0]

    # Soundex mapping dict
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }

    code = [first_letter]
    prev_digit = mapping.get(first_letter, '')

    for char in cleaned[1:]:
        curr_digit = mapping.get(char, '')
        if curr_digit:
            if curr_digit != prev_digit:
                code.append(curr_digit)
            prev_digit = curr_digit
        else:
            # H and W do not act as separators for double letters, but A, E, I, O, U, Y do reset prev_digit
            if char not in ('H', 'W'):
                prev_digit = ''
        if len(code) == 4:
            break

    # Pad with zeros if necessary
    while len(code) < 4:
        code.append('0')

    return "".join(code)

def soundex_match(name1: str, name2: str) -> bool:
    """
    Checks if two names yield the same Soundex code.
    If names consist of multiple words, checks if any word codes match.
    """
    if not name1 or not name2:
        return False

    code1 = soundex(name1)
    code2 = soundex(name2)
    if code1 == code2:
        return True

    words1 = [w for w in name1.split() if w]
    words2 = [w for w in name2.split() if w]

    codes1 = {soundex(w) for w in words1}
    codes2 = {soundex(w) for w in words2}

    return len(codes1.intersection(codes2)) > 0
