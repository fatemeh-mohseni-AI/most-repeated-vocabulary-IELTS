
def generate_html_table(words):
    # Generate table rows
    table_rows = ''.join([
        f"<tr><td>{word.word}</td><td>{word.count}</td><td>{word.book}</td><td>{word.sentences}</td></tr>"
        for word in words
    ])

    # Return HTML content
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
                text-align: left;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #ddd;
            }}
        </style>
    </head>
    <body>
        <h2>Most Repeated Words</h2>
        <table>
            <tr>
                <th>Word</th>
                <th>Count</th>
                <th>Book</th>
                <th>Sentences</th>
            </tr>
            {table_rows}
        </table>
    </body>
    </html>
    """
