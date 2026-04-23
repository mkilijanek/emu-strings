# Emu-Strings API Documentation

> **Version**: 1.1.0  
> **Last Updated**: 2026-04-23

## Base URL

```
http://localhost:64205/
```

## Authentication

Currently, the API does not require authentication. Rate limiting is applied to prevent abuse.

## Rate Limiting

- **Submit endpoint**: 10 requests per minute per IP
- **Other endpoints**: No rate limiting currently applied

## Health Checks

### GET /health

Liveness probe - returns 200 if the application is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "emu-strings"
}
```

**Status Codes**:
- `200` - Service is healthy

### GET /ready

Readiness probe - checks if all dependencies are available.

**Response (Success)**:
```json
{
  "status": "ready",
  "checks": {
    "mongodb": "ok",
    "redis": "ok"
  }
}
```

**Response (Failure)**:
```json
{
  "status": "not ready",
  "checks": {
    "mongodb": "error: Connection refused"
  }
}
```

**Status Codes**:
- `200` - All dependencies are available
- `503` - One or more dependencies are unavailable

## Analysis Endpoints

### POST /api/submit

Submit a new file for analysis.

**Request**:
- **Content-Type**: `multipart/form-data`
- **Max File Size**: 10MB (configurable via `MAX_FILE_SIZE` env var)

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | The script file to analyze |
| options | JSON | No | Analysis options |

**Options Object**:
```json
{
  "language": "auto-detect|jscript|vbscript|jscript.encode|vbscript.encode",
  "soft_timeout": 120,
  "hard_timeout": 150
}
```

**Response (Success)**:
```json
{
  "aid": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (Error)**:
```json
{
  "error": "File not specified"
}
```

**Status Codes**:
- `200` - Analysis submitted successfully
- `400` - Bad request (missing file)
- `413` - File too large (exceeds MAX_FILE_SIZE)
- `429` - Rate limit exceeded
- `500` - Internal server error

**Example**:
```bash
curl -X POST \
  http://localhost:64205/api/submit \
  -F "file=@/path/to/script.js" \
  -F 'options={"language": "auto-detect"}'
```

### GET /api/analysis

List all analyses with pagination.

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| lastId | string | No | ID of the last analysis for pagination |

**Response**:
```json
[
  {
    "_id": "550e8400e29b41d4a7164466",
    "aid": "550e8400-e29b-41d4-a716-446655440000",
    "sample": {
      "name": "script.js",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "language": "JScript"
    },
    "status": "success",
    "timestamp": "2026-04-23T10:00:00"
  }
]
```

**Status Codes**:
- `200` - Success

### GET /api/analysis/{aid}

Get detailed information about a specific analysis.

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| aid | UUID | Yes | Analysis ID |

**Response**:
```json
{
  "sample": {
    "name": "script.js",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "language": "JScript"
  },
  "status": "success",
  "timestamp": "2026-04-23T10:00:00",
  "results": {
    "strings": ["ActiveXObject", "WScript.Shell"],
    "urls": ["http://example.com"],
    "snippets": {}
  },
  "options": {
    "language": "auto-detect",
    "soft_timeout": 120,
    "hard_timeout": 150
  }
}
```

**Status Codes**:
- `200` - Success
- `400` - Invalid UUID format

### GET /api/analysis/{aid}/{key}/{identifier}

Retrieve a specific artifact from an analysis.

**Security Note**: This endpoint is protected against path traversal attacks. Keys and identifiers are validated and sanitized.

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| aid | UUID | Yes | Analysis ID |
| key | string | Yes | Artifact key (e.g., "snippets", "logfiles") |
| identifier | string | Yes | Artifact identifier |

**Response**: Binary data (file contents)

**Status Codes**:
- `200` - Success
- `400` - Invalid UUID or path traversal attempt
- `404` - Analysis or artifact not found

**Valid Keys**:
- `snippets` - Code snippets extracted during analysis
- `logfiles` - Emulator log files
- `urls` - Extracted URLs

## Security Considerations

### Input Validation

All user inputs are validated:

1. **UUID Validation**: Analysis IDs must be valid UUID format
2. **Path Sanitization**: File paths cannot contain `..` or path separators
3. **Filename Sanitization**: Uploaded filenames are sanitized
4. **Size Limits**: File uploads are limited to 10MB by default

### Rate Limiting

The submit endpoint is rate-limited to prevent abuse:
- 10 requests per minute per IP address
- Returns HTTP 429 when limit exceeded

## Error Handling

All errors return a JSON response with an `error` field:

```json
{
  "error": "Description of the error"
}
```

Common error status codes:
- `400` - Bad Request (validation error)
- `404` - Not Found
- `413` - Payload Too Large
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable (readiness check failed)

## Data Types

### Analysis Status

| Status | Description |
|--------|-------------|
| `pending` | Analysis queued but not started |
| `in-progress` | Analysis is running |
| `success` | Analysis completed successfully |
| `failed` | Analysis failed |
| `orphaned` | Analysis was orphaned |

### Sample Language

| Language | Description |
|----------|-------------|
| `JScript` | JavaScript for Windows |
| `VBScript` | Visual Basic Script |
| `JScript.Encode` | Encoded JScript (.jse) |
| `VBScript.Encode` | Encoded VBScript (.vbe) |

## Changelog

### v1.1.0 (2026-04-23)
- Added `/health` endpoint for liveness checks
- Added `/ready` endpoint for readiness checks
- Added file upload size limits (10MB default)
- Added rate limiting for submit endpoint
- Added path traversal protection
- Removed MD5 hashing (using SHA256 only)

### v1.0.0
- Initial API release
