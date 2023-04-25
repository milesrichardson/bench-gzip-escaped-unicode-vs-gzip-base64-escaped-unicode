import random
import base64
import gzip
import csv
import sys

import random
import base64
import gzip
import binascii

from emoji.unicode_codes.data_dict import EMOJI_DATA

import re
import os

# Set DEBUG=1 to print emoji, escaped octets, and base64 encoded escaped octets
DEBUG = os.getenv("DEBUG") == 1

# The keys of EMOJI_DATA are already utf-8 encoded e.g. u'\U0001F947'
EMOJIS = list(EMOJI_DATA.keys())


# emoji should be key of EMOJI_DATA
def encode_emoji(emoji):
    emoji_bytes = emoji.encode("utf-8")
    emoji_hex = binascii.hexlify(emoji_bytes).decode("ascii")
    escaped_emoji = re.sub(r"(..)", r"\\\\x\1", emoji_hex)
    return escaped_emoji


def encode_and_compress_emoji(num_emojis, emojis):
    # Get a random sample of emojis from the dict
    emojis = random.sample(emojis, num_emojis)

    # The actual emojis
    if DEBUG:
        print("".join([emoji for emoji in emojis]))

    # Join the emojis together into a string
    escaped_octets = "".join([encode_emoji(emoji) for emoji in emojis])

    if DEBUG:
        print(escaped_octets)

    # Encode the emojis using Base64
    # base64_encoded = base64.b64encode(escaped_octets).decode("utf-8")
    base64_encoded = base64.b64encode(escaped_octets.encode("utf-8"))

    if DEBUG:
        print(base64_encoded)

    # Compress both encoded strings using gzip
    escaped_octets_compressed = gzip.compress(escaped_octets.encode("utf-8"))
    base64_compressed = gzip.compress(base64_encoded)

    # Return the sizes of the compressed data
    return len(escaped_octets_compressed), len(base64_compressed)


# Define the range of numbers of emojis to test
num_emojis_range = range(100, 1001, 100)

# Open a CSV file for output
with open("emoji_encoding_benchmark.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row to the CSV file
    writer.writerow(["Num Emojis", "Escaped Octets Size", "Base64 Encoded Size"])

    # Iterate through the range of numbers of emojis
    for num_emojis in num_emojis_range:
        # Call the encode_and_compress_emoji function
        escaped_octets_size, base64_encoded_size = encode_and_compress_emoji(
            num_emojis, EMOJIS
        )

        # Write the results to the CSV file
        writer.writerow([num_emojis, escaped_octets_size, base64_encoded_size])

        # Write the results to stdout as well
        sys.stdout.write(
            f"Num Emojis: {num_emojis}, Escaped Octets Size: {escaped_octets_size}, Base64 Encoded Size: {base64_encoded_size}\n"
        )

import matplotlib.pyplot as plt
import csv

# Read the CSV file
with open("emoji_encoding_benchmark.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    data = {"num_emojis": [], "escaped_octets_size": [], "base64_encoded_size": []}
    for row in reader:
        data["num_emojis"].append(int(row["Num Emojis"]))
        data["escaped_octets_size"].append(int(row["Escaped Octets Size"]))
        data["base64_encoded_size"].append(int(row["Base64 Encoded Size"]))

# Create a plot
plt.plot(data["num_emojis"], data["escaped_octets_size"], label="Escaped Octets Size")
plt.plot(data["num_emojis"], data["base64_encoded_size"], label="Base64 Encoded Size")
plt.xlabel("Number of Emojis")
plt.ylabel("Size")
plt.title("Emoji Encoding Benchmark Results")
plt.legend()

# Save the plot as a PNG image
plt.savefig("emoji_encoding_benchmark.png")
