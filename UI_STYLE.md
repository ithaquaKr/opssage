# Claude UI Design Style Guide

## Overview

This document defines the design system and visual language used in Claude's interface. Use these guidelines to create interfaces that feel consistent with Claude's aesthetic.

---

## Color Palette

### Primary Colors

- **Background**: `#FFFFFF` (White)
- **Text Primary**: `#1F1F1F` (Near Black)
- **Text Secondary**: `#666666` (Medium Gray)
- **Accent Orange**: `#CC785C` (Warm terracotta)
- **Accent Hover**: `#B86B50` (Darker orange)

### Neutral Scale

- **Gray 50**: `#F9F9F9` (Lightest background)
- **Gray 100**: `#F3F3F3` (Hover states)
- **Gray 200**: `#E5E5E5` (Borders)
- **Gray 300**: `#D4D4D4` (Dividers)
- **Gray 400**: `#A3A3A3` (Disabled text)
- **Gray 500**: `#737373` (Secondary text)
- **Gray 600**: `#525252` (Body text)
- **Gray 900**: `#171717` (Headings)

### Semantic Colors

- **Success**: `#16A34A` (Green)
- **Warning**: `#EA580C` (Orange)
- **Error**: `#DC2626` (Red)
- **Info**: `#2563EB` (Blue)

---

## Typography

### Font Family

- **Primary**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- **Monospace**: `"SF Mono", "Monaco", "Inconsolata", "Fira Code", "Dank Mono", monospace`

### Font Sizes

```css
--text-xs: 0.75rem; /* 12px */
--text-sm: 0.875rem; /* 14px */
--text-base: 1rem; /* 16px */
--text-lg: 1.125rem; /* 18px */
--text-xl: 1.25rem; /* 20px */
--text-2xl: 1.5rem; /* 24px */
--text-3xl: 1.875rem; /* 30px */
```

### Font Weights

- **Regular**: `400`
- **Medium**: `500`
- **Semibold**: `600`
- **Bold**: `700`

### Line Heights

- **Tight**: `1.25`
- **Normal**: `1.5`
- **Relaxed**: `1.625`
- **Loose**: `1.75`

---

## Spacing System

Use a consistent 4px base unit spacing scale:

```css
--space-1: 0.25rem; /* 4px */
--space-2: 0.5rem; /* 8px */
--space-3: 0.75rem; /* 12px */
--space-4: 1rem; /* 16px */
--space-5: 1.25rem; /* 20px */
--space-6: 1.5rem; /* 24px */
--space-8: 2rem; /* 32px */
--space-10: 2.5rem; /* 40px */
--space-12: 3rem; /* 48px */
--space-16: 4rem; /* 64px */
```

---

## Border Radius

```css
--radius-sm: 0.25rem; /* 4px - Small elements */
--radius-md: 0.5rem; /* 8px - Buttons, inputs */
--radius-lg: 0.75rem; /* 12px - Cards */
--radius-xl: 1rem; /* 16px - Large containers */
--radius-full: 9999px; /* Fully rounded */
```

---

## Components

### Buttons

#### Primary Button

```css
background: #cc785c;
color: #ffffff;
padding: 0.625rem 1.25rem; /* 10px 20px */
border-radius: 0.5rem; /* 8px */
font-weight: 500;
font-size: 0.875rem; /* 14px */
border: none;
transition: all 0.2s ease;

/* Hover */
background: #b86b50;
transform: translateY(-1px);
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
```

#### Secondary Button

```css
background: #ffffff;
color: #1f1f1f;
padding: 0.625rem 1.25rem;
border-radius: 0.5rem;
font-weight: 500;
font-size: 0.875rem;
border: 1px solid #e5e5e5;
transition: all 0.2s ease;

/* Hover */
background: #f9f9f9;
border-color: #d4d4d4;
```

#### Ghost Button

```css
background: transparent;
color: #666666;
padding: 0.5rem 0.75rem;
border-radius: 0.5rem;
font-weight: 500;
font-size: 0.875rem;
border: none;

/* Hover */
background: #f3f3f3;
color: #1f1f1f;
```

### Input Fields

```css
background: #ffffff;
border: 1px solid #e5e5e5;
border-radius: 0.5rem;
padding: 0.625rem 0.875rem; /* 10px 14px */
font-size: 0.875rem;
color: #1f1f1f;
transition: all 0.2s ease;

/* Focus */
border-color: #cc785c;
outline: none;
box-shadow: 0 0 0 3px rgba(204, 120, 92, 0.1);

/* Disabled */
background: #f9f9f9;
color: #a3a3a3;
cursor: not-allowed;
```

### Cards

```css
background: #ffffff;
border: 1px solid #e5e5e5;
border-radius: 0.75rem; /* 12px */
padding: 1.5rem; /* 24px */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
transition: all 0.2s ease;

/* Hover (if interactive) */
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
border-color: #d4d4d4;
```

### Message Bubbles

#### User Message

```css
background: #f9f9f9;
border-radius: 1rem 1rem 0.25rem 1rem;
padding: 0.875rem 1rem;
color: #1f1f1f;
max-width: 70%;
margin-left: auto;
```

#### Assistant Message

```css
background: #ffffff;
border: 1px solid #e5e5e5;
border-radius: 1rem 1rem 1rem 0.25rem;
padding: 0.875rem 1rem;
color: #1f1f1f;
max-width: 70%;
```

### Navigation

