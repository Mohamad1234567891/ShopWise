# Contribution Report — Ömer Ağaoğlu

**Student Name:** ÖMER AĞAOĞLU  
**Student ID:** 2509115344  
**GitHub Username:** omraga000  
**Project:** ShopWise

## 1. User Interface Architecture and Core Components

I was responsible for designing and implementing the graphical user interface (GUI) of ShopWise using the PySide6 (Qt for Python) framework.

The implemented interface components include:

- **Search Bar and Header Controls:** Designed and implemented an intuitive search bar allowing users to enter queries smoothly, complete with custom search buttons, clear inputs, and action triggers.
- **Product Card Display Widgets:** Created modular, reusable product card widgets to display individual item details, including product titles, price tags, visual indicators, ratings, and deal highlights.
- **Scrollable Product View:** Built smooth, responsive scroll areas (`QScrollArea`) to handle long lists of search results and product comparisons without UI lag.
- **Loading Indicators and States:** Implemented visual loading indicators and progress states to provide dynamic user feedback while asynchronous data fetching and product processing take place.
- **Interactive Action Buttons:** Implemented and connected interactive control buttons (filtering triggers, view toggles, and detail inspections).

## 2. Visual Styling, Layouts, and User Experience (UX)

I developed the entire visual identity and styling system for the desktop application using Qt Style Sheets (QSS):

- **Modern Visual Theme:** Created a cohesive color scheme, balanced margins, rounded card corners, and modern drop-shadow effects to give the application a clean, professional aesthetic.
- **Dynamic Layout Management:** Structured layouts using nested vertical and horizontal box layouts (`QVBoxLayout`, `QHBoxLayout`, and `QGridLayout`) to ensure the user interface scales responsively across different screen sizes and resolutions.
- **Component States & Transitions:** Styled interactive states for buttons and inputs (normal, hover, pressed, and disabled states) to enhance accessibility and user feedback.

## 3. UI-Data Integration and Event Handling

My contribution bridged the graphical interface with the application's underlying logic:

- Connected UI signals and slots to link user actions (such as submitting a search query or clicking a product card) to backend processing pipelines.
- Formatted raw product attributes into visually structured layouts within the product cards.
- Ensured smooth thread handling so that search operations and calculations do not freeze the main graphical interface during runtime.

## 4. Libraries Used

The implementations described in this report rely on the following libraries:

- **PySide6 (Qt for Python)**
  - `PySide6.QtWidgets`: Used for core UI elements (`QWidget`, `QPushButton`, `QLineEdit`, `QScrollArea`, `QVBoxLayout`, `QHBoxLayout`, `QLabel`).
  - `PySide6.QtCore`: Used for event handling, Qt alignment flags, and signal-slot communication.
  - `PySide6.QtGui`: Used for custom fonts, icons, color palettes, and rendering.

## 5. Key Contributions

My main contribution to ShopWise was engineering the complete front-end user experience and desktop interface.

Specifically, I developed the search inputs, custom product card widgets, scrollable containers, dynamic loading indicators, and overall layout styling using PySide6.

Together, these contributions translate the project's data processing and ranking algorithms into an interactive, intuitive, and responsive desktop application for the end user.