<#
.SYNOPSIS
    Takes a screenshot of the screen or a specific region.
    Supports interactive selection and hiding the console window.

.PARAMETER Path
    Full path to save the image (e.g., "C:\Images\screenshot.png").
    Required.

.PARAMETER Bounds
    Optional. A string in "x,y,width,height" format (e.g., "0,0,1920,1080").
    If omitted and -Interactive is NOT specified, captures the primary screen.

.PARAMETER Interactive
    Optional Switch. If set, overlays a transparent window for mouse selection.
    Overrides -Bounds if both are present.

.PARAMETER HideConsole
    Optional Switch. If set, hides the current console window before capturing.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [string]$Bounds = "",

    [switch]$Interactive,

    [switch]$HideConsole
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# --- Win32 API for Console Hiding ---
$Win32Signature = @'
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern int SetForegroundWindow(IntPtr hwnd);
'@
$Win32 = Add-Type -MemberDefinition $Win32Signature -Name "Win32Utils" -Namespace Win32 -PassThru

# Constants for ShowWindow
$SW_HIDE = 0
$SW_SHOW = 5

# --- Helper: Parse Bounds ---
function Get-RectangleFromBounds {
    param([string]$b)
    try {
        $parts = $b -split "," | ForEach-Object { [int]$_ }
        if ($parts.Count -eq 4) {
            return New-Object System.Drawing.Rectangle($parts[0], $parts[1], $parts[2], $parts[3])
        }
    } catch {}
    return $null
}

# --- Helper: Interactive Selection ---
function Get-InteractiveRectangle {
    # Create a full-screen form
    $form = New-Object System.Windows.Forms.Form
    $form.FormBorderStyle = "None"
    $form.WindowState = "Maximized"
    $form.TopMost = $true
    $form.Cursor = [System.Windows.Forms.Cursors]::Cross
    $form.ShowInTaskbar = $false
    
    # Use a specific color for transparency key
    $form.BackColor = [System.Drawing.Color]::White
    $form.TransparencyKey = [System.Drawing.Color]::White
    $form.Opacity = 0.5 # Slight dim to indicate selection mode? No, TransparencyKey makes it fully transparent.
                        # To do a "dimmed" overlay with a clear selection box is complex in pure PS WinForms.
                        # Let's stick to a simple nearly-transparent overlay that draws a red box.
    $form.Opacity = 0.3
    $form.BackColor = [System.Drawing.Color]::Black 
    # Use Black with 0.3 opacity to dim screen. We can't easily punch a hole in it with WinForms.
    # Alternative: Just draw a rectangle on top of the screen.

    # Better approach for simple "snipping":
    # Full screen, almost transparent white, draw red rectangle.
    
    $rect = New-Object System.Drawing.Rectangle(0, 0, 0, 0)
    $startPos = $null
    $drawing = $false

    $form.Add_MouseDown({
        param($sender, $e)
        if ($e.Button -eq [System.Windows.Forms.MouseButtons]::Left) {
            $script:startPos = $e.Location
            $script:drawing = $true
        }
    })

    $form.Add_MouseMove({
        param($sender, $e)
        if ($script:drawing) {
            $x = [Math]::Min($script:startPos.X, $e.X)
            $y = [Math]::Min($script:startPos.Y, $e.Y)
            $w = [Math]::Abs($e.X - $script:startPos.X)
            $h = [Math]::Abs($e.Y - $script:startPos.Y)
            $script:rect = New-Object System.Drawing.Rectangle($x, $y, $w, $h)
            $form.Invalidate()
        }
    })

    $form.Add_MouseUp({
        param($sender, $e)
        $script:drawing = $false
        $form.Close()
    })

    $form.Add_Paint({
        param($sender, $e)
        if ($script:rect.Width -gt 0) {
            $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Red, 2)
            $e.Graphics.DrawRectangle($pen, $script:rect)
            
            # Optional: Fill inside with transparent color? Not easily possible on this layer
        }
    })

    $form.Add_KeyDown({
        param($sender, $e)
        if ($e.KeyCode -eq [System.Windows.Forms.Keys]::Escape) {
            $script:rect = New-Object System.Drawing.Rectangle(0, 0, 0, 0)
            $form.Close()
        }
    })

    [void]$form.ShowDialog()
    return $script:rect
}

# --- Main Logic ---

# --- Hide Console ---
$consoleHandle = [IntPtr]::Zero
if ($HideConsole) {
    # Strategy: Assume the CLI is the currently active window when the command runs.
    $consoleHandle = $Win32::GetForegroundWindow()
    
    if ($consoleHandle -ne [IntPtr]::Zero) {
        [void]$Win32::ShowWindow($consoleHandle, $SW_HIDE)
        Start-Sleep -Milliseconds 500 # Increased delay to ensure window is fully hidden
    } else {
        Write-Warning "Could not find foreground window to hide."
    }
}

$captureRect = $null

if ($Interactive) {
    Write-Host "Please select a region on screen..."
    $captureRect = Get-InteractiveRectangle
    if ($captureRect.Width -eq 0 -or $captureRect.Height -eq 0) {
        Write-Error "Selection cancelled or invalid."
        exit 1
    }
}
elseif (-not [string]::IsNullOrWhiteSpace($Bounds)) {
    $captureRect = Get-RectangleFromBounds $Bounds
    if ($null -eq $captureRect) {
        Write-Error "Invalid bounds format. Use 'x,y,w,h'."
        exit 1
    }
}
else {
    # Default: Full Screen (Primary Screen)
    $captureRect = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
}

try {
    # --- Capture ---
    $bmp = New-Object System.Drawing.Bitmap($captureRect.Width, $captureRect.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bmp)
    
    $graphics.CopyFromScreen($captureRect.Location, [System.Drawing.Point]::Empty, $captureRect.Size)
    
    # --- Save ---
    # Ensure directory exists
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    
    $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "Screenshot saved to: $Path"

}
catch {
    Write-Error "Failed to capture screenshot: $_"
}
finally {
    # Cleanup
    if ($graphics) { $graphics.Dispose() }
    if ($bmp) { $bmp.Dispose() }

    # --- Restore Console ---
    if ($HideConsole -and $consoleHandle -ne [IntPtr]::Zero) {
        [void]$Win32::ShowWindow($consoleHandle, $SW_SHOW)
        [void]$Win32::SetForegroundWindow($consoleHandle)
    }
}
