# API Response Structure Documentation

This document describes the standardized response structure used throughout the Chatbot Control Panel Backend API.

## Overview

All API responses follow a consistent structure to provide clarity, consistency, and ease of use for frontend applications and API consumers.

## Response Structure

### Base Response Interface

```typescript
interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
  error?: string;
  errors?: string[];
  timestamp: string;
}
```

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | `'success' \| 'error'` | ✅ | Indicates whether the request was successful or failed |
| `message` | `string` | ❌ | Human-readable message describing the result |
| `data` | `T` | ❌ | Response data (only present in success responses) |
| `error` | `string` | ❌ | Error message (only present in error responses) |
| `errors` | `string[]` | ❌ | Array of detailed error messages (validation errors) |
| `timestamp` | `string` | ✅ | ISO 8601 timestamp when the response was generated |

## Response Types

### 1. Success Response with Data

Used for successful operations that return data (GET requests, POST requests that create resources).

```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "admin",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 2. Success Response with Message Only

Used for successful operations that don't return data (DELETE requests, status updates).

```json
{
  "status": "success",
  "message": "Division deleted successfully",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 3. Error Response

Used for failed operations with a single error message.

```json
{
  "status": "error",
  "error": "Division not found",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 4. Validation Error Response

Used for validation failures with detailed error information.

```json
{
  "status": "error",
  "error": "Validation error: username is required",
  "errors": [
    "username is required",
    "password must be at least 6 characters long"
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## HTTP Status Codes

The API uses standard HTTP status codes along with the response structure:

### Success Codes
- `200 OK` - Successful GET, PUT, PATCH requests
- `201 Created` - Successful POST requests that create resources
- `204 No Content` - Successful DELETE requests (rarely used, prefer 200 with message)

### Error Codes
- `400 Bad Request` - Validation errors, malformed requests
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Authentication successful but insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate names)
- `500 Internal Server Error` - Server errors

## Implementation

### ResponseHandler Utility

The API uses a `ResponseHandler` utility class to ensure consistent responses:

```typescript
import { ResponseHandler } from '../utils/response';

// Success with data
return ResponseHandler.success(res, userData, 'User retrieved successfully');

// Success with message only
return ResponseHandler.successMessage(res, 'User deleted successfully');

// Created resource
return ResponseHandler.created(res, newUser, 'User created successfully');

// Error responses
return ResponseHandler.notFound(res, 'User not found');
return ResponseHandler.validationError(res, 'Invalid input', ['username is required']);
```

### Available Methods

| Method | Status Code | Use Case |
|--------|-------------|----------|
| `success(res, data, message?, statusCode?)` | 200 | Successful operations with data |
| `successMessage(res, message, statusCode?)` | 200 | Successful operations without data |
| `created(res, data, message?)` | 201 | Resource creation |
| `validationError(res, error, errors?)` | 400 | Input validation failures |
| `unauthorized(res, error?)` | 401 | Authentication failures |
| `forbidden(res, error?)` | 403 | Permission denied |
| `notFound(res, error?)` | 404 | Resource not found |
| `conflict(res, error)` | 409 | Resource conflicts |
| `internalError(res, error?)` | 500 | Server errors |

## Examples by Endpoint

### Authentication Endpoints

#### POST /api/v1/auth/register
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "admin",
      "role": "admin"
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### POST /api/v1/auth/login
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "admin",
      "role": "admin"
    }
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Division Management

#### GET /api/v1/divisions
```json
{
  "status": "success",
  "message": "Divisions retrieved successfully",
  "data": [
    {
      "id": "456e7890-e12b-34c5-d678-901234567890",
      "name": "Engineering",
      "description": "Engineering team documents",
      "is_active": true,
      "created_at": "2024-01-01T12:00:00.000Z",
      "updated_at": "2024-01-01T12:00:00.000Z"
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### DELETE /api/v1/divisions/:id
```json
{
  "status": "success",
  "message": "Division deactivated successfully",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Error Examples

#### 404 Not Found
```json
{
  "status": "error",
  "error": "Division not found",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### 400 Validation Error
```json
{
  "status": "error",
  "error": "Validation error: name is required",
  "errors": [
    "name is required",
    "name must be at least 1 character long"
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### 401 Unauthorized
```json
{
  "status": "error",
  "error": "Access token required",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Frontend Integration

### JavaScript/TypeScript

```typescript
interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
  error?: string;
  errors?: string[];
  timestamp: string;
}

// Handling responses
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const result: ApiResponse = await response.json();

if (result.status === 'success') {
  console.log('Success:', result.message);
  console.log('Data:', result.data);
} else {
  console.error('Error:', result.error);
  if (result.errors) {
    console.error('Details:', result.errors);
  }
}
```

### React Hook Example

```typescript
const useApiCall = <T>() => {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const callApi = async (url: string, options?: RequestInit) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url, options);
      const result: ApiResponse<T> = await response.json();

      if (result.status === 'success') {
        setData(result.data || null);
      } else {
        setError(result.error || 'Unknown error');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return { data, error, loading, callApi };
};
```

## Testing

### Test Helpers

Use the provided test helpers for consistent testing:

```typescript
import { expectSuccessResponse, expectErrorResponse } from '../helpers/responseHelpers';

// Test success response
const response = await request(app).get('/api/v1/divisions');
const result = expectSuccessResponse(response, 200, 'Divisions retrieved successfully');
expect(result.data).toHaveLength(2);

// Test error response
const errorResponse = await request(app).get('/api/v1/divisions/invalid-id');
expectErrorResponse(errorResponse, 404, 'Division not found');
```

## Migration Guide

### From Old Structure

If you're migrating from the old response structure:

**Old:**
```json
{
  "id": "123",
  "username": "admin"
}
```

**New:**
```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "id": "123",
    "username": "admin"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Frontend Changes Required

1. **Access data through `data` property:**
   ```typescript
   // Old: const user = response.body;
   const user = response.body.data;
   ```

2. **Check status before accessing data:**
   ```typescript
   if (response.body.status === 'success') {
     const user = response.body.data;
   }
   ```

3. **Handle errors consistently:**
   ```typescript
   if (response.body.status === 'error') {
     console.error(response.body.error);
   }
   ```

## Benefits

1. **Consistency** - All endpoints use the same response structure
2. **Error Handling** - Standardized error format makes error handling easier
3. **Debugging** - Timestamps help with debugging and logging
4. **Validation** - Detailed validation errors improve user experience
5. **Type Safety** - TypeScript interfaces provide compile-time checking
6. **Future-Proof** - Easy to extend with additional fields if needed

## Best Practices

1. **Always use ResponseHandler** - Don't manually create response objects
2. **Provide meaningful messages** - Include descriptive success/error messages
3. **Use appropriate status codes** - Match HTTP status codes to the situation
4. **Include timestamps** - Automatically handled by ResponseHandler
5. **Validate response structure in tests** - Use provided test helpers
6. **Handle both success and error cases** - Frontend should handle both scenarios
