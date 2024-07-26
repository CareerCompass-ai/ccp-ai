def nl2br_bullet(text):
    lines = text.split('\n')
    return ''.join(f'<li>&bull; {line}</li>' for line in lines if line)