# LLM Prompts Repository - Frontend

React frontend for the LLM Prompts Repository application.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (or 16+)
- npm or yarn

### Local Development Setup

1. **Install dependencies:**
```bash
npm install
# or
yarn install
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env if needed (default points to localhost:8000)
```

3. **Start development server:**
```bash
npm run dev
# or
yarn dev
```

The app will be available at `http://localhost:5173`

### 🏗️ Build for Production

```bash
npm run build
# or
yarn build
```

The build output will be in the `dist/` directory.

### 📦 Preview Production Build

```bash
npm run preview
# or
yarn preview
```

## 🎨 Tech Stack

- **React 18** - UI library
- **Vite** - Build tool (faster than Create React App)
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable components
│   │   ├── Header.jsx
│   │   ├── PromptCard.jsx
│   │   ├── PromptModal.jsx
│   │   └── SearchBar.jsx
│   ├── pages/            # Page components
│   │   ├── HomePage.jsx
│   │   └── AddPromptPage.jsx
│   ├── hooks/            # Custom React hooks
│   │   └── usePrompts.js
│   ├── utils/            # Utilities
│   │   └── api.js
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## ✨ Features

### Browse Prompts
- **Search**: Search by title, category, or tags
- **Filter**: Filter by category
- **Sort**: Sort by date (newest) or popularity (most views)
- **View Modes**: Grid or list view
- **Detailed View**: Click any prompt to see full details in a modal

### Add Prompts
- Simple form to add new prompts
- Category selection
- Tag support
- Source attribution
- Real-time validation

### User Experience
- **Copy to Clipboard**: One-click copy of prompt text
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Loading States**: Visual feedback during API calls
- **Error Handling**: User-friendly error messages

## 🔧 Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

For production, update this to your deployed backend URL:
```env
VITE_API_URL=https://your-backend.railway.app
```

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel
3. Configure:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variable: `VITE_API_URL` → your backend URL
4. Deploy!

### Netlify

1. Push your code to GitHub
2. Import project in Netlify
3. Configure:
   - Build Command: `npm run build`
   - Publish Directory: `dist`
   - Environment Variable: `VITE_API_URL` → your backend URL
4. Deploy!

### Manual Deployment

```bash
# Build the project
npm run build

# Upload the dist/ folder to your hosting service
# (AWS S3, DigitalOcean, etc.)
```

## 🎯 Key Components

### HomePage
- Displays all prompts in grid or list view
- Includes search, filter, and sort functionality
- Opens detailed modal when clicking a prompt

### AddPromptPage
- Form to add new prompts
- Validation and error handling
- Auto-redirect after successful submission

### PromptCard
- Displays prompt preview
- One-click copy functionality
- Shows category, tags, views, and date

### PromptModal
- Full prompt details
- Large copy button
- Metadata display
- Keyboard shortcuts (ESC to close)

### SearchBar
- Search input with icon
- Category dropdown filter
- Sort options
- Grid/List view toggle

## 🎨 Customization

### Colors
Edit `tailwind.config.js` to change the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      }
    }
  }
}
```

### Styling
- All styles use Tailwind CSS utility classes
- Custom components defined in `index.css`
- Modify component classes directly in JSX files

## 📱 Responsive Design

The app is fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🔍 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📝 Development Tips

### Hot Module Replacement (HMR)
Vite provides instant HMR - changes appear immediately without full page reload.

### API Proxy
The Vite config includes a proxy to avoid CORS issues in development:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

### Component Development
Components are functional and use React Hooks for state management.

## 🐛 Troubleshooting

**API calls fail:**
- Check that backend is running on port 8000
- Verify VITE_API_URL in .env file
- Check browser console for CORS errors

**Styles not loading:**
- Ensure Tailwind CSS is properly configured
- Run `npm install` to install all dependencies
- Check that index.css imports are correct

**Build fails:**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node.js version (should be 16+)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
