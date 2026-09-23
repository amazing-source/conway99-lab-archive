param(
    [switch]$CompareRecorded
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http

$auditDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$resultsPath = Join-Path $auditDir 'results.json'

$targets = @(
    [pscustomobject]@{
        Id = 'B01'
        Url = 'https://aeb.win.tue.nl/graphs/srg/srgtab.html'
        MatrixPattern = $null
    },
    [pscustomobject]@{
        Id = 'B02'
        Url = 'https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html'
        MatrixPattern = $null
    },
    [pscustomobject]@{
        Id = 'B03'
        Url = 'https://assets.cambridge.org/97813165/12036/index/9781316512036_index.pdf'
        MatrixPattern = $null
    },
    [pscustomobject]@{
        Id = 'M01'
        Url = 'https://45acc.github.io/slides/McKay.pdf'
        MatrixPattern = $null
    },
    [pscustomobject]@{
        Id = 'R01'
        Url = 'https://www.math.uniri.hr/~sanjar/structures/'
        MatrixPattern = $null
    },
    [pscustomobject]@{
        Id = 'R02'
        Url = 'https://www.math.uniri.hr/~sanjar/structures/0_README_the_content_of_folders_and_references.txt'
        MatrixPattern = $null
    },
    [pscustomobject]@{
        Id = 'R03'
        Url = 'https://www.math.uniri.hr/~sanjar/structures/FOLDER1%202-%2871%2C15%2C3%29%20designs/'
        MatrixPattern = 'href="D(\d+)\.MAT"'
    },
    [pscustomobject]@{
        Id = 'R04'
        Url = 'https://www.math.uniri.hr/~sanjar/structures/FOLDER2%202-%2815%2C3%2C2%29%20designs/'
        MatrixPattern = 'href="d(\d+)\.mat"'
    }
)

$recordedById = @{}
if ($CompareRecorded) {
    $recorded = Get-Content -LiteralPath $resultsPath -Raw | ConvertFrom-Json
    foreach ($item in $recorded.remote_resources) {
        $recordedById[$item.id] = $item
    }
}

$handler = [System.Net.Http.HttpClientHandler]::new()
$client = [System.Net.Http.HttpClient]::new($handler)
$client.DefaultRequestHeaders.UserAgent.ParseAdd(
    'Wave34ExternalSourceAudit/1.0'
)

try {
    $observed = foreach ($target in $targets) {
        $response = $client.GetAsync($target.Url).GetAwaiter().GetResult()
        $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()

        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hash = (
                [System.BitConverter]::ToString($sha.ComputeHash($bytes))
            ).Replace('-', '').ToLowerInvariant()
        }
        finally {
            $sha.Dispose()
        }

        $record = [ordered]@{
            id = $target.Id
            url = $target.Url
            accessed_at_utc = (
                [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
            )
            http_status = [int]$response.StatusCode
            response_body_bytes = $bytes.Length
            response_body_sha256 = $hash
            matrix_link_count = $null
            matrix_number_minimum = $null
            matrix_number_maximum = $null
            matrix_sequence_complete = $null
            matrix_duplicate_count = $null
            matches_recorded_bytes = $null
            matches_recorded_sha256 = $null
        }

        if ($null -ne $target.MatrixPattern) {
            $html = [System.Text.Encoding]::UTF8.GetString($bytes)
            $numbers = @(
                [regex]::Matches($html, $target.MatrixPattern) |
                    ForEach-Object { [int]$_.Groups[1].Value }
            )
            $unique = @($numbers | Sort-Object -Unique)
            $record.matrix_link_count = $numbers.Count
            $record.matrix_number_minimum = $unique[0]
            $record.matrix_number_maximum = $unique[-1]
            $record.matrix_sequence_complete = (
                $unique.Count -eq ($unique[-1] - $unique[0] + 1)
            )
            $record.matrix_duplicate_count = $numbers.Count - $unique.Count
        }

        if ($CompareRecorded) {
            $expected = $recordedById[$target.Id]
            if ($null -eq $expected) {
                throw "No recorded remote resource for $($target.Id)"
            }
            $record.matches_recorded_bytes = (
                $bytes.Length -eq [int64]$expected.response_body_bytes
            )
            $record.matches_recorded_sha256 = (
                $hash -eq [string]$expected.response_body_sha256
            )
        }

        [pscustomobject]$record
    }
}
finally {
    $client.Dispose()
    $handler.Dispose()
}

$observed | ConvertTo-Json -Depth 4
