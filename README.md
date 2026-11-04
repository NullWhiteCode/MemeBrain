# MemeBrain 😼

A local-first media browser with AI-assisted search and organisation.

Browse, search and organise your local image collection without uploading your files to the cloud.

**Search by filenames, OCR-extracted text, or what's actually in your images using local AI models.**

**Generate searchable descriptions of your images using local AI.**

Coming later: AI-assisted file renaming using locally generated image descriptions.

Designed for people whose folders look like this:

```text
Memes/
├── Reaction Images/
├── Downloads/
├── New Folder (7)/
├── Untitled.png
├── Untitled (2).png
└── IMG_0835.PNG
```

## Philosophy

- 🖥️ Local first
- 🔒 Offline by default
- 👤 You own your data
- 🤖 Bring your own AI model
- 🚫 No telemetry
- ☁️ No hidden uploads
- 🔍 Everything should be inspectable
- 😑 Content agnostic _(yes, **those** folders work too...)_

MemeBrain is designed around local processing, user control and inspectable behaviour.

Your media stays on your machine. AI processing uses locally installed models rather than cloud-based inference services.

## Current Features

### Library

- ✅ Recursive folder scanning
- ✅ Persistent library selection
- ✅ Persistent SQLite library index
- ✅ Automatic library synchronisation
- ✅ File change and missing-file tracking
- ✅ Breadcrumb navigation
- ✅ Folder navigation

### Media

- ✅ Thumbnail gallery
- ✅ Cached thumbnail generation
- ✅ Background thumbnail generation
- ✅ Local image viewer
- ✅ Image metadata viewer
- ✅ Lightbox image preview
- ✅ Animated GIF support in AI captioning and OCR through representative-frame extraction

### Search

- ✅ Instant filename search
- ✅ Exact duplicate detection
- ✅ OmniSearch combining filename, OCR and AI caption results
- ✅ Search image contents using AI-generated descriptions
- ✅ Search text extracted from images using OCR
- ✅ SQLite persistence of searchable caption and OCR data

### AI Caption Generation

- ✅ Local image caption generation using Qwen3-VL
- ✅ Image content analysis without cloud uploads
- ✅ GIF caption generation using representative frames
- ✅ User-selectable local caption model directory
- ✅ Optional persistence of selected model configuration
- ✅ Automatic restoration of remembered model selection
- ✅ Background caption generation using a dedicated worker thread
- ✅ Batch-based caption processing
- ✅ Live caption generation progress
- ✅ Worker lifecycle reporting: idle, running, completed and failed
- ✅ Per-image error handling
- ✅ Model-loading and worker failure recovery
- ✅ Retry support after failed generation
- ✅ Persistent caption storage in SQLite

### OCR

- ✅ Local text extraction using RapidOCR
- ✅ OCR support for animated GIFs using representative frames
- ✅ Background OCR processing
- ✅ Persistent OCR results in SQLite
- ✅ OCR results integrated into OmniSearch
- ✅ OCR engine and version metadata stored alongside results
- ✅ OCR worker progress and lifecycle reporting
- ✅ Manual OCR start and stop controls
- ✅ OCR processing status displayed in the interface

### Interface

- ✅ Responsive web interface
- ✅ Native folder picker
- ✅ Caption model selection controls
- ✅ Remember-model preference
- ✅ Caption generation progress panel
- ✅ Live worker status and Generate button updates
- ✅ Flask JSON endpoints for model configuration and processing status
- ✅ PSone Noir dark interface
- ✅ Charcoal gradient dashboard panels with metallic borders
- ✅ Retro-styled headings, buttons and progress indicators
- ✅ Gallery cards with metallic styling and hover feedback
- ✅ Subtle CRT scanlines, RGB texture and vignette behind gallery cards
- ✅ Preserved thumbnail clarity without CRT distortion
- ✅ Responsive dashboard and gallery layout

## Development Roadmap

