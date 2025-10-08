# Server-Sent Events (SSE) Implementation

## Overview

This document describes the Server-Sent Events (SSE) implementation for real-time notifications about document processing status in the Chatbot Control Panel backend.

## Architecture

The SSE implementation consists of three main components:

1. **Express.js Backend** - SSE server and webhook receiver
2. **FastAPI Microservice** - Document processing and webhook sender
3. **Frontend Client** - SSE event listener

## Flow Diagram

```
Frontend Client          Express Backend          FastAPI Microservice
     |                        |                           |
     |-- SSE Connect -------->|                           |
     |<-- Connected Event ----|                           |
     |                        |                           |
     |-- Upload Document ---->|                           |
     |<-- Parsing Started ----|                           |
     |                        |-- Parse Request --------->|
     |                        |                           |-- Start Processing
     |                        |<-- Webhook Notification --|
     |<-- Parsing Complete ---|                           |
     |                        |<-- Webhook Notification --|
     |<-- Embedding Started --|                           |
     |                        |<-- Webhook Notification --|
     |<-- Processing Complete-|                           |
```

## Implementation Details

### 1. SSE Service (`sseClientService.ts`)

Enhanced SSE service with the following features:

- **Client Management**: Track connected clients with unique IDs
- **Event Broadcasting**: Send events to all clients or specific clients
- **Document Processing Events**: Specialized method for document status updates
- **Error Handling**: Automatic cleanup of disconnected clients
- **Heartbeat**: Keep connections alive with periodic heartbeats

#### Key Methods:

```typescript
// Add a new SSE client
addClient(clientId: string, response: Response)

// Remove a client
removeClient(clientId: string)

// Send event to specific client
sendEventToClient(clientId: string, event: string, payload: any)

// Send event to all clients
sendEventToAllClients(event: string, payload: any)

// Send document processing event
sendDocumentProcessingEvent(documentId: string, status: string, message: string, metadata?: any)
```

### 2. Event Controller (`eventController.ts`)

Handles SSE connections and webhook notifications:

#### SSE Endpoint: `GET /api/v1/events`

- Establishes SSE connection with unique client ID
- Sends initial connection event
- Maintains heartbeat every 30 seconds
- Handles client disconnection cleanup

#### Webhook Endpoint: `POST /api/v1/events/webhook/document-processing`

- Receives notifications from FastAPI microservice
- Validates webhook authenticity with API key
- Forwards notifications to all connected SSE clients

### 3. Document Controller Integration

Modified document upload flow to send initial SSE events:

- Sends "parsing_started" event when document upload completes
- Sends "parsing_failed" event if FastAPI call fails
- Integrates with existing document processing workflow

### 4. FastAPI Webhook Service (`webhook_service.py`)

New service for sending notifications to Express backend:

#### Key Methods:

```python
# Send general notification
send_document_processing_notification(document_id, status, message, metadata)

# Specific notification methods
notify_parsing_started(document_id, filename, file_type)
notify_parsing_completed(document_id, filename, chunk_count)
notify_embedding_started(document_id, filename)
notify_embedding_completed(document_id, filename, embedding_count)
notify_processing_failed(document_id, filename, error, stage)
```

### 5. FastAPI Integration

Modified `process_document_parsing` function to send webhook notifications at each stage:

1. **Parsing Started** - When parsing begins
2. **Parsing Completed** - When document is successfully parsed
3. **Embedding Started** - When embedding generation begins
4. **Embedding Completed** - When processing is fully complete
5. **Processing Failed** - When any stage fails

## Event Types

### SSE Events

1. **connected** - Initial connection established
2. **heartbeat** - Periodic keep-alive message
3. **document_processing** - Document status updates

### Document Processing Statuses

- `parsing_started` - Document upload complete, parsing initiated
- `parsing` - Document parsing in progress
- `parsed` - Document parsing completed
- `embedding` - Embedding generation in progress
- `embedded` - Processing completed successfully
- `failed` - Processing failed at any stage

## Configuration

### Express Backend Environment Variables

```env
INTERNAL_API_KEY=your-internal-key
FASTAPI_URL=http://localhost:8000
```

### FastAPI Environment Variables

```env
EXPRESS_API_URL=http://localhost:3000
INTERNAL_API_KEY=your-internal-key
```

## Frontend Integration

### JavaScript Example

```javascript
// Connect to SSE endpoint
const eventSource = new EventSource('/api/v1/events');

// Listen for connection event
eventSource.addEventListener('connected', function(event) {
    const data = JSON.parse(event.data);
    console.log('Connected:', data);
});

// Listen for document processing events
eventSource.addEventListener('document_processing', function(event) {
    const data = JSON.parse(event.data);
    console.log('Document processing:', data);
    
    // Update UI based on status
    switch(data.status) {
        case 'parsing_started':
            showParsingStarted(data.documentId);
            break;
        case 'parsed':
            showParsingComplete(data.documentId);
            break;
        case 'embedding':
            showEmbeddingStarted(data.documentId);
            break;
        case 'embedded':
            showProcessingComplete(data.documentId);
            break;
        case 'failed':
            showProcessingFailed(data.documentId, data.metadata.error);
            break;
    }
});

// Handle connection errors
eventSource.onerror = function(event) {
    console.error('SSE connection error:', event);
};
```

## Testing

### Manual Testing

1. **Start both services**:
   ```bash
   # Express backend
   npm run dev
   
   # FastAPI microservice
   cd fastapi-ml
   uvicorn app.main:app --reload
   ```

2. **Test SSE connection**:
   ```bash
   # Install test dependency
   npm install eventsource
   
   # Run test script
   node test-sse.js
   ```

3. **Test document upload**:
   - Upload a document through the API
   - Monitor SSE events in the test script
   - Verify webhook notifications are received

### Test Script Features

The `test-sse.js` script provides:

- SSE connection testing
- Event monitoring
- Webhook endpoint testing
- 60-second connection duration

## Security Considerations

1. **Webhook Authentication**: Uses API key validation
2. **CORS Headers**: Properly configured for SSE
3. **Client Cleanup**: Automatic removal of disconnected clients
4. **Error Handling**: Graceful handling of connection failures

## Monitoring and Logging

- All SSE connections are logged with client IDs
- Webhook notifications are logged with document IDs and status
- Error conditions are logged with detailed information
- Heartbeat events are logged at debug level

## Troubleshooting

### Common Issues

1. **SSE Connection Fails**
   - Check CORS configuration
   - Verify Express server is running
   - Check network connectivity

2. **Webhook Notifications Not Received**
   - Verify API key configuration
   - Check FastAPI service connectivity
   - Review webhook service logs

3. **Events Not Broadcasting**
   - Check SSE client connections
   - Verify webhook endpoint is accessible
   - Review Express backend logs

### Debug Commands

```bash
# Check SSE connections
curl -H "Accept: text/event-stream" http://localhost:3000/api/v1/events

# Test webhook endpoint
curl -X POST http://localhost:3000/api/v1/events/webhook/document-processing \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Key: your-internal-key" \
  -d '{"documentId":"test","status":"embedded","message":"Test"}'
```

## Future Enhancements

1. **User-specific Events**: Filter events by user ID
2. **Event Persistence**: Store events for offline clients
3. **Rate Limiting**: Prevent webhook spam
4. **Event Filtering**: Allow clients to subscribe to specific document types
5. **Metrics**: Add performance monitoring and analytics
