<#
.SYNOPSIS
Independently validates an srg-edge-list-v1 certificate using exact arithmetic.

.DESCRIPTION
This implementation is intentionally separate from check_srg.py. It parses the
JSON certificate itself and checks every degree and common-neighbor count using
.NET HashSet instances. Exit code 0 means valid, 1 means mathematically invalid,
and 2 means malformed input or an execution error.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Certificate,

    [int]$Vertices = 99,
    [int]$Degree = 14,
    [int]$AdjacentCommon = 1,
    [int]$NonadjacentCommon = 2,
    [int]$MaxErrors = 20
)

$ErrorActionPreference = 'Stop'

function Test-JsonInteger {
    param([object]$Value)

    return (
        ($Value -is [sbyte]) -or
        ($Value -is [byte]) -or
        ($Value -is [int16]) -or
        ($Value -is [uint16]) -or
        ($Value -is [int32]) -or
        ($Value -is [uint32]) -or
        ($Value -is [int64]) -or
        ($Value -is [uint64])
    )
}

function Stop-Malformed {
    param([string]$Message)

    [Console]::Error.WriteLine("malformed certificate: $Message")
    exit 2
}

function Get-TopLevelJsonPropertyNames {
    param([string]$Json)

    $names = New-Object 'System.Collections.Generic.List[string]'
    $objectDepth = 0
    $arrayDepth = 0
    $inString = $false
    $escaped = $false
    $tokenStart = -1

    for ($index = 0; $index -lt $Json.Length; $index++) {
        $character = $Json[$index]
        if ($inString) {
            if ($escaped) {
                $escaped = $false
                continue
            }
            if ($character -eq '\') {
                $escaped = $true
                continue
            }
            if ($character -eq '"') {
                $inString = $false
                if (($objectDepth -eq 1) -and ($arrayDepth -eq 0)) {
                    $next = $index + 1
                    while (($next -lt $Json.Length) -and [char]::IsWhiteSpace($Json[$next])) {
                        $next++
                    }
                    if (($next -lt $Json.Length) -and ($Json[$next] -eq ':')) {
                        $rawName = $Json.Substring($tokenStart, $index - $tokenStart + 1)
                        try {
                            $decodedName = $rawName | ConvertFrom-Json
                        } catch {
                            Stop-Malformed "invalid JSON property name: $($_.Exception.Message)"
                        }
                        [void]$names.Add([string]$decodedName)
                    }
                }
            }
            continue
        }

        if ($character -eq '"') {
            $inString = $true
            $tokenStart = $index
        } elseif ($character -eq '{') {
            $objectDepth++
        } elseif ($character -eq '}') {
            $objectDepth--
        } elseif ($character -eq '[') {
            $arrayDepth++
        } elseif ($character -eq ']') {
            $arrayDepth--
        }
    }

    return $names.ToArray()
}

if ($Vertices -lt 1) {
    Stop-Malformed 'Vertices must be positive'
}
if (($Degree -lt 0) -or ($Degree -ge $Vertices)) {
    Stop-Malformed 'Degree must lie in [0, Vertices)'
}
if (($AdjacentCommon -lt 0) -or ($NonadjacentCommon -lt 0)) {
    Stop-Malformed 'common-neighbor parameters must be nonnegative'
}
if ($MaxErrors -lt 0) {
    Stop-Malformed 'MaxErrors must be nonnegative'
}

try {
    $resolvedPath = (Resolve-Path -LiteralPath $Certificate).Path
    $rawJson = Get-Content -Raw -LiteralPath $resolvedPath
    $data = $rawJson | ConvertFrom-Json
} catch {
    Stop-Malformed $_.Exception.Message
}

if ($null -eq $data) {
    Stop-Malformed 'certificate root must be a JSON object'
}

$requiredProperties = @('format', 'vertices', 'edges')
$topLevelProperties = @(Get-TopLevelJsonPropertyNames $rawJson)
$actualProperties = @($data.PSObject.Properties.Name)
foreach ($property in $requiredProperties) {
    $occurrences = @($topLevelProperties | Where-Object { $_ -ceq $property }).Count
    if ($occurrences -eq 0) {
        Stop-Malformed "missing certificate key: $property"
    }
    if ($occurrences -gt 1) {
        Stop-Malformed "duplicate JSON object key: $property"
    }
    if ($actualProperties -cnotcontains $property) {
        Stop-Malformed "missing certificate key: $property"
    }
}
foreach ($property in $topLevelProperties) {
    if ($requiredProperties -cnotcontains $property) {
        Stop-Malformed "unknown certificate key: $property"
    }
}

