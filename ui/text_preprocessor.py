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
        list: List of text chunks with preserved line breaks
    """
    if not text or len(text) <= max_chunk_size:
        return [text] if text else []

    # Split by periods (.) and line breaks
    # Keep the delimiter (period or line break) with the preceding text
    segments = []
    line_break_markers = []  # Track which segments had line breaks after them

    # Split by line breaks first
    lines = text.split("\n")
    for i, line in enumerate(lines):
        is_last_line = i == len(lines) - 1

        if not line.strip():
            # Keep empty lines as separate segments
            segments.append("")
            line_break_markers.append(True)
            continue

        # Then split by periods within each line
        period_segments = re.split(r"(\.)", line)

        # Combine periods with their preceding text
        j = 0
        while j < len(period_segments):
            if j + 1 < len(period_segments) and period_segments[j + 1] == ".":
                segments.append(period_segments[j] + ".")
                line_break_markers.append(False)  # Not a line break yet
                j += 2
            else:
                segments.append(period_segments[j])
                line_break_markers.append(False)  # Not a line break yet
                j += 1

        # Mark the last segment of this line for a line break if not the last line
        if not is_last_line and segments:
            line_break_markers[-1] = True

    # Combine segments into chunks that don't exceed max_chunk_size
    chunks = []
    current_chunk = ""
    chunk_line_breaks = []  # To track which chunks should end with a line break

    for i, segment in enumerate(segments):
        has_line_break = line_break_markers[i] if i < len(line_break_markers) else False

        # If adding this segment would exceed the limit, start a new chunk
        if len(current_chunk) + len(segment) > max_chunk_size:
            if current_chunk:  # Don't add empty chunks
                chunks.append(current_chunk)
                chunk_line_breaks.append(False)  # No extra line break
            current_chunk = segment
        else:
            # If the segment is a paragraph break (empty string), keep it as is
            if segment == "":
                if current_chunk:  # Add current chunk if it's not empty
                    chunks.append(current_chunk)
                    chunk_line_breaks.append(True)  # Add line break
                    current_chunk = ""
                # Don't add empty segments as separate chunks
            else:
                # Otherwise, add the segment to the current chunk
                if current_chunk and not current_chunk.endswith("\n"):
                    current_chunk += " " + segment.lstrip()
                else:
                    current_chunk += segment

        # If this segment should end with a line break and it's not the last segment
        if has_line_break and current_chunk and i < len(segments) - 1:
            chunks.append(current_chunk)
            chunk_line_breaks.append(True)  # Add line break
            current_chunk = ""

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
        chunk_line_breaks.append(False)  # No extra line break for the last chunk

    # Format chunks with proper line breaks
    formatted_chunks = []
    for i, chunk in enumerate(chunks):
        if i < len(chunk_line_breaks) and chunk_line_breaks[i]:
            formatted_chunks.append(chunk + "\n")
        else:
            formatted_chunks.append(chunk)

    return formatted_chunks


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
