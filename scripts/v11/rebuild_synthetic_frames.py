#!/usr/bin/env python3
"""Build and validate the canonical synthetic research-frame fixtures.

The fixtures are deterministic raster drawings made only from abstract shapes.
They are encoded with the Python standard library as metadata-free PNG files.
Ownership is proven by an exact raster comparison with this generator plus a
strict PNG structure check, rather than by embedding a mutable metadata field.

Research prototype only. Synthetic fixtures only. Not a medical device.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import os
import struct
import tempfile
import zlib
from functools import lru_cache
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "docs" / "training" / "frames"
FRAME_GENERATOR_ID = "eyewalker.synthetic.frames.v1"
FRAME_COUNT = 26
WIDTH = 640
HEIGHT = 480
WATERMARK = "SIMULATED RESEARCH FIXTURE \N{EM DASH} NOT A DETECTION"
CANONICAL_NAMES = tuple(f"fixture_{index:04d}.png" for index in range(1, FRAME_COUNT + 1))
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_CHUNK_CONTRACT = (b"IHDR", b"PLTE", b"IDAT", b"IEND")

# A fixed sixteen-color palette keeps the PNGs small and the raster encoding
# fully deterministic. PLTE is image data required by indexed PNG, not metadata.
PALETTE = (
    (10, 17, 30),
    (26, 42, 68),
    (248, 250, 252),
    (255, 199, 36),
    (70, 215, 220),
    (238, 91, 154),
    (116, 218, 119),
    (255, 139, 65),
    (101, 88, 196),
    (59, 130, 246),
    (154, 166, 185),
    (227, 84, 84),
    (81, 62, 112),
    (28, 75, 78),
    (91, 55, 39),
    (46, 49, 60),
)

# Minimal 5x7 bitmap font. It contains only the glyphs used by the two fixture
# labels, so no host font or platform-dependent font renderer is involved.
FONT = {
    " ": ("00000",) * 7,
    "\N{EM DASH}": (
        "00000", "00000", "00000", "11111", "00000", "00000", "00000"
    ),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
}


def _chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _stored_zlib(payload: bytes) -> bytes:
    """Return a platform-independent zlib stream using stored DEFLATE blocks."""

    stream = bytearray(b"\x78\x01")
    cursor = 0
    while cursor < len(payload):
        block = payload[cursor : cursor + 65535]
        cursor += len(block)
        stream.append(1 if cursor == len(payload) else 0)
        size = len(block)
        stream.extend(struct.pack("<HH", size, size ^ 0xFFFF))
        stream.extend(block)
    stream.extend(struct.pack(">I", zlib.adler32(payload) & 0xFFFFFFFF))
    return bytes(stream)


class _BitWriter:
    """Small LSB-first bit writer for deterministic fixed-Huffman DEFLATE."""

    def __init__(self) -> None:
        self.output = bytearray()
        self.pending = 0
        self.pending_bits = 0

    def write(self, value: int, width: int) -> None:
        self.pending |= value << self.pending_bits
        self.pending_bits += width
        while self.pending_bits >= 8:
            self.output.append(self.pending & 0xFF)
            self.pending >>= 8
            self.pending_bits -= 8

    def finish(self) -> bytes:
        if self.pending_bits:
            self.output.append(self.pending & 0xFF)
        return bytes(self.output)


def _reverse_bits(value: int, width: int) -> int:
    reversed_value = 0
    for _ in range(width):
        reversed_value = (reversed_value << 1) | (value & 1)
        value >>= 1
    return reversed_value


def _write_fixed_symbol(writer: _BitWriter, symbol: int) -> None:
    if 0 <= symbol <= 143:
        code, width = 0x30 + symbol, 8
    elif 144 <= symbol <= 255:
        code, width = 0x190 + symbol - 144, 9
    elif 256 <= symbol <= 279:
        code, width = symbol - 256, 7
    elif 280 <= symbol <= 287:
        code, width = 0xC0 + symbol - 280, 8
    else:
        raise ValueError(f"invalid fixed-Huffman symbol: {symbol}")
    writer.write(_reverse_bits(code, width), width)


LENGTH_CODES = (
    (257, 3, 0),
    (258, 4, 0),
    (259, 5, 0),
    (260, 6, 0),
    (261, 7, 0),
    (262, 8, 0),
    (263, 9, 0),
    (264, 10, 0),
    (265, 11, 1),
    (266, 13, 1),
    (267, 15, 1),
    (268, 17, 1),
    (269, 19, 2),
    (270, 23, 2),
    (271, 27, 2),
    (272, 31, 2),
    (273, 35, 3),
    (274, 43, 3),
    (275, 51, 3),
    (276, 59, 3),
    (277, 67, 4),
    (278, 83, 4),
    (279, 99, 4),
    (280, 115, 4),
    (281, 131, 5),
    (282, 163, 5),
    (283, 195, 5),
    (284, 227, 5),
    (285, 258, 0),
)


def _write_length_distance_one(writer: _BitWriter, length: int) -> None:
    if not 3 <= length <= 258:
        raise ValueError(f"invalid DEFLATE match length: {length}")
    for code, base, extra_bits in reversed(LENGTH_CODES):
        if length >= base:
            maximum = base + ((1 << extra_bits) - 1 if extra_bits else 0)
            if length <= maximum or code == 285:
                _write_fixed_symbol(writer, code)
                if extra_bits:
                    writer.write(length - base, extra_bits)
                writer.write(0, 5)  # fixed distance code 0 means distance one
                return
    raise ValueError(f"cannot encode DEFLATE match length: {length}")


def _fixed_zlib(payload: bytes) -> bytes:
    """Encode deterministic fixed-Huffman DEFLATE with distance-one runs."""

    writer = _BitWriter()
    writer.write(1, 1)  # BFINAL
    writer.write(1, 2)  # BTYPE=01, fixed Huffman
    cursor = 0
    while cursor < len(payload):
        if cursor > 0 and payload[cursor] == payload[cursor - 1]:
            run_end = cursor
            while (
                run_end < len(payload)
                and payload[run_end] == payload[cursor - 1]
                and run_end - cursor < 258
            ):
                run_end += 1
            run_length = run_end - cursor
            if run_length >= 3:
                _write_length_distance_one(writer, run_length)
                cursor = run_end
                continue
        _write_fixed_symbol(writer, payload[cursor])
        cursor += 1
    _write_fixed_symbol(writer, 256)
    compressed = writer.finish()
    return (
        b"\x78\x01"
        + compressed
        + struct.pack(">I", zlib.adler32(payload) & 0xFFFFFFFF)
    )


def _set_pixel(canvas: bytearray, x: int, y: int, color: int) -> None:
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        canvas[y * WIDTH + x] = color


def _rectangle(
    canvas: bytearray,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: int,
) -> None:
    left, right = sorted((max(0, x0), min(WIDTH - 1, x1)))
    top, bottom = sorted((max(0, y0), min(HEIGHT - 1, y1)))
    row = bytes([color]) * (right - left + 1)
    for y in range(top, bottom + 1):
        start = y * WIDTH + left
        canvas[start : start + len(row)] = row


def _line(
    canvas: bytearray,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: int,
    width: int = 1,
) -> None:
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    radius = max(0, width // 2)
    while True:
        _rectangle(canvas, x0 - radius, y0 - radius, x0 + radius, y0 + radius, color)
        if x0 == x1 and y0 == y1:
            break
        doubled = 2 * error
        if doubled >= dy:
            error += dy
            x0 += sx
        if doubled <= dx:
            error += dx
            y0 += sy


def _circle(canvas: bytearray, cx: int, cy: int, radius: int, color: int) -> None:
    radius_squared = radius * radius
    for y in range(max(0, cy - radius), min(HEIGHT - 1, cy + radius) + 1):
        offset = int((radius_squared - (y - cy) ** 2) ** 0.5)
        _rectangle(canvas, cx - offset, y, cx + offset, y, color)


def _triangle(
    canvas: bytearray,
    points: tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
    color: int,
) -> None:
    vertices = sorted(points, key=lambda point: point[1])
    minimum_y = max(0, vertices[0][1])
    maximum_y = min(HEIGHT - 1, vertices[-1][1])
    for y in range(minimum_y, maximum_y + 1):
        intersections: list[float] = []
        for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
            if y0 == y1:
                continue
            if min(y0, y1) <= y < max(y0, y1):
                intersections.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        if len(intersections) >= 2:
            intersections.sort()
            _rectangle(canvas, round(intersections[0]), y, round(intersections[-1]), y, color)


def _text_width(text: str, scale: int) -> int:
    return len(text) * 6 * scale - scale


def _text(
    canvas: bytearray,
    x: int,
    y: int,
    text: str,
    color: int,
    scale: int = 2,
) -> None:
    cursor = x
    for character in text:
        glyph = FONT.get(character)
        if glyph is None:
            raise ValueError(f"unsupported fixture-label glyph: {character!r}")
        for row_index, row in enumerate(glyph):
            for column_index, bit in enumerate(row):
                if bit == "1":
                    _rectangle(
                        canvas,
                        cursor + column_index * scale,
                        y + row_index * scale,
                        cursor + (column_index + 1) * scale - 1,
                        y + (row_index + 1) * scale - 1,
                        color,
                    )
        cursor += 6 * scale


def _fixture_pixels(index: int) -> bytearray:
    if not 1 <= index <= FRAME_COUNT:
        raise ValueError(f"fixture index must be 1..{FRAME_COUNT}: {index}")

    background = (1, 12, 13, 14, 15)[index % 5]
    canvas = bytearray([background]) * (WIDTH * HEIGHT)

    # Framing bands make the disclosure persistent and high contrast.
    _rectangle(canvas, 0, 0, WIDTH - 1, 43, 0)
    _rectangle(canvas, 0, HEIGHT - 35, WIDTH - 1, HEIGHT - 1, 0)
    watermark_x = (WIDTH - _text_width(WATERMARK, 2)) // 2
    _text(canvas, watermark_x, 14, WATERMARK, 2, scale=2)
    fixture_label = f"FIXTURE {index:02d}  ABSTRACT SHAPE TEST"
    label_x = (WIDTH - _text_width(fixture_label, 2)) // 2
    _text(canvas, label_x, HEIGHT - 26, fixture_label, 3, scale=2)

    # Every index produces a distinct, abstract geometry exercise. There is no
    # captured scene and no semantic object or person represented by the marks.
    primary = 3 + (index * 3) % 8
    secondary = 3 + (index * 5 + 1) % 8
    accent = 3 + (index * 7 + 2) % 8
    offset_x = 45 + (index * 29) % 135
    offset_y = 80 + (index * 17) % 75

    _circle(canvas, offset_x + 75, offset_y + 75, 30 + index % 31, primary)
    _circle(canvas, WIDTH - offset_x - 55, HEIGHT - offset_y - 55, 18 + index % 25, secondary)
    _rectangle(
        canvas,
        230 + (index * 11) % 90,
        105 + (index * 13) % 75,
        315 + (index * 17) % 120,
        175 + (index * 19) % 95,
        accent,
    )
    _triangle(
        canvas,
        (
            (85 + (index * 23) % 150, 350 - (index * 7) % 75),
            (250 + (index * 19) % 190, 245 + (index * 11) % 85),
            (470 + (index * 13) % 100, 370 - (index * 5) % 60),
        ),
        3 + (index * 2) % 8,
    )
    for segment in range(6):
        start_x = 40 + segment * 102
        start_y = 230 + ((index + segment) % 3) * 24
        end_y = start_y + (-1 if segment % 2 else 1) * (45 + index % 24)
        _line(canvas, start_x, start_y, start_x + 72, end_y, secondary, 5 + index % 4)
    _line(canvas, 28, 58 + index * 5, 611, 409 - index * 4, primary, 3)
    _line(canvas, 611, 65 + index * 3, 28, 400 - index * 2, accent, 3)
    return canvas


def _pack_scanlines(pixels: bytearray, *, bit_depth: int = 8) -> bytes:
    packed = bytearray()
    for y in range(HEIGHT):
        packed.append(0)  # PNG filter type: None
        start = y * WIDTH
        row = pixels[start : start + WIDTH]
        if bit_depth == 8:
            packed.extend(row)
        elif bit_depth == 4:
            for x in range(0, WIDTH, 2):
                packed.append((row[x] << 4) | row[x + 1])
        else:
            raise ValueError(f"unsupported fixture bit depth: {bit_depth}")
    return bytes(packed)


@lru_cache(maxsize=FRAME_COUNT * 2)
def _fixture_png_bytes(index: int, *, bit_depth: int) -> bytes:
    pixels = _fixture_pixels(index)
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, bit_depth, 3, 0, 0, 0)
    palette = bytes(component for color in PALETTE for component in color)
    return b"".join(
        (
            PNG_SIGNATURE,
            _chunk(b"IHDR", ihdr),
            _chunk(b"PLTE", palette),
            _chunk(
                b"IDAT",
                _fixed_zlib(_pack_scanlines(pixels, bit_depth=bit_depth)),
            ),
            _chunk(b"IEND", b""),
        )
    )


def expected_fixture_bytes(index: int) -> bytes:
    """Return the canonical 8-bit indexed PNG bytes for one fixture."""

    return _fixture_png_bytes(index, bit_depth=8)


def _legacy_4bit_fixture_bytes(index: int) -> bytes:
    """Recognize the brief, generator-owned 4-bit draft for atomic migration."""

    pixels = _fixture_pixels(index)
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 4, 3, 0, 0, 0)
    palette = bytes(component for color in PALETTE for component in color)
    return b"".join(
        (
            PNG_SIGNATURE,
            _chunk(b"IHDR", ihdr),
            _chunk(b"PLTE", palette),
            _chunk(b"IDAT", _stored_zlib(_pack_scanlines(pixels, bit_depth=4))),
            _chunk(b"IEND", b""),
        )
    )


def inspect_png(raw: bytes) -> dict[str, object]:
    """Validate the complete PNG structure and return its media properties."""

    if not raw.startswith(PNG_SIGNATURE):
        raise ValueError("source fixture does not have PNG magic bytes")
    cursor = len(PNG_SIGNATURE)
    chunks: list[bytes] = []
    payloads: dict[bytes, list[bytes]] = {}
    while cursor < len(raw):
        if cursor + 12 > len(raw):
            raise ValueError("truncated PNG chunk")
        length = struct.unpack(">I", raw[cursor : cursor + 4])[0]
        kind = raw[cursor + 4 : cursor + 8]
        end = cursor + 12 + length
        if end > len(raw):
            raise ValueError("truncated PNG payload")
        payload = raw[cursor + 8 : cursor + 8 + length]
        expected_crc = struct.unpack(">I", raw[cursor + 8 + length : end])[0]
        actual_crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"invalid PNG CRC for {kind!r}")
        chunks.append(kind)
        payloads.setdefault(kind, []).append(payload)
        cursor = end
        if kind == b"IEND":
            break
    if cursor != len(raw):
        raise ValueError("trailing bytes after PNG IEND")
    if tuple(chunks) != PNG_CHUNK_CONTRACT:
        raise ValueError(
            "PNG chunk contract requires only IHDR, PLTE, IDAT, IEND "
            f"but found {chunks!r}"
        )
    ihdr = payloads[b"IHDR"][0]
    if len(ihdr) != 13:
        raise ValueError("invalid PNG IHDR length")
    width, height, depth, color, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )
    if (width, height) != (WIDTH, HEIGHT):
        raise ValueError(
            f"source fixture dimensions must be {WIDTH}x{HEIGHT}: {width}x{height}"
        )
    if (depth, color, compression, filtering, interlace) != (8, 3, 0, 0, 0):
        raise ValueError("source fixture has an unsupported PNG encoding")
    expected_palette = bytes(component for entry in PALETTE for component in entry)
    if payloads[b"PLTE"][0] != expected_palette:
        raise ValueError("source fixture palette is not canonical")
    try:
        scanlines = zlib.decompress(payloads[b"IDAT"][0])
    except zlib.error as exc:
        raise ValueError("source fixture PNG pixels do not decompress") from exc
    expected_scanline_size = HEIGHT * (1 + WIDTH)
    if len(scanlines) != expected_scanline_size:
        raise ValueError("source fixture PNG pixel length is invalid")
    row_size = 1 + WIDTH
    if any(scanlines[row * row_size] != 0 for row in range(HEIGHT)):
        raise ValueError("source fixture PNG uses a noncanonical row filter")
    return {
        "width": width,
        "height": height,
        "bit_depth": depth,
        "color_type": color,
        "chunks": tuple(kind.decode("ascii") for kind in chunks),
        "metadata_free": True,
        "pixel_sha256": hashlib.sha256(scanlines).hexdigest(),
    }


def _validated_directory(frames_dir: Path) -> Path:
    try:
        resolved = frames_dir.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"canonical fixture directory does not exist: {frames_dir}") from exc
    if frames_dir.is_symlink() or not resolved.is_dir():
        raise ValueError(f"canonical fixture path is not a regular directory: {frames_dir}")
    return resolved


def validate_fixture_directory(frames_dir: Path = FRAMES) -> list[tuple[Path, str, int]]:
    """Validate exact membership, format, ownership, and unique source bytes."""

    directory = _validated_directory(frames_dir)
    entries = sorted(directory.iterdir(), key=lambda path: (path.name.casefold(), path.name))
    actual_names = [path.name for path in entries]
    if actual_names != list(CANONICAL_NAMES):
        missing = sorted(set(CANONICAL_NAMES) - set(actual_names))
        unexpected = sorted(set(actual_names) - set(CANONICAL_NAMES))
        raise ValueError(
            f"canonical fixture set must contain exactly {FRAME_COUNT} owned PNG files; "
            f"missing={missing}, unexpected={unexpected}"
        )

    records: list[tuple[Path, str, int]] = []
    hashes: dict[str, Path] = {}
    for index, path in enumerate(entries, start=1):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"canonical fixture is not a regular file: {path}")
        raw = path.read_bytes()
        properties = inspect_png(raw)
        expected_pixels = _pack_scanlines(_fixture_pixels(index), bit_depth=8)
        if properties["pixel_sha256"] != hashlib.sha256(expected_pixels).hexdigest():
            raise ValueError(
                f"canonical fixture ownership mismatch for {path.name}; "
                f"recreate it with {Path(__file__).name}"
            )
        digest = hashlib.sha256(raw).hexdigest()
        previous = hashes.get(digest)
        if previous is not None:
            raise ValueError(
                f"canonical fixtures must have unique content: {previous.name}, {path.name}"
            )
        hashes[digest] = path
        records.append((path, digest, len(raw)))
    if len(records) != FRAME_COUNT or len(hashes) != FRAME_COUNT:
        raise ValueError("canonical fixture count or unique-content invariant failed")
    return records


def _validate_output_path(frames_dir: Path, root: Path) -> Path:
    root_resolved = root.resolve(strict=True)
    root_lexical = Path(os.path.abspath(root))
    output = Path(os.path.abspath(frames_dir))
    try:
        relative = output.relative_to(root_lexical)
    except ValueError as exc:
        raise ValueError(f"fixture output is outside repository root: {frames_dir}") from exc
    cursor = root_lexical
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"fixture output must not traverse a symlink: {cursor}")
        if cursor.exists() and not cursor.is_dir():
            raise ValueError(f"fixture output component is not a directory: {cursor}")
    existing = output
    while not existing.exists() and existing != root_lexical:
        existing = existing.parent
    try:
        existing.resolve(strict=True).relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise ValueError(f"fixture output resolves outside repository root: {frames_dir}") from exc
    return output


def _replace_atomically(contents: Iterable[tuple[Path, bytes]]) -> None:
    staged: list[tuple[Path, Path]] = []
    try:
        for target, raw in contents:
            descriptor, name = tempfile.mkstemp(
                prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
            )
            temporary = Path(name)
            os.fchmod(descriptor, 0o644)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((temporary, target))
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _ in staged:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def rebuild(
    *,
    root: Path = ROOT,
    frames_dir: Path = FRAMES,
) -> list[tuple[Path, str, int]]:
    """Create missing canonical files after a mutation-free full preflight."""

    output = _validate_output_path(frames_dir, root)
    expected = {
        name: expected_fixture_bytes(index)
        for index, name in enumerate(CANONICAL_NAMES, start=1)
    }
    expected_hashes = {hashlib.sha256(raw).hexdigest() for raw in expected.values()}
    if len(expected) != FRAME_COUNT or len(expected_hashes) != FRAME_COUNT:
        raise ValueError("generated fixture count or unique-content preflight failed")
    for index, name in enumerate(CANONICAL_NAMES, start=1):
        properties = inspect_png(expected[name])
        expected_pixels = _pack_scanlines(_fixture_pixels(index), bit_depth=8)
        if properties["pixel_sha256"] != hashlib.sha256(expected_pixels).hexdigest():
            raise ValueError(f"generated fixture ownership preflight failed: {name}")
    existing_entries = list(output.iterdir()) if output.exists() else []
    unexpected = sorted(path.name for path in existing_entries if path.name not in expected)
    if unexpected:
        raise ValueError(f"unexpected path in canonical fixture directory: {unexpected}")

    replacements: list[tuple[Path, bytes]] = []
    for index, name in enumerate(CANONICAL_NAMES, start=1):
        target = output / name
        if not target.exists():
            replacements.append((target, expected[name]))
            continue
        if target.is_symlink() or not target.is_file():
            raise ValueError(f"canonical fixture target is not a regular file: {target}")
        existing = target.read_bytes()
        if existing == expected[name] and (target.stat().st_mode & 0o777) == 0o644:
            continue
        if existing == expected[name]:
            replacements.append((target, expected[name]))
            continue
        if existing == _legacy_4bit_fixture_bytes(index):
            replacements.append((target, expected[name]))
            continue
        try:
            properties = inspect_png(existing)
        except ValueError as exc:
            raise ValueError(
                f"refusing to overwrite noncanonical fixture bytes: {target}"
            ) from exc
        expected_pixels = _pack_scanlines(_fixture_pixels(index), bit_depth=8)
        if properties["pixel_sha256"] == hashlib.sha256(expected_pixels).hexdigest():
            replacements.append((target, expected[name]))
            continue
        if existing != expected[name]:
            raise ValueError(f"refusing to overwrite noncanonical fixture bytes: {target}")

    output.mkdir(parents=True, exist_ok=True)
    _replace_atomically(replacements)
    records = validate_fixture_directory(output)
    print(f"validated {len(records)} canonical metadata-free PNG fixtures in {output}")
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate without creating missing canonical fixture files",
    )
    args = parser.parse_args()
    records = validate_fixture_directory(FRAMES) if args.check else rebuild()
    if args.check:
        print(f"validated {len(records)} canonical metadata-free PNG fixtures in {FRAMES}")


if __name__ == "__main__":
    main()