```css
background: #ffffff;
border-right: 1px solid #e5e5e5;
padding: 1rem;
width: 260px;

/* Navigation Item */
.nav-item {
    padding: 0.625rem 0.875rem;
    border-radius: 0.5rem;
    color: #666666;
    font-size: 0.875rem;
    transition: all 0.15s ease;
}

.nav-item:hover {
    background: #f3f3f3;
    color: #1f1f1f;
}

.nav-item.active {
    background: #fdf6f3;
    color: #cc785c;
    font-weight: 500;
}
```

### Tooltips

```css
background: #1f1f1f;
color: #ffffff;
padding: 0.5rem 0.75rem;
border-radius: 0.375rem;
font-size: 0.75rem;
line-height: 1.25;
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
```

### Modals

```css
background: #ffffff;
border-radius: 1rem;
padding: 2rem;
box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
max-width: 500px;
width: 90%;

/* Backdrop */
.modal-backdrop {
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
}
```

---

## Layout Principles

### Container Widths

- **Small**: `640px`
- **Medium**: `768px`
- **Large**: `1024px`
- **XL**: `1280px`
- **Chat Container**: `768px` (max-width for readable conversation)

### Grid System

- Use CSS Grid or Flexbox
- Standard gap: `1rem` (16px)
- Sidebar width: `260px`
- Main content: `flex: 1` or `minmax(0, 1fr)`

---

## Animation & Transitions

### Default Transition

```css
transition: all 0.2s ease;
```

### Easing Functions

- **Ease**: `cubic-bezier(0.25, 0.1, 0.25, 1)` - Default
- **Ease-out**: `cubic-bezier(0, 0, 0.2, 1)` - Exit animations
- **Ease-in**: `cubic-bezier(0.4, 0, 1, 1)` - Enter animations

### Common Animations

#### Fade In

```css
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

animation: fadeIn 0.3s ease;
```

#### Slide Up

```css
@keyframes slideUp {
    from {
        transform: translateY(10px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

animation: slideUp 0.3s ease;
```

---

## Elevation (Shadows)

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 2px 4px rgba(0, 0, 0, 0.08);
--shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 8px 24px rgba(0, 0, 0, 0.12);
--shadow-2xl: 0 20px 50px rgba(0, 0, 0, 0.15);
```

---

## Icons

### Icon Sizes

- **Small**: `16px`
- **Medium**: `20px`
- **Large**: `24px`
- **XL**: `32px`

### Icon Style

- Use outline/stroke icons by default
- Stroke width: `1.5px` to `2px`
- Match icon color to text color
- Recommended: Lucide Icons, Heroicons, or Feather Icons

---

## Responsive Breakpoints

```css
/* Mobile First Approach */
--breakpoint-sm: 640px; /* Small devices */
--breakpoint-md: 768px; /* Tablets */
--breakpoint-lg: 1024px; /* Desktops */
--breakpoint-xl: 1280px; /* Large screens */
--breakpoint-2xl: 1536px; /* Extra large screens */
```

---

## Accessibility

### Focus States

```css
/* All interactive elements should have visible focus */
:focus-visible {
    outline: 2px solid #cc785c;
    outline-offset: 2px;
}
```

### Color Contrast

- Maintain WCAG AA standard (4.5:1 for normal text)
- Primary text on white: `#1F1F1F` (16.4:1 ratio)
- Secondary text on white: `#666666` (5.7:1 ratio)

### Interactive Elements

- Minimum touch target: `44px × 44px`
- Clickable areas should be generous
- Clear hover and active states

---

## Best Practices

### Design Principles

1. **Clarity Over Cleverness** - Prioritize readability and usability
2. **Generous Whitespace** - Let content breathe
3. **Consistent Hierarchy** - Use size, weight, and color to establish importance
4. **Subtle Interactions** - Animations should enhance, not distract
5. **Responsive by Default** - Design for mobile first, enhance for desktop

### Component Guidelines

- Keep components simple and composable
- Use semantic HTML elements
- Implement proper ARIA labels
- Test with keyboard navigation
- Ensure screen reader compatibility

### Performance

- Minimize animation complexity
- Use CSS transforms for animations (GPU accelerated)
- Lazy load images and heavy components
- Optimize font loading

---

## Code Examples

### React Component Example (Tailwind)

```jsx
// Primary Button
<button className="bg-[#CC785C] hover:bg-[#B86B50] text-white font-medium
  text-sm py-2.5 px-5 rounded-lg transition-all duration-200
  hover:-translate-y-0.5 hover:shadow-md">
  Send Message
</button>

// Card Component
<div className="bg-white border border-gray-200 rounded-xl p-6
  shadow-sm hover:shadow-md transition-all duration-200">
  <h3 className="text-lg font-semibold text-gray-900 mb-2">
    Card Title
  </h3>
  <p className="text-sm text-gray-600">
    Card content goes here
  </p>
</div>
```

### CSS Variables Implementation

```css
:root {
    /* Colors */
    --color-primary: #cc785c;
    --color-primary-hover: #b86b50;
    --color-text-primary: #1f1f1f;
    --color-text-secondary: #666666;
    --color-border: #e5e5e5;
    --color-background: #ffffff;
    --color-background-hover: #f9f9f9;

    /* Spacing */
    --space-4: 1rem;
    --space-6: 1.5rem;

    /* Radius */
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;

    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 2px 4px rgba(0, 0, 0, 0.08);
}
```

---

## Resources

### Design Tools

- Use Figma for mockups and prototypes
- Refer to claude.ai for live examples
- Test in multiple browsers and devices

### Recommended Libraries

- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Unstyled, accessible components
- **Framer Motion** - Animation library
- **Lucide React** - Icon library

---

## Version

Document Version: 1.0
Last Updated: December 2024
Based on: Claude.ai interface design

---

_This style guide is intended for use with Claude Code and other development tools to maintain consistency with Claude's visual design language._
