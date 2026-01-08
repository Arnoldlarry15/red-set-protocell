# Adding Your Logo to Red Set ProtoCell UI

## Overview

The Red Set ProtoCell web UI has two locations where your logo should be displayed:
1. **Authentication Page**: Large logo display (120x120px)
2. **Dashboard Header**: Small logo display (48x48px)

Currently, these locations use a placeholder Shield icon. Follow this guide to replace them with your custom logo.

## Step 1: Prepare Your Logo

### Recommended Specifications

**For Authentication Page:**
- Format: PNG or SVG
- Size: 120x120 pixels (or larger, will be scaled)
- Background: Transparent
- Style: Should work on dark backgrounds

**For Dashboard Header:**
- Format: PNG or SVG
- Size: 48x48 pixels (or larger, will be scaled)
- Background: Transparent
- Style: Should work on dark backgrounds

### Naming Convention

Save your logo files as:
- `logo.png` or `logo.svg` for PNG/SVG format
- Optionally, create multiple sizes: `logo-large.png`, `logo-small.png`

## Step 2: Add Logo to Project

Place your logo file(s) in the public directory:

```bash
cp /path/to/your/logo.png /home/runner/work/red-set-protocell/red-set-protocell/rsp-ui/public/logo.png
```

Or if using SVG:

```bash
cp /path/to/your/logo.svg /home/runner/work/red-set-protocell/red-set-protocell/rsp-ui/public/logo.svg
```

## Step 3: Update Authentication Page

Edit `/rsp-ui/src/pages/AuthPage.tsx`:

### Find the Logo Section (around line 34-37):

```tsx
<div className="logo-placeholder">
  <Shield size={64} className="logo-icon" />
</div>
```

### Replace with:

**For PNG logo:**
```tsx
<div className="logo-placeholder">
  <img 
    src="/logo.png" 
    alt="Red Set ProtoCell" 
    style={{ width: '80px', height: '80px', objectFit: 'contain' }}
  />
</div>
```

**For SVG logo:**
```tsx
<div className="logo-placeholder">
  <img 
    src="/logo.svg" 
    alt="Red Set ProtoCell" 
    style={{ width: '80px', height: '80px', objectFit: 'contain' }}
  />
</div>
```

### Optional: Remove the Shield import

If you're no longer using the Shield icon, you can remove it from the imports at the top:

```tsx
// Remove Shield from this line:
import { Shield, Lock } from 'lucide-react';

// Change to:
import { Lock } from 'lucide-react';
```

## Step 4: Update Dashboard Header

Edit `/rsp-ui/src/pages/Dashboard.tsx`:

### Find the Header Logo Section (around line 174-176):

```tsx
<div className="header-logo">
  <Shield size={32} className="header-logo-icon" />
</div>
```

### Replace with:

**For PNG logo:**
```tsx
<div className="header-logo">
  <img 
    src="/logo.png" 
    alt="RSP" 
    style={{ width: '32px', height: '32px', objectFit: 'contain' }}
  />
</div>
```

**For SVG logo:**
```tsx
<div className="header-logo">
  <img 
    src="/logo.svg" 
    alt="RSP" 
    style={{ width: '32px', height: '32px', objectFit: 'contain' }}
  />
</div>
```

### Optional: Remove the Shield import

If you're no longer using the Shield icon on this page, update the imports:

```tsx
// Remove Shield from this line:
import { Shield, Play, Pause, Square } from 'lucide-react';

// Change to:
import { Play, Pause, Square } from 'lucide-react';
```

## Step 5: Adjust Logo Styling (Optional)

If your logo needs custom styling, you can modify the CSS:

### For Authentication Page

Edit `/rsp-ui/src/styles/Auth.css` and add:

```css
.logo-placeholder img {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
  /* Add any additional styling */
}
```

### For Dashboard Header

Edit `/rsp-ui/src/styles/Dashboard.css` and add:

```css
.header-logo img {
  border-radius: 8px;
  /* Add any additional styling */
}
```

## Step 6: Test Your Changes

### Development Server

1. Start the development server:
```bash
cd rsp-ui
npm run dev
```

2. Open http://localhost:3000 in your browser

3. Check both pages:
   - Authentication page: You should see your logo
   - Dashboard: After logging in, check the header logo

### Production Build

1. Build the project:
```bash
npm run build
```

2. Preview the build:
```bash
npm run preview
```

3. Verify logos are displayed correctly

## Common Issues and Solutions

### Logo Not Appearing

**Problem**: Logo file path is incorrect

**Solution**: Ensure the file is in `/rsp-ui/public/` and the path in code matches exactly:
- ✅ Correct: `src="/logo.png"`
- ❌ Incorrect: `src="./logo.png"` or `src="../public/logo.png"`

### Logo Too Large/Small

**Problem**: Logo size doesn't match the design

**Solution**: Adjust the width and height in the style prop:

```tsx
style={{ width: 'XXpx', height: 'XXpx', objectFit: 'contain' }}
```

### Logo Has Wrong Colors

**Problem**: Logo designed for light backgrounds looks bad on dark background

**Solution**: 
1. Create a version of your logo optimized for dark backgrounds
2. Or add a CSS filter to adjust colors:

```css
.logo-placeholder img {
  filter: brightness(1.2) contrast(1.1);
}
```

### Logo Pixelated

**Problem**: PNG logo looks pixelated on high-DPI screens

**Solution**: 
1. Use SVG format instead (recommended)
2. Or provide a larger PNG (2x or 3x the display size)

## Complete Example

Here's a complete example with both locations updated:

### AuthPage.tsx
```tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock } from 'lucide-react';  // Removed Shield
import '../styles/Auth.css';

// ... rest of component code ...

<div className="logo-section">
  <div className="logo-placeholder">
    <img 
      src="/logo.png" 
      alt="Red Set ProtoCell" 
      style={{ width: '80px', height: '80px', objectFit: 'contain' }}
    />
  </div>
  <h1 className="logo-text">RED SET PROTOCELL</h1>
  <p className="logo-subtitle">Autonomous AI Red Teaming System</p>
</div>
```

### Dashboard.tsx
```tsx
import React, { useState } from 'react';
import { Play, Pause, Square } from 'lucide-react';  // Removed Shield
// ... other imports ...

// ... rest of component code ...

<div className="header-left">
  <div className="header-logo">
    <img 
      src="/logo.png" 
      alt="RSP" 
      style={{ width: '32px', height: '32px', objectFit: 'contain' }}
    />
  </div>
  <div className="header-info">
    <h1>RED SET PROTOCELL</h1>
    <p className="session-id">Session: {sessionStats.sessionId}</p>
  </div>
</div>
```

## Next Steps

After adding your logo:

1. **Commit the changes**:
```bash
git add rsp-ui/public/logo.png
git add rsp-ui/src/pages/AuthPage.tsx
git add rsp-ui/src/pages/Dashboard.tsx
git commit -m "Add custom Red Set ProtoCell logo"
```

2. **Update the favicon**: Replace `/rsp-ui/public/shield.svg` with your logo as favicon

3. **Build and deploy**: Follow the deployment guide in WEB_UI_SETUP.md

## Support

If you encounter any issues adding your logo, please:
1. Check the browser console for errors
2. Verify file paths and formats
3. Ensure the logo file was uploaded correctly
4. Review the examples in this guide

For additional help, open an issue on the GitHub repository.
