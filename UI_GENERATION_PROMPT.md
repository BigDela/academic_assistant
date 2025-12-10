# Academic Assistant UI Generation Prompt for bolt.new / v0

## Project Overview
Create a modern, responsive UI component library for an academic resource-sharing platform. The design system should be easily integrable into an existing Django 6.0 project with minimal modifications.

## Design System Specifications

### Color Palette
**Light Mode:**
- Primary Blue: `#4A90E2`
- Light Blue (backgrounds): `#E8F4FD`
- Dark Blue (hover states): `#2E5C8A`
- Accent Blue: `#5BA3F5`
- Text Dark: `#2C3E50`
- Text Gray: `#6B7280`
- Border Color: `#E5E7EB`
- White: `#FFFFFF`
- Success: `#10B981`
- Danger: `#EF4444`
- Warning: `#F59E0B`

**Dark Mode:**
- Primary Blue: `#5BA3F5`
- Light Blue (backgrounds): `#1E3A5F`
- Dark Blue (accents): `#6BB6FF`
- Accent Blue: `#7EC8FF`
- Text Dark: `#E5E7EB`
- Text Gray: `#9CA3AF`
- Border Color: `#374151`
- White (cards/surfaces): `#1F2937`
- Background Gradient: `linear-gradient(135deg, #111827 0%, #1F2937 100%)`

