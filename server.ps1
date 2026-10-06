param(
    [int]$Port = 8080
)

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Prefixes.Add("http://127.0.0.1:$Port/")
$listener.Start()
Write-Output "Web server is active at http://localhost:$Port/"

$mimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".htm"  = "text/html; charset=utf-8"
    ".css"  = "text/css; charset=utf-8"
    ".js"   = "application/javascript; charset=utf-8"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".jpeg" = "image/jpeg"
    ".svg"  = "image/svg+xml"
    ".pdf"  = "application/pdf"
    ".json" = "application/json"
    ".ico"  = "image/x-icon"
}

try {
    while ($listener.IsListening) {
        try {
            $context = $listener.GetContext()
            $request = $context.Request
            $response = $context.Response

            $rawUrl = $request.Url.LocalPath.TrimStart('/')
            if ([string]::IsNullOrWhiteSpace($rawUrl)) {
                $rawUrl = "index.html"
            }

            # Prevent directory traversal
            $filePath = Join-Path (Get-Location) $rawUrl
            $filePath = [System.IO.Path]::GetFullPath($filePath)
            $currentDir = [System.IO.Path]::GetFullPath((Get-Location))

            if ($filePath.StartsWith($currentDir) -and (Test-Path $filePath -PathType Leaf)) {
                $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
                $mime = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { "application/octet-stream" }
                $response.ContentType = $mime
                
                $bytes = [System.IO.File]::ReadAllBytes($filePath)
                $response.ContentLength64 = $bytes.Length
                $response.StatusCode = 200
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                $response.StatusCode = 404
                $msg = [System.Text.Encoding]::UTF8.GetBytes("File not found")
                $response.OutputStream.Write($msg, 0, $msg.Length)
            }

            $response.Close()
        } catch {
            # Safely handle client disconnects, socket resets, or stream aborts
        }
    }
} finally {
    if ($listener.IsListening) {
        $listener.Stop()
    }
}
