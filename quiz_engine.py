import random

# ==============================================================================
# ROLE-BASED QUESTION CATALOG WITH SHORTCUT ROADMAP METADATA
# Each question contains:
# - q: question text
# - options: list of 4 choices
# - ans: correct choice index (0-3)
# - topic: specific sub-skill
# - explanation: why the answer is correct
# - doc_url: high-quality tutorial/doc link
# - shortcut_tip: quick conceptual shortcut to remember
# ==============================================================================

ROLE_QUESTIONS = {
    "🌐 Full Stack Developer": [
        {
            "q": "Which HTTP status code should a REST API return when a resource is successfully created?",
            "options": ["200 OK", "201 Created", "204 No Content", "301 Moved Permanently"],
            "ans": 1,
            "topic": "REST API Design",
            "explanation": "201 Created indicates that the request has succeeded and led to the creation of a new resource, commonly accompanied by a Location header.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/201",
            "shortcut_tip": "Remember: 200 = Success with content, 201 = Created (POST), 204 = No content (DELETE/PUT)."
        },
        {
            "q": "What is the primary difference between localStorage and sessionStorage in the browser?",
            "options": [
                "localStorage has smaller storage capacity",
                "sessionStorage persists after the browser tab is closed",
                "sessionStorage is cleared when the page session / tab ends",
                "localStorage sends data with every HTTP request"
            ],
            "ans": 2,
            "topic": "Browser Storage",
            "explanation": "sessionStorage data is scoped to the browser tab lifecycle and is cleared when the tab closes, whereas localStorage persists indefinitely until cleared.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage",
            "shortcut_tip": "Shortcut: 'Session' dies with the tab; 'Local' stays on the machine forever."
        },
        {
            "q": "In database architecture, what does the 'I' in ACID transactions stand for?",
            "options": ["Integrity", "Isolation", "Inheritance", "Immutability"],
            "ans": 1,
            "topic": "Database Fundamentals",
            "explanation": "Isolation ensures that concurrent transactions execute without interfering with one another, preventing dirty reads and non-repeatable reads.",
            "doc_url": "https://www.geeksforgeeks.org/acid-properties-in-dbms/",
            "shortcut_tip": "ACID: Atomicity (all or nothing), Consistency (valid state), Isolation (no clash), Durability (persisted)."
        },
        {
            "q": "Which technique prevents SQL injection vulnerabilities in backend queries?",
            "options": ["Client-side input length validation", "Parameterized queries / Prepared statements", "Base64 encoding user inputs", "Using GET requests instead of POST"],
            "ans": 1,
            "topic": "Web Security & SQL",
            "explanation": "Parameterized queries separate the query structure from the data input, ensuring the database engine treats user input strictly as parameters, not executable code.",
            "doc_url": "https://owasp.org/www-community/attacks/SQL_Injection",
            "shortcut_tip": "Never string-concatenate user inputs into SQL queries; always use ORM or query parameters ($1, ?, :param)."
        },
        {
            "q": "In React, what will happen if you update state directly without calling the setState/dispatch hook?",
            "options": [
                "A syntax error is immediately thrown",
                "React will not trigger a re-render and the UI will be out of sync",
                "React automatically detects mutations using proxies and re-renders",
                "The component will unmount"
            ],
            "ans": 1,
            "topic": "React State Management",
            "explanation": "React compares state references to decide whether to re-render. Mutating state directly retains the same memory reference, so React skips re-rendering.",
            "doc_url": "https://react.dev/learn/updating-objects-in-state",
            "shortcut_tip": "Treat React state as immutable. Always use setter functions or spread syntax (`[...prev, newItem]`)."
        },
        {
            "q": "What is the primary purpose of CORS (Cross-Origin Resource Sharing)?",
            "options": [
                "To accelerate frontend file downloads",
                "To allow servers to specify who can access their resources from other origins",
                "To encrypt API payloads across the internet",
                "To manage browser cookie sessions automatically"
            ],
            "ans": 1,
            "topic": "Web Architecture & Security",
            "explanation": "CORS is an HTTP-header based security mechanism enforced by browsers that allows a server to indicate which origins are permitted to read its responses.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS",
            "shortcut_tip": "CORS is enforced by the BROWSER, not the server. Configure 'Access-Control-Allow-Origin' on the backend."
        },
        {
            "q": "Which data format is native to Node.js and MongoDB ecosystems for wire communication and storage?",
            "options": ["XML", "JSON / BSON", "Protobuf", "YAML"],
            "ans": 1,
            "topic": "MERN Stack / MongoDB",
            "explanation": "MongoDB stores data internally in BSON (Binary JSON), which maps seamlessly to JavaScript/Node.js JSON objects.",
            "doc_url": "https://www.mongodb.com/docs/manual/core/document/",
            "shortcut_tip": "BSON adds support for types like Date and Binary that pure JSON lacks."
        },
        {
            "q": "What is the role of a reverse proxy like NGINX in full stack deployments?",
            "options": [
                "Compiles TypeScript into JavaScript",
                "Handles load balancing, SSL termination, and static file caching before requests hit backend apps",
                "Runs SQL migrations on deployment",
                "Replaces backend Node.js code"
            ],
            "ans": 1,
            "topic": "DevOps & Deployment",
            "explanation": "A reverse proxy sits in front of backend servers to forward client requests, terminate SSL certificates, manage rate limiting, and balance load.",
            "doc_url": "https://www.nginx.com/resources/glossary/reverse-proxy-server/",
            "shortcut_tip": "Clients talk to NGINX; NGINX talks to backend microservices/Node.js on localhost."
        },
        {
            "q": "In JWT (JSON Web Token) authentication, what constitutes the three parts separated by dots?",
            "options": [
                "Username, Password, Role",
                "Header, Payload, Signature",
                "API Key, User ID, Timestamp",
                "Public Key, Private Key, Hash"
            ],
            "ans": 1,
            "topic": "Authentication & JWT",
            "explanation": "A JWT consists of Header (algorithm & token type), Payload (claims/user data), and Signature (verifies integrity).",
            "doc_url": "https://jwt.io/introduction",
            "shortcut_tip": "JWT = header.payload.signature. Remember: payload is Base64 encoded, NOT encrypted! Never store passwords inside."
        },
        {
            "q": "What does CSS Flexbox `justify-content` align items along?",
            "options": [
                "The Cross Axis",
                "The Main Axis",
                "The Z-Index Depth",
                "The Viewport Diagonal"
            ],
            "ans": 1,
            "topic": "CSS Flexbox",
            "explanation": "`justify-content` aligns flex items along the main axis (horizontal by default, or vertical if flex-direction is column).",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/CSS/justify-content",
            "shortcut_tip": "Justify = Main Axis (flow direction). Align-items = Cross Axis (perpendicular)."
        },
        {
            "q": "Which Git command creates a new branch and immediately switches your working directory to it?",
            "options": ["git branch -new <name>", "git checkout -b <name>", "git switch -save <name>", "git merge <name>"],
            "ans": 1,
            "topic": "Git Version Control",
            "explanation": "`git checkout -b <branch>` (or modern `git switch -c <branch>`) creates and checks out the new branch in one step.",
            "doc_url": "https://git-scm.com/docs/git-checkout",
            "shortcut_tip": "Use `git checkout -b new-feature` or `git switch -c new-feature`."
        },
        {
            "q": "What is the Big-O time complexity of searching for a value in a balanced Hash Map by key?",
            "options": ["O(1) Average", "O(log n)", "O(n)", "O(n log n)"],
            "ans": 0,
            "topic": "Data Structures",
            "explanation": "Hash tables compute an index via a hash function, providing O(1) constant time average lookup, insertion, and deletion.",
            "doc_url": "https://en.wikipedia.org/wiki/Hash_table",
            "shortcut_tip": "Hash table / Dictionary lookup by key = O(1) instant lookup."
        },
        {
            "q": "What is a Web Worker used for in modern JavaScript?",
            "options": [
                "Styling web pages in the background",
                "Running scripts in background threads without blocking the main UI thread",
                "Managing database tables",
                "Encrypting HTTP requests automatically"
            ],
            "ans": 1,
            "topic": "JavaScript Concurrency",
            "explanation": "JavaScript is single-threaded. Web Workers allow heavy computational jobs to run on a separate background thread without freezing user interaction.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API",
            "shortcut_tip": "UI frozen by heavy loop? Offload it to a Web Worker thread."
        },
        {
            "q": "In microservices, what pattern is commonly used to prevent cascading system failures when a downstream service is down?",
            "options": ["Singleton Pattern", "Circuit Breaker Pattern", "Observer Pattern", "Decorator Pattern"],
            "ans": 1,
            "topic": "System Architecture",
            "explanation": "The Circuit Breaker pattern trips open when a dependency fails repeatedly, immediately returning a fallback response rather than letting threads stall and crash the whole system.",
            "doc_url": "https://martinfowler.com/bliki/CircuitBreaker.html",
            "shortcut_tip": "Like an electrical fuse: if a remote microservice fails 5 times, stop calling it for 30 seconds."
        },
        {
            "q": "What does the `async/await` syntax in JavaScript provide over plain Promises?",
            "options": [
                "Allows multiple threads to execute concurrently",
                "Synchronous-looking syntax for asynchronous code, improving readability and error handling with try/catch",
                "Forces network requests to run faster",
                "Eliminates the event loop"
            ],
            "ans": 1,
            "topic": "Asynchronous JavaScript",
            "explanation": "async/await is syntactic sugar over Promises that allows asynchronous code to be written sequentially, making error handling clean with standard try/catch blocks.",
            "doc_url": "https://javascript.info/async-await",
            "shortcut_tip": "An async function always returns a Promise. `const res = await fetch()` pauses execution without blocking the event loop."
        }
    ],

    "💻 Frontend Developer (React / JS / Web)": [
        {
            "q": "Which React hook is designed specifically to execute side effects after layout painting has finished?",
            "options": ["useLayoutEffect", "useEffect", "useMemo", "useCallback"],
            "ans": 1,
            "topic": "React Hooks Lifecycle",
            "explanation": "`useEffect` runs asynchronously after the render has been committed and painted to the screen, ideal for data fetching, timers, and subscriptions.",
            "doc_url": "https://react.dev/reference/react/useEffect",
            "shortcut_tip": "Use `useEffect` for 99% of side effects. Use `useLayoutEffect` only when reading DOM layout to prevent visual flickers."
        },
        {
            "q": "What is the purpose of `React.memo`?",
            "options": [
                "To cache database records",
                "To prevent unnecessary re-renders of a functional component when its props haven't changed",
                "To manage global application state",
                "To bind event listeners to the window"
            ],
            "ans": 1,
            "topic": "React Performance",
            "explanation": "React.memo is a higher-order component that performs a shallow comparison of current and next props. If they match, React reuses the previous render.",
            "doc_url": "https://react.dev/reference/react/memo",
            "shortcut_tip": "Wrap pure presentation components in `React.memo` if parent re-renders frequently."
        },
        {
            "q": "What is the CSS Box Model order from the innermost element outwards?",
            "options": [
                "Content -> Padding -> Border -> Margin",
                "Content -> Margin -> Border -> Padding",
                "Content -> Border -> Padding -> Margin",
                "Padding -> Content -> Border -> Margin"
            ],
            "ans": 0,
            "topic": "CSS Core Fundamentals",
            "explanation": "The CSS box model consists of: Content (inner), Padding (space inside border), Border, and Margin (space outside border).",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model",
            "shortcut_tip": "Rule: Content (the text) -> Padding (inner cushion) -> Border (the frame) -> Margin (space between elements)."
        },
        {
            "q": "What is the key benefit of CSS `box-sizing: border-box`?",
            "options": [
                "Removes margins from all elements",
                "Includes padding and border within the specified element width and height",
                "Makes all borders 1px solid black",
                "Enables Flexbox layout automatically"
            ],
            "ans": 1,
            "topic": "CSS Layout",
            "explanation": "With `border-box`, setting `width: 200px` means the total width remains 200px even when padding and borders are added.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing",
            "shortcut_tip": "Always set `* { box-sizing: border-box; }` at the top of your global CSS."
        },
        {
            "q": "What does Event Bubbling mean in the browser DOM?",
            "options": [
                "Events travel from the window down to the target element",
                "Events trigger on the deepest target element first, then propagate upwards through its ancestors",
                "Events trigger simultaneously on all DOM elements",
                "Events are canceled automatically after 1 second"
            ],
            "ans": 1,
            "topic": "DOM Event Model",
            "explanation": "Event bubbling moves up like an air bubble from the target child element up to document root. Call `event.stopPropagation()` to halt it.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Building_blocks/Events#event_bubbling",
            "shortcut_tip": "Capturing goes Down; Bubbling goes Up (Child -> Parent -> Document)."
        },
        {
            "q": "In TypeScript, what is the key difference between an `interface` and a `type` alias?",
            "options": [
                "Interfaces can be merged (declaration merging), whereas types cannot",
                "Types can only represent primitives",
                "Interfaces cannot describe object structures",
                "Types cannot be exported from modules"
            ],
            "ans": 0,
            "topic": "TypeScript",
            "explanation": "TypeScript interfaces support declaration merging (multiple definitions of the same name merge), while type aliases cannot be reopened once declared.",
            "doc_url": "https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#differences-between-type-aliases-and-interfaces",
            "shortcut_tip": "Use `interface` for extensible object contracts and libraries; use `type` for unions, primitives, and tuples."
        },
        {
            "q": "Which attribute on a `<script>` tag downloads the file asynchronously and executes it as soon as download completes?",
            "options": ["defer", "async", "preload", "lazy"],
            "ans": 1,
            "topic": "Web Performance & Script Loading",
            "explanation": "`async` downloads in parallel and executes immediately upon completion (may break execution order). `defer` preserves HTML parsing order and runs after HTML parse.",
            "doc_url": "https://javascript.info/script-async-defer",
            "shortcut_tip": "Use `defer` for scripts dependent on DOM or other scripts; use `async` for independent analytics/trackers."
        },
        {
            "q": "What is the Virtual DOM's reconciliation algorithm in React?",
            "options": [
                "Re-rendering the entire HTML document on every state change",
                "Diffing the new Virtual DOM tree against the previous snapshot to perform minimal surgical updates to the real DOM",
                "Translating React JSX to C++ machine code",
                "Compressing SVG assets"
            ],
            "ans": 1,
            "topic": "React Virtual DOM",
            "explanation": "Reconciliation compares the two Virtual DOM trees (heuristic O(n) diff) and calculates the minimal batch mutations needed for the real browser DOM.",
            "doc_url": "https://legacy.reactjs.org/docs/reconciliation.html",
            "shortcut_tip": "Virtual DOM is fast because reading/writing real DOM is expensive. React diffs in memory first."
        },
        {
            "q": "Why must unique and stable `key` props be assigned to items in a React list?",
            "options": [
                "To provide CSS class hooks",
                "To help React distinguish which list items were added, removed, or reordered during reconciliation",
                "To register indexedDB keys",
                "To satisfy TypeScript strict mode"
            ],
            "ans": 1,
            "topic": "React Lists & Keys",
            "explanation": "Without unique keys (or when using array indices for dynamic lists), React may re-render unintended child states when elements are inserted or deleted.",
            "doc_url": "https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key",
            "shortcut_tip": "Never use array index `(item, index) => <div key={index}>` if items can be sorted or filtered. Use unique IDs."
        },
        {
            "q": "What does Debouncing a function do in frontend applications?",
            "options": [
                "Executes the function immediately and then disables it for 1 second",
                "Postpones function execution until a specified delay has elapsed since the last time the event was triggered",
                "Runs the function at regular intervals indefinitely",
                "Duplicates the function on multiple browser cores"
            ],
            "ans": 1,
            "topic": "Performance Optimization (Debounce vs Throttle)",
            "explanation": "Debouncing ensures that costly functions (like search auto-complete API requests) only run once the user has stopped typing for e.g. 300ms.",
            "doc_url": "https://www.freecodecamp.org/news/javascript-debounce-example/",
            "shortcut_tip": "Debounce = 'Wait until user pauses typing'. Throttle = 'Run at most once every X milliseconds'."
        },
        {
            "q": "What is the CSS Grid property to create responsive columns that automatically fit without media queries?",
            "options": [
                "grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))",
                "grid-template-columns: flex-wrap(250px)",
                "grid-columns: auto-responsive",
                "display: grid-responsive"
            ],
            "ans": 0,
            "topic": "CSS Grid",
            "explanation": "`repeat(auto-fit, minmax(250px, 1fr))` creates as many 250px+ columns as will fit into the container width automatically.",
            "doc_url": "https://css-tricks.com/auto-sizing-columns-css-grid-auto-fill-vs-auto-fit/",
            "shortcut_tip": "The ultimate CSS Grid one-liner: `grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));`"
        },
        {
            "q": "What is tree shaking in modern frontend bundlers like Webpack and Vite?",
            "options": [
                "Formatting CSS source code",
                "Dead-code elimination that removes unused JavaScript exports from the final production bundle",
                "Compressing JPEG and PNG assets",
                "Simulating browser click events"
            ],
            "ans": 1,
            "topic": "Build Tools & Bundling",
            "explanation": "Tree shaking relies on ES6 static `import/export` syntax to detect which modules are unused and prune them from the bundle.",
            "doc_url": "https://webpack.js.org/guides/tree-shaking/",
            "shortcut_tip": "Always use named ES6 imports (`import { button } from 'library'`) rather than CommonJS `require` to enable tree-shaking."
        },
        {
            "q": "In React 18, what is the role of `useTransition`?",
            "options": [
                "Animates CSS transforms",
                "Marks certain state updates as non-urgent transitions so the UI remains responsive during heavy renders",
                "Switches browser URLs",
                "Creates WebSockets connections"
            ],
            "ans": 1,
            "topic": "React 18 Concurrent Features",
            "explanation": "`useTransition` separates urgent updates (like typing in an input) from non-urgent transitions (like filtering a massive list), preventing UI lag.",
            "doc_url": "https://react.dev/reference/react/useTransition",
            "shortcut_tip": "`startTransition(() => setSearchResults(data))` keeps keystroke typing silky smooth."
        },
        {
            "q": "What does progressive web app (PWA) 'Service Worker' allow a web app to do?",
            "options": [
                "Run C++ code natively in the browser",
                "Intercept network requests, cache assets, and enable offline functionality and push notifications",
                "Access client system root files",
                "Host database servers inside CSS"
            ],
            "ans": 1,
            "topic": "Progressive Web Apps (PWA)",
            "explanation": "A Service Worker is a client-side programmable network proxy that intercepts requests and serves cached responses when offline.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API",
            "shortcut_tip": "Service Worker = Programmable proxy sitting between your app and the network."
        },
        {
            "q": "What is the CSS pseudo-class `:has()` commonly known as?",
            "options": [
                "The Child Pseudo-Class",
                "The Parent Selector",
                "The Hover Fallback",
                "The Grid Multiplier"
            ],
            "ans": 1,
            "topic": "Modern CSS Selectors",
            "explanation": "`:has()` allows developers to style a parent element based on its children or sibling states (e.g. `card:has(img)` or `label:has(input:checked)`).",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/CSS/:has",
            "shortcut_tip": "`div:has(input:invalid)` styles the container when its child input is invalid. No JavaScript needed!"
        }
    ],

    "⚙️ Backend Developer (Python / Node.js / Java)": [
        {
            "q": "In Python, what is the Global Interpreter Lock (GIL)?",
            "options": [
                "A compiler that speeds up arithmetic operations",
                "A mutex that prevents multiple native threads from executing Python bytecodes simultaneously in CPython",
                "A security firewall for socket connections",
                "A memory deallocator"
            ],
            "ans": 1,
            "topic": "Python Internals & Concurrency",
            "explanation": "The GIL ensures thread safety in CPython by restricting bytecode execution to one thread at a time. For CPU-bound tasks, use `multiprocessing` instead of `threading`.",
            "doc_url": "https://realpython.com/python-gil/",
            "shortcut_tip": "CPU-bound task in Python? Use `multiprocessing`. I/O-bound (network/disk)? Use `asyncio` or `threading`."
        },
        {
            "q": "What is the difference between synchronous and asynchronous I/O in backend servers?",
            "options": [
                "Synchronous is always faster than asynchronous",
                "In synchronous I/O, the execution thread blocks until data is returned; in async I/O, the thread can handle other requests while waiting",
                "Asynchronous I/O requires multi-GPU clusters",
                "Synchronous I/O cannot work with databases"
            ],
            "ans": 1,
            "topic": "Concurrency & I/O",
            "explanation": "Async I/O non-blockingly registers callbacks/event loop polling, allowing a single thread (like Node.js or FastAPI) to handle tens of thousands of concurrent connections.",
            "doc_url": "https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick",
            "shortcut_tip": "Async I/O = High concurrency without spawning thousands of heavy OS threads."
        },
        {
            "q": "What is database Connection Pooling?",
            "options": [
                "Storing all database data in a shared RAM pool",
                "Maintaining a cache of open database connections that can be reused rather than creating a new connection for every query",
                "Encrypting database connections",
                "Merging multiple databases into one table"
            ],
            "ans": 1,
            "topic": "Database Architecture",
            "explanation": "Creating TCP connections and performing database handshakes is expensive. Connection pools keep a set of warm connections ready for instant query execution.",
            "doc_url": "https://en.wikipedia.org/wiki/Connection_pool",
            "shortcut_tip": "Always use connection pooling in production (e.g. pgpool, SQLAlchemy pool, HikariCP)."
        },
        {
            "q": "Which HTTP method is considered idempotent according to HTTP specifications?",
            "options": ["POST", "PUT", "PATCH (non-idempotent by default)", "CONNECT"],
            "ans": 1,
            "topic": "RESTful Principles",
            "explanation": "An idempotent method can be called multiple times without changing the final server state beyond the initial call. PUT, GET, and DELETE are idempotent; POST is not.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Glossary/Idempotent",
            "shortcut_tip": "Idempotent = Calling 1 time or 100 times produces the same end result. PUT is idempotent; POST creates duplicate records."
        },
        {
            "q": "What is the purpose of an Index in a relational database like PostgreSQL or MySQL?",
            "options": [
                "Compresses table storage size",
                "Speeds up data retrieval (SELECT) queries at the cost of additional storage and slower writes (INSERT/UPDATE)",
                "Enforces primary key nullability",
                "Encrypts sensitive columns"
            ],
            "ans": 1,
            "topic": "Database Indexing & B-Trees",
            "explanation": "Indexes use B-Trees or Hash structures to locate rows in O(log n) time instead of performing full table scans (O(n)).",
            "doc_url": "https://use-the-index-luke.com/",
            "shortcut_tip": "Index columns used in `WHERE`, `JOIN`, and `ORDER BY`. Don't over-index columns with frequent bulk writes."
        },
        {
            "q": "In caching strategies, what does Cache Aside (Lazy Loading) mean?",
            "options": [
                "Data is written only to cache and never to database",
                "The application checks the cache first; if missing (miss), it fetches from database and writes back to cache",
                "Cache is refreshed every 1 millisecond automatically",
                "Cache is written asynchronously in batch mode"
            ],
            "ans": 1,
            "topic": "Caching & Redis",
            "explanation": "Cache-Aside queries cache first. On miss, database is queried and cache is populated with TTL.",
            "doc_url": "https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside",
            "shortcut_tip": "App logic: `val = redis.get(key) or db.fetch(key) -> redis.set(key, val, ttl)`"
        },
        {
            "q": "What is the N+1 query problem in Object-Relational Mappers (ORMs)?",
            "options": [
                "Database allows only N+1 users",
                "Executing 1 query to fetch parent records, followed by N separate queries to fetch children of each record instead of a single JOIN",
                "Query execution taking N+1 seconds",
                "A syntax error in SQL statements"
            ],
            "ans": 1,
            "topic": "ORM Performance",
            "explanation": "When iterating over N users and fetching their orders lazily, N+1 queries fire. Use eager loading (`select_related`, `include`, or `JOIN`) to fix it.",
            "doc_url": "https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem-in-orm-object-relational-mapping",
            "shortcut_tip": "Fix N+1 with Eager Loading (SQLAlchemy `joinedload`, Django `select_related / prefetch_related`)."
        },
        {
            "q": "What is the primary difference between Redis and Memcached?",
            "options": [
                "Memcached supports complex data structures like Lists, Sets, and Hashes",
                "Redis supports rich data structures, persistence to disk, pub/sub, and replication",
                "Memcached persists data to NVMe disks by default",
                "Redis does not support key expiration"
            ],
            "ans": 1,
            "topic": "In-Memory Datastores",
            "explanation": "Memcached is a simple pure-memory key-value store. Redis is an advanced data structure store supporting strings, sets, sorted sets, streams, and disk persistence.",
            "doc_url": "https://aws.amazon.com/elasticache/redis-vs-memcached/",
            "shortcut_tip": "Need simple key-value cache? Memcached. Need queues, sorted sets, leaderboards, persistence? Redis."
        },
        {
            "q": "What does a message queue like RabbitMQ or Kafka provide in backend systems?",
            "options": [
                "Compiles backend binaries",
                "Decouples producer and consumer services, enabling asynchronous processing and traffic smoothing",
                "Replaces relational databases for all storage",
                "Generates frontend templates"
            ],
            "ans": 1,
            "topic": "Message Queues & Event-Driven Architecture",
            "explanation": "Message queues allow slow or heavy operations (like sending emails or transcoding video) to be processed asynchronously without blocking the user API response.",
            "doc_url": "https://www.rabbitmq.com/tutorials/tutorial-one-python.html",
            "shortcut_tip": "Never process heavy jobs inside an HTTP request. Push to RabbitMQ/Celery/Kafka and return HTTP 202 Accepted."
        },
        {
            "q": "What is rate limiting used for on backend endpoints?",
            "options": [
                "Limiting disk write speeds",
                "Controlling the rate of incoming requests to prevent abuse, DoS attacks, and API quotas exhaustion",
                "Restricting developers to 40 hours of work per week",
                "Throttling CPU clocks"
            ],
            "ans": 1,
            "topic": "API Security & Reliability",
            "explanation": "Rate limiting (e.g. via Token Bucket or Leaky Bucket algorithms) limits requests per user/IP to e.g. 60 req/min, returning HTTP 429 Too Many Requests on breach.",
            "doc_url": "https://cloud.google.com/architecture/rate-limiting-strategies-techniques",
            "shortcut_tip": "HTTP 429 = 'Too Many Requests'. Protect public login and search endpoints with rate limits."
        },
        {
            "q": "In Python, what is the purpose of a generator function using the `yield` keyword?",
            "options": [
                "To terminate the Python program",
                "To produce a sequence of values lazily on-the-fly without storing the entire sequence in memory",
                "To import packages concurrently",
                "To catch exceptions"
            ],
            "ans": 1,
            "topic": "Python Iterators & Generators",
            "explanation": "`yield` pauses the function state and yields a value to the caller, consuming minimal memory when reading gigabyte-scale files or streams.",
            "doc_url": "https://realpython.com/introduction-to-python-generators/",
            "shortcut_tip": "Reading a 5GB file? Don't use `file.readlines()`. Use a generator loop with `yield` to keep RAM at 5MB."
        },
        {
            "q": "What is the key principle of the Twelve-Factor App methodology regarding configuration?",
            "options": [
                "Hardcode database credentials inside Git commits",
                "Store configuration in environment variables rather than application code",
                "Commit configuration in XML files",
                "Never change configuration"
            ],
            "ans": 1,
            "topic": "12-Factor App Principles",
            "explanation": "Factor III states: Store config in the environment. This ensures code can transition between staging, QA, and production without code recompilation.",
            "doc_url": "https://12factor.net/config",
            "shortcut_tip": "Rule: Code is identical in Dev, Staging, and Prod. Only ENV variables change."
        },
        {
            "q": "What is the CAP Theorem trade-off in distributed database systems?",
            "options": [
                "CPU, Architecture, Performance",
                "Consistency, Availability, and Partition Tolerance — you can only strongly guarantee two in the presence of a network partition",
                "Cost, Accuracy, Precision",
                "Caching, Authentication, Persistence"
            ],
            "ans": 1,
            "topic": "Distributed Systems",
            "explanation": "When network partitions (P) occur in distributed clusters, you must choose between Consistency (all nodes return latest data) or Availability (every request gets a response).",
            "doc_url": "https://en.wikipedia.org/wiki/CAP_theorem",
            "shortcut_tip": "Partition tolerance is inevitable in networks. You must choose CP (MongoDB, HBase) or AP (Cassandra, DynamoDB)."
        },
        {
            "q": "What does SQL `GROUP BY` require for columns selected in the query that are not in the GROUP BY clause?",
            "options": [
                "They must be unique keys",
                "They must be wrapped in aggregate functions like SUM, COUNT, AVG, MIN, or MAX",
                "They must be integers",
                "They must be indexed"
            ],
            "ans": 1,
            "topic": "SQL Aggregations",
            "explanation": "Any column not listed in `GROUP BY` must be reduced to a single value using an aggregate function.",
            "doc_url": "https://www.w3schools.com/sql/sql_groupby.asp",
            "shortcut_tip": "Rule: If it's not in the GROUP BY list, you MUST wrap it in an aggregate function."
        },
        {
            "q": "What does a database Deadlock represent?",
            "options": [
                "A corrupted hard drive",
                "A situation where two or more transactions each hold locks that the other requires, freezing both indefinitely",
                "A database reboot",
                "An expired database license"
            ],
            "ans": 1,
            "topic": "Database Concurrency & Locks",
            "explanation": "Transaction A holds lock on row 1 and wants row 2. Transaction B holds row 2 and wants row 1. DBMS detects this and rolls back one transaction.",
            "doc_url": "https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-DEADLOCKS",
            "shortcut_tip": "Prevent deadlocks by always acquiring multiple table/row locks in the exact same consistent order across all transactions."
        }
    ],

    "🧠 Data Scientist & AI / ML Engineer": [
        {
            "q": "What does the term 'Overfitting' mean in supervised machine learning?",
            "options": [
                "Model has poor performance on both training and test data",
                "Model learns the noise and specifics of training data too well, resulting in poor generalization on unseen validation/test data",
                "Model takes too few training epochs",
                "Model has insufficient parameters"
            ],
            "ans": 1,
            "topic": "Model Generalization",
            "explanation": "Overfitting happens when a model has high variance and memorizes training data. Mitigate using regularization, dropout, data augmentation, or simpler models.",
            "doc_url": "https://www.ibm.com/topics/overfitting",
            "shortcut_tip": "High training accuracy + Low test accuracy = Overfitting. Fix with Dropout, L1/L2 regularization, or more training data."
        },
        {
            "q": "When evaluating an imbalanced classification dataset (e.g. 99% negative, 1% fraud), why is raw Accuracy misleading?",
            "options": [
                "Accuracy is mathematically impossible to compute",
                "A naive model predicting always 'negative' achieves 99% accuracy while detecting 0% of fraud cases",
                "Accuracy only applies to regression problems",
                "Accuracy requires GPU acceleration"
            ],
            "ans": 1,
            "topic": "ML Evaluation Metrics",
            "explanation": "Accuracy paradox: high accuracy does not mean high performance. For imbalanced classes, evaluate Precision, Recall, F1-Score, and ROC-AUC.",
            "doc_url": "https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall",
            "shortcut_tip": "Imbalanced dataset? Never rely on accuracy. Use F1-Score, PR-AUC curve, and Confusion Matrix."
        },
        {
            "q": "What is the primary difference between L1 (Lasso) and L2 (Ridge) regularization?",
            "options": [
                "L1 penalizes sum of squared weights; L2 penalizes sum of absolute weights",
                "L1 encourages sparse weights by driving non-important feature coefficients exactly to zero; L2 shrinks weights towards zero without making them zero",
                "L2 is used only for text processing",
                "L1 can only be used with decision trees"
            ],
            "ans": 1,
            "topic": "Regularization Techniques",
            "explanation": "L1 (Lasso) uses absolute values, acting as an automatic feature selector. L2 (Ridge) uses squared values, preventing any single weight from exploding.",
            "doc_url": "https://towardsdatascience.com/ridge-and-lasso-regression-a-complete-guide-with-python-scikit-learn-e20e34bcbf0b",
            "shortcut_tip": "L1 = Lasso = Lines = Zeroes out weights (Feature selection). L2 = Ridge = Rounds weights down close to zero."
        },
        {
            "q": "In deep learning, what problem does the vanishing gradient problem cause during backpropagation?",
            "options": [
                "Weights grow to infinity (NaN)",
                "Gradients exponentially shrink as they propagate back through deep layers, halting learning in earlier layers",
                "GPU memory runs out",
                "Loss function divides by zero"
            ],
            "ans": 1,
            "topic": "Deep Learning & Backpropagation",
            "explanation": "With activation functions like Sigmoid or Tanh, derivatives are < 1. Repeated multiplication across deep layers causes gradients to vanish towards 0. ReLU and Residual connections (ResNet) solve this.",
            "doc_url": "https://en.wikipedia.org/wiki/Vanishing_gradient_problem",
            "shortcut_tip": "Sigmoid causes vanishing gradients. Use ReLU, LeakyReLU, or Residual Skip Connections to keep gradients flowing."
        },
        {
            "q": "What mechanism enables the Transformer architecture (BERT, GPT) to process entire sequences in parallel?",
            "options": [
                "Recurrent feedback loops",
                "Self-Attention mechanism (Scaled Dot-Product Attention)",
                "Convolutions with kernel size 1",
                "Markov Decision Process"
            ],
            "ans": 1,
            "topic": "Transformers & NLP",
            "explanation": "Self-attention computes dynamic weights between every token and every other token in parallel via Query, Key, and Value matrices, removing RNN sequential bottlenecks.",
            "doc_url": "https://jalammar.github.io/illustrated-transformer/",
            "shortcut_tip": "Attention: $Attention(Q,K,V) = softmax(QK^T / \\sqrt{d_k}) V$. Computes word relationships in parallel."
        },
        {
            "q": "What does PCA (Principal Component Analysis) achieve?",
            "options": [
                "Supervised text translation",
                "Linear dimensionality reduction while preserving maximum variance of the dataset",
                "Clustering data into K discrete groups",
                "Tokenizing text documents"
            ],
            "ans": 1,
            "topic": "Dimensionality Reduction",
            "explanation": "PCA projects high-dimensional data onto orthogonal axes (principal components) ordered by the amount of variance they explain.",
            "doc_url": "https://scikit-learn.org/stable/modules/decomposition.html#pca",
            "shortcut_tip": "Have 100 features and need to visualize or compress? Run PCA to keep the top 2 or 3 components."
        },
        {
            "q": "In pandas, what is the difference between `df.loc` and `df.iloc`?",
            "options": [
                "`df.loc` is label-based indexing; `df.iloc` is integer position-based indexing",
                "`df.iloc` is faster label-based indexing",
                "`df.loc` can only be used on string columns",
                "`df.iloc` modifies the original dataframe in-place"
            ],
            "ans": 0,
            "topic": "Pandas Data Manipulation",
            "explanation": "`loc` accesses by label/index name: `df.loc['row_name', 'col_name']`. `iloc` accesses by integer coordinates: `df.iloc[0, 2]`.",
            "doc_url": "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html",
            "shortcut_tip": "Shortcut: **i**loc = **i**nteger positions (0, 1, 2). loc = labels ('age', 'name')."
        },
        {
            "q": "What is the purpose of Data Normalization (e.g. Min-Max or Standard scaling) prior to training distance-based algorithms?",
            "options": [
                "Converts text into numbers",
                "Ensures features with larger scales do not disproportionately dominate gradient descent and Euclidean distance calculations",
                "Removes null values",
                "Increases training dataset size"
            ],
            "ans": 1,
            "topic": "Data Preprocessing",
            "explanation": "Algorithms like KNN, SVM, and Neural Networks rely on distances and gradients. A feature scaled 0–100,000 will overwhelm a feature scaled 0–1 without normalization.",
            "doc_url": "https://scikit-learn.org/stable/modules/preprocessing.html",
            "shortcut_tip": "Always scale features for KNN, SVM, PCA, and Neural Nets. Trees (Random Forest, XGBoost) do not require scaling."
        },
        {
            "q": "What ensemble technique is used by Random Forest?",
            "options": ["Boosting (Sequential)", "Bagging (Bootstrap Aggregation with random feature subsets)", "Stacking with Neural Nets", "K-Means"],
            "ans": 1,
            "topic": "Ensemble Methods",
            "explanation": "Random Forest builds multiple decision trees in parallel using bootstrapped data samples and random feature subsets, then averages their predictions (Bagging).",
            "doc_url": "https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees",
            "shortcut_tip": "Bagging = Trees built in parallel (Random Forest). Boosting = Trees built sequentially fixing errors (XGBoost)."
        },
        {
            "q": "What is the ROC-AUC score measuring?",
            "options": [
                "CPU memory utilization of the model",
                "The model's ability to discriminate between positive and negative classes across all possible classification thresholds",
                "The training speed per epoch",
                "The number of parameters in the model"
            ],
            "ans": 1,
            "topic": "Classification Evaluation",
            "explanation": "AUC = Area Under the ROC Curve (True Positive Rate vs False Positive Rate). 1.0 is perfect classification; 0.5 is equivalent to a random coin flip.",
            "doc_url": "https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc",
            "shortcut_tip": "AUC 0.5 = Random guessing. AUC 0.8+ = Good. AUC 1.0 = Perfect separation."
        },
        {
            "q": "In NLP, what is the role of Lemmatization compared to Stemming?",
            "options": [
                "Stemming uses grammatical dictionaries; lemmatization just truncates suffixes",
                "Lemmatization considers vocabulary and morphological analysis to return valid dictionary root words (lemma); stemming heuristically chops word endings",
                "They are identical algorithms",
                "Lemmatization translates English to French"
            ],
            "ans": 1,
            "topic": "NLP Text Preprocessing",
            "explanation": "Stemming turns 'better' into 'better' or 'studying' into 'study'. Lemmatization uses grammar to convert 'better' -> 'good' and 'was' -> 'be'.",
            "doc_url": "https://nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html",
            "shortcut_tip": "Stemming = crude chops ('operating' -> 'operat'). Lemmatization = smart dictionary base ('ran' -> 'run')."
        },
        {
            "q": "What is Cross-Validation (e.g. 5-Fold CV) primarily used for?",
            "options": [
                "Deploying models to Kubernetes",
                "Assessing how well model parameters generalize to an independent dataset and guarding against data leakage / overfitting",
                "Compressing model size",
                "Encrypting model weights"
            ],
            "ans": 1,
            "topic": "Model Validation",
            "explanation": "K-Fold cross-validation splits data into K equal folds, iteratively training on K-1 and testing on the remaining fold to generate a stable, unbiased score.",
            "doc_url": "https://scikit-learn.org/stable/modules/cross_validation.html",
            "shortcut_tip": "Never tune hyperparameters on test data! Tune on K-Fold CV, and test only ONCE on your held-out test set."
        },
        {
            "q": "What does the Learning Rate hyperparameter control in Gradient Descent?",
            "options": [
                "The step size taken towards the local minimum of the loss function in each parameter update",
                "The number of neurons in the hidden layer",
                "The batch size of the dataset",
                "The maximum depth of trees"
            ],
            "ans": 0,
            "topic": "Optimization & Deep Learning",
            "explanation": "Too high learning rate leads to divergent oscillations; too low learning rate causes painfully slow convergence or getting trapped in local sub-optimal minima.",
            "doc_url": "https://machinelearningmastery.com/understand-the-dynamics-of-learning-rate-on-deep-learning-neural-networks/",
            "shortcut_tip": "Use adaptive optimizers like Adam (`lr=0.001` or `lr=3e-4`) or learning rate schedulers."
        },
        {
            "q": "What is Cosine Similarity commonly used for in vector embeddings?",
            "options": [
                "Measuring the angular direction between two embedding vectors regardless of their magnitude",
                "Calculating Euclidean distance in pixels",
                "Multiplying matrices for GPU shaders",
                "Calculating database storage sizes"
            ],
            "ans": 0,
            "topic": "Vector Search & Embeddings",
            "explanation": "Cosine similarity ranges from -1 to 1 (or 0 to 1 for normalized vectors). It assesses semantic similarity in LLMs and RAG pipelines based on vector angles.",
            "doc_url": "https://en.wikipedia.org/wiki/Cosine_similarity",
            "shortcut_tip": "Vector Search / RAG: Cosine similarity of 1.0 means vectors point in the identical semantic direction."
        },
        {
            "q": "What is Data Leakage in a machine learning workflow?",
            "options": [
                "A cyberattack exporting user records",
                "When information from outside the training dataset (such as target labels or future test data) is inadvertently used to create the model",
                "A memory leak in Python",
                "When pandas dataframe is exported to CSV"
            ],
            "ans": 1,
            "topic": "ML Best Practices",
            "explanation": "Example: fitting a scaler on the entire dataset BEFORE splitting into train/test. Always `fit_transform` on train data only, and `transform` test data.",
            "doc_url": "https://scikit-learn.org/stable/common_pitfalls.html#data-leakage",
            "shortcut_tip": "Golden Rule: Always split into Train and Test FIRST. Fit all encoders and scalers strictly on Train data."
        }
    ],

    "☁️ Cloud & DevOps Engineer": [
        {
            "q": "What is the key difference between a Docker Image and a Docker Container?",
            "options": [
                "Images are running instances; containers are static blueprints",
                "An image is an immutable read-only template with application code and dependencies; a container is a runnable, isolated instance of that image",
                "Containers are built using docker-compose only",
                "Images only run on Linux"
            ],
            "ans": 1,
            "topic": "Docker Fundamentals",
            "explanation": "An image is the packaged snapshot (layers). Running `docker run <image>` creates an active container process with its own writable layer.",
            "doc_url": "https://docs.docker.com/get-started/overview/",
            "shortcut_tip": "OOP Analogy: Docker Image = Class definition. Docker Container = Object instance in memory."
        },
        {
            "q": "In Kubernetes, what is the smallest deployable computing unit that can be created and managed?",
            "options": ["Cluster", "Node", "Pod", "Service"],
            "ans": 2,
            "topic": "Kubernetes Architecture",
            "explanation": "A Pod encapsulates one or more closely coupled containers, storage resources, and a unique network IP.",
            "doc_url": "https://kubernetes.io/docs/concepts/workloads/pods/",
            "shortcut_tip": "Kubernetes hierarchy: Cluster -> Nodes (Machines) -> Pods (Smallest unit) -> Containers."
        },
        {
            "q": "What does Infrastructure as Code (IaC) like Terraform provide?",
            "options": [
                "Compiles Go code into Docker binaries",
                "Declarative provisioning and management of cloud resources through human-readable configuration files with version control",
                "Replaces AWS console with a chat interface",
                "Monitors server CPU temperature"
            ],
            "ans": 1,
            "topic": "Terraform & IaC",
            "explanation": "IaC allows infrastructure (VPCs, EC2, S3, databases) to be codified in Git, reviewed via pull requests, and deployed deterministically.",
            "doc_url": "https://developer.hashicorp.com/terraform/intro",
            "shortcut_tip": "No clicking in AWS Console! Write `.tf` files, run `terraform plan`, then `terraform apply`."
        },
        {
            "q": "In CI/CD pipelines, what is the difference between Continuous Delivery and Continuous Deployment?",
            "options": [
                "Continuous Deployment requires manual human approval before releasing to production; Continuous Delivery is fully automated",
                "Continuous Delivery automates builds and tests up to a production-ready artifact with manual release trigger; Continuous Deployment automatically deploys every passing change directly to production",
                "They are exact synonyms",
                "Continuous Delivery is only for mobile apps"
            ],
            "ans": 1,
            "topic": "CI/CD Practices",
            "explanation": "Continuous Delivery keeps code always releasable with a manual button press. Continuous Deployment pushes every passing commit live to production with zero human intervention.",
            "doc_url": "https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment",
            "shortcut_tip": "Delivery = Deployment pipeline stops before Prod waiting for a human green light. Deployment = No human in the loop."
        },
        {
            "q": "What is the purpose of Kubernetes Horizontal Pod Autoscaler (HPA)?",
            "options": [
                "Increases the RAM and CPU of existing Pods",
                "Automatically scales the number of Pod replicas up or down based on observed CPU/memory utilization or custom metrics",
                "Moves pods to different geographic regions",
                "Restarts crashed pods"
            ],
            "ans": 1,
            "topic": "Kubernetes Autoscaling",
            "explanation": "HPA scales out (adding more pod replicas) when load spikes and scales in when traffic subsides.",
            "doc_url": "https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/",
            "shortcut_tip": "HPA = Horizontal (more pods). VPA = Vertical (bigger CPU/RAM on existing pod)."
        },
        {
            "q": "What AWS service provides managed Kubernetes control plane?",
            "options": ["AWS ECS", "AWS EKS", "AWS Fargate", "AWS Lambda"],
            "ans": 1,
            "topic": "AWS Cloud Services",
            "explanation": "Amazon EKS (Elastic Kubernetes Service) manages the Kubernetes master control plane nodes, etcd, and high availability.",
            "doc_url": "https://aws.amazon.com/eks/",
            "shortcut_tip": "EKS = Elastic Kubernetes Service. ECS = AWS Proprietary Container Service."
        },
        {
            "q": "What is the purpose of a Multi-Stage Dockerfile?",
            "options": [
                "Builds containers on multiple cloud providers simultaneously",
                "Separates build-time dependencies (compilers, SDKs) from the final lean runtime container to drastically reduce image size",
                "Enables multiple people to edit a Dockerfile at once",
                "Deploys images to multiple environments"
            ],
            "ans": 1,
            "topic": "Docker Best Practices",
            "explanation": "Multi-stage builds compile artifacts in an initial build container, then copy only the compiled binary to a minimal Alpine/Distroless image.",
            "doc_url": "https://docs.docker.com/build/building/multi-stage/",
            "shortcut_tip": "Use multi-stage builds to turn 1.5GB build images into 35MB production images."
        },
        {
            "q": "What is the function of a Kubernetes Ingress Controller?",
            "options": [
                "Backs up cluster storage",
                "Routes external HTTP/HTTPS traffic to internal cluster Services based on hostname and URI paths",
                "Compiles Go code for pods",
                "Generates SSL certificates manually"
            ],
            "ans": 1,
            "topic": "Kubernetes Networking",
            "explanation": "Ingress acts as the smart reverse proxy (often powered by NGINX or Traefik) routing traffic like `api.domain.com/users` to specific internal service pods.",
            "doc_url": "https://kubernetes.io/docs/concepts/services-networking/ingress/",
            "shortcut_tip": "Ingress = The front door of your Kubernetes cluster handling domains, paths, and SSL."
        },
        {
            "q": "In Linux systems administration, what command displays real-time running processes and CPU/RAM consumption?",
            "options": ["ls -la", "top / htop", "netstat -r", "chmod +x"],
            "ans": 1,
            "topic": "Linux Systems Administration",
            "explanation": "`top` or modern `htop` provides dynamic real-time visibility into CPU threads, memory, swap, process IDs, and system load averages.",
            "doc_url": "https://man7.org/linux/man-pages/man1/top.1.html",
            "shortcut_tip": "Use `htop` for visual task manager. Press `P` to sort by CPU, `M` to sort by Memory."
        },
        {
            "q": "What does GitOps (e.g. using ArgoCD or Flux) enforce in cloud deployments?",
            "options": [
                "Using Git as the single source of truth for declarative infrastructure and continuous automated synchronization to clusters",
                "Writing Git commits using Python",
                "Deleting Git history after deployment",
                "Running Docker commands manually over SSH"
            ],
            "ans": 0,
            "topic": "GitOps & ArgoCD",
            "explanation": "GitOps uses Git repos containing Kubernetes manifests as the desired state. An agent (ArgoCD) monitors Git and automatically applies any diffs to the cluster.",
            "doc_url": "https://argo-cd.readthedocs.io/en/stable/",
            "shortcut_tip": "GitOps: No direct `kubectl apply` commands in production! All changes committed to Git, synced by ArgoCD."
        },
        {
            "q": "What is the difference between a Blue/Green and Canary deployment strategy?",
            "options": [
                "Blue/Green releases to all users at once; Canary deploys to a small percentage of users first to verify metrics before full rollout",
                "Canary deployment requires shutting down all servers for 1 hour",
                "Blue/Green is only used for databases",
                "Canary deployments cannot be rolled back"
            ],
            "ans": 0,
            "topic": "Deployment Strategies",
            "explanation": "Blue/Green swaps 100% of traffic between identical environments. Canary gradually shifts traffic (e.g. 5% -> 25% -> 100%) while observing error rates.",
            "doc_url": "https://cloud.google.com/architecture/devops/devops-tech-continuous-delivery",
            "shortcut_tip": "Canary in the coal mine: Route 2% traffic to new version. If errors spike, rollback instantly before affecting all users."
        },
        {
            "q": "What does Prometheus primarily collect in microservice monitoring architectures?",
            "options": [
                "Full text database backups",
                "Time-series metrics scraped periodically via HTTP pull endpoints (`/metrics`)",
                "Source code repositories",
                "Raw MP4 video feeds"
            ],
            "ans": 1,
            "topic": "Observability & Monitoring",
            "explanation": "Prometheus scrapes numeric time-series metrics (gauges, counters, histograms) and provides a powerful query language (PromQL), often visualized via Grafana.",
            "doc_url": "https://prometheus.io/docs/introduction/overview/",
            "shortcut_tip": "Prometheus pulls metrics. Grafana dashboards visualize them. Alertmanager sends Slack/pager alerts."
        },
        {
            "q": "In cloud networking, what is a VPC (Virtual Private Cloud)?",
            "options": [
                "A video processing cluster",
                "A logically isolated virtual network dedicated to your cloud account with customizable IP address ranges, subnets, and routing",
                "A public internet cable",
                "A virtual machine monitor"
            ],
            "ans": 1,
            "topic": "Cloud Networking (AWS VPC)",
            "explanation": "A VPC provides isolated networking in AWS/GCP where you place private subnets (for databases) and public subnets (for load balancers).",
            "doc_url": "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html",
            "shortcut_tip": "Put web servers in public subnets with Internet Gateways; put databases in private subnets with NAT Gateways."
        },
        {
            "q": "What does the command `chmod 755 script.sh` assign for file permissions?",
            "options": [
                "Read, write, execute for Owner; read and execute for Group and Others",
                "Full permissions for everyone (dangerous)",
                "Read-only for all users",
                "Write-only for owner"
            ],
            "ans": 0,
            "topic": "Linux Security & File Permissions",
            "explanation": "7 = rwx (4+2+1) for owner. 5 = r-x (4+0+1) for group. 5 = r-x (4+0+1) for others.",
            "doc_url": "https://en.wikipedia.org/wiki/Chmod",
            "shortcut_tip": "Remember values: 4 = Read, 2 = Write, 1 = Execute. 7 = 4+2+1 (All), 5 = 4+1 (Read + Exec)."
        },
        {
            "q": "What is Chaos Engineering (e.g. Chaos Monkey)?",
            "options": [
                "Writing unformatted messy code",
                "The discipline of experimenting on a system in production by intentionally injecting failures to build resilience against outages",
                "Deleting production backups",
                "Overclocking cloud CPUs"
            ],
            "ans": 1,
            "topic": "Site Reliability Engineering (SRE)",
            "explanation": "Chaos Engineering intentionally kills instances or introduces network latency to prove that failover and redundancy mechanisms work seamlessly.",
            "doc_url": "https://principlesofchaos.org/",
            "shortcut_tip": "Test failure before it tests you in production. Randomly terminate pods to ensure zero downtime."
        }
    ],

    "🗄️ Database & Data Engineer": [
        {
            "q": "In SQL, what is the key difference between ROW_NUMBER() and DENSE_RANK() window functions?",
            "options": [
                "ROW_NUMBER assigns strictly sequential integers without duplicates; DENSE_RANK assigns the same rank to identical values without skipping numbers",
                "DENSE_RANK only works on string columns",
                "ROW_NUMBER requires GROUP BY",
                "They are exact synonyms"
            ],
            "ans": 0,
            "topic": "SQL Window Functions",
            "explanation": "ROW_NUMBER() always increments (1, 2, 3, 4). RANK() leaves gaps for ties (1, 2, 2, 4). DENSE_RANK() shares ranks without gaps (1, 2, 2, 3).",
            "doc_url": "https://www.postgresql.org/docs/current/tutorial-window.html",
            "shortcut_tip": "For leaderboards with ties: `DENSE_RANK() OVER (ORDER BY score DESC)`."
        },
        {
            "q": "What is Sharding in MongoDB database architecture?",
            "options": [
                "Replicating the entire database on 3 machines for backup",
                "Distributing large datasets and write throughput horizontally across multiple clusters using a shard key",
                "Compressing BSON documents on disk",
                "Validating email schemas"
            ],
            "ans": 1,
            "topic": "MongoDB Sharding & Scaling",
            "explanation": "Sharding enables horizontal scaling by partitioning data collections across multiple replica sets based on a shard key.",
            "doc_url": "https://www.mongodb.com/docs/manual/sharding/",
            "shortcut_tip": "Replication = High Availability (redundant copies). Sharding = Horizontal Scaling (splitting data)."
        },
        {
            "q": "What is the primary difference between OLTP and OLAP systems?",
            "options": [
                "OLTP is optimized for heavy multi-table analytical aggregations; OLAP is for fast transactional lookups",
                "OLTP handles high volumes of fast transactional reads/writes (e.g. e-commerce orders); OLAP handles complex queries across massive datasets for business intelligence",
                "OLTP requires NoSQL; OLAP requires CSV",
                "OLAP does not support indexes"
            ],
            "ans": 1,
            "topic": "Data Architecture (OLTP vs OLAP)",
            "explanation": "OLTP = Online Transaction Processing (row-oriented, normalized, fast writes). OLAP = Online Analytical Processing (column-oriented, historical rollups).",
            "doc_url": "https://aws.amazon.com/compare/the-difference-between-olap-and-oltp/",
            "shortcut_tip": "OLTP = Live operational app database (Postgres/MySQL). OLAP = Data Warehouse (Snowflake, BigQuery, ClickHouse)."
        },
        {
            "q": "In relational database design, what does Third Normal Form (3NF) mandate?",
            "options": [
                "All tables must have exactly three columns",
                "Every non-prime attribute must be non-transitively dependent on the primary key (no A -> B -> C dependencies)",
                "All tables must use foreign keys to every other table",
                "Data must be duplicated across three databases"
            ],
            "ans": 1,
            "topic": "Database Normalization",
            "explanation": "3NF requires meeting 2NF and eliminating transitive dependencies: non-key attributes must depend only on the primary key, nothing else.",
            "doc_url": "https://en.wikipedia.org/wiki/Third_normal_form",
            "shortcut_tip": "Normalization mantra: 'The key, the whole key, and nothing but the key, so help me Codd.'"
        },
        {
            "q": "In columnar storage formats like Apache Parquet, why are analytical queries much faster than CSV or JSON?",
            "options": [
                "Parquet encrypts all numbers with AES",
                "Columns are stored contiguously on disk, allowing queries to scan only the specific columns requested without reading irrelevant row data",
                "Parquet runs directly on GPU VRAM",
                "Parquet does not store nulls"
            ],
            "ans": 1,
            "topic": "Columnar Storage (Parquet)",
            "explanation": "If a table has 100 columns and query selects 2, Parquet skips 98% of disk I/O through column pruning and dictionary compression.",
            "doc_url": "https://parquet.apache.org/docs/overview/",
            "shortcut_tip": "Row-based (CSV/Postgres) = Great for inserting whole rows. Columnar (Parquet) = Blazing fast for `SELECT AVG(salary)` across 10M rows."
        },
        {
            "q": "What does EXPLAIN ANALYZE reveal when optimizing slow SQL queries in PostgreSQL?",
            "options": [
                "Checks spelling errors in table names",
                "Executes the query and returns the real-time planner cost, actual execution time per node, and whether Index Scan or Seq Scan was used",
                "Deletes slow rows automatically",
                "Reboots the database"
            ],
            "ans": 1,
            "topic": "SQL Query Optimization",
            "explanation": "`EXPLAIN ANALYZE` shows the actual execution tree, revealing costly sequential table scans, hash joins, or misestimated row counts.",
            "doc_url": "https://www.postgresql.org/docs/current/using-explain.html",
            "shortcut_tip": "Slow SQL query? Run `EXPLAIN (ANALYZE, BUFFERS) <query>` to spot where disk reads choke performance."
        },
        {
            "q": "In MongoDB, what does the `$group` stage in an aggregation pipeline do?",
            "options": [
                "Creates user permissions",
                "Groups input documents by a specified identifier expression and applies accumulator expressions (e.g. $sum, $avg) to each group",
                "Sorts documents alphabetically",
                "Exports documents to CSV"
            ],
            "ans": 1,
            "topic": "MongoDB Aggregations",
            "explanation": "Equivalent to SQL `GROUP BY`, `$group` groups documents by `_id: '$category'` and aggregates metrics like `totalRevenue: { $sum: '$price' }`.",
            "doc_url": "https://www.mongodb.com/docs/manual/reference/operator/aggregation/group/",
            "shortcut_tip": "Pipeline flow: `$match` (filter rows first) -> `$group` (aggregate) -> `$sort` (order results)."
        },
        {
            "q": "What is Change Data Capture (CDC) in modern data pipelines?",
            "options": [
                "Manually taking database screenshots every hour",
                "A design pattern that monitors and captures row-level inserts, updates, and deletes from database transaction logs (WAL) to stream changes in real-time",
                "Changing data types of columns",
                "A compiler for SQL"
            ],
            "ans": 1,
            "topic": "Data Pipelines & CDC",
            "explanation": "CDC tools (like Debezium) read database transaction logs and stream changes to Kafka with near-zero latency and minimal load on the primary DB.",
            "doc_url": "https://debezium.io/documentation/reference/stable/architecture.html",
            "shortcut_tip": "Don't poll the database with `SELECT * WHERE updated_at > last_sync`. Use CDC from the database WAL."
        },
        {
            "q": "What is a Star Schema in Data Warehousing?",
            "options": [
                "A database designed specifically for astronomy data",
                "A dimensional data model consisting of a central Fact table containing metrics connected directly to multiple surrounding Dimension tables",
                "A circular linked list of tables",
                "A database without primary keys"
            ],
            "ans": 1,
            "topic": "Data Warehousing (Star vs Snowflake)",
            "explanation": "The Star Schema simplifies analytical queries by having one central fact table (e.g., Sales) surrounded by denormalized dimension tables (Customer, Date, Product).",
            "doc_url": "https://en.wikipedia.org/wiki/Star_schema",
            "shortcut_tip": "Star Schema = Denormalized dimensions (fewer joins, faster analytics). Snowflake Schema = Normalized dimensions."
        },
        {
            "q": "In Apache Airflow, what does a DAG represent?",
            "options": [
                "Data Analysis Gateway",
                "Directed Acyclic Graph — a collection of all tasks you want to run, organized to reflect their relationships and upstream/downstream dependencies without circular loops",
                "Database Administrator Group",
                "Direct API Gateway"
            ],
            "ans": 1,
            "topic": "ETL Orchestration (Airflow)",
            "explanation": "DAGs specify execution order: Task A >> [Task B, Task C] >> Task D. 'Acyclic' ensures no infinite execution loops.",
            "doc_url": "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html",
            "shortcut_tip": "Airflow DAGs define workflow dependencies. Use operators (PythonOperator, BashOperator) to construct pipelines."
        },
        {
            "q": "What is Write-Ahead Logging (WAL) in database engines?",
            "options": [
                "Writing logs to Twitter before updating databases",
                "A technique where changes are first recorded to a sequential append-only log on disk before being applied to the actual data pages",
                "Writing logs only when queries fail",
                "Deleting logs before saving"
            ],
            "ans": 1,
            "topic": "Database Internals & Durability",
            "explanation": "WAL guarantees ACID durability. If the server crashes mid-transaction, the DBMS replays the WAL on restart to restore consistent state.",
            "doc_url": "https://www.postgresql.org/docs/current/wal-intro.html",
            "shortcut_tip": "Sequential disk writes to WAL are 100x faster than random writes to data tables. Durability is achieved via WAL."
        },
        {
            "q": "What is the purpose of Database Connection Pool sizing guidelines (e.g. HikariCP formula `connections = ((core_count * 2) + effective_spindle_count)`)?",
            "options": [
                "To ensure 100,000 connections are always open",
                "To prevent thread context switching thrashing and CPU CPU starvation by keeping active connections aligned with hardware core capacity",
                "To reduce database licensing fees",
                "To prevent SQL queries from timing out"
            ],
            "ans": 1,
            "topic": "Database Connection Management",
            "explanation": "Having 5,000 open connections to an 8-core database server degrades performance due to excessive context switching. A smaller, well-tuned pool delivers higher throughput.",
            "doc_url": "https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing",
            "shortcut_tip": "More connections != faster! A pool of 20-50 connections can easily serve 10,000 requests/sec on an 8-core DB."
        },
        {
            "q": "What does a Covered Index mean in SQL query execution?",
            "options": [
                "An index protected by database encryption",
                "An index that contains all the columns requested by the SELECT, WHERE, and JOIN clauses, satisfying the query entirely from index memory without table row lookups",
                "An index covering all tables in the database",
                "An index built on primary keys only"
            ],
            "ans": 1,
            "topic": "Database Indexing Optimization",
            "explanation": "When an index covers all queried fields (using `INCLUDE` in PostgreSQL), the query engine skips expensive heap/table data block lookups entirely.",
            "doc_url": "https://use-the-index-luke.com/sql/clustering/index-organized-tables",
            "shortcut_tip": "Index Only Scan = Query answered 100% from index cache without touching table disk rows."
        },
        {
            "q": "What is Data Idempotency in ETL data pipeline tasks?",
            "options": [
                "Ensuring tasks run only once per calendar year",
                "The property that re-running the same pipeline task with the same input data multiple times produces the identical state without duplicating records",
                "Encrypting pipeline outputs",
                "Converting data to JSON"
            ],
            "ans": 1,
            "topic": "Data Engineering Best Practices",
            "explanation": "If a pipeline fails midway and restarts, idempotent tasks (e.g. partition overwrite instead of append) safely restore state without duplicating records.",
            "doc_url": "https://en.wikipedia.org/wiki/Idempotence",
            "shortcut_tip": "Always write ETL pipelines with `INSERT OVERWRITE PARTITION` or upserts (`ON CONFLICT DO UPDATE`) to ensure idempotency."
        },
        {
            "q": "In MongoDB, what does a compound index on `{ status: 1, created_at: -1 }` support efficiently?",
            "options": [
                "Queries filtering only by `created_at`",
                "Queries filtering by `status` alone, or filtering by `status` AND sorting by `created_at`",
                "Text search across all strings",
                "Only queries on collections with fewer than 100 documents"
            ],
            "ans": 1,
            "topic": "MongoDB Indexing",
            "explanation": "Compound indexes follow the Prefix Rule. An index on (A, B) supports queries on (A) and (A, B), but cannot efficiently support queries on (B) alone.",
            "doc_url": "https://www.mongodb.com/docs/manual/core/index-compound/",
            "shortcut_tip": "ESR Rule for compound indexes: Equality fields first, Sort fields second, Range fields last."
        }
    ],

    "🛡️ Cybersecurity & Network Analyst": [
        {
            "q": "What is the primary difference between Symmetric and Asymmetric encryption?",
            "options": [
                "Symmetric uses the same secret key for encryption and decryption; Asymmetric uses a mathematically linked public and private key pair",
                "Symmetric encryption is only for passwords",
                "Asymmetric encryption does not use keys",
                "Symmetric encryption is impossible to decrypt"
            ],
            "ans": 0,
            "topic": "Cryptography Fundamentals",
            "explanation": "Symmetric (AES) is fast and uses one shared secret key. Asymmetric (RSA/ECC) uses a public key to encrypt and private key to decrypt, solving the key exchange problem.",
            "doc_url": "https://www.cloudflare.com/learning/ssl/what-is-asymmetric-encryption/",
            "shortcut_tip": "Symmetric (AES) = Fast bulk data encryption. Asymmetric (RSA/ECC) = Secure key exchange and digital signatures."
        },
        {
            "q": "In web application security, what is Cross-Site Scripting (XSS)?",
            "options": [
                "An attack where malicious scripts are injected into trusted websites and executed in the victim's browser",
                "Overloading a web server with traffic",
                "Guessing database passwords via brute force",
                "Intercepting Wi-Fi router signals"
            ],
            "ans": 0,
            "topic": "OWASP Top 10 (XSS)",
            "explanation": "XSS allows attackers to execute arbitrary JavaScript in the victim's browser context, stealing session cookies (document.cookie) or redirecting users.",
            "doc_url": "https://owasp.org/www-community/attacks/xss/",
            "shortcut_tip": "Prevent XSS by sanitizing/escaping all output HTML, using Content Security Policy (CSP), and storing session tokens in `HttpOnly` cookies."
        },
        {
            "q": "Why should password authentication always use a slow, adaptive hashing algorithm like `bcrypt` or `Argon2` rather than `MD5` or `SHA-256`?",
            "options": [
                "MD5 produces too long hashes",
                "Fast algorithms like SHA-256 allow attackers to compute billions of guesses per second on modern GPUs; bcrypt includes a tunable work factor (cost) to defeat brute-force and rainbow tables",
                "Bcrypt does not require a database",
                "SHA-256 cannot hash numbers"
            ],
            "ans": 1,
            "topic": "Password Security & Hashing",
            "explanation": "SHA-256 is designed to be fast for verification. Password hashes need to be intentionally slow and salted to make brute-force attacks economically infeasible.",
            "doc_url": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html",
            "shortcut_tip": "Never hash passwords with MD5, SHA-1, or plain SHA-256. Always use `bcrypt` with cost >= 12 or `Argon2id`."
        },
        {
            "q": "What is the role of the `HttpOnly` flag on browser cookies?",
            "options": [
                "Ensures cookies can only be read over HTTP, not HTTPS",
                "Prevents client-side scripts (JavaScript) from accessing `document.cookie`, mitigating credential theft via XSS",
                "Deletes cookies after 1 minute",
                "Disables cookies on mobile devices"
            ],
            "ans": 1,
            "topic": "Web Application Security",
            "explanation": "Even if an attacker finds an XSS vulnerability, an `HttpOnly` cookie cannot be read by `document.cookie` in JavaScript.",
            "doc_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies",
            "shortcut_tip": "Authentication cookie checklist: `HttpOnly` (stops XSS theft), `Secure` (HTTPS only), `SameSite=Strict/Lax` (stops CSRF)."
        },
        {
            "q": "What is the TCP 3-Way Handshake process used to establish a reliable connection?",
            "options": [
                "HELLO -> VERIFY -> CONNECT",
                "SYN -> SYN-ACK -> ACK",
                "PING -> PONG -> ACK",
                "REQ -> RES -> CLOSE"
            ],
            "ans": 1,
            "topic": "Networking Protocols (TCP/IP)",
            "explanation": "1. Client sends SYN (Synchronize). 2. Server responds with SYN-ACK (Acknowledge). 3. Client replies with ACK. Connection established.",
            "doc_url": "https://www.geeksforgeeks.org/tcp-3-way-handshake-process/",
            "shortcut_tip": "Remember: SYN (Let's connect), SYN-ACK (I hear you, let's connect), ACK (Got it, we are connected)."
        },
        {
            "q": "What does a SYN Flood attack attempt to do to a target server?",
            "options": [
                "Downloads all server files",
                "Exhausts server connection backlog queues by sending thousands of SYN packets with spoofed IPs and never completing the final ACK",
                "Corrupts the Linux kernel",
                "Physically damages network cables"
            ],
            "ans": 1,
            "topic": "Network Attacks & DDoS",
            "explanation": "The server allocates memory for half-open connections awaiting ACK. Once the backlog fills up, legitimate clients cannot connect. SYN Cookies mitigate this.",
            "doc_url": "https://www.cloudflare.com/learning/ddos/syn-flood-ddos-attack/",
            "shortcut_tip": "Mitigate SYN floods with SYN Cookies enabled in the Linux kernel (`net.ipv4.tcp_syncookies = 1`)."
        },
        {
            "q": "What is the core principle of a 'Zero Trust' security architecture?",
            "options": [
                "Never trust internal developers",
                "'Never trust, always verify' — treat all network traffic as hostile, requiring continuous verification, strict access controls, and least privilege even inside the perimeter",
                "Disable all corporate firewalls",
                "Ban all cloud infrastructure"
            ],
            "ans": 1,
            "topic": "Zero Trust Security",
            "explanation": "Old security was 'Castle and Moat' (perimeter security). Zero Trust assumes attackers already breached the perimeter; every request must authenticate and authorize.",
            "doc_url": "https://www.nist.gov/publications/zero-trust-architecture",
            "shortcut_tip": "Zero Trust = No implicit trust based on network location or IP address. Continuous authentication + micro-segmentation."
        },
        {
            "q": "What does CSRF (Cross-Site Request Forgery) exploit in web browsers?",
            "options": [
                "Stealing database credentials through brute force",
                "Tricking an authenticated victim's browser into executing unauthorized state-changing actions on a trusted site where they are logged in",
                "Cracking Wi-Fi WPA2 keys",
                "Compromising Linux root access"
            ],
            "ans": 1,
            "topic": "OWASP Top 10 (CSRF)",
            "explanation": "Because browsers automatically send session cookies with cross-site requests, a malicious website can trigger a bank transfer unless CSRF tokens or SameSite cookies protect it.",
            "doc_url": "https://owasp.org/www-community/attacks/csrf",
            "shortcut_tip": "Mitigate CSRF using `SameSite=Lax/Strict` cookies and anti-CSRF synchronizer tokens in form payloads."
        },
        {
            "q": "What is DNS Spoofing / Cache Poisoning?",
            "options": [
                "Deleting domain names from the internet",
                "Injecting corrupt or fraudulent IP address mappings into a recursive DNS resolver cache, redirecting unsuspecting users to a phishing website",
                "Accelerating website loading speeds",
                "Resetting domain registrar passwords"
            ],
            "ans": 1,
            "topic": "DNS & Network Security",
            "explanation": "DNS translates domain names to IPs. If poisoned, typing `bank.com` resolves to the attacker's server. DNSSEC uses cryptographic signatures to prevent this.",
            "doc_url": "https://www.cloudflare.com/learning/dns/dns-cache-poisoning/",
            "shortcut_tip": "DNSSEC (Domain Name System Security Extensions) adds cryptographic signatures to verify DNS records."
        },
        {
            "q": "What does the Principle of Least Privilege (PoLP) dictate?",
            "options": [
                "Giving all employees administrator passwords",
                "Every user, process, and system must have access to only the absolute minimum resources and permissions necessary to perform its legitimate function",
                "Writing the shortest code possible",
                "Restricting work to 4 days a week"
            ],
            "ans": 1,
            "topic": "Security Governance & Access Control",
            "explanation": "If a service account is compromised, least privilege ensures the attacker cannot escalate to root or read unrelated databases.",
            "doc_url": "https://en.wikipedia.org/wiki/Principle_of_least_privilege",
            "shortcut_tip": "Never run Docker containers or web applications as `root`. Create dedicated non-root service accounts."
        },
        {
            "q": "In a TLS / HTTPS handshake, what does the server digital certificate provide to the client?",
            "options": [
                "The server's private key",
                "Cryptographic proof of the server's domain identity signed by a trusted Certificate Authority (CA) and the server's public key",
                "A free domain name",
                "A list of database passwords"
            ],
            "ans": 1,
            "topic": "TLS / SSL Infrastructure (PKI)",
            "explanation": "Browsers store trusted Root CAs. When connecting to `example.com`, the server presents its certificate chain proving ownership of the domain.",
            "doc_url": "https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/",
            "shortcut_tip": "Digital Certificate = Server Public Key + Domain Name + CA Digital Signature. Proves identity and defeats MitM."
        },
        {
            "q": "What does an open network port like 22 commonly correspond to?",
            "options": ["HTTP Web Traffic", "SSH (Secure Shell) Remote Management", "DNS Queries", "MySQL Database"],
            "ans": 1,
            "topic": "Network Ports & Protocols",
            "explanation": "Port 22 is SSH. Port 80 is HTTP. Port 443 is HTTPS. Port 53 is DNS. Port 3306 is MySQL. Port 27017 is MongoDB.",
            "doc_url": "https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers",
            "shortcut_tip": "Never expose port 22 or port 27017/3306 directly to the public internet. Restrict with firewall/VPN."
        },
        {
            "q": "What is a SQL Injection vulnerability caused by?",
            "options": [
                "Running out of hard drive space",
                "Concatenating untrusted user input directly into dynamic SQL query strings without sanitization or parameter binding",
                "Using MySQL instead of PostgreSQL",
                "Writing SQL queries in lowercase"
            ],
            "ans": 1,
            "topic": "OWASP Top 10 (SQL Injection)",
            "explanation": "An input like `' OR '1'='1` alters the SQL syntax logic. Always use Parameterized Queries (Prepared Statements) or ORMs.",
            "doc_url": "https://owasp.org/www-community/attacks/SQL_Injection",
            "shortcut_tip": "Golden Rule: Treat all user input as malicious data, never as executable SQL code."
        },
        {
            "q": "What is Port Scanning tool Nmap primarily used for in defensive security?",
            "options": [
                "Cracking Wi-Fi passwords",
                "Network discovery, identifying active hosts, detecting open ports, running services, and auditing vulnerability exposure on a network",
                "Formatting hard drives",
                "Running antivirus scans on Windows"
            ],
            "ans": 1,
            "topic": "Network Auditing & Penetration Testing",
            "explanation": "Nmap (`nmap -sV -sC target_ip`) identifies exposed attack surfaces so administrators can close unnecessary open ports.",
            "doc_url": "https://nmap.org/book/man.html",
            "shortcut_tip": "Auditing tip: `nmap -sS target` performs a stealth SYN scan to check which ports listen."
        },
        {
            "q": "In authentication, what are the three classic factors of Multi-Factor Authentication (MFA)?",
            "options": [
                "Email, SMS, Phone call",
                "Something you know (password), Something you have (authenticator app/hardware key), and Something you are (biometrics)",
                "Username, Password, PIN",
                "Location, IP address, Device"
            ],
            "ans": 1,
            "topic": "Authentication & MFA",
            "explanation": "True MFA requires at least two distinct categories: Knowledge (knowledge factor), Possession (possession factor), or Inherence (biometric factor).",
            "doc_url": "https://www.cisa.gov/resources-tools/resources/multi-factor-authentication-mfa",
            "shortcut_tip": "Two passwords is NOT two-factor auth! MFA requires two different categories (Password + Authenticator App/YubiKey)."
        }
    ]
}

