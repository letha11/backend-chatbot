# Login Sequence Diagram

This document describes the sequence of interactions during the user login process, based on the frontend PRD and backend implementation.

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant LoginForm as Login Form<br/>(React Component)
    participant RTKQuery as RTK Query<br/>(Mutation)
    participant ReduxStore as Redux Store<br/>(authSlice)
    participant ExpressRouter as Express Router<br/>(/api/v1/auth/login)
    participant ValidationMW as Validation Middleware<br/>(validateBody)
    participant AuthController as Auth Controller<br/>(login)
    participant Database as PostgreSQL<br/>(User Repository)
    participant bcrypt as bcrypt
    participant jwt as jsonwebtoken
    participant ReactRouter as React Router

    User->>LoginForm: Enter username & password
    User->>LoginForm: Click "Login" button
    
    Note over LoginForm: Client-side validation<br/>(Zod + React Hook Form)
    
    alt Validation fails
        LoginForm->>User: Display validation errors
    else Validation passes
        LoginForm->>RTKQuery: dispatch(loginMutation({username, password}))
        activate RTKQuery
        
        RTKQuery->>ExpressRouter: POST /api/v1/auth/login<br/>{username, password}
        activate ExpressRouter
        
        ExpressRouter->>ValidationMW: validateBody(loginSchema)
        activate ValidationMW
        
        alt Request body validation fails
            ValidationMW->>ExpressRouter: Return 400 (Validation Error)
            ExpressRouter->>RTKQuery: 400 Response
            RTKQuery->>ReduxStore: Update error state
            RTKQuery->>LoginForm: Return error
            LoginForm->>User: Show Toast: "Validation error"
        else Request body validation passes
            ValidationMW->>AuthController: next()
            deactivate ValidationMW
            
            activate AuthController
            AuthController->>Database: findOne({username, is_active: true})
            activate Database
            
            alt User not found or inactive
                Database->>AuthController: null
                deactivate Database
                AuthController->>ExpressRouter: Return 401 (Unauthorized)
                ExpressRouter->>RTKQuery: 401 Response<br/>{"message": "Invalid credentials"}
                RTKQuery->>ReduxStore: Update error state
                RTKQuery->>LoginForm: Return error
                LoginForm->>User: Show Toast: "Invalid credentials"
            else User found
                Database->>AuthController: User object
                deactivate Database
                
                AuthController->>bcrypt: compare(password, user.password_hash)
                activate bcrypt
                
                alt Password invalid
                    bcrypt->>AuthController: false
                    deactivate bcrypt
                    AuthController->>ExpressRouter: Return 401 (Unauthorized)
                    ExpressRouter->>RTKQuery: 401 Response<br/>{"message": "Invalid credentials"}
                    RTKQuery->>ReduxStore: Update error state
                    RTKQuery->>LoginForm: Return error
                    LoginForm->>User: Show Toast: "Invalid credentials"
                else Password valid
                    bcrypt->>AuthController: true
                    deactivate bcrypt
                    
                    AuthController->>jwt: sign({userId, username}, secret, {expiresIn})
                    activate jwt
                    jwt->>AuthController: JWT token
                    deactivate jwt
                    
                    AuthController->>ExpressRouter: Return 200 (Success)<br/>{token, user: {id, name, username, role}}
                    deactivate AuthController
                    
                    ExpressRouter->>RTKQuery: 200 Response<br/>{token, user}
                    deactivate ExpressRouter
                    
                    RTKQuery->>ReduxStore: dispatch(setAuth({token, user, isAuthenticated: true}))
                    activate ReduxStore
                    ReduxStore->>ReduxStore: Update authSlice state
                    deactivate ReduxStore
                    
                    RTKQuery->>LoginForm: Return success data
                    deactivate RTKQuery
                    
                    LoginForm->>LoginForm: Store JWT token<br/>(localStorage/cookie)
                    LoginForm->>ReactRouter: navigate('/dashboard')
                    activate ReactRouter
                    ReactRouter->>User: Redirect to Dashboard
                    deactivate ReactRouter
                end
            end
        end
    end
```

## Components Description

### Frontend Components

1. **Login Form (React Component)**
   - Uses Shadcn UI `Form` component
   - Client-side validation with Zod + React Hook Form
   - Handles form submission and error display

2. **RTK Query Mutation**
   - Handles API call to `POST /api/v1/auth/login`
   - Manages loading, success, and error states
   - Automatically caches and updates Redux store

3. **Redux Store (authSlice)**
   - Stores authentication state: `token`, `user`, `isAuthenticated`
   - Updated via RTK Query mutations

4. **React Router**
   - Handles navigation after successful login
   - Redirects to `/dashboard` on success
   - Redirects to `/login` on logout

### Backend Components

1. **Express Router**
   - Route: `POST /api/v1/auth/login`
   - Public route (no authentication required)

2. **Validation Middleware**
   - Validates request body using Joi schema
   - Schema: `{ username: string (required), password: string (required) }`
   - Returns 400 if validation fails

3. **Auth Controller (login)**
   - Finds user in database (must be active)
   - Verifies password using bcrypt
   - Generates JWT token
   - Returns token and user info

4. **Database (PostgreSQL)**
   - User repository query: `findOne({ username, is_active: true })`
   - Returns user object or null

5. **bcrypt**
   - Password hashing and verification
   - Compares plain password with stored hash

6. **jsonwebtoken**
   - Generates JWT token with payload: `{ userId, username }`
   - Uses secret from environment config
   - Includes expiration time

## Request/Response Format

### Request
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

### Success Response (200)
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "name": "Admin User",
      "username": "admin",
      "role": "admin"
    }
  }
}
```

### Error Responses

**401 Unauthorized (Invalid credentials)**
```json
{
  "success": false,
  "message": "Invalid credentials",
  "data": null
}
```

**400 Bad Request (Validation error)**
```json
{
  "success": false,
  "message": "Validation error: username is required",
  "data": null,
  "errors": ["username is required"]
}
```

## Security Considerations

1. **Password Security**
   - Passwords are hashed using bcrypt with 12 salt rounds
   - Plain passwords are never stored or logged

2. **JWT Token**
   - Token contains user ID and username
   - Token has expiration time (configured in environment)
   - Token should be stored securely (HttpOnly cookies recommended for production)

3. **User Status**
   - Only active users (`is_active: true`) can log in
   - Inactive users are rejected even with correct credentials

4. **Error Messages**
   - Generic "Invalid credentials" message prevents username enumeration
   - Same error message for both invalid username and invalid password

## Related Files

### Frontend (to be implemented)
- `src/pages/Login.tsx` - Login form component
- `src/store/slices/authSlice.ts` - Redux auth slice
- `src/store/api/authApi.ts` - RTK Query API for auth endpoints

### Backend
- `src/routes/authRoutes.ts` - Auth routes definition
- `src/controllers/authController.ts` - Login controller logic
- `src/middlewares/validation.ts` - Request validation middleware
- `src/middlewares/auth.ts` - JWT authentication middleware
- `src/models/User.ts` - User model definition
- `src/utils/validation.ts` - Joi validation schemas











