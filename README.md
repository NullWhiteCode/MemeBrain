# MemeBrain 😼

A local-first media browser with AI-assisted search and organisation.

Browse, search and organise your local image collection without uploading your files to the cloud.

**Search by filenames, OCR-extracted text, or what's actually in your images using local AI models.**

**Generate searchable descriptions of your images using local AI, then inspect those descriptions alongside image metadata, OCR results and duplicate information.**

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
- ✅ Integrated image viewer
- ✅ Full-size image previews
- ✅ Previous and next image navigation
- ✅ Image metadata display
- ✅ Stored AI caption display
- ✅ Stored OCR text display
- ✅ Exact duplicate information and previews
- ✅ Scrollable image details panel
- ✅ Lightbox-style image viewing
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
- ✅ Caption retrieval and display through the integrated image viewer

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
- ✅ Stored OCR text displayed in the integrated image viewer

### Integrated Image Viewer

The integrated viewer brings together image previews and existing indexed information in a single interface.

- ✅ Full-size image viewing
- ✅ Previous and next image navigation
- ✅ Image filename and technical metadata
- ✅ Stored AI-generated image descriptions
- ✅ Stored OCR-extracted text
- ✅ Exact duplicate information and preview thumbnails
- ✅ Graceful handling of missing caption and OCR records
- ✅ Scrollable information panel
- ✅ Readable formatting for longer descriptions and extracted text
- ✅ Consistent PSone Noir visual styling

The viewer retrieves existing information through Flask JSON endpoints backed by SQLite.

Opening an image does not trigger additional AI inference. Captions and OCR results are read from previously stored records.

### Interface

- ✅ Responsive web interface
- ✅ Native folder picker
- ✅ Caption model selection controls
- ✅ Remember-model preference
- ✅ Caption generation progress panel
- ✅ Live worker status and Generate button updates
- ✅ Flask JSON endpoints for model configuration and processing status
- ✅ Flask JSON endpoint for image metadata, captions, OCR and duplicate information
- ✅ PSone Noir dark interface
- ✅ Charcoal gradient dashboard panels with metallic borders
- ✅ Retro-styled headings, buttons and progress indicators
- ✅ Gallery cards with metallic styling and hover feedback
- ✅ Subtle CRT scanlines, RGB texture and vignette behind gallery cards
- ✅ Preserved thumbnail clarity without CRT distortion
- ✅ Integrated image viewer with matching dark styling
- ✅ Styled metadata rows and information sections
- ✅ Readable caption and OCR panels
- ✅ Responsive dashboard and gallery layout

## Development Roadmap

MemeBrain is under active development.

The roadmap records completed development milestones and identifies longer-term candidates. It is not a fixed release schedule.

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

**Status: Complete**

Replaced the fragmented image-viewing experience with a unified interface that combines full-size media previews and indexed image information.

Delivered:

- Full-size image previews
- Previous and next image navigation
- Image metadata display
- Stored AI-generated captions
- Stored OCR-extracted text
- Exact duplicate information and previews
- Graceful handling of missing caption and OCR records
- Readable formatting for generated and extracted text
- Scrollable details panel
- Consistent PSone Noir styling

The viewer reuses MemeBrain's existing indexing, database, captioning, OCR and duplicate-detection functionality rather than introducing separate processing systems.

Image information is retrieved through Flask JSON endpoints, with caption and OCR records loaded from SQLite.

The viewer does not perform additional AI inference when displaying previously processed images.

### Future Development Candidates

The following features are candidates for future development. Their order and implementation scope have not yet been finalised.

**Semantic Search**

Use local image and text embeddings to retrieve images by meaning rather than relying entirely on exact keyword matches.

This would complement the existing filename, caption and OCR search systems.

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

Caption generation runs in a dedicated background worker thread, with progress reporting, error handling and retry support.

Stored captions are also available in the integrated image viewer, allowing users to inspect the generated descriptions associated with individual images.

Caption generation and caption display are separate operations. Opening the viewer retrieves stored information without loading or running the caption model.

### Text Extraction — RapidOCR

RapidOCR extracts visible text from images.

Extracted text is stored in SQLite and can be searched through OmniSearch.

OCR processing runs in a background worker with manual start and stop controls and progress reporting.

Previously extracted text is also displayed in the integrated image viewer.

RapidOCR currently uses its default model configuration. Custom OCR model selection is planned for a future release.

For animated GIFs, MemeBrain extracts a representative frame for captioning and OCR processing.

### Persistent AI Data

MemeBrain stores generated captions and extracted OCR text in its local SQLite database.

This allows previously processed information to be reused without repeating inference or text extraction.

Stored information supports two primary workflows:

1. **Search:** OmniSearch uses filenames, AI captions and OCR text to find matching images.
2. **Inspection:** The integrated image viewer displays existing caption and OCR records alongside image metadata and duplicate information.

Images without stored captions or OCR results can still be viewed normally. The interface handles missing records without requiring additional processing.

## Development Status

**MemeBrain is under active development.**

The application has established its core local library indexing, thumbnail generation, search, OCR and AI-captioning systems.

Two major interface milestones are complete:

- **Ticket #110 — PSone Noir UI Redesign:** Established MemeBrain's cohesive dark visual identity.
- **Ticket #111 — Integrated Image Viewer:** Unified full-size image previews, navigation, metadata, duplicate information, stored AI captions and OCR results.

MemeBrain now supports a local workflow for indexing images, generating searchable information, finding media through OmniSearch and inspecting stored information within the viewer.

Future development candidates include semantic search, visual similarity detection, AI-assisted file renaming, additional organisation tools and expanded media support.

MemeBrain is not yet a finished release. Features, interfaces and internal architecture may change as development continues.

The long-term goal is a flexible, inspectable and extensible local media manager that remains useful without requiring cloud services, subscriptions or external accounts.

---

**Your memes. Your machine. Your models. 😼**
