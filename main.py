import base64
import os
import sys


def main():
    bundle_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "entry.png.b64"
    )
    try:
        with open(bundle_path, "rb") as bundle:
            image_bytes = base64.b64decode(bundle.read().strip(), validate=True)
    except (OSError, ValueError) as error:
        sys.exit(f"Cannot decode bundled image: {error}")
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        sys.exit("Bundled image does not have a valid PNG signature")
    output_directory = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(output_directory, exist_ok=True)
        output_path = os.path.join(output_directory, "entry.png")
        with open(output_path, "wb") as output_file:
            output_file.write(image_bytes)
    except OSError as error:
        sys.exit(f"Cannot write entry.png: {error}")


if __name__ == "__main__":
    main()
