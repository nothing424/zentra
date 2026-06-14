#!/usr/bin/env python3
"""
Generate Zentra PWA icons (SVG-based PNG via Pillow or pure SVG fallback)
"""

import os
import struct
import zlib

os.makedirs('icons', exist_ok=True)

sizes = [72, 96, 128, 144, 152, 192, 384, 512]

def make_png(size):
    """Create a minimal valid PNG with the Zentra Z logo"""
    # Simple gradient background with Z letter using raw PNG
    width = height = size
    
    # Create pixel data
    img_data = bytearray()
    for y in range(height):
        img_data.append(0)  # filter type: none
        for x in range(width):
            # Background gradient: #0B1020 to #12182D
            t = (x + y) / (width + height)
            r = int(11 + t * 7)
            g = int(16 + t * 8)
            b = int(32 + t * 13)
            
            # Draw Z letter
            cx = x - width // 2
            cy = y - height // 2
            margin = size * 0.25
            thick = max(1, size // 12)
            in_z = False
            
            # Top bar
            if abs(cy + height * 0.28) < thick and abs(cx) < width * 0.28:
                in_z = True
            # Bottom bar
            if abs(cy - height * 0.28) < thick and abs(cx) < width * 0.28:
                in_z = True
            # Diagonal
            if not in_z:
                # Line from top-right to bottom-left
                dx = cx - width * 0.28
                dy = cy + height * 0.28
                # Parametric: from (W*0.28, -H*0.28) to (-W*0.28, H*0.28)
                # Line equation
                lx = -width * 0.56
                ly = height * 0.56
                # Distance from point to line
                px = cx + width * 0.28
                py = cy + height * 0.28
                t2 = (px * lx + py * ly) / (lx*lx + ly*ly)
                t2 = max(0, min(1, t2))
                nx = px - t2 * lx
                ny = py - t2 * ly
                dist = (nx*nx + ny*ny) ** 0.5
                if dist < thick:
                    in_z = True
            
            if in_z:
                # Gradient blue: #4F8CFF to #7C5CFF
                fr = x / width
                pr = int(79 + fr * 45)
                pg = int(140 - fr * 56)
                pb = int(255)
                img_data.extend([pr, pg, pb, 255])
            else:
                # Slight glow from center
                dist_center = ((cx/width)**2 + (cy/height)**2) ** 0.5
                glow = max(0, 1 - dist_center * 3)
                r2 = min(255, r + int(glow * 20))
                g2 = min(255, g + int(glow * 30))
                b2 = min(255, b + int(glow * 50))
                img_data.extend([r2, g2, b2, 255])
    
    # Compress
    compressed = zlib.compress(bytes(img_data), 9)
    
    def chunk(name, data):
        c = name + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack('>I', len(data)) + c + struct.pack('>I', crc)
    
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    png = (
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', ihdr_data) +
        chunk(b'IDAT', compressed) +
        chunk(b'IEND', b'')
    )
    return png

for size in sizes:
    png_data = make_png(size)
    path = f'icons/icon-{size}.png'
    with open(path, 'wb') as f:
        f.write(png_data)
    print(f'Created {path} ({size}x{size})')

# Also create a simple screenshot placeholder
ss = make_png(390)
with open('icons/screenshot-mobile.png', 'wb') as f:
    f.write(ss)
print('Created icons/screenshot-mobile.png')
print('All icons generated!')
