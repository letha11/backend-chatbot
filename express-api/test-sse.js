/**
 * Simple test script to verify SSE functionality
 * Run with: node test-sse.js
 */

const EventSource = require('eventsource');

// Test SSE connection
function testSSEConnection() {
    console.log('Testing SSE connection...');
    
    const eventSource = new EventSource('http://localhost:3000/api/v1/events');
    
    eventSource.onopen = function(event) {
        console.log('✅ SSE connection opened');
    };
    
    eventSource.addEventListener('connected', function(event) {
        const data = JSON.parse(event.data);
        console.log('✅ Connected event received:', data);
    });
    
    eventSource.addEventListener('heartbeat', function(event) {
        const data = JSON.parse(event.data);
        console.log('💓 Heartbeat received:', data.timestamp);
    });
    
    eventSource.addEventListener('document_processing', function(event) {
        const data = JSON.parse(event.data);
        console.log('📄 Document processing event:', {
            documentId: data.documentId,
            status: data.status,
            message: data.message,
            timestamp: data.timestamp
        });
    });
    
    eventSource.onerror = function(event) {
        console.error('❌ SSE connection error:', event);
    };
    
    // Keep the connection alive for 60 seconds
    setTimeout(() => {
        console.log('Closing SSE connection...');
        eventSource.close();
        process.exit(0);
    }, 60000);
}

// Test webhook endpoint
async function testWebhookEndpoint() {
    console.log('\nTesting webhook endpoint...');
    
    const testPayload = {
        documentId: 'test-document-123',
        status: 'embedded',
        message: 'Document processing completed successfully',
        metadata: {
            filename: 'test-document.pdf',
            embeddingCount: 10,
            stage: 'embedding_complete'
        }
    };
    
    try {
        const response = await fetch('http://localhost:3000/api/v1/events/webhook/document-processing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Webhook-Key': 'your-internal-key' // Use the same key from your config
            },
            body: JSON.stringify(testPayload)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log('✅ Webhook test successful:', result);
        } else {
            console.error('❌ Webhook test failed:', result);
        }
    } catch (error) {
        console.error('❌ Webhook test error:', error.message);
    }
}

// Main test function
async function runTests() {
    console.log('🚀 Starting SSE functionality tests...\n');
    
    // Start SSE connection test
    testSSEConnection();
    
    // Wait a bit then test webhook
    setTimeout(async () => {
        await testWebhookEndpoint();
    }, 2000);
}

// Check if EventSource is available
if (typeof EventSource === 'undefined') {
    console.log('Installing eventsource package...');
    console.log('Run: npm install eventsource');
    process.exit(1);
}

// Run tests
runTests();
