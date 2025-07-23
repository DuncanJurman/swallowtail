# WebSocket Documentation

## Overview

Swallowtail uses Socket.io for real-time updates, allowing clients to receive instant notifications about task progress, status changes, and execution steps.

## Connection

Connect to the WebSocket server at the same URL as the API:

```javascript
const socket = io('http://localhost:8000', {
    transports: ['websocket'],
    upgrade: false
});
```

## Events

### Client → Server Events

#### `subscribe_instance`
Subscribe to updates for a specific instance.

```javascript
socket.emit('subscribe_instance', {
    instance_id: 'uuid-here'
});
```

#### `unsubscribe_instance`
Unsubscribe from instance updates.

```javascript
socket.emit('unsubscribe_instance', {
    instance_id: 'uuid-here'
});
```

### Server → Client Events

#### `connected`
Emitted when successfully connected to the server.

#### `subscribed`
Confirmation of successful subscription.

```javascript
{
    instance_id: 'uuid-here'
}
```

#### `task_update`
General task update event.

```javascript
{
    instance_id: 'uuid-here',
    task_id: 'uuid-here',
    type: 'task_update',
    data: {
        progress: 75,
        message: 'Processing content...',
        timestamp: '2024-01-01T12:00:00Z'
    }
}
```

#### `execution_step`
New execution step added to a task.

```javascript
{
    instance_id: 'uuid-here',
    task_id: 'uuid-here',
    type: 'execution_step',
    data: {
        step_id: 'generate_content',
        agent: 'ContentCreator',
        action: 'Generating social media content',
        status: 'completed',
        output: {...},
        started_at: '2024-01-01T12:00:00Z',
        completed_at: '2024-01-01T12:01:00Z'
    }
}
```

#### `error`
Error messages from the server.

```javascript
{
    message: 'Error description'
}
```

## Example Client Implementation

### JavaScript/TypeScript

```javascript
import { io } from 'socket.io-client';

class TaskWebSocketClient {
    constructor(url) {
        this.socket = null;
        this.url = url;
        this.subscriptions = new Set();
    }
    
    connect() {
        this.socket = io(this.url, {
            transports: ['websocket']
        });
        
        this.socket.on('connect', () => {
            console.log('Connected to WebSocket');
            // Resubscribe to all instances
            this.subscriptions.forEach(instanceId => {
                this.subscribe(instanceId);
            });
        });
        
        this.socket.on('task_update', (data) => {
            this.handleTaskUpdate(data);
        });
        
        this.socket.on('execution_step', (data) => {
            this.handleExecutionStep(data);
        });
    }
    
    subscribe(instanceId) {
        if (this.socket && this.socket.connected) {
            this.socket.emit('subscribe_instance', { instance_id: instanceId });
            this.subscriptions.add(instanceId);
        }
    }
    
    unsubscribe(instanceId) {
        if (this.socket && this.socket.connected) {
            this.socket.emit('unsubscribe_instance', { instance_id: instanceId });
            this.subscriptions.delete(instanceId);
        }
    }
    
    handleTaskUpdate(data) {
        // Update UI with task progress
        console.log(`Task ${data.task_id} progress: ${data.data.progress}%`);
    }
    
    handleExecutionStep(data) {
        // Add execution step to UI
        console.log(`New step for task ${data.task_id}: ${data.data.action}`);
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Usage
const client = new TaskWebSocketClient('http://localhost:8000');
client.connect();
client.subscribe('instance-uuid-here');
```

### Python

```python
import socketio

class TaskWebSocketClient:
    def __init__(self, url):
        self.sio = socketio.Client()
        self.url = url
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.sio.on('connect')
        def on_connect():
            print('Connected to WebSocket')
        
        @self.sio.on('task_update')
        def on_task_update(data):
            print(f"Task {data['task_id']} update: {data['data']}")
        
        @self.sio.on('execution_step')
        def on_execution_step(data):
            print(f"Execution step: {data['data']}")
    
    def connect(self):
        self.sio.connect(self.url, transports=['websocket'])
    
    def subscribe(self, instance_id):
        self.sio.emit('subscribe_instance', {'instance_id': instance_id})
    
    def disconnect(self):
        self.sio.disconnect()

# Usage
client = TaskWebSocketClient('http://localhost:8000')
client.connect()
client.subscribe('instance-uuid-here')
```

## Testing

A test client is available at `docs/websocket_client_example.html`. Open it in a browser to test WebSocket connectivity and events.

## Integration with Task Processing

The task processors automatically emit WebSocket events when:

1. **Status changes**: When a task transitions between states (SUBMITTED → QUEUED → IN_PROGRESS → COMPLETED)
2. **Progress updates**: During task execution (0% → 25% → 50% → 100%)
3. **Execution steps**: When agents complete individual steps

This allows frontends to show real-time progress without polling the API.

## Security Considerations

1. **Authentication**: Currently, WebSocket connections are not authenticated. In production:
   - Implement JWT token validation on connection
   - Verify user has access to the instance they're subscribing to

2. **Rate Limiting**: Consider implementing rate limits for subscriptions per client

3. **Data Privacy**: Ensure sensitive data is not broadcast in WebSocket events