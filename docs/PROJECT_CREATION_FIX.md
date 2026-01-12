# Project Creation Fix

## Issue
Pressing "Create Project" button gets stuck/hangs.

## Root Cause
The project creation endpoint calls Ollama to generate PROJECT.md, which can:
1. Take a long time (default timeout was 300 seconds)
2. Hang if Ollama server is not running
3. Hang if Ollama server is slow to respond
4. Have no timeout on frontend requests

## Fixes Applied

### Backend Changes

1. **Added Ollama availability check** (`backend/app/api/projects.py`)
   - Checks if Ollama server is available before attempting generation
   - Falls back to basic PROJECT.md if Ollama is not available
   - Falls back to basic PROJECT.md if generation fails

2. **Reduced default timeout** (`backend/app/core/settings.py`)
   - Changed from 300 seconds to 120 seconds (2 minutes)

3. **Better error handling**
   - Catches Ollama connection errors
   - Provides fallback project creation without AI

### Frontend Changes

1. **Added request timeout** (`frontend/src/services/api.ts`)
   - Set axios timeout to 120 seconds (2 minutes)

2. **Improved error messages** (`frontend/src/components/Project/NewProject.tsx`)
   - Shows actual error message from backend
   - Better user feedback

3. **Enhanced loading state**
   - Added loading spinner
   - Added helpful message during creation
   - Disabled cancel button during loading

## Behavior Now

### If Ollama is Available
1. Check Ollama server (5 second timeout)
2. Generate PROJECT.md with AI (up to 2 minutes)
3. Create project with AI-generated content

### If Ollama is Not Available
1. Check Ollama server fails quickly (5 seconds)
2. Create basic PROJECT.md immediately
3. Project is created successfully without AI

### If Ollama Generation Fails
1. Attempt AI generation
2. If it fails, fallback to basic PROJECT.md
3. Project is created successfully

## Testing

To test the fix:

1. **With Ollama running:**
   ```bash
   ollama serve  # In one terminal
   # Then create project - should work with AI generation
   ```

2. **Without Ollama:**
   ```bash
   # Stop Ollama or don't start it
   # Create project - should work with basic PROJECT.md
   ```

3. **Check browser console:**
   - Look for any error messages
   - Check network tab for request status

## User Experience

- **Before**: Button gets stuck, no feedback, user doesn't know what's happening
- **After**: 
  - Shows loading spinner
  - Shows "Creating Project..." message
  - Shows helpful text about generation taking time
  - Times out after 2 minutes with error message
  - Works even if Ollama is not available
