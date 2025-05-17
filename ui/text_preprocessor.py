"""
Text Preprocessor for Arabic Diacritization

This module handles chunking of large text inputs to avoid model size limitations.
"""

import re


def split_and_chunk_text(text, max_chunk_size=900):
    """
    Splits Arabic text by periods and line breaks and then creates chunks
    that don't exceed the max_chunk_size (with some buffer below the model's
    1024 token limit).

    Args:
        text (str): Input Arabic text
        max_chunk_size (int): Maximum size of each chunk (default: 900 characters)
                             to leave buffer below the model's 1024 limit

    Returns:
        list: List of text chunks
    """
    if not text or len(text) <= max_chunk_size:
        return [text] if text else []

    # Split by periods (.) and line breaks
    # Keep the delimiter (period or line break) with the preceding text
    segments = []

    # Split by line breaks first
    lines = text.split("\n")
    for line in lines:
        if not line.strip():
            # Keep empty lines as separate segments
            segments.append("")
            continue

        # Then split by periods within each line
        period_segments = re.split(r"(\.)", line)

        # Combine periods with their preceding text
        i = 0
        while i < len(period_segments):
            if i + 1 < len(period_segments) and period_segments[i + 1] == ".":
                segments.append(period_segments[i] + ".")
                i += 2
            else:
                segments.append(period_segments[i])
                i += 1

    # Combine segments into chunks that don't exceed max_chunk_size
    chunks = []
    current_chunk = ""

    for segment in segments:
        # If adding this segment would exceed the limit, start a new chunk
        if len(current_chunk) + len(segment) > max_chunk_size:
            if current_chunk:  # Don't add empty chunks
                chunks.append(current_chunk)
            current_chunk = segment
        else:
            # If the segment is a paragraph break (empty string), keep it as is
            if segment == "":
                if current_chunk:  # Add current chunk if it's not empty
                    chunks.append(current_chunk)
                    current_chunk = ""
                # Don't add empty segments as separate chunks
            else:
                # Otherwise, add the segment to the current chunk
                # Add a space if the current chunk is not empty and doesn't end with a newline
                if current_chunk and not current_chunk.endswith("\n"):
                    current_chunk += " " + segment.lstrip()
                else:
                    current_chunk += segment

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def process_and_join_chunks(chunks, process_function):
    """
    Process each chunk using the provided function and join the results.

    Args:
        chunks (list): List of text chunks
        process_function (callable): Function that processes each chunk
                                    and returns a processed result

    Returns:
        str: Combined processed text
    """
    if not chunks:
        return ""

    processed_chunks = []

    for chunk in chunks:
        processed = process_function(chunk)
        processed_chunks.append(processed)

    # Join the processed chunks
    return "".join(processed_chunks)
