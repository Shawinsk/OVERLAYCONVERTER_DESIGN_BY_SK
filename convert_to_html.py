import json
import os

# Configuration
INPUT_FILE = r'd:/works/MY project/secret/pulse overlay/pulse.json'
OUTPUT_DIR = r'd:/works/MY project/secret/pulse overlay/web_overlay'
ASSETS_DIR = r'd:/works/MY project/secret/pulse overlay'
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_html(data):
    items = data.get('scenes', {}).get('items', [])[0].get('slots', {}).get('items', [])
    
    html_elements = []
    
    # Sort items by some z-index if available, or just list order (usually bottom to top in JSON = back to front?)
    # In OBS, top of list is top layer? Or bottom?
    # Usually list index 0 is bottom? Let's assume painter's algorithm (later items on top) unless z-order specified.
    # We will verify this.
    
    for item in items:
        if item.get('sceneNodeType') != 'item' or not item.get('visible', True):
            continue
            
        # Basic properties
        name = item.get('name', 'element')
        x_pct = item.get('x', 0)
        y_pct = item.get('y', 0)
        
        # Convert to pixels
        left = x_pct * CANVAS_WIDTH
        top = y_pct * CANVAS_HEIGHT
        
        content = item.get('content', {})
        node_type = content.get('nodeType')
        
        style = f"position: absolute; left: {left}px; top: {top}px;"
        
        # Transforms?
        # rotation = item.get('rotation', 0)
        # if rotation:
        #    style += f" transform: rotate({rotation}deg);"
        
        element_html = ""
        
        if node_type == 'ImageNode':
            filename = content.get('filename')
            if filename:
                element_html = f'<img src="{filename}" style="{style}" alt="{name}">'
        
        elif node_type == 'VideoNode':
            filename = content.get('filename')
            if filename:
                loop = 'loop' if content.get('settings', {}).get('looping', True) else ''
                element_html = f'<video src="{filename}" {loop} autoplay muted playsinline style="{style}"></video>'
                
        elif node_type == 'TextNode' or node_type == 'StreamlabelNode':
            # Handle text
            text_source = content.get('textSource', content) if node_type == 'StreamlabelNode' else content
            settings = text_source.get('settings', {})
            text_content = settings.get('text', 'TEXT')
            
            # Font
            font = settings.get('font', {})
            font_size = font.get('size', 16)
            font_family = font.get('face', 'Arial')
            
            # Color
            # Color is often an integer. format: 0xBBGGRR or similar?
            # Or decimal representation.
            color_int = settings.get('color', 16777215)
            # 16777215 is FFFFFF (White).
            b = (color_int >> 16) & 0xFF
            g = (color_int >> 8) & 0xFF
            r = color_int & 0xFF
            # Note: OBS sometimes uses BGR or RGB. 16777215 is all ones, so order doesn't matter for white.
            # Let's assume RGB for now, or check typical JSON format.
            # Actually, standard integer color often BGR in Windowish contexts.
            # Let's try RGB first.
            
            # wait, 16777215 = 0xFFFFFF.
            hex_color = f"#{r:02x}{g:02x}{b:02x}" # Assuming RGB per byte extraction?
            # Actually if it is BGR:
            # r = color_int & 0xFF
            # g = (color_int >> 8) & 0xFF
            # b = (color_int >> 16) & 0xFF
            
            # Opacity
            opacity = settings.get('opacity', 100) / 100.0
            
            font_style = f"font-family: '{font_family}', sans-serif; font-size: {font_size}px; color: {hex_color}; opacity: {opacity};"
            
            # Alignment?
            # If align is center, we might need transform translate.
            
            element_html = f'<div style="{style} {font_style} white-space: nowrap;">{text_content}</div>'
            
        elif node_type == 'WebcamNode':
             # Placeholder for webcam
             w = content.get('width', 0) * CANVAS_WIDTH # ??? content.width is normalized items?
             # Pulse JSON: content.width: 0.365...
             # We should probably interpret it.
             # element_html = f'<div style="{style} width: {w}px; height: {w}px; background: rgba(0,0,0,0.5); border: 2px solid green;">WEBCAM</div>'
             # Skip webcam for overlay static file? Or add placeholder?
             # User wants "pulse.overlay to convert pulse.json" -> "convert html file".
             # Better to leave it distinct or just render the overlay parts.
             pass

        elif node_type == 'GameCaptureNode':
             # Usually background
             filename = content.get('placeholderFile')
             if filename:
                 element_html = f'<img src="{filename}" style="{style}" alt="{name}">'
        
        if element_html:
            html_elements.append(element_html)
            
    return html_elements

def main():
    ensure_dir(OUTPUT_DIR)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    elements = generate_html(data)
    
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pulse Overlay</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000; /* or transparent */
            overflow: hidden;
            width: {CANVAS_WIDTH}px;
            height: {CANVAS_HEIGHT}px;
        }}
        .overlay-container {{
            position: relative;
            width: 100%;
            height: 100%;
        }}
        /* Font faces imports usually needed */
    </style>
</head>
<body>
    <div class="overlay-container">
        {chr(10).join(elements)}
    </div>
</body>
</html>
    '''
    
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML Generated Successfully")

if __name__ == "__main__":
    main()
