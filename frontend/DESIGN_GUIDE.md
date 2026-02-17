# Red Set ProtoCell Design System Guide

## Overview

The Red Set ProtoCell UI implements a modern, cohesive design system with glassmorphism effects, dynamic animations, and a comprehensive color palette centered around the red (#ef4444) brand color. This guide documents the design tokens, component architecture, and best practices for maintaining visual consistency.

---

## Table of Contents

1. [Color System](#color-system)
2. [Typography](#typography)
3. [Spacing & Layout](#spacing--layout)
4. [Components](#components)
5. [Animations](#animations)
6. [Accessibility](#accessibility)
7. [Responsive Design](#responsive-design)
8. [Image Optimization](#image-optimization)
9. [Performance Guidelines](#performance-guidelines)

---

## Color System

### Primary Colors

- **Red (Primary)**: `#ef4444` - Main brand color, used for CTAs and highlights
- **Red Dark**: `#dc2626` - Hover states and emphasis
- **Red Light**: `#f87171` - Lighter accents and backgrounds
- **Red Lighter**: `#fca5a5` - Subtle backgrounds
- **Red Accent**: `#991b1b` - Deep emphasis

### Neutral Colors

- **Black**: `#0a0a0a` - Primary background
- **Dark**: `#1a1a1a` - Secondary background
- **White**: `#ffffff` - Primary text
- **Gray**: `#9ca3af` - Secondary text
- **Gray Light**: `#e5e7eb` - Tertiary text

### Status Colors

- **Success**: `#22c55e` - Positive states
- **Warning**: `#eab308` - Attention states
- **Info**: `#0077bb` - Informational
- **Critical**: `#dc2626` - Error/critical states

### Glass Effects

```css
--glass-bg: rgba(26, 26, 26, 0.7);
--glass-bg-dark: rgba(10, 10, 10, 0.85);
--glass-border: rgba(255, 255, 255, 0.1);
--glass-border-accent: rgba(239, 68, 68, 0.2);
--glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
```

---

## Typography

### Font Stack

```css
font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
font-family (mono): 'Courier New', 'Courier', monospace;
```

### Font Weights

- Light: 300
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700
- Extrabold: 800
- Black: 900

### Font Sizes

| Size | Value | Usage |
|------|-------|-------|
| xs | 0.75rem (12px) | Labels, badges |
| sm | 0.875rem (14px) | Helper text |
| base | 1rem (16px) | Body text |
| lg | 1.125rem (18px) | Card headers |
| xl | 1.25rem (20px) | Section headers |
| 2xl | 1.5rem (24px) | Page headers |
| 3xl | 1.875rem (30px) | Hero titles (second) |
| 4xl | 2.25rem (36px) | Component titles |
| 5xl | 3rem (48px) | Hero titles (main) |

---

## Spacing & Layout

### Spacing Scale

All spacing uses a consistent 4px baseline:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 0.25rem (4px) | Minimal gaps |
| sm | 0.5rem (8px) | Compact spacing |
| md | 1rem (16px) | Standard spacing |
| lg | 1.5rem (24px) | Component spacing |
| xl | 2rem (32px) | Section spacing |
| 2xl | 2.5rem (40px) | Large gaps |
| 3xl | 3rem (48px) | Extra large gaps |
| 4xl | 4rem (64px) | Huge gaps |

### Border Radius

- **sm**: 8px - Subtle rounding
- **md**: 12px - Standard rounding
- **lg**: 16px - Card rounding
- **xl**: 20px - Large elements
- **2xl**: 24px - Extra large
- **full**: 9999px - Pill buttons

---

## Components

### Glass Panel

The fundamental component using glassmorphism:

```css
.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--glass-shadow);
}

.glass-panel-dark {
  background: var(--glass-bg-dark);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--glass-shadow);
}
```

### Button Variants

#### Primary Button
- Background: Red (#ef4444)
- Hover: Darker red with glow shadow
- Active: Reduced glow
- Disabled: 50% opacity

#### Secondary Button
- Background: Glass panel
- Border: White (10% opacity)
- Hover: Lighter glass with red border
- Active: Darker background

#### Ghost Button
- Background: Transparent
- Border: Glass border
- Hover: Red border and text

### Cards & Panels

All cards use the glass-panel base with consistent:
- Padding: 20px
- Border-radius: var(--radius-lg)
- Transition: all 0.3s ease
- Hover effects: Border color change, subtle scale

### Form Controls

- **Input/Textarea/Select**: Glass background with 12px padding
- **Focus state**: Red border with 0 0 0 3px red glow
- **Error state**: Red border with red background overlay

---

## Animations

### Animation Timing

- **Fast**: 0.15s ease-out (micro-interactions)
- **Base**: 0.3s ease (standard transitions)
- **Slow**: 0.5s ease-in-out (complex animations)
- **Slower**: 0.8s ease-in-out (hero animations)

### Key Animations

#### Pulse Red
Fades opacity for attention-grabbing:
```css
@keyframes pulse-red {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

#### Slide In Up
Entry animation from bottom:
```css
@keyframes slide-in-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

#### Glow
Red glow pulse effect:
```css
@keyframes glow {
  0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
  50% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.6); }
}
```

#### Float
Subtle vertical movement:
```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
```

### Usage Classes

- `.animate-pulse-red` - Attention pulse
- `.animate-slide-in` - Entrance animation
- `.animate-glow` - Red glow effect
- `.animate-float` - Floating motion
- `.animate-bounce` - Bounce effect
- `.animate-spin` - Rotation
- `.animate-shake` - Error shake

---

## Accessibility

### Color Contrast

All text colors meet WCAG AA standards (4.5:1 minimum):

- White text on dark backgrounds: ✓
- Red text on dark backgrounds: ✓ (4.9:1)
- Gray text on dark backgrounds: ✓ (4.6:1)

### Keyboard Navigation

- All interactive elements are keyboard accessible
- Focus indicators use red border with glow
- Tab order follows visual left-to-right flow

### Screen Readers

- All images include descriptive alt text
- Button purposes are clear without color alone
- Form labels are properly associated with inputs
- Error messages are announced to screen readers

### Reduced Motion

Components respect `prefers-reduced-motion`:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

---

## Responsive Design

### Breakpoints

| Device | Breakpoint | Usage |
|--------|-----------|-------|
| Mobile | 480px max | Phones |
| Tablet | 768px max | Tablets |
| Small Laptop | 1024px max | Small laptops |
| Desktop | 1280px+ | Desktop |
| Large | 1536px+ | 4K displays |

### Responsive Grid

**Desktop**: 3-column layout (2:2:1)
```css
grid-template-columns: 1fr 1fr 400px;
```

**Tablet**: 2-column layout (1:1)
```css
grid-template-columns: 1fr 400px;
```

**Mobile**: 1-column layout
```css
grid-template-columns: 1fr;
```

### Touch Targets

On mobile, all interactive elements meet 44×44px minimum:

```css
.btn {
  padding: 10px 16px; /* Desktop */
}

@media (max-width: 768px) {
  .btn {
    padding: 12px 20px; /* Larger for touch */
  }
}
```

---

## Image Optimization

### Image Assets Configuration

Images are configured in `src/config/imageAssets.ts` with CDN URLs for optimal delivery.

### Lazy Loading

```tsx
<img 
  src={imageAssets.heroes.redSetProtocell}
  alt="Descriptive text"
  loading="lazy"
  decoding="async"
/>
```

### Blur-Up Effect

For hero images, a placeholder blur effect is applied:

```tsx
import { BlurUpImage } from '../utils/imageOptimization';

// Initialize with low-res placeholder
const blurUp = new BlurUpImage(imgElement);
await blurUp.initializeWithPlaceholder(lowResUrl);
```

### Responsive Images

Use srcset for multiple device resolutions:

```tsx
import { generateResponsiveSrcSet } from '../utils/imageOptimization';

const srcSet = generateResponsiveSrcSet(imageUrl);
<img srcSet={srcSet} sizes="(max-width: 768px) 100vw, 50vw" />
```

---

## Performance Guidelines

### Image Performance Targets

- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Lighthouse Score**: > 90

### Image Optimization Checklist

- [ ] All images use CDN with format parameter (webp)
- [ ] Image quality set to 85% for balance
- [ ] Max width optimized for viewport
- [ ] Lazy loading enabled for below-fold images
- [ ] Alt text is descriptive and meaningful
- [ ] Srcset includes multiple resolutions
- [ ] Placeholder images are used for above-fold content

### CSS Performance

- [ ] CSS is minified in production
- [ ] Media queries are mobile-first
- [ ] `will-change` is used sparingly
- [ ] Animations use `transform` and `opacity` only
- [ ] Glass effects use GPU acceleration via `backdrop-filter`

### JavaScript Performance

- [ ] Image preloading is done asynchronously
- [ ] Intersection Observer for lazy loading
- [ ] Debounced resize handlers
- [ ] Memoized React components
- [ ] Code splitting for large components

---

## Usage Examples

### Creating a New Component

```tsx
import '../styles/Components.css';

interface MyComponentProps {
  title: string;
  children: React.ReactNode;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, children }) => {
  return (
    <div className="glass-panel">
      <div className="panel-header">
        <div className="panel-header-title">
          <h3>{title}</h3>
        </div>
      </div>
      {children}
    </div>
  );
};
```

### Using Design Tokens

```css
.my-custom-element {
  padding: var(--space-lg);
  font-size: var(--font-base);
  font-weight: var(--font-semibold);
  color: var(--color-white);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.my-custom-element:hover {
  border-color: var(--color-red);
  box-shadow: var(--shadow-red-md);
  transform: translateY(-2px);
}
```

### Adding Animations

```tsx
<div className="animate-slide-in">
  <h2>This slides in from bottom</h2>
</div>

<button className="animate-glow">
  Glowing button
</button>
```

---

## Testing Checklist

### Visual Testing

- [ ] All colors render correctly
- [ ] Fonts render properly (especially Inter)
- [ ] Glassmorphism blur is visible
- [ ] Shadow effects are subtle and professional
- [ ] Animations are smooth (60fps)

### Responsive Testing

- [ ] Mobile (375px): All content visible, touch targets adequate
- [ ] Tablet (768px): Layout adjusts appropriately
- [ ] Desktop (1440px): Full multi-column layout works
- [ ] 4K (2560px): Content doesn't stretch excessively

### Browser Testing

- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Accessibility Testing

- [ ] Keyboard navigation works throughout
- [ ] Screen reader announces content correctly
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Focus indicators are visible
- [ ] Motion animations can be disabled

### Performance Testing

- [ ] Lighthouse score > 90
- [ ] LCP < 2.5s
- [ ] First Contentful Paint < 2s
- [ ] Total Blocking Time < 200ms
- [ ] Images optimized and compressed

---

## Maintenance

### Updating Design Tokens

Design tokens are defined in `globals.css`. To update:

1. Modify CSS variables in `:root`
2. All components automatically update
3. No individual file changes needed

### Adding New Colors

```css
:root {
  --color-new-color: #123456;
  --color-new-color-dark: #0a1b2c;
}
```

### Creating New Animations

```css
@keyframes my-animation {
  from { /* initial state */ }
  to { /* final state */ }
}

.animate-my-animation {
  animation: my-animation var(--transition-base);
}
```

---

## Support & Questions

For questions about the design system, refer to:
- Color definitions: `globals.css` `:root`
- Component styles: `Components.css`
- Page styles: `Auth.css`, `Dashboard.css`
- Image assets: `config/imageAssets.ts`
- Image utilities: `utils/imageOptimization.ts`

---

**Last Updated**: 2024
**Version**: 1.0.0
**Status**: Production Ready
