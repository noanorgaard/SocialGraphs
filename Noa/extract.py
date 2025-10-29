import re
import html
import os

def extract_genres_from_wikitext(wikitext_content):
    genre_pattern = re.compile(
        r'\|\s*genre\s*=\s*(.*?)(?=\n\s*\||\n}})',
        re.DOTALL | re.IGNORECASE
    )

    link_pattern = re.compile(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]')
    citation_pattern = re.compile(r'\{\{cite.*?\}\}', re.DOTALL | re.IGNORECASE)
    template_pattern = re.compile(r'\{\{(?:flatlist|hlist|nowrap)\|?', re.IGNORECASE)
    #ref_tag_pattern = re.compile(r'<ref[^>]*?>.*?</ref>|<ref[^>]*/>', re.DOTALL | re.IGNORECASE)
    ref_tag_pattern = re.compile(r'(<ref[^>]*?>.*?</ref>|<ref[^>]*/>)|(&lt;ref[^&gt;]*?&gt;.*?&lt;/ref&gt;|&lt;ref[^&gt;]*/&gt;)', re.DOTALL | re.IGNORECASE)
    html_comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)

    match = genre_pattern.search(wikitext_content)
    if match:
        raw_genres = match.group(1)

        # Unescape HTML entities
        raw_genres = html.unescape(raw_genres)

        # Remove HTML tags like <small>, <i>, etc.
        raw_genres = re.sub(r'<[^>]+>', '', raw_genres) 

        # Remove HTML comments, citations, <ref> tags, and nested templates
        raw_genres = html_comment_pattern.sub('', raw_genres)
        raw_genres = citation_pattern.sub('', raw_genres)
        raw_genres = ref_tag_pattern.sub('', raw_genres)
        raw_genres = template_pattern.sub('', raw_genres)

        # Remove lines that look like citation metadata
        raw_genres = re.sub(r'\b(title|url|access-date|publisher|quote|last|first|website|date|archive-url|archive-date|language)\b.*', '', raw_genres)

        # Remove trailing explanations like "The following sources refer to..."
        raw_genres = re.sub(r'(The following.*)', '', raw_genres)

        # Remove stray brackets and asterisks
        raw_genres = raw_genres.replace('[[', '').replace(']]', '')
        raw_genres = raw_genres.replace('{{', '').replace('}}', '')
        raw_genres = raw_genres.replace('*', '')

        # Split by common delimiters
        genre_candidates = re.split(r'\||\n|,', raw_genres)

        # Clean and filter
        genres = []
        for genre in genre_candidates:
            genre = link_pattern.sub(r'\1', genre).strip()
            if genre:
                genres.append(genre)

        return list(set(genres))
    return []

# Define the directory where your band data files are located
data_directory = "Bands"
band_genres = {}

# Iterate over all files in the specified directory
for filename in os.listdir(data_directory):
    file_path = os.path.join(data_directory, filename)
    band_name = os.path.splitext(filename)[0] # Get band name from filename

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            wikitext_content = content

            genres = extract_genres_from_wikitext(wikitext_content)
            band_genres[band_name] = genres
    except Exception as e:
        print(f"Error processing file {filename}: {e}")

# order the band list alphabetically
band_genres = dict(sorted(band_genres.items()))

# print number of bands that have infoboxes:
num_bands_with_infoboxes = sum(1 for genres in band_genres.values() if genres)
print(f"Number of bands with infoboxes: {num_bands_with_infoboxes} \n")

# Print the extracted genres for each band
for band, genres in band_genres.items():
    print(f"{band}: {genres}")