### Typography
- **Font Family:** Inter (Google Fonts) with system fallbacks: `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Font Weights:** 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Base Line Height:** 1.6
- **Font Sizes:**
  - Hero headings: 2.5rem (40px)
  - Section headings: 1.75rem - 2rem (28-32px)
  - Card titles: 1.25rem (20px)
  - Body text: 1rem (16px)
  - Small text/metadata: 0.85rem - 0.9rem (14-15px)

### Layout Architecture

#### Left Sidebar Navigation
- **Width (expanded):** 260px
- **Width (collapsed):** 70px
- **Features:**
  - Fixed position, full height (100vh)
  - Smooth collapse animation (cubic-bezier(0.4, 0, 0.2, 1))
  - White background with subtle shadow
  - Scrollable content area
  - Sticky header with brand logo
  - Bottom footer with user profile
  - Toggle button for collapse/expand
  
- **Navigation Sections:**
  1. Main (Home, Groups, Documents)
  2. Social (Friends, Messages)
  3. Account (Profile, Settings)

- **Mobile Behavior:**
  - Slides in from left with overlay backdrop
  - Hamburger menu button (fixed top-left)
  - Overlay closes on tap
  - Breakpoint: 968px

#### Main Content Area
- **Margin-left:** Adjusts based on sidebar state (260px expanded, 70px collapsed)
- **Max-width:** 1200px (centered)
- **Padding:** 2rem 1.5rem
- **Background:** Light gradient (`linear-gradient(135deg, #E8F4FD 0%, #F0F9FF 100%)`)

### Component Library Needed

#### 1. Navigation Components
**Sidebar Navigation:**
```html
- Collapsible sidebar with icon + text labels
- Active state highlighting (blue background)
- Hover states (light blue background)
- Icons only mode when collapsed
- User avatar with profile picture support
```

**Mobile Menu:**
```html
- Hamburger button (48x48px, rounded corners)
- Slide-in drawer animation
- Dark overlay backdrop (rgba(0,0,0,0.5))
- Close on outside click
```

#### 2. Button Components
**Styles Needed:**
- `.btn` - Base button (padding: 0.625rem 1.25rem, border-radius: 8px)
- `.btn-primary` - Blue background, white text, hover lift effect
- `.btn-outline` - Transparent with blue border, fills on hover
- `.btn-danger` - Red background for destructive actions
- `.btn-small` - Compact version (padding: 0.375rem 0.75rem)
- All buttons have smooth transitions and hover scale/shadow effects

#### 3. Card Components
**Feature Card:**
```css
- White background, rounded corners (12px)
- Subtle shadow (0 2px 8px rgba(0,0,0,0.08))
- Padding: 2rem
- Hover: lift (-4px) + stronger shadow
- Icon (2.5rem), title (1.25rem), description (0.9rem)
```

**User/Group Card:**
```css
- Horizontal flex layout
- Avatar circle (50-60px) with gradient background
- Content area with name + metadata
- Action buttons on right
- Light blue background on hover
```

**Profile Card:**
```css
- Larger padding (2rem - 2.5rem)
- Header section with large avatar (120px)
- Info sections with labeled fields
- Action buttons at bottom
```

#### 4. Form Components
**Input Fields:**
```css
- Width: 100%
- Padding: 0.875rem 1rem
- Border: 2px solid #E5E7EB
- Border-radius: 8px
- Focus: Blue border + shadow ring (0 0 0 3px rgba(74,144,226,0.1))
- Smooth transitions on all states
```

**Textarea:**
```css
- Same styling as inputs
- Min-height: 120px
- Resize: vertical
```

**Select Dropdown:**
```css
- Matches input styling
- Custom arrow icon if possible
```

**File Upload:**
```css
- Custom styled file input
- Drag-and-drop zone option
- File preview capability
```

#### 5. Messaging Components
**Chat Interface:**
```css
Messenger-style layout:
- Left sidebar (360px) with member list
- Main chat area with messages container
- Messages aligned left (others) / right (own)
- Bubble design (rounded 18px)
- Own messages: blue background, white text
- Other messages: white background, gray text, left corner squared
- Message input: rounded textbox (24px) with circular send button
- Animations: slide-in on new messages
```

**Chat List Item:**
```css
- Avatar (60px circle)
- Username + last message preview
- Timestamp (top-right)
- Unread badge (optional)
- Hover: light blue background
```

#### 6. Profile Components
**Profile Header:**
```css
- Large avatar (120px) with image support + placeholder fallback
- Name (1.75rem bold)
- Username (1.1rem gray)
- Metadata badges (program, year, etc.)
- Action buttons row
```

**Profile Sections:**
```css
- White cards with section titles
- Info grid layout (auto-fit, minmax(200px, 1fr))
- Label/value pairs
- Empty states with helpful text
```

#### 7. List Components
**Friends List:**
```css
- Grid layout (auto-fill, minmax(280px, 1fr))
- Cards with avatar + name + actions
- Multiple sections (friends, requests, suggestions)
- Section headers with counts
```

**Document List:**
```css
- Table or card-based layout
- File type icons
- Download/view actions
- Filter options
- Tags/metadata display
```

#### 8. Modal/Dialog Components
**Overlay Modal:**
```css
- Centered on screen
- Dark backdrop (rgba(0,0,0,0.5))
- White card (max-width: 600px)
- Close button (top-right)
- Form content area
- Action buttons (bottom)
```

#### 9. Alert/Toast Components
**Toast Notifications:**
```css
- Fixed position (top-right)
- Slide-in animation from right
- Color-coded (success: green, error: red, info: blue)
- Auto-dismiss after 5 seconds
- Close button
- Max-width: 400px
```

### Animation Specifications

**Standard Transitions:**
```css
transition: all 0.2s ease;  /* Default for buttons, cards */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);  /* Sidebar, major layout shifts */
```

**Hover Effects:**
```css
- Cards: transform: translateY(-4px) + shadow increase
- Buttons: transform: translateY(-2px) + shadow
- Icons/small buttons: transform: scale(1.05)
```

**Slide-in Animation:**
```css
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
/* Duration: 0.3s ease-out */
```

**Message Animation:**
```css
@keyframes messageSlideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
/* Duration: 0.2s ease-out */
```

### Responsive Breakpoints

**Desktop (>968px):**
- Full sidebar visible
- Multi-column layouts
- Hover states active

**Tablet (768px - 968px):**
- Sidebar overlay mode
- 2-column grids
- Adjusted padding

**Mobile (<768px):**
- Single column layouts
- Stacked navigation
- Full-width components
- Touch-friendly sizing (min 44px tap targets)
- Larger fonts for readability

### Accessibility Requirements
- WCAG 2.1 AA compliant contrast ratios
- Keyboard navigation support (Tab, Enter, Escape)
- Focus visible states (blue outline/shadow)
- ARIA labels for icon-only buttons
- Screen reader friendly alt text
- Skip navigation links

### Dark Mode Implementation
Use CSS variables for all colors. Body class toggle:
```css
body.dark-mode {
  /* All color variables redefined */
}
```
Theme persists via localStorage, toggled by button in user profile.

## Integration Requirements

### Expected Output Format
Generate standalone HTML files with:
1. Inline CSS (for easy extraction to Django templates)
2. Minimal JavaScript (vanilla JS, no framework dependencies)
3. Django template placeholder syntax ready:
   - `{{ variable }}` for data binding
   - `{% url 'name' %}` for links
   - `{% for item in list %}` for loops
   - `{% if condition %}` for conditionals

### Component Structure
Each component should be:
- **Self-contained:** Can be copied into Django template
- **CSS Variables:** All colors via var(--color-name)
- **No external dependencies:** Except Google Fonts (Inter)
- **Mobile-first:** Responsive by default
- **Accessible:** Semantic HTML5, ARIA where needed

### File Organization
Provide components in separate files:
```
/components
  /navigation
    sidebar.html
    mobile-menu.html
  /buttons
    button-variants.html
  /cards
    feature-card.html
    user-card.html
    profile-card.html
  /forms
    input-group.html
    textarea.html
    file-upload.html
  /messaging
    chat-interface.html
    chat-list-item.html
  /modals
    modal-template.html
  /alerts
    toast-notification.html
```

## Usage Example
Here's how components integrate into Django:
```django
{% extends 'base.html' %}
{% block content %}
<!-- Drop in component HTML here -->
<div class="feature-card">
  <div class="feature-icon">📚</div>
  <h3>{{ title }}</h3>
  <p>{{ description }}</p>
  <a href="{% url 'detail' id=item.id %}" class="btn btn-primary">
    View Details
  </a>
</div>
{% endblock %}
```

## Key Differences from Standard Frameworks
- **No React/Vue:** Pure HTML + CSS + vanilla JS
- **Django template syntax:** Ready for {{ variables }}
- **Inline styles:** All CSS in `<style>` tags (not external files)
- **No build step:** Direct copy-paste into Django templates
- **Progressive enhancement:** Works without JS, enhanced with JS

## Deliverables Requested
1. **Complete component library** (all components listed above)
2. **Base layout template** (sidebar + main content wrapper)
3. **Dark mode toggle** (JavaScript + CSS)
4. **Responsive navigation** (mobile menu with overlay)
5. **Demo pages** showing components in use:
   - Landing page with hero + features
   - Dashboard with sidebar + cards
   - Profile page with user info sections
   - Chat interface (Messenger-style)
   - Form page with all input types
   - List page with grid layout

## Design Inspiration
Style should feel like:
- **Modern web apps:** Clean, minimal, lots of white space
- **Messenger/WhatsApp:** For chat interfaces
- **Notion/Linear:** For card-based layouts
- **GitHub:** For list views and navigation
- **Tailwind CSS aesthetics:** But implemented with custom CSS

## Color Psychology
- **Blue tones:** Trust, professionalism, academic setting
- **Light backgrounds:** Clean, uncluttered, focus on content
- **Subtle shadows:** Depth without heavy visual weight
- **Rounded corners:** Friendly, modern, approachable

Generate components that match this exact design system while being flexible enough to handle various content types common in an academic platform (documents, groups, messages, profiles, etc.).
