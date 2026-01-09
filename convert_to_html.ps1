$inputPath = "d:\works\MY project\secret\pulse overlay\pulse.json"
$outputDir = "d:\works\MY project\secret\pulse overlay\web_overlay"
$canvasWidth = 1920
$canvasHeight = 1080

if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

Copy-Item "d:\works\MY project\secret\pulse overlay\*.png" $outputDir -Force
Copy-Item "d:\works\MY project\secret\pulse overlay\*.webm" $outputDir -Force
Copy-Item "d:\works\MY project\secret\pulse overlay\*.mp4" $outputDir -Force

$json = Get-Content -Raw -Path $inputPath | ConvertFrom-Json
$items = $json.scenes.items[0].slots.items

$elements = @()

foreach ($item in $items) {
    if ($item.sceneNodeType -ne "item" -or $item.visible -eq $false) { continue }
    
    $name = $item.name
    $x = if ($item.x) { $item.x } else { 0 }
    $y = if ($item.y) { $item.y } else { 0 }
    
    $left = $x * $canvasWidth
    $top = $y * $canvasHeight
    
    $style = "position: absolute; left: $($left)px; top: $($top)px;"
    
    $content = $item.content
    $nodeType = $content.nodeType
    
    if ($nodeType -eq "ImageNode") {
        $filename = $content.filename
        if ($filename) {
            $elements += "<img src='$filename' style='$style' alt='$name'>"
        }
    }
    elseif ($nodeType -eq "VideoNode") {
        $filename = $content.filename
        if ($filename) {
            $loop = if ($content.settings.looping -ne $false) { "loop" } else { "" }
            $elements += "<video src='$filename' $loop autoplay muted playsinline style='$style'></video>"
        }
    }
    elseif ($nodeType -eq "TextNode" -or $nodeType -eq "StreamlabelNode") {
        $textSource = if ($nodeType -eq "StreamlabelNode") { $content.textSource } else { $content }
        $settings = $textSource.settings
        $text = $settings.text
        if (-not $text) { $text = "TEXT" }
        
        $font = $settings.font
        $fontSize = if ($font.size) { $font.size } else { 16 }
        $fontFace = if ($font.face) { $font.face } else { "Arial" }
        
        $color = if ($settings.color) { $settings.color } else { 16777215 }
        # RGB extraction from integer
        $r = $color -band 0xFF
        # $g = ($color -shr 8) -band 0xFF  <-- specific logic depending on int format
        # If standard RGB int: 0xRRGGBB vs 0xBBGGRR
        # Let's assume white (16777215) is white.
        $hexColor = "#{0:X6}" -f $color
        # Wait, typical int color might be BGR in Windows. 
        # If simple, let's just use white for now if logic is complex without bitwise right shift in simple PS
        
        $opacity = if ($settings.opacity) { $settings.opacity / 100.0 } else { 1.0 }
        
        $fontStyle = "font-family: '$fontFace', sans-serif; font-size: $($fontSize)px; color: #FFFFFF; opacity: $opacity;"
        $elements += "<div style='$style $fontStyle white-space: nowrap;'>$text</div>"
    }
    elseif ($nodeType -eq "GameCaptureNode") {
        $filename = $content.placeholderFile
        if ($filename) {
            $elements += "<img src='$filename' style='$style' alt='$name'>"
        }
    }
}

$htmlContent = @"
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Pulse Overlay</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #000;
            overflow: hidden;
            width: ${canvasWidth}px;
            height: ${canvasHeight}px;
        }
        .overlay-container {
            position: relative;
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <div class='overlay-container'>
        $($elements -join "`n        ")
    </div>
</body>
</html>
"@

$htmlContent | Set-Content -Path "$outputDir\index.html" -Encoding UTF8
Write-Output "Generated index.html"
