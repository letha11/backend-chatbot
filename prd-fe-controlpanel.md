## Product Requirements Document: Chatbot Control Panel Frontend

This document outlines the detailed product requirements for the frontend web application of the Chatbot Control Panel. The frontend will be built using **React with Vite**, leveraging Shadcn UI components for a consistent and modern user experience. **Redux Toolkit** will be used for state management. It will consume the API endpoints defined in the `backend_endpoints.md` document, communicating with both the Express.js Backend API and the FastAPI ML Service (via the Express.js proxy).

### General Requirements

*   **Technology Stack:** React, Vite, TypeScript, Redux Toolkit, Shadcn UI, Tailwind CSS.
*   **Theme/Colorscheme:**
    *   Primary: `#ED1E28`
    *   Secondary: `#B6252A`
    *   Neutral Dark: `#55565B`
    *   Neutral Light: `#959597`
    *   (Implement using Tailwind CSS custom colors)
*   **Responsiveness:** The application must be fully responsive, providing an optimal viewing and interaction experience across various devices (desktop, tablet, mobile).
*   **Browser Compatibility:** Support for modern web browsers (Chrome, Firefox, Edge, Safari latest versions).
*   **Accessibility:** Adhere to WCAG 2.1 AA standards where applicable.
*   **Authentication:** Integrate with the Express.js JWT-based authentication system.
*   **State Management:** **Redux Toolkit** will be used for efficient and predictable state management.
*   **Data Fetching:** Utilize **RTK Query** (part of Redux Toolkit) for efficient data fetching, caching, and revalidation, interacting with the defined API endpoints.
*   **Error Handling:** Display user-friendly error messages for API failures, network issues, and client-side validation errors.
*   **Loading States:** Provide clear loading indicators for asynchronous operations.
*   **Notifications:** Implement a robust notification system (e.g., toast messages using Shadcn `Toast`) for user feedback.
*   **Routing:** Use `react-router-dom` for client-side routing.

---

### Phase 5: Frontend (Admin Panel)

**Feature 5.1: Project Setup & Core Layout**

*   **Description:** Initialize the React project with Vite, configure Shadcn UI, Redux Toolkit, `react-router-dom`, and establish the main application layout including navigation, headers, and footers.
*   **User Stories:**
    *   As a developer, I need a well-structured React project with Vite, Shadcn UI, and Redux Toolkit configured so that I can rapidly build and maintain the admin panel.
    *   As an administrator, I need a clear and consistent navigation layout so that I can easily access different sections of the control panel.
*   **Technical Specifications:**
    *   **Vite Setup:** Use `npm create vite@latest` or `yarn create vite` with React + TypeScript template.
    *   **Shadcn UI Integration:** Follow official Shadcn UI installation guides, including `components.json` configuration and adding components.
    *   **Tailwind CSS Configuration:** Define custom color palette based on specified theme colors.
    *   **Redux Toolkit Setup:**
        *   Configure Redux store (`store.ts`) with slices for authentication, divisions, documents, and chat.
        *   Integrate RTK Query for API interactions.
    *   **React Router DOM Setup:** Configure main routes (`/`, `/login`, `/dashboard`, `/divisions`, `/documents`, `/chat`).
    *   **Layout Components:**
        *   `Layout` component with common elements (header, sidebar/navigation, main content area, footer).
        *   `Header`: Contains application title/logo, user avatar/dropdown, logout button.
        *   `Sidebar/Navigation`: Link to Dashboard, Divisions, Documents, Chatbot.
    *   **Global Styles:** Apply base typography and styles.
*   **Acceptance Criteria:**
    *   A React application is initialized with Vite and runs successfully.
    *   Shadcn UI components are correctly integrated and styled with the custom theme.
    *   Redux store and initial slices are set up.
    *   `react-router-dom` is configured for basic routing.
    *   A basic layout with a header and navigation sidebar is visible on all admin pages.
    *   Custom theme colors are applied correctly throughout the application.

**Feature 5.2: Authentication UI (Login/Logout)**

*   **Description:** Implement the user login and logout functionality, allowing administrators to securely access the control panel.
*   **User Stories:**
    *   As an administrator, I need a login page to securely access the control panel.
    *   As an administrator, I need to be able to log out from any page to secure my session.
    *   As a system, I need to redirect unauthenticated users to the login page.
