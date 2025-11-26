# OpsSage Dashboard

Modern, beautiful web dashboard for OpsSage - Multi-Agent Incident Analysis & Remediation System.

## Features

- **Real-time Incident Monitoring**: View and track all incidents analyzed by the system
- **Alert Submission**: Submit alerts directly from the dashboard
- **Knowledge Base Management**: Upload, manage, and search documents, playbooks, and incident reports
- **Semantic Search**: Search the knowledge base using AI-powered semantic similarity
- **Interactive Data Tables**: Browse incidents and documents with AG Grid
- **Responsive Design**: Beautiful, modern UI built with Tailwind CSS
- **Type-Safe**: Full TypeScript support throughout

## Tech Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Full type safety
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **AG Grid**: Enterprise-grade data tables
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **Lucide React**: Beautiful icon library
- **date-fns**: Modern date utility library
- **react-hot-toast**: Elegant toast notifications

## Prerequisites

- Node.js 18+ (20+ recommended)
- npm or yarn
- OpsSage backend running on `http://localhost:8000`

## Installation

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Development

### Project Structure

```
dashboard/
├── src/
│   ├── api/              # API client and endpoints
│   │   └── client.ts     # Axios client and API functions
│   ├── components/       # Reusable UI components
│   │   ├── Layout.tsx    # Main layout with navigation
│   │   ├── Card.tsx      # Card component
│   │   ├── Button.tsx    # Button component
│   │   └── Badge.tsx     # Badge component
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx        # Dashboard overview
│   │   ├── Alerts.tsx           # Alert submission
│   │   ├── Incidents.tsx        # Incidents list
│   │   ├── IncidentDetail.tsx   # Incident details
│   │   ├── Documents.tsx        # Document management
│   │   └── Search.tsx           # Knowledge search
│   ├── types/            # TypeScript type definitions
│   │   └── index.ts      # All types and interfaces
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # App entry point
│   └── index.css         # Global styles
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies and scripts
```

### Available Scripts

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### API Integration

The dashboard connects to the OpsSage backend through a proxy configured in `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

All API calls are made through the centralized API client in `src/api/client.ts`.

## Usage

### Dashboard Overview

The main dashboard shows:
- Total incidents count
- Active incidents count
- Documents and playbooks count
- Recent incidents list

### Submitting Alerts

1. Navigate to **Alerts** page
2. Fill in alert details:
   - Alert name
   - Severity (critical, high, medium, low)
   - Message
   - Firing condition
   - Labels (optional)
3. Click **Submit Alert**
4. You'll be redirected to the incident detail page

### Viewing Incidents

1. Navigate to **Incidents** page
2. Browse all incidents in the data table
3. Filter by status (pending, analyzing, completed, failed)
4. Click on any incident to view full details
5. View diagnostic report, root cause analysis, and remediation recommendations

### Managing Documents

1. Navigate to **Documents** page
2. Select collection (Documents, Playbooks, or Incidents)
3. Click **Upload** to add new documents
4. Upload supported formats: TXT, MD, PDF, DOCX, JSON
5. Set document type and category
6. View and delete documents from the table

### Searching Knowledge Base

1. Navigate to **Search** page
2. Enter your search query (natural language supported)
3. Select collection to search
4. Click **Search**
5. Results are ranked by semantic relevance
6. View matching document excerpts with relevance scores

## Customization

### Styling

The dashboard uses Tailwind CSS for styling. To customize:

1. Edit `tailwind.config.js` to change theme colors
2. Modify `src/index.css` for global styles
3. Use Tailwind utility classes in components

### Adding New Pages

1. Create new page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/Layout.tsx`

### API Endpoints

All API endpoints are defined in `src/api/client.ts`. To add new endpoints:

```typescript
export const newApi = {
  getData: () => client.get('/new-endpoint'),
  postData: (data: any) => client.post('/new-endpoint', data),
}
```

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Output will be in dist/ directory
```

The production build can be served with any static file server:

```bash
# Preview production build
npm run preview

# Or use any static server
npx serve dist
```

## Deployment

### Docker

Create a `Dockerfile` in the dashboard directory:

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Variables

For production deployments, configure the backend API URL:

```typescript
// vite.config.ts
export default defineConfig({
  // ...
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(
      process.env.VITE_API_URL || 'http://localhost:8000'
    ),
  },
})
```

## Troubleshooting

### Backend Connection Issues

If the dashboard can't connect to the backend:

1. Ensure backend is running: `http://localhost:8000`
2. Check proxy configuration in `vite.config.ts`
3. Verify CORS settings in backend
4. Check browser console for errors

### Build Errors

If you encounter build errors:

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite

# Rebuild
npm run build
```

### Type Errors

If TypeScript shows errors:

```bash
# Rebuild type declarations
npm run build

# Check TypeScript configuration
npx tsc --noEmit
```

## Contributing

When contributing to the dashboard:

1. Follow the existing code style
2. Use TypeScript for all new code
3. Add types for all API responses
4. Test your changes in both dev and production builds
5. Ensure responsive design works on mobile

## License

Apache License 2.0 - Same as OpsSage main project

## Support

For issues and questions:
- GitHub Issues: https://github.com/ithaquaKr/opssage/issues
- Documentation: https://github.com/ithaquaKr/opssage/docs