if ($data.format -cne 'srg-edge-list-v1') {
    Stop-Malformed "format must be exactly 'srg-edge-list-v1'"
}
if (-not (Test-JsonInteger $data.vertices)) {
    Stop-Malformed 'vertices must be an integer'
}
$certificateVertices = [int]$data.vertices
if ($certificateVertices -ne $Vertices) {
    [Console]::Error.WriteLine(
        "invalid certificate: declares $certificateVertices vertices, expected $Vertices"
    )
    exit 1
}
if ($data.edges -isnot [System.Array]) {
    Stop-Malformed 'edges must be a JSON array'
}

$adjacency = @()
for ($vertex = 0; $vertex -lt $Vertices; $vertex++) {
    $adjacency += ,(New-Object 'System.Collections.Generic.HashSet[int]')
}
$seen = @{}
$edgeCount = 0

foreach ($edge in $data.edges) {
    if (($edge -isnot [System.Array]) -or ($edge.Count -ne 2)) {
        Stop-Malformed "edge $edgeCount must be a two-element JSON array"
    }
    if ((-not (Test-JsonInteger $edge[0])) -or (-not (Test-JsonInteger $edge[1]))) {
        Stop-Malformed "edge $edgeCount endpoints must be integers"
    }
    $u = [int]$edge[0]
    $v = [int]$edge[1]
    if (($u -lt 0) -or ($u -ge $Vertices) -or ($v -lt 0) -or ($v -ge $Vertices)) {
        Stop-Malformed "edge $edgeCount endpoint is outside [0, $Vertices)"
    }
    if ($u -eq $v) {
        Stop-Malformed "edge $edgeCount is a self-loop at vertex $u"
    }
    if ($u -gt $v) {
        $temporary = $u
        $u = $v
        $v = $temporary
    }
    $key = "$u,$v"
    if ($seen.ContainsKey($key)) {
        Stop-Malformed "duplicate undirected edge ($u, $v)"
    }
    $seen[$key] = $true
    [void]$adjacency[$u].Add($v)
    [void]$adjacency[$v].Add($u)
    $edgeCount++
}

$failureCount = 0
$shownErrors = New-Object 'System.Collections.Generic.List[string]'

function Add-Failure {
    param([string]$Message)

    $script:failureCount++
    if ($script:shownErrors.Count -lt $MaxErrors) {
        [void]$script:shownErrors.Add($Message)
    }
}

for ($u = 0; $u -lt $Vertices; $u++) {
    $actualDegree = $adjacency[$u].Count
    if ($actualDegree -ne $Degree) {
        Add-Failure "degree[$u]=$actualDegree, expected $Degree"
    }
}

for ($u = 0; $u -lt $Vertices; $u++) {
    for ($v = $u + 1; $v -lt $Vertices; $v++) {
        $common = 0
        foreach ($neighbor in $adjacency[$u]) {
            if ($adjacency[$v].Contains($neighbor)) {
                $common++
            }
        }
        $adjacent = $adjacency[$u].Contains($v)
        $expected = if ($adjacent) { $AdjacentCommon } else { $NonadjacentCommon }
        if ($common -ne $expected) {
            $relation = if ($adjacent) { 'edge' } else { 'nonedge' }
            Add-Failure "common[$u,$v]=$common on $relation, expected $expected"
        }
    }
}

$valid = $failureCount -eq 0
$report = [ordered]@{
    certificate = $resolvedPath
    parameters = [ordered]@{
        vertices = $Vertices
        degree = $Degree
        lambda = $AdjacentCommon
        mu = $NonadjacentCommon
    }
    edge_count = $edgeCount
    valid = $valid
    check = [ordered]@{
        name = 'powershell_hashset_common_neighbors'
        valid = $valid
        error_count = $failureCount
        errors_shown = @($shownErrors)
    }
}

$report | ConvertTo-Json -Depth 5
if ($valid) {
    exit 0
}
exit 1