*   **Technical Specifications:**
    *   **Login Page (`/login`):**
        *   Shadcn `Form` component for `username` and `password`.
        *   Input fields for `username` and `password`.
        *   Submit button.
        *   Client-side validation (e.g., Zod with React Hook Form).
        *   Calls `POST /api/v1/auth/login` endpoint via **RTK Query mutation**.
        *   Dispatches actions to Redux store to update authentication state (`isAuthenticated`, `user`, `token`).
        *   Stores JWT token in secure storage (e.g., HttpOnly cookies, or local storage for dev, then migrate to secure methods).
        *   Uses `react-router-dom` to navigate to the dashboard on successful login.
        *   Displays error messages using Shadcn `Toast` for invalid credentials.
    *   **Logout Functionality:**
        *   A "Logout" button/link in the header or user dropdown.
        *   Dispatches action to Redux store to clear authentication state.
        *   Clears JWT token from storage.
        *   Uses `react-router-dom` to navigate to the login page.
    *   **Auth Guard/Private Routes:** Implement a custom `PrivateRoute` component or route wrapper using `react-router-dom` to protect admin routes, redirecting unauthenticated users to `/login`.
*   **Acceptance Criteria:**
    *   A dedicated login page is accessible at `/login`.
    *   Users can successfully log in with valid credentials, receive a JWT, and be navigated to the dashboard.
    *   Users receive appropriate error messages for invalid login attempts via toast notifications.
    *   Users can log out, which clears their session and redirects them to the login page.
    *   All admin-specific routes are protected, requiring authentication.

**Feature 5.3: Dashboard Page**

*   **Description:** Create a dashboard page that provides a high-level overview of key metrics and recent activities within the chatbot system.
*   **User Stories:**
    *   As an administrator, I want to see a summary of the system's status when I log in, so I can quickly assess its health and activity.
*   **Technical Specifications:**
    *   **Route:** `/dashboard` (protected)
    *   **UI Components:** Shadcn `Card` components for displaying different metrics.
    *   **Content (initial):**
        *   Total Divisions (count).
        *   Total Documents (count).
        *   Active Documents (count).
        *   Documents by Status (e.g., uploaded, parsing, embedded, failed - count per status).
        *   (Future: Recent user queries, top divisions by usage, etc.)
    *   **Data Source:** Uses **RTK Query hooks** (`useGetDivisionsQuery`, `useGetDocumentsQuery`) to fetch data from `GET /api/v1/divisions` and `GET /api/v1/documents`. Data will be aggregated in the component.
*   **Acceptance Criteria:**
    *   The dashboard page loads successfully after login.
    *   Displays accurate counts for total divisions, total documents, and active documents.
    *   Shows a breakdown of document statuses.
    *   All data displayed is fetched from the Express.js API using RTK Query.

**Feature 5.4: Division Management Page**

*   **Description:** A dedicated page for administrators to view, create, edit, and deactivate divisions.
*   **User Stories:**
    *   As an administrator, I need to see a list of all divisions with their details so I can manage them.
    *   As an administrator, I need to create new divisions for organizational purposes.
    *   As an administrator, I need to update division names or descriptions to keep them current.
    *   As an administrator, I need to activate or deactivate divisions to control their visibility to the chatbot.
*   **Technical Specifications:**
    *   **Route:** `/divisions` (protected)
    *   **UI Components:**
        *   Shadcn `DataTable` to display a list of divisions (ID, Name, Description, Active Status, Created At, Actions).
        *   "Add New Division" button.
        *   Shadcn `Dialog` (modal) for "Create Division" and "Edit Division" forms.
        *   Shadcn `Form` components within modals for input fields: `name` (text), `description` (textarea), `is_active` (switch/checkbox).
        *   Shadcn `Button` for edit, toggle active status, and delete actions.
        *   Shadcn `AlertDialog` for confirmation before deactivating/deleting.
    *   **API Interactions:**
        *   Uses **RTK Query hook** (`useGetDivisionsQuery`) to fetch and display divisions.
        *   Uses **RTK Query mutations** (`useCreateDivisionMutation`, `useUpdateDivisionMutation`, `useDeleteDivisionMutation`) for creating, updating, and soft deleting/deactivating a division.
    *   **Validation:** Client-side form validation (e.g., Zod with React Hook Form) matching API requirements.
    *   **Loading/Error States:** Display appropriate feedback using Shadcn `Toast` for success/error messages. Loading states integrated with RTK Query.