# ==============================================================================
# HELPER FUNCTIONS: GENERATION & DIAGNOSTIC ROADMAP
# ==============================================================================

def get_available_roles():
    """Returns the available professional roles for selection."""
    return list(ROLE_QUESTIONS.keys())

def generate_test_for_role(role_name: str, num: int = 15):
    """Generates exactly 15 tailored questions for the chosen role."""
    pool = ROLE_QUESTIONS.get(role_name, [])
    if not pool:
        # Fallback to full stack if not matched
        pool = ROLE_QUESTIONS["🌐 Full Stack Developer"]
        
    shuffled = list(pool)
    random.shuffle(shuffled)
    
    # Return exactly min(num, len(shuffled))
    return shuffled[:num]

def build_diagnostic_roadmap(role_name: str, questions: list, answers_record: list):
    """
    Analyzes incorrect answers, groups them by weak topics,
    and returns a tailored shortcut roadmap with direct study links and tips.
    """
    weak_topics_dict = {}
    strong_topics = []
    
    for idx, (q, given_ans) in enumerate(zip(questions, answers_record)):
        is_correct = (given_ans == q["ans"])
        topic = q.get("topic", "General Engineering")
        
        if is_correct:
            if topic not in strong_topics:
                strong_topics.append(topic)
        else:
            if topic not in weak_topics_dict:
                weak_topics_dict[topic] = {
                    "topic": topic,
                    "missed_count": 0,
                    "explanation": q.get("explanation", ""),
                    "doc_url": q.get("doc_url", "https://developer.mozilla.org"),
                    "shortcut_tip": q.get("shortcut_tip", "Review core fundamentals."),
                    "sample_question": q.get("q", "")
                }
            weak_topics_dict[topic]["missed_count"] += 1
            
    # Format into ranked shortcut roadmap steps
    roadmap_steps = []
    for rank, (topic, data) in enumerate(weak_topics_dict.items(), 1):
        est_time = "15 - 25 Mins" if data["missed_count"] == 1 else "45 Mins - 1 Hour"
        roadmap_steps.append({
            "step": rank,
            "topic": topic,
            "priority": "HIGH PRIORITY 🚨" if data["missed_count"] > 1 else "RECOMMENDED ⚡",
            "est_time": est_time,
            "explanation": data["explanation"],
            "shortcut_tip": data["shortcut_tip"],
            "doc_url": data["doc_url"],
            "sample_question": data["sample_question"]
        })
        
    return {
        "weak_count": len(roadmap_steps),
        "strong_count": len(strong_topics),
        "strong_topics": strong_topics,
        "roadmap_steps": roadmap_steps
    }
