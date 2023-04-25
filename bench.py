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

import matplotlib.pyplot as plt


# Set DEBUG=1 to print emoji, escaped octets, and base64 encoded escaped octets
DEBUG = os.getenv("DEBUG") == "1"

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

    # gzip(escape(emoji))
    escaped_emoji = "".join([encode_emoji(emoji) for emoji in emojis])
    if DEBUG:
        print(escaped_emoji)
    gzipped_escaped_emoji = gzip.compress(escaped_emoji.encode("utf-8"))

    # gzip(base64(escape(emoji)))
    base64_escaped_emoji = base64.b64encode(escaped_emoji.encode("utf-8"))
    if DEBUG:
        print(base64_escaped_emoji)
    gzipped_base64_escaped_emoji = gzip.compress(base64_escaped_emoji)

    # gzip(base64(emoji))
    base64_emoji = base64.b64encode("".join(emojis).encode("utf-8"))
    gzipped_base64_emoji = gzip.compress(base64_emoji)

    return (
        len(gzipped_escaped_emoji),
        len(gzipped_base64_escaped_emoji),
        len(gzipped_base64_emoji),
    )


# Define the range of numbers of emojis to test
num_emojis_range = range(100, 1001, 100)

# Open a CSV file for output
with open("emoji_encoding_benchmark.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row to the CSV file
    writer.writerow(
        [
            "Num Emojis",
            "gzip(escape(emoji))",
            "gzip(base64(escape(emoji)))",
            "gzip(base64(emoji))",
        ]
    )

    # Iterate through the range of numbers of emojis
    for num_emojis in num_emojis_range:
        # Call the encode_and_compress_emoji function
        (
            gzipped_escaped_emoji_size,
            gzipped_base64_escaped_emoji_size,
            gzipped_base64_emoji_size,
        ) = encode_and_compress_emoji(num_emojis, EMOJIS)

        # Write the results to the CSV file
        writer.writerow(
            [
                num_emojis,
                gzipped_escaped_emoji_size,
                gzipped_base64_escaped_emoji_size,
                gzipped_base64_emoji_size,
            ]
        )

        # Write the results to stdout as well
        sys.stdout.write(
            f"Num Emojis: {num_emojis}, gzip(escape(emoji)): {gzipped_escaped_emoji_size}, gzip(base64(escape(emoji))): {gzipped_base64_escaped_emoji_size}, gzip(base64(emoji)): {gzipped_base64_emoji_size}\n"
        )

# Read the CSV file
with open("emoji_encoding_benchmark.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    data = {
        "num_emojis": [],
        "gzip(escape(emoji))": [],
        "gzip(base64(escape(emoji)))": [],
        "gzip(base64(emoji))": [],
    }
    for row in reader:
        data["num_emojis"].append(int(row["Num Emojis"]))
        data["gzip(escape(emoji))"].append(int(row["gzip(escape(emoji))"]))
        data["gzip(base64(escape(emoji)))"].append(
            int(row["gzip(base64(escape(emoji)))"])
        )
        data["gzip(base64(emoji))"].append(int(row["gzip(base64(emoji))"]))

# Create a plot
plt.plot(data["num_emojis"], data["gzip(escape(emoji))"], label="gzip(escape(emoji))")
plt.plot(
    data["num_emojis"],
    data["gzip(base64(escape(emoji)))"],
    label="gzip(base64(escape(emoji)))",
)
plt.plot(data["num_emojis"], data["gzip(base64(emoji))"], label="gzip(base64(emoji))")
plt.xlabel("Number of Emojis")
plt.ylabel("Size")
plt.title("Emoji Encoding Benchmark Results")
plt.legend()

# Save the plot as a PNG image
plt.savefig("emoji_encoding_benchmark.png")