*   **Acceptance Criteria:**
    *   The `/divisions` page displays a table of all divisions with their relevant details, fetched via RTK Query.
    *   Administrators can open a modal, fill out a form, and successfully create a new division, reflected in the UI.
    *   Administrators can edit existing division details via a modal form, and changes are persisted.
    *   Administrators can toggle the `is_active` status of a division, with immediate UI feedback.
    *   Confirmation prompts appear before critical actions.
    *   Success/error notifications appear for all operations.

**Feature 5.5: Document Management Page**

*   **Description:** A comprehensive page for administrators to upload, view, filter, toggle active status, and delete documents.
*   **User Stories:**
    *   As an administrator, I need to upload new document files to the system so they can be processed for the chatbot.
    *   As an administrator, I need to see a list of all documents, with their processing status, so I can monitor their readiness for the chatbot.
    *   As an administrator, I need to filter documents by division and active status to find specific information.
    *   As an administrator, I need to activate or deactivate documents to control their availability to the chatbot.
    *   As an administrator, I need to delete documents that are no longer needed or are incorrect.
*   **Technical Specifications:**
    *   **Route:** `/documents` (protected)
    *   **UI Components:**
        *   Shadcn `DataTable` to display documents (Original Filename, Division, File Type, Status, Active Status, Uploaded By, Created At, Actions).
        *   "Upload Document" button.
        *   Shadcn `Dialog` (modal) for the "Upload Document" form.
        *   Shadcn `Form` components within the modal: `division_id` (Shadcn `Select` dropdown populated from `useGetDivisionsQuery`), `file` (file input).
        *   Shadcn `Input` for search/filter by filename.
        *   Shadcn `Select` or `Combobox` for filtering by `division_id`.
        *   Shadcn `Switch` or `Checkbox` for filtering by `is_active`.
        *   Shadcn `Badge` for visually representing `status` (e.g., 'uploaded', 'parsing', 'embedded', 'failed') with custom colors.
        *   Shadcn `Button` for toggle active status and delete actions.
        *   Shadcn `AlertDialog` for confirmation before deleting.
    *   **API Interactions:**
        *   Uses **RTK Query hook** (`useGetDocumentsQuery`) to fetch documents with `division_id` and `is_active` query params.
        *   Uses **RTK Query mutations** (`useUploadDocumentMutation`, `useToggleDocumentActiveMutation`, `useDeleteDocumentMutation`) for upload, toggle, and delete.
    *   **File Upload:** Handle `multipart/form-data` correctly using `fetch` or `axios`. Display upload progress using a Shadcn `Progress` bar within the modal.
    *   **Document Status Flow:** The UI should react to status changes through RTK Query's caching and revalidation mechanisms, possibly with a polling interval for documents in `parsing` status.
    *   **Error Handling:** Display specific error messages using Shadcn `Toast` for invalid file types, size limits, or backend processing failures.
*   **Acceptance Criteria:**
    *   The `/documents` page displays a filterable table of all documents with their details, fetched via RTK Query.
    *   Administrators can filter documents by division and active status.
    *   Administrators can successfully upload a document to a chosen division, and its initial status (`uploaded`) is reflected with progress.
    *   Administrators can toggle the active status of documents, with validation that only `embedded` documents can be activated.
    *   Administrators can delete documents, with a confirmation prompt.
    *   Document statuses are clearly visible, styled, and update automatically.

**Feature 5.6: Basic Stats View (on Documents Page or separate)**

*   **Description:** Provide a small section (e.g., at the top of the documents page, or as part of the dashboard) displaying key statistics related to documents.
*   **User Stories:**
    *   As an administrator, I want to quickly see the number of active vs. inactive documents so I can understand the chatbot's current knowledge base.