MemeBrain is under active development. The roadmap identifies the next development priority and longer-term candidates; it is not a fixed release schedule.

### Ticket #110 — PSone Noir UI Redesign

**Status: Complete**

Introduced MemeBrain's first cohesive visual identity, inspired by late-1990s console interfaces.

Delivered:

- Five-panel dashboard styling
- Charcoal gradients and metallic borders
- Pixel-style headings
- Consistent button interactions
- Styled progress indicators
- Metallic gallery cards
- Subtle CRT gallery background
- Scanlines, RGB texture and vignette
- Processing-panel spacing improvements
- Responsive layout polish

The CRT effect is intentionally restricted to the gallery background. Image content remains unaffected.

### Ticket #111 — Integrated Image Viewer

**Status: Next — Planning**

Replace the fragmented image-viewing experience with a unified interface that brings together the image and its associated information.

Proposed capabilities:

- Full-size image viewing
- Image metadata
- Stored AI-generated captions
- Stored OCR-extracted text
- Navigation between gallery images
- Consistent integration with the PSone Noir interface

The viewer should reuse existing indexing, database and processing functionality rather than duplicate it.

Scope, interaction design and implementation details will be established before development begins.

### Future Development Candidates

**Semantic Search**

Use local image and text embeddings to retrieve images by meaning rather than relying entirely on exact keyword matches.

**AI-Assisted File Renaming**

Generate descriptive filenames using existing AI captions, with user review and confirmation before modifying files.

**Visual Similarity and Reverse Image Search**

Identify visually related images, including images that may not be byte-for-byte duplicates.

**Organisation Tools**

Introduce tagging and additional ways to manage and organise media collections.

**Configurable Interface Skins**

Expand beyond PSone Noir with alternative visual themes and appearance preferences.

## Planned Features

### Search

- Semantic image search using embeddings
- Reverse image search
- Visual similarity ranking
- Improved search relevance and ranking

### Organisation

- Tagging
- AI-assisted file renaming
- Descriptive filename generation
- EXIF support
- Multi-folder libraries

### Media

- Integrated image viewer (Ticket #111)
- Expanded GIF support
- Video support
- AI-assisted image editing

### AI and Processing

- Optional automatic background OCR
- Persistent OCR processing preferences
- Optional custom OCR models or alternative OCR engines
- Improved background and idle-time processing

### Interface and Appearance

- Configurable UI skins
- Appearance preferences
- Further responsive layout improvements
- Expanded image-viewer interactions

### Integrations

- Plugin system
- REST API
- ComfyUI nodes

### Quality of Life

- Idle indexing
- System tray integration
- Additional background processing controls

## AI Processing

MemeBrain currently uses two separate local processing systems.

### Image Captioning — Qwen3-VL

Qwen3-VL generates natural-language descriptions of image contents.

These descriptions are stored in SQLite and made searchable through OmniSearch.

Users can select a locally installed caption model directory and optionally remember that selection between application sessions.

Caption generation runs in a background worker, with progress reporting, error handling and retry support.

### Text Extraction — RapidOCR

RapidOCR extracts visible text from images.

Extracted text is stored in SQLite and can be searched through OmniSearch.

OCR processing runs in a background worker with manual start and stop controls and progress reporting.

RapidOCR currently uses its default model configuration. Custom OCR model selection is planned for a future release.

For animated GIFs, MemeBrain extracts a representative frame for captioning and OCR processing.

## Development Status

**MemeBrain is under active development.**

The application has established its core local library indexing, thumbnail generation, search, OCR and AI-captioning systems.

The PSone Noir interface redesign is complete. The next planned development task is Ticket #111, integrating image viewing and stored image information into a unified experience.

MemeBrain is not yet a finished release. Features, interfaces and internal architecture may change as development continues.

The long-term goal is a flexible, inspectable and extensible local media manager that remains useful without requiring cloud services, subscriptions or external accounts.

---

**Your memes. Your machine. Your models. 😼**