*   **Technical Specifications:**
    *   **Placement:** Integrated into the `/documents` page, or as a widget on `/dashboard`.
    *   **UI Components:** Shadcn `Card` or simple text displays.
    *   **Content:**
        *   Total documents.
        *   Number of active documents.
        *   Number of inactive documents.
        *   Number of documents with `failed` status.
    *   **Data Source:** Aggregated from `useGetDocumentsQuery` data available in the Redux store.
*   **Acceptance Criteria:**
    *   The stats view accurately displays the counts of total, active, inactive, and failed documents.
    *   The stats are updated when documents are uploaded, toggled, or deleted via RTK Query's revalidation.

---

### Phase 6: Frontend (Chatbot UI)

**Feature 6.1: User Chatbot Interface**

*   **Description:** Build the user-facing chat interface where users can select a division, ask questions, and receive answers from the RAG-powered chatbot.
*   **User Stories:**
    *   As a user, I need a simple chat interface to ask questions.
    *   As a user, I need to select a division so the chatbot answers from relevant documents.
    *   As a user, I need to see the chatbot's responses and any source documents used.
*   **Technical Specifications:**
    *   **Route:** `/chat` (can be public or protected, initially protected for simplicity).
    *   **UI Components:**
        *   Shadcn `Select` or `Combobox` to choose a `division_id` (populated from `useGetDivisionsQuery`).
        *   Chat history display area (scrollable `Div` with custom styling).
        *   User input area (Shadcn `Textarea` or `Input`).
        *   Send button (Shadcn `Button`).
        *   Chat bubbles for user queries and chatbot responses (custom components or Shadcn `Card` for bubbles).
        *   Shadcn `Collapsible` or `Accordion` for displaying source document details (filename, chunk preview, distance) below the answer.
    *   **API Interaction:** Uses **RTK Query mutation** (`useSendChatMessageMutation`) to send queries to `POST /api/v1/chat` and receive answers.
    *   **State Management:** Chat history (messages, sources, loading state) managed within a Redux slice (`chatSlice`). User queries and chatbot responses are added to this state.
    *   **Loading States:** Show typing indicator (custom component) or spinner (Shadcn `Spinner`) while waiting for chatbot response.
    *   **Error Handling:** Display user-friendly messages using Shadcn `Toast` if the chatbot cannot answer or there's an API error.
    *   **Initial State:** Default to a specific division or prompt the user to select one if none is selected.
    *   **"Clear Chat" Button:** A button to clear the current chat history.
*   **Acceptance Criteria:**
    *   Users can select an active division from a dropdown.
    *   Users can type a query and send it to the chatbot.
    *   The chatbot's answer is displayed in a chat bubble format, persisted in Redux state.
    *   If available, source documents (filename, preview) are displayed along with the answer, toggleable for detail.
    *   The interface remains responsive and user-friendly during interactions.
    *   Proper loading indicators are shown while waiting for the chatbot response.
    *   Users can clear the current chat history.

---

### Phase 7: QA & Iteration

*   **Description:** Conduct comprehensive testing across all features, fix bugs, and gather feedback for improvements.
*   **User Stories:**
    *   As a tester, I need to verify that all features work as expected and that the UI is consistent and bug-free.
    *   As an administrator, I want a stable and reliable system for managing my chatbot knowledge base.
*   **Technical Specifications:**
    *   **Testing Frameworks:** Jest/React Testing Library for unit/integration tests, Cypress/Playwright for E2E tests.
    *   **Test Cases:**
        *   User registration and login/logout flows.
        *   Division CRUD operations (creation, viewing, editing, deactivating) - verify Redux state updates.
        *   Document upload (various file types), viewing, filtering, toggling active status, deletion - verify Redux state and UI consistency.
        *   Chatbot functionality (selecting division, asking diverse queries, verifying responses and sources) - verify Redux state for chat history.
        *   Responsiveness across different screen sizes.
        *   Error message display for all anticipated API errors via toast notifications.
        *   Performance testing for UI responsiveness and data loading.
    *   **Feedback Mechanism:** Integrate a feedback tool (e.g., Sentry for error tracking, or simple internal form).
*   **Acceptance Criteria:**
    *   All identified bugs are fixed.
    *   The application functions correctly across supported browsers and devices.
    *   User feedback is collected and prioritized.
    *   A stable beta release is ready for wider testing.
